

# This is our application object. It could have any name,
# except when using mod_wsgi where it must be "application".
# *arguments*:
# `environ` points to a dictionary containing CGI like environment variables
# which is filled by the server for each received request from the client
# `start_response` is a callback function supplied by the server
# which will be used to send the HTTP status and headers to the server
def application(environ, start_response):
    response_body = 'The request ENV: {0}'.format(repr(environ))
    http_status_code_and_msg = '200 OK'
    response_headers = [('Content-Type', 'text/plain'),
                        ('Content-Length', str(len(response_body)))]

    start_response(http_status_code_and_msg, response_headers)
    return [response_body]  # it could be any iterable.

