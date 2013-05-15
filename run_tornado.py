#!/usr/bin/env python

import json
import os
import random
import time

import tornadoredis

import tornado.gen
import tornado.httpserver
import tornado.ioloop
import tornado.template
import tornado.web
import tornado.websocket

import sockjs.tornado

import settings

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render( 'index.html')

class ServertimeHandler(tornado.web.RequestHandler):
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
    app.listen(80)
    tornado.ioloop.IOLoop.instance().start()
