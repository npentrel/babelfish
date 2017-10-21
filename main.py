import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
import json
import requests
import os
from string import Template
from auth import AzureAuthClient
from xml.etree import ElementTree
import nexmo
from config import NEXMO_APPLICATION_ID, NEXMO_PRIVATE_KEY, MICROSOFT_TRANSLATION_CLIENT_SECRET, HOSTNAME

client = nexmo.Client(application_id=NEXMO_APPLICATION_ID, private_key=NEXMO_PRIVATE_KEY)

language_model = 'en-UK_NarrowbandModel' # Specify the Narrowband model for your language

auth_client = AzureAuthClient(MICROSOFT_TRANSLATION_CLIENT_SECRET)
microsoft_translator_bearer_token = 'Bearer ' + auth_client.get_access_token()

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.content_type = 'text/plain'
        self.write("Hiii")
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
        body = self.request.body
        self.content_type = 'text/plain'
        self.write('ok')
        self.finish()

class MessageHandler():
    def __init__(self, message):
        self.msg = message

    def handle(self):
        print self.msg
        resp = json.loads(self.msg)
        if resp:
            if 'results' in resp and 'alternatives' in resp['results'][0]:
                if resp['results'][0]['final'] == True:
                    if 'transcript' in resp['results'][0]['alternatives'][0]:
                        text = resp["results"][0]["alternatives"][0]["transcript"]
                        print('To be translated: ' + text)
                        translate(text, 'en', 'de')

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("Websocket Call Connected")

    def tts_completed(self, new_message):
        print "TTS COMPLETED"
        h = MessageHandler(new_message)
        result = h.handle()

    @gen.coroutine
    def on_message(self, message):
        print "Received Message"

    @gen.coroutine
    def on_close(self):
        print("Websocket Call Disconnected")

def translate(text, from_language, to_language):
    headers = {"Authorization ": microsoft_translator_bearer_token}
    translateUrl = "http://api.microsofttranslator.com/v2/Http.svc/Translate?text={}&from={}&to={}".format(text, from_language, to_language)
    translationData = requests.get(translateUrl, headers = headers)

    translation = ElementTree.fromstring(translationData.text.encode('utf-8'))
    print("Translated: " + translation.text)
    return translation.text

def speak(uuid, text, voice_name):
    response = client.send_speech(uuid, text=text, voice_name='Marlene')

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
    print "Running on port: " + str(port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
