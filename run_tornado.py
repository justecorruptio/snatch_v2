#!/usr/bin/env python

import json
import os
import random
import socket
import time

import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.netutil
import tornado.template
import tornado.web
import tornado.websocket

import sockjs.tornado

import settings

class MiddlewareMixin(object):
    def prepare(self):
        appsession = self.get_cookie('RASPIN', '%08x' % (random.getrandbits(32),))
        self.set_cookie('RASPIN', appsession)


class IndexHandler(MiddlewareMixin, tornado.web.RequestHandler):
    def get(self):
        self.render( 'index.html')


class ServertimeHandler(MiddlewareMixin, tornado.web.RequestHandler):
    def get(self):
        self.write({
            'a': self.get_argument('a'),
            'b': int(time.time() * 1000),
        })


class MessageHandler(sockjs.tornado.SockJSConnection):

    clients = set()

    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)


    def on_open(self, info):
        self.clients.add(self)


    def on_message(self, msg):
        #os.system('/usr/local/flask_snatch/blink1-tool -m 1 --rgb %d,%d,%d &' %
        #    (random.randint(0,255),random.randint(0,255),random.randint(0,255),))
        self.broadcast(self.clients, msg)

    def on_close(self):
        self.clients.remove(self)


app = tornado.web.Application(
    handlers = [
        ('/', IndexHandler),
        ('/servertime', ServertimeHandler),
    ]  +
    sockjs.tornado.SockJSRouter(MessageHandler, '/s').urls,
    **settings.TORNADO_SETTINGS
)


if __name__ == "__main__":
    from tornado.httpserver import HTTPServer
    server = HTTPServer(app)
    socks = tornado.netutil.bind_sockets(port=80, family=socket.AF_INET)
    server.add_sockets(socks)
    tornado.ioloop.IOLoop.instance().start()
