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

    def get(self, name, default_value):
        return self._db.get(name, default_value)

    def all(self):
        return self._db.keys()

    def set(self, key, value):
        self._db[key] = value
        self._db.sync()

    def delete(self, key):
        del self._db[key]
        self._db.sync()


# ===========================
#
#   Controller and Router
#
# ===========================

class Router(object):
    def __init__(self):
        self._paths = {}

    def route(self, environ, start_response):
        path = environ['PATH_INFO']
        query_dict = parse_qs(environ['QUERY_STRING'])

        # try:
        #     request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        # except ValueError:
        #     request_body_size = 0
        #
        # request_body = environ['wsgi.input'].read(request_body_size)
        # body_query_dict = parse_qs(request_body)
        # print(body_query_dict)

        if path in self._paths:
            res = self._paths[path](query_dict)
        else:
            res = self.default_response(query_dict)

        return res

    def register(self, path, callback):
        self._paths[path] = callback

    def default_response(self, *args):
        return 404, "Nooo 404!"


class TextController(object):
    @staticmethod
    def index(query_dict):
        text = query_dict.get('id', [''])[0]
        text = model.get(text, '')

        titles = model.all()
        context = {
            'titles': titles,
            'text': text,
        }

        return 200, view_text.render(context)

    @staticmethod
    def add(query_dict):
        key = query_dict.get('k', [''])[0]
        value = query_dict.get('v', [''])[0]
        model.set(key, value)
        context = {'url': "/text"}
        return 200, view_redirect.render(context)


# ===========================
#
#           View
#
# ===========================

class TextView(object):
    @staticmethod
    def render(context):
        context['titles'] = [
            '<li>{0}</li>'.format(x) for x in context['titles']
        ]
        context['titles'] = '\n'.join(context['titles'])

        t = """
        <form method="GET">
            <input type=text name=id />
            <input type=submit value=read />
        </form>
        <form method="GET" action="/text/add" >
            <input type=text name=k /> <input type=text name=v />
            <input type=submit value=write />
        </form>
        <div style="color: gray;">{text}</div>
        <ul>{titles}</ul>
        """
        return t.format(**context)


class RedirectView(object):
    @staticmethod
    def render(context):
        return '<meta http-equiv="refresh" content="0; url={url}" />' \
            .format(**context)


# ===========================
#
#          Main
#
# ===========================

rout = Router()
model = TextModel()
view_text = TextView()
view_redirect = RedirectView()
controller = TextController()

rout.register('/', lambda x: (200, "Index HI!"))
rout.register('/text', controller.index)
rout.register('/text/add', controller.add)


# ===========================
#
#          WSGI
#
# ===========================

def application(environ, start_response):
    http_status_code, response_body = rout.route(environ, start_response)
    response_body += '<br><br> The request ENV: {0}'.format(repr(environ))
    http_status_code_and_msg = http_status(http_status_code)
    response_headers = [('Content-Type', 'text/html')]

    start_response(http_status_code_and_msg, response_headers)
    return [response_body]  # it could be any iterable.
