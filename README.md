# babelfish

Using speech to text in combination with text translation and text to speech, we built a tool not unlike Google's _new_ babel platform. Call someone and they will hear what you say in their language 😮.

Both parties call the service's Nexmo number which will connect them to one another. However, both parties do not hear each other directly. They hear a translated version of one another thus enabling them both to speak and hear the other side in their preferred language. The way that works is that the audio stream of the speech on one caller's side will be transcribed and translated by the Microsoft Translator Speech API and the resulting text will be spoken to the other person. A German could thus hear a British person speaking German and respond in German. The response would be heard by the British person in English.

## Stack

Python, Microsoft Translator Speech API, Nexmo Voice API, Ngrok.

## Requirements

- A Nexmo number with voice capability and a Nexmo application
- When setting up the Nexmo Application use a Ngrok forwarding URL for both the Event URL and the Answer URL:
    - Event URL: [http://<abc123>.ngrok.io/event](http://<abc123>.ngrok.io/event)
    - Answer URL: [http://<abc123>.ngrok.io/ncco](http://<abc123>.ngrok.io/ncco)

## Setup:

```
virtualenv venv
source venv/bin/activate
vim requirements.txt
pip install -r requirements.txt
```

In another terminal window run:
```
ngrok http 5000
```
