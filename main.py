from string import Template
import json
import os
import struct
import StringIO

from tornado import httpserver, httpclient, ioloop, web, websocket, gen
import nexmo

from azure_auth_client import AzureAuthClient
from config import HOSTNAME, CALLER, LANGUAGE1, VOICE1, LANGUAGE2, VOICE2
from secrets import NEXMO_APPLICATION_ID, NEXMO_PRIVATE_KEY, MICROSOFT_TRANSLATION_SPEECH_CLIENT_SECRET, NEXMO_NUMBER


nexmo_client = nexmo.Client(application_id=NEXMO_APPLICATION_ID,
                            private_key=NEXMO_PRIVATE_KEY)
azure_auth_client = AzureAuthClient(MICROSOFT_TRANSLATION_SPEECH_CLIENT_SECRET)

conversation_id_by_phone_number = {}
call_id_by_conversation_id = {}


class CallHandler(web.RequestHandler):
    @web.asynchronous
    def get(self):
        data = {}
        data['hostname'] = HOSTNAME
        data['nexmo_number'] = NEXMO_NUMBER
        data['whoami'] = self.get_query_argument('from')
        data['cid'] = self.get_query_argument('conversation_uuid')
        conversation_id_by_phone_number[self.get_query_argument('from')] = self.get_query_argument('conversation_uuid')
        print(conversation_id_by_phone_number)
        filein = open('ncco.json')
        src = Template(filein.read())
        filein.close()
        ncco = json.loads(src.substitute(data))
        self.write(json.dumps(ncco))
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        self.finish()

class EventHandler(web.RequestHandler):
    @web.asynchronous
    def post(self):
        body = json.loads(self.request.body)
        if 'direction' in body and body['direction'] == 'inbound':
            if 'uuid' in body and 'conversation_uuid' in body:
                call_id_by_conversation_id[body['conversation_uuid']] = body['uuid']
        self.content_type = 'text/plain'
        self.write('ok')
        self.finish()


class WSHandler(websocket.WebSocketHandler):
    whoami = None

    def open(self):
        print("Websocket Call Connected")

    def translator_future(self, translate_from, translate_to):
        uri = "wss://dev.microsofttranslator.com/speech/translate?from={0}&to={1}&api-version=1.0".format(translate_from[:2], translate_to)
        request = httpclient.HTTPRequest(uri, headers={
            'Authorization': 'Bearer ' + azure_auth_client.get_access_token(),
        })
        return websocket.websocket_connect(
            request,
            on_message_callback=self.speech_to_translation_completed)

    def speech_to_translation_completed(self, new_message):
        if new_message is None:
            print("Got None Message")
            return
        msg = json.loads(new_message)
        if msg['translation'] != '':
            print("Translated: '{}' -> '{}'".format(msg['recognition'],
                                                    msg['translation']))
            for key, value in conversation_id_by_phone_number.iteritems():
                if key != self.whoami and value is not None:
                    if self.whoami == CALLER:
                        speak(call_id_by_conversation_id[value],
                              msg['translation'],
                              VOICE2)
                    else:
                        speak(call_id_by_conversation_id[value],
                              msg['translation'],
                              VOICE1)

    @gen.coroutine
    def on_message(self, message):
        if type(message) == str:
            ws = yield self.ws_future
            ws.write_message(message, binary=True)
        else:
            message = json.loads(message)
            self.whoami = message['whoami']
            print("Sending wav header")
            header = make_wave_header(16000)

            if self.whoami == CALLER:
                self.ws_future = self.translator_future(LANGUAGE1, LANGUAGE2)
            else:
                self.ws_future = self.translator_future(LANGUAGE2, LANGUAGE1)

            ws = yield self.ws_future
            ws.write_message(header, binary=True)

    @gen.coroutine
    def on_close(self):
        print("Websocket Call Disconnected")


def make_wave_header(frame_rate):
    """
    Generate WAV header that precedes actual audio data sent to the speech
    translation service. :param frame_rate: Sampling frequency (8000 for 8kHz
    or 16000 for 16kHz). :return: binary string
    """

    if frame_rate not in [8000, 16000]:
        raise ValueError(
            "Sampling frequency, frame_rate, should be 8000 or 16000.")

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


def speak(uuid, text, vn):
    print("speaking to: {} {}".format(uuid, text))
    response = nexmo_client.send_speech(uuid, text=text, voice_name=vn)
    print(response)


def main():
    application = web.Application([
        (r"/event", EventHandler),
        (r"/ncco", CallHandler),
        (r"/socket", WSHandler),
    ])

    http_server = httpserver.HTTPServer(application)
    port = int(os.environ.get("PORT", 5000))
    http_server.listen(port)
    print("Running on port: " + str(port))

    ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
