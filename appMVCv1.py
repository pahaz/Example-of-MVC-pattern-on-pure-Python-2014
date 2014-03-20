# ===========================
# Example of MVC pattern on pure Python. Whiten for "Use Python in the Web"
# course. Institute Mathematics and Computer Science at Ural Federal University
# in 2014.
#
# By Pahaz Blivon.
# ===========================

__author__ = 'pahaz'

# ===========================
#
#        Utilities
#
# ===========================

from cgi import escape
from urlparse import parse_qs


def http_status(code):
    return "200 OK" if code == 200 else "404 Not Found"


def parse_http_get_data(environ):
    return parse_qs(environ["QUERY_STRING"])


def take_one_or_None(dict_, key):
    """
    Take one value by key from dict or return None.

        >>> d = {"foo":[1,2,3], "baz":7}
        >>> take_one_or_None(d, "foo")
        1
        >>> take_one_or_None(d, "bar") is None
        True
        >>> take_one_or_None(d, "baz")
        7
    """
    val = dict_.get(key)
    if type(val) in (list, tuple) and len(val) > 0:
        val = val[0]
    return val


# ===========================
#
#           Model
#
# ===========================

import shelve


class TextModel(object):
    DB_FILE = 'main.db'

    def __init__(self):
        self._db = shelve.open(self.DB_FILE)

    def get_content_by(self, title):
        return self._db.get(title)

    def get_all_titles(self):
        return self._db.keys()

    def create(self, title, content):
        if title in self._db:
            return False

        self._db[title] = content
        self._db.sync()
        return True


# ===========================
#
#         Controller
#
# ===========================


class TextController(object):
    def __init__(self, model, index_view, add_view):
        self.model = model
        self.index_view = index_view
        self.add_view = add_view

    def index(self, request_get_data):
        title = take_one_or_None(request_get_data, 'title')
        content = self.model.get_content_by(title)
        titles = self.model.get_all_titles()
        context = {
            'titles': titles,
            'current_content': content,
            'current_title': title,
        }
        return 200, self.index_view.render(context)

    def add(self, request_get_data):
        title = take_one_or_None(request_get_data, 'title')
        content = take_one_or_None(request_get_data, 'content')

        if not title or not content:
            error = "Need fill the form fields."
        else:
            error = None
            is_created = self.model.create(title, content)
            if not is_created:
                error = "Title already exist."

        context = {
            'title': title,
            'content': content,
            'error': error,
        }
        return 200, self.add_view.render(context)


# ===========================
#
#           View
#
# ===========================

class TextIndexView(object):
    @staticmethod
    def render(context):
        context['titles'] = [
            '<li>{0}</li>'.format(x) for x in context['titles']
        ]
        context['titles'] = '\n'.join(context['titles'])

        t = """
        <form method="GET">
            <input type=text name=title placeholder="Text title" />
            <input type=submit value=read />
        </form>
        <form method="GET" action="/text/add">
            <input type=text name=title placeholder="Text title" /> <br>
            <textarea name=content placeholder="Text content!" ></textarea> <br>
            <input type=submit value=write />
        </form>
        <h1>{current_title}</h1>
        <div>{current_content}</div>
        <ul>{titles}</ul>
        """
        return t.format(**context)


class RedirectView(object):
    @staticmethod
    def render(context):
        return '<meta http-equiv="refresh" content="0; url=/text" />'


# ===========================
#
#          WSGI
#
# ===========================

text_model = TextModel()
text_controller = TextController(text_model, TextIndexView, RedirectView)


def application(environ, start_response):
    request_path = environ["PATH_INFO"]
    request_get_data = parse_http_get_data(environ)

    if request_path == "/text":
        processor = text_controller.index
    elif request_path == "/text/add":
        processor = text_controller.add
    elif request_path == "/":
        processor = lambda x: (200, "Index HI!")
    else:
        processor = defaut_prcessor

    http_status_code, response_body = processor(request_get_data)
    # response_body += '<br><br> The request ENV: {0}'.format(repr(environ))
    http_status_code_and_msg = http_status(http_status_code)
    response_headers = [('Content-Type', 'text/html')]

    start_response(http_status_code_and_msg, response_headers)
    return [response_body]  # it could be any iterable.


def defaut_prcessor(environ, start_response):
    return 404, "Nooo 404!"