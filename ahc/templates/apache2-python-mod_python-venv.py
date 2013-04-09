__author__ = 'gotlium'

from mod_python import apache


def handler(req):
    req.content_type = "text/html"
    req.send_http_header()
    req.write('Python:Hello, world!\n')
    return apache.OK
