# babelfish

Using speech to text in combination with text translation and text to speech, we built a tool not unlike Google's _new_ babel platform. Call someone and they will hear what you say in their language 😮.

Both parties call the service's Nexmo number which will connect them to one another. However, both parties do not hear each other directly. They hear a translated version of one another thus enabling them both to speak and hear the other side in their preferred language. The way that works is that the audio stream of the speech on one caller's side will be transcribed and translated by the Microsoft Translator Speech API and the resulting text will be spoken to the other person. A German could thus hear a British person speaking German and respond in German. The response would be heard by the British person in English.

## Stack

Python, Microsoft Translator Speech API, Nexmo Voice API, Ngrok.

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

### Creating a Nexmo account

* [Create a Nexmo account](https://dashboard.nexmo.com/sign-up)
* [Install Nexmo CLI](https://github.com/Nexmo/nexmo-cli)
* Create an application
  ```bash
    nexmo app:create "Babelfish" http://your_url.ngrok.io/ncco http://your_url.ngrok.io/event --keyfile private.key
  ```
* Purchase a number
  ```bash
    nexmo number:buy --country_code GB --confirm
  ```
* Link your number and application
  ```bash
    nexmo link:app <number> <application_id>
  ```

### Creating a Microsoft cognitive services account

* [Create a Microsoft Azure account](https://portal.azure.com)
* Search for Cognitive Services in the search bar
* Click `add` and create a new `Translator Speech API`
* Once created, click on the new translator service, then click on `Keys` under the `Resource Management` header
* Copy `KEY 1` for use in your application

## Requirements

- A Nexmo number with voice capability and a Nexmo application
- When setting up the Nexmo Application use a Ngrok forwarding URL for both the Event URL and the Answer URL:
    - Event URL: [http://abc123.ngrok.io/event](http://<abc123>.ngrok.io/event)
    - Answer URL: [http://abc123.ngrok.io/ncco](http://<abc123>.ngrok.io/ncco)
- [Microsoft’s Translator Speech API](http://docs.microsofttranslator.com/speech-translate.html) key
- Follow the instructions in the `secrets.py` and `config.py` files.

### Configuring the application

Create `config.py` with the following contents:

```python
HOSTNAME="your_host.ngrok.io" # Do not add HTTP
CALLER="<your_number>"
LANGUAGE1 = 'de-DE' # the caller's language
VOICE1 = 'Marlene' # a Nexmo voice for the caller's language

LANGUAGE2 = 'en-US' # the other person's language
VOICE2 = 'Kimberly' # a Nexmo voice for the other person's language
```

Create `secrets.py` with the following contents:

```python
NEXMO_API_KEY = "<your-api-key>"
NEXMO_API_SECRET = "<your-api-secret>"
NEXMO_NUMBER = "+447512345678"
NEXMO_APPLICATION_ID = "<nexmo-application-id>"
NEXMO_PRIVATE_KEY = '''-----BEGIN PRIVATE KEY-----
<your-private-key>
-----END PRIVATE KEY-----'''

# You will have to sign up for a free Microsoft account to use the Microsoft Translator Speech API: http://docs.microsofttranslator.com/speech-translate.html
MICROSOFT_TRANSLATION_SPEECH_CLIENT_SECRET = "<your-api-key>"
```

### Running the application

Run `python main.py` then have two (or more) people call your Nexmo number. When one person speaks, the rest will hear in another language. To change the languages used, edit `config.py`.
