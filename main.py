import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
import json
import requests
import os
from string import Template

import nexmo
from config import NEXMO_APPLICATION_ID, NEXMO_PRIVATE_KEY, WATSON_USERNAME, WATSON_PASSWORD, WATSON_URL

client = nexmo.Client(application_id=NEXMO_APPLICATION_ID, private_key=NEXMO_PRIVATE_KEY)

language_model = 'en-UK_NarrowbandModel' # Specify the Narrowband model for your language

HOSTNAME = 'de24b617.ngrok.io'

def gettoken():
    resp = requests.get('https://stream.watsonplatform.net/authorization/api/v1/token', auth=(WATSON_USERNAME, WATSON_PASSWORD), params={'url' : WATSON_URL})
    token = None
    if resp.status_code == 200:
        token = resp.content
    else:
        print resp.status_code
        print resp.content

    return token


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.content_type = 'text/plain'
        self.write("Watson STT Example")
        self.finish()


class CallHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        data={}
        data['hostname'] = HOSTNAME
        filein = open('ncco.json')
        src = Template(filein.read())
        filein.close()
        ncco = json.loads(src.substitute(data))
        self.write(json.dumps(ncco))
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        self.finish()


class EventHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        print self.request.body
        self.content_type = 'text/plain'
        self.write('ok')
        self.finish()

class MessageHandler():
    def __init__(self, message):
        self.msg = message

    def handle(self):
        print self.msg


class WSHandler(tornado.websocket.WebSocketHandler):
    watson_future = None
    def open(self):
        print("Websocket Call Connected")
        uri = 'wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize?watson-token={}&model={}'.format(gettoken(), language_model)
        self.watson_future = tornado.websocket.websocket_connect(uri, on_message_callback=self.on_watson_message)

    @gen.coroutine
    def on_message(self, message):
        watson = yield self.watson_future
        if type(message) == str:
            watson.write_message(message, binary=True)
        else:
            data = json.loads(message)
            data['action'] = "start"
            data['continuous'] = True
            data['interim_results'] = True
            print json.dumps(data)
            watson.write_message(json.dumps(data), binary=False)

    @gen.coroutine
    def on_close(self):
        print("Websocket Call Disconnected")
        watson = yield self.watson_future
        data = {'action' : 'stop'}
        watson.write_message(json.dumps(data), binary=False)
        watson.close()

    def on_watson_message(self, message):
        handler = MessageHandler(message)
        handler.handle()




def main():
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    application = tornado.web.Application([(r"/", MainHandler),
                                           (r"/event", EventHandler),
                                           (r"/ncco", CallHandler),
                                           (r"/socket", WSHandler),
                                           (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
                                          ])
    http_server = tornado.httpserver.HTTPServer(application)
    port = int(os.environ.get("PORT", 8000))
    http_server.listen(port)
    print gettoken()
    print "Running on port: " + str(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

