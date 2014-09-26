#! /usr/bin/env python2.7
import os
import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
import sys
import django.core.handlers.wsgi
import pwd
import settings

os.environ['PYTHON_EGG_CACHE'] = '/tmp'

def main(port):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'sqp_project.settings'
    application = django.core.handlers.wsgi.WSGIHandler()
    container = tornado.wsgi.WSGIContainer(application)
    http_server = tornado.httpserver.HTTPServer(container)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    if len(sys.argv) <= 1 or len(sys.argv) > 2:
        raise Exception('Port not set. Usage: %s port' % sys.argv[0])
    main(sys.argv[1])

