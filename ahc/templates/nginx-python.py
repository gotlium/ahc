#!/usr/bin/env python


def helloworld(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Python:Hello, World!\n']


def runfcgi(func, socket_path='%(socket_path)s'):
    import flup.server.fcgi as flups

    return flups.WSGIServer(func, multiplexed=True,
                            bindAddress=socket_path).run()


runfcgi(helloworld)
