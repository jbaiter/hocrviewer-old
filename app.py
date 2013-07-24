import os

from flask import Flask, jsonify, abort, request, send_file
from wand.image import Image

# NOTE: This directory should contain one subdirectory per book, structured as
#       follows:
#         <name>.hocr
#         img/<pagenum>.jpg
#       pagenum should be zero-padded to four, i.e. 0001.jpg
BOOK_PATH = os.path.join(os.path.expanduser('~'), 'scans')

app = Flask(__name__)


@app.route('/')
def list():
    """ Return list of all available books. """
    return jsonify(os.listdir(BOOK_PATH))


@app.route('/reindex')
@app.route('/reindex/<str:bookname>')
def reindex(bookname=None):
    """ Recreate Whoosh index for all or a single book. """
    if bookname and not bookname in os.listdir(BOOK_PATH):
        abort(404)
    # TODO: Reindex whoosh with either all books or the specific bookname
    raise NotImplementedError


@app.route('/<str:bookname>', methods=['GET'])
def get_book(bookname):
    """ Obtain metadata for book. """
    if not bookname in os.listdir(BOOK_PATH):
        abort(404)
    # TODO: Open book.hocr, read DC metadata header, turn to json
    raise NotImplementedError


@app.route('/<str:bookname>/toc', methods=['GET'])
def get_book_toc(bookname):
    """ Obtain table of contents for book. """
    if not bookname in os.listdir(BOOK_PATH):
        abort(404)
    # TODO: Open book.hocr, extract toc structure, turn to json
    raise NotImplementedError


@app.route('<str:bookname>/search/<str:search_term>', methods=['GET'])
def search_book(bookname, search_term):
    """ Search for a pattern inside a book. """
    if not bookname in os.listdir(BOOK_PATH):
        abort(404)
    # TODO: Use Whoosh to obtain page, higlighted terms and context
    # TODO: To get the coordinates of our match:
    #   - Search for occurences, where the first highlighted term appears
    #     followed by the second term, etc.
    #   - Get coordinates for every occurance
    #   - If Y is the same for both occurance, merge the two
    #   Compare to Islandora source, they used the same approach for their
    #   highlighting
    # TODO: Construct a dict from results, turn to json
    raise NotImplementedError


@app.route('/<str:bookname>/dimensions/<int:page_idx>', methods=['GET'])
def get_dimensions(bookname, page_idx):
    """ Obtain width and height for a given page from a book. """
    if not bookname in os.listdir(BOOK_PATH):
        abort(404)
    fname = os.path.join(BOOK_PATH, 'img', '0:04.jpg'.format(page_idx))
    if not os.path.exists(fname):
        abort(404)
    with Image(filename=fname) as img:
        dimensions = {'width': img.width, 'height': img.height}
    return jsonify(dimensions)


@app.route('/<str:bookname>/img/<int:page_idx>', methods=['GET'])
def get_image(bookname, page_idx):
    """ Obtain the image of a given page from a book. """
    if not bookname in os.listdir(BOOK_PATH):
        abort(404)
    fname = os.path.join(BOOK_PATH, 'img', '0:04.jpg'.format(page_idx))
    if not os.path.exists(fname):
        abort(404)
    scale_factor = request.args.get('scale', type=int)
    rotate = request.args.get('rotate', type=int)
    if not scale_factor and not rotate:
        return send_file(fname, mimetype='image/jpeg')
    with Image(fname) as img:
        if scale_factor:
            # TODO: What is the exact form of the zoom parameter?
            img.transform("{0}x{1}".format(scale_factor*img.width,
                                           scale_factor*img.height))
        if rotate:
            img.rotate(rotate)
        # TODO: Send it via send_file + StringIO
        raise NotImplementedError


@app.route('/<str:bookname>/read/<int:page_idx>', methods=['GET'])
def read_page(bookname, page_idx):
    """ Obtain spoken text of given page. """
    if not bookname in os.listdir(BOOK_PATH):
        abort(404)
    # TODO: Return MP3 with voice that reads the page at page_idx
    raise NotImplementedError


if __name__ == '__main__':
    app.run(debug=True)
