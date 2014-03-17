## Run simple WSGI server example

   >python server.py

## Run MVC example

   >python serverMVC.py

# MVC v2 for lovers of esthetics

![Screenshot](https://raw.github.com/pahaz/Example-of-MVC-pattern-on-pure-Python/master/screenshot.png "MVC pure python example - html view")

## Coupling

![Components coupling](https://raw.github.com/pahaz/Example-of-MVC-pattern-on-pure-Python/master/coupling.png "MVC on pure python example - components coupling")

## How to use

    > python serverMVCv2.py  # Run server
    Run: http://localhost:8051/
    127.0.0.1 - - [18/Mar/2014 01:13:19] "GET /text HTTP/1.1" 200 538
    127.0.0.1 - - [18/Mar/2014 01:13:34] "GET /text?title=foo HTTP/1.1" 200 580
    127.0.0.1 - - [18/Mar/2014 01:21:25] "GET /text/add?title=MVC&content=%3Cb%3EMVC%3C%2Fb%3E+%3D+Model+View+Controller HTTP/1.1" 200 52
    127.0.0.1 - - [18/Mar/2014 01:13:47] "GET /text?title=MVC HTTP/1.1" 200 579

    > pyhton appMVCv2.py       # Run doctests

