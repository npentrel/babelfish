import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
import json
import requests
import os
import struct
from string import Template
from auth import AzureAuthClient
from xml.etree import ElementTree
import nexmo
import StringIO
from config import NEXMO_APPLICATION_ID, NEXMO_PRIVATE_KEY, MICROSOFT_TRANSLATION_SPEECH_CLIENT_SECRET, HOSTNAME, NEXMO_NUMBER

client = nexmo.Client(application_id=NEXMO_APPLICATION_ID, private_key=NEXMO_PRIVATE_KEY)
auth_client = AzureAuthClient(MICROSOFT_TRANSLATION_SPEECH_CLIENT_SECRET)
microsoft_translator_bearer_token = 'Bearer ' + auth_client.get_access_token()

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.content_type = 'text/plain'
        self.write("Hiii")
        self.finish()

conversation_id_by_phone_number = {
}

call_id_by_conversation_id = {
}

class CallHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        data={}
        data['hostname'] = HOSTNAME
        data['whoami'] = self.get_query_argument('from')
        data['cid'] = self.get_query_argument('conversation_uuid')
        conversation_id_by_phone_number[self.get_query_argument('from')] = self.get_query_argument('conversation_uuid')
        print conversation_id_by_phone_number
        filein = open('ncco.json')
        src = Template(filein.read())
        filein.close()
        ncco = json.loads(src.substitute(data))
        self.write(json.dumps(ncco))
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        self.finish()

class CallHandler2(tornado.web.RequestHandler):
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
        body = json.loads(self.request.body)
        if 'uuid' in body and 'conversation_uuid' in body and 'direction' in body and body['direction'] == 'inbound':
            call_id_by_conversation_id[body['conversation_uuid']] = body['uuid']
        print call_id_by_conversation_id
        self.content_type = 'text/plain'
        self.write('ok')
        self.finish()

def make_wave_header(frame_rate):
    """
    Generate WAV header that precedes actual audio data sent to the speech translation service.
    :param frame_rate: Sampling frequency (8000 for 8kHz or 16000 for 16kHz).
    :return: binary string
    """

    if frame_rate not in [8000, 16000]:
        raise ValueError("Sampling frequency, frame_rate, should be 8000 or 16000.")

    nchannels = 1
    bytes_per_sample = 2

    output = StringIO.StringIO()
    output.write('RIFF')
    output.write(struct.pack('<L', 0))
    output.write('WAVE')
    output.write('fmt ')
    output.write(struct.pack('<L', 18))
    output.write(struct.pack('<H', 0x0001))
    output.write(struct.pack('<H', nchannels))
    output.write(struct.pack('<L', frame_rate))
    output.write(struct.pack('<L', frame_rate * nchannels * bytes_per_sample))
    output.write(struct.pack('<H', nchannels * bytes_per_sample))
    output.write(struct.pack('<H', bytes_per_sample * 8))
    output.write(struct.pack('<H', 0))
    output.write('data')
    output.write(struct.pack('<L', 0))

    data = output.getvalue()

    output.close()

    return data


class WSHandler(tornado.websocket.WebSocketHandler):
    SentHeader = False
    whoami = None

    def open(self):
        print("Websocket Call Connected")
        translate_from = 'de'
        translate_to = 'en-US'
        features = "Partial"
        uri = "wss://dev.microsofttranslator.com/speech/translate?from={0}&to={1}&features={2}&api-version=1.0".format(translate_from, translate_to, features)
        request = tornado.httpclient.HTTPRequest(uri, headers={
            'Authorization': 'Bearer ' + auth_client.get_access_token(),
        })

        self.ws_future = tornado.websocket.websocket_connect(request, on_message_callback=self.tts_completed)

    def tts_completed(self, new_message):
        if new_message == None:
            print "Got None Message"
            return
        msg = json.loads(new_message)
        if msg['type'] == 'final' and msg['translation'] != '':
            print "Complete: " + "'" + msg['recognition'] + "' -> '" + msg['translation'] + "'"
            for key, value in conversation_id_by_phone_number.iteritems():
                if key != self.whoami and value != None:
                    speak(call_id_by_conversation_id[value], msg['translation'], 'Kimberly')

    def update_headers(self, message):
        self.whoami = message['whoami']

    @gen.coroutine
    def on_message(self, message):
        if self.SentHeader == False:
            self.update_headers(json.loads(message))
            print "Sending wav header"
            ws = yield self.ws_future
            header = make_wave_header(16000)
            ws.write_message(header, binary=True)
            self.SentHeader = True
        else:
            ws = yield self.ws_future
            ws.write_message(message, binary=True)

    @gen.coroutine
    def on_close(self):
        print("Websocket Call Disconnected")

def speak(uuid, text, vn):
    print "speaking to: " + uuid  + " " + text
    response = client.send_speech(uuid, text=text, voice_name=vn)
    print response

def main():
    static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    application = tornado.web.Application([(r"/", MainHandler),
                                           (r"/event", EventHandler),
                                           (r"/ncco", CallHandler),
                                           (r"/ncco2", CallHandler2),
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
