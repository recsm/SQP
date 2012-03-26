import os
import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
import sys
import django.core.handlers.wsgi
import pwd


sys.path.append('/srv/production/sqp_project')
sys.path.append('/srv/production')
os.environ['PYTHON_EGG_CACHE'] = '/tmp'



def main():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'sqp_project.settings'
    application = django.core.handlers.wsgi.WSGIHandler()
    container = tornado.wsgi.WSGIContainer(application)
    http_server = tornado.httpserver.HTTPServer(container)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
if __name__ == "__main__":
    main()

