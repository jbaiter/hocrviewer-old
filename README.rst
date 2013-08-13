hOCRviewer
==========
This application will display hOCR files using the OpenLibrary BookReader.
To run it, you need Flask, lxml, wand and whoosh.
Edit the ``BOOK_PATH`` variable in ``app.py`` to suit your environment and run
the app with::

    $ python app.py

You can now access the web interface on port 5000.

The directory with the books should have the following structure::

    +<bookname>
        <bookname>.hocr
        +img
            0000.png
            0001.png
            ...

To generate an index with all of your books, direct a HTTP GET query to the
``/api/reindex`` endpoint.
