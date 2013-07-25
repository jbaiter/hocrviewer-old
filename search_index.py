from __future__ import unicode_literals

import os
import re
from lxml import etree

from whoosh import highlight
from whoosh.fields import Schema, ID, NUMERIC, TEXT
from whoosh.index import create_in, open_dir
from whoosh.query import And, Term
from whoosh.qparser import QueryParser

schema = Schema(
    bookname=ID(stored=True),
    pagenum=NUMERIC(stored=True),
    content=TEXT(stored=True)
)

BOOK_PATH = os.path.join(os.path.expanduser('~'), 'scans')
INDEX_PATH = os.path.join(BOOK_PATH, '.index')


class StringFormatter(highlight.Formatter):
    def __init__(self, begin_str, end_str):
        self.begin_str = begin_str
        self.end_str = end_str

    def format_token(self, text, token, replace=False):
        tokentext = highlight.get_text(text, token, replace)
        return "{0}{1}{2}".format(self.begin_str, tokentext, self.end_str)


def _get_index():
    if not os.path.exists(INDEX_PATH):
        os.mkdir(INDEX_PATH)
        ix = create_in(INDEX_PATH, schema)
    else:
        ix = open_dir(INDEX_PATH)
    return ix


def index_book(bookname):
    # TODO: Index by paragraph, not page
    idx = _get_index()
    writer = idx.writer()
    writer.delete_by_term('bookname', unicode(bookname))
    path = os.path.join(BOOK_PATH, bookname, "{0}.hocr".format(bookname))
    bookname = unicode(os.path.splitext(os.path.basename(path))[0])
    booktree = etree.parse(path)
    for page in booktree.xpath('//div[@class="ocr_page"]'):
        # Get cleaned up text for page
        text = "\n".join("".join(x.itertext()).strip()
                         for x in page.xpath('.//span[@class="ocr_line"]'))
        pagenum = int(page.get('id')[5:])
        writer.add_document(bookname=bookname, pagenum=pagenum, content=text)
    writer.commit()


def search(term, bookname=None, limit=None):
    out_list = []
    with _get_index().searcher() as searcher:
        parser = QueryParser("content", schema=schema)
        query = parser.parse(term)
        if bookname:
            query = And([query, Term("bookname", unicode(bookname))])
        results = searcher.search(query, limit=limit)
        results.fragmenter.charlimit = None
        results.formatter = StringFormatter('{{{', '}}}')
        for hit in results:
            out_list.append({
                'bookname': hit['bookname'],
                'pagenum': hit['pagenum'],
                'snippet': hit.highlights("content"),
                'highlights': _get_highlights(hit)
            })
    return out_list


def _get_highlights(result):
    # FIXME: This is f*****ing slow...
    highlights = []
    fname = os.path.join(BOOK_PATH, result['bookname'],
                         "{0}.hocr".format(result['bookname']))
    tree = etree.parse(fname)
    page = tree.xpath('//div[@id="page_{0}"]'.format(result['pagenum']))[0]
    hl_tokens = re.findall(r'{{{([^{}]+)}}}', result.highlights("content"))
    for token in hl_tokens:
        occurences = [x for x in page.xpath('.//span[@class="ocrx_word"]')
                      if x.text and token.lower() in x.text.lower()]
        for hit in occurences:
            highlights.append(tuple(hit.get('title').replace('bbox ', '')
                              .split(' ')))
    return tuple(highlights)
