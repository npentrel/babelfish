from flask import Flask, request, make_response
import nexmo

from config import NEXMO_APPLICATION_ID, NEXMO_PRIVATE_KEY

client = nexmo.Client(application_id=NEXMO_APPLICATION_ID, private_key=NEXMO_PRIVATE_KEY)
app = Flask(__name__)


@app.route('/')
def index():
    return "Hello World!"


@app.route('/call_received', methods=['GET', 'POST'])
def call_received():
    print("call_received")
    if request.method == 'POST':
        print(request)
        return make_response("", 200)
    else:
        return make_response("Not a post request", 200)


if __name__ == '__main__':
    app.run()
