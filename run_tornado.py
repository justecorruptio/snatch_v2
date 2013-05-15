import json
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


pub_client = tornadoredis.Client()
pub_client.connect()

class MessageHandler(sockjs.tornado.SockJSConnection):

    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)
        self.listen()

    @tornado.gen.engine
    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield tornado.gen.Task(self.client.subscribe, 'test_chan')
        self.client.listen(self.on_sub)

    def on_sub(self, msg):
        if msg.kind != 'message':
            return
        self.send({
            'route': 'test_chan',
            'message': msg.body,
            'time': time.time() * 1000,
            })

    def on_message(self, msg):
        data = json.loads(msg)
        pub_client.publish('test_chan', data['message']);

    def on_close(self):
        if self.client.subscribed:
            self.client.unsubscribe('test_chan')
            self.client.disconnect()


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
