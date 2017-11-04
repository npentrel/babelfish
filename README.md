# babelfish

Using speech to text in combination with text translation and text to speech, we built a tool not unlike Google's `new` babel platform. Call someone, input the language and they will hear what you say in another language 😮. #amazing #mindblown.

One party calls the service's Nexmo number which will initiate a call to the other party. The audio stream of the speech on the caller's side will be transcribed and translated by the Microsoft Speech API and the resulting text will be spoken to on the other end. The person called can this hear the caller in a language they understand and respond alike. The response will again be translated so that the caller hears it in their favorite language.

## Stack 

Python, Microsoft Speech API, Nexmo. 

## Setup:

```
virtualenv venv
source venv/bin/activate
vim requirements.txt
pip install -r requirements.txt
```

### Creating a Nexmo account

* [Create a Nexmo account](https://dashboard.nexmo.com/sign-up)
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

### Configuring the application

Create `config.py` with the following contents:

```python
NEXMO_APPLICATION_ID="<your_application_id>"
NEXMO_PRIVATE_KEY="/path/to/private.key"
MICROSOFT_TRANSLATION_SPEECH_CLIENT_SECRET="<azure_KEY_1>"
HOSTNAME="your_host.ngrok.io" # Do not add HTTP
NEXMO_NUMBER="<your_nexmo_number>"
```

### Running the application

Run `python main.py` then have two (or more) people call your Nexmo number. When one person speaks, the rest will hear in another language. To change the languages used, edit `main.py` lines `120-121`.
