# coding: utf-8
from gevent.wsgi import WSGIServer
from jzsadmin import create_app

app = create_app('production.cfg')

http_server = WSGIServer(('127.0.0.1', 8100), app)
http_server.serve_forever()
