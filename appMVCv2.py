# ===========================
# Example of MVC pattern on pure Python. Whiten for "Use Python in the Web"
# course. Institute Mathematics and Computer Science at Ural Federal University
# in 2014.
#
# By Pahaz Blivon.
# ===========================

__author__ = "pahaz"

DB_FILE = "main.db"
DEBUG = False

# ===========================
#
#        Utilities
#
# ===========================

from cgi import escape
from urlparse import parse_qs
import shelve


def http_status(code):
    """
    Return a str representation of HTTP response status from int `code`.
    """
    return "200 OK" if code == 200 else "404 Not Found"


def parse_http_post_data(environ):
    """
    Parse a HTTP post data form WSGI `environ` argument.
    """
    try:
        request_body_size = int(environ.get("CONTENT_LENGTH", 0))
    except ValueError:
        request_body_size = 0

    request_body = environ["wsgi.input"].read(request_body_size)
    body_query_dict = parse_qs(request_body)

    return body_query_dict


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
#         1. Model
#
# ===========================


class TextModel(object):
    def __init__(self, title, content):
        self.title = title
        self.content = content


class TextManager(object):
    def __init__(self):
        self._db = shelve.open(DB_FILE)

    def get_by_title(self, title):
        """
        Get Text object by name if exist else return None.
        """
        content = self._db.get(title)
        return TextModel(title, content) if content else None

    def get_all(self):
        """
        Get list of all Text objects.
        """
        return [
            TextModel(title, content) for title, content in self._db.items()
        ]

    def create(self, title, content):
        self._db[title] = content
        self._db.sync()

    def delete(self, title):
        del self._db[title]
        self._db.sync()


# ===========================
#
#   Controller and Router
#
# ===========================

class Router(object):
    """
    Router for requests.

    """
    def __init__(self):
        self._paths = {}

    def route(self, environ, start_response):
        path = environ["PATH_INFO"]
        request_get_data = parse_http_get_data(environ)

        if path in self._paths:
            res = self._paths[path](request_get_data)
        else:
            res = self.default_response(request_get_data)

        return res

    def register(self, path, callback):
        self._paths[path] = callback

    def default_response(self, *args):
        return 404, "Nooo 404!"


class TextController(object):
    def __init__(self, view, manager):
        self.view = view
        self.text_manager = manager

    def index(self, request_get_data):
        title = take_one_or_None(request_get_data, "title")
        current_text = self.text_manager.get_by_title(title)

        all_texts = self.text_manager.get_all()

        context = {
            "all": all_texts,
            "current": current_text,
        }

        return 200, self.view.render(context)

    def add(self, request_get_data):
        title = take_one_or_None(request_get_data, "title")
        content = take_one_or_None(request_get_data, "content")

        self.text_manager.create(title, content)

        context = {
            "url": "/text"
        }

        return 200, RedirectView.render(context)


# ===========================
#
#           View
#
# ===========================

class TextView(object):
    @staticmethod
    def render(context):
        context["titles"] = "\n".join([
            "<li>{0.title}</li>".format(text) for text in context["all"]
        ])

        if context["current"]:
            context["content"] = """
            <h1>{0.title}</h1>
            {0.content}
            """.format(context["current"])
        else:
            context["content"] = 'What do you want read?'

        t = """
        <form method="GET">
            <input type=text name=title placeholder="Text title" />
            <input type=submit value=read />
        </form>
        <form method="GET" action="/text/add">
            <input type=text name=title placeholder="Text title" /> <br>
            <textarea name=content placeholder="Text content!" ></textarea> <br>
            <input type=submit value=write/rewrite />
        </form>
        <div>{content}</div>
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

router = Router()
text_manager = TextManager()
text_view = TextView()
controller = TextController(text_view, text_manager)

router.register("/", lambda x: (200, "Index HI!"))
router.register("/text", controller.index)
router.register("/text/add", controller.add)


# ===========================
#
#          WSGI
#
# ===========================

def application(environ, start_response):
    http_status_code, response_body = router.route(environ, start_response)

    if DEBUG:
        response_body += "<br><br> The request ENV: {0}".format(repr(environ))

    response_status = http_status(http_status_code)
    response_headers = [("Content-Type", "text/html")]

    # TODO: You can add this interesting think to Router
    # print(parse_http_post_data(environ))

    start_response(response_status, response_headers)
    return [response_body]  # it could be any iterable.


# if run as script do tests.
if __name__ == "__main__":
    import doctest
    doctest.testmod()