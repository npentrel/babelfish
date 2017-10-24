# babelfish

_Typing is hard. Calling someone is harder._

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
