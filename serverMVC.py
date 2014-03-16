__author__ = 'pahaz'

from wsgiref.simple_server import make_server
import appMVC as app

# Instantiate the WSGI server.
# It will receive the request, pass it to the application
# and send the application's response to the client
httpd = make_server(
    'localhost',
    8051,
    app.application
)

print "Run: http://localhost:8051/"
httpd.serve_forever()
