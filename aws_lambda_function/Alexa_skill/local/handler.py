from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name, get_slot_value
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard

from flask import Flask
from flask_ask_sdk.skill_adapter import SkillAdapter
from googletrans import Translator

import requests
from bs4 import BeautifulSoup



def extractSource(url):
    return requests.get(url).text



def extract_event_data(url):
    dict = {}
    soup = BeautifulSoup(extractSource(url), "html.parser")
    event = soup.find('div', {'class':'tedx-events-table'}) \
        .find('tr', {'class': 'tedx-events-table__event tedx-events-table__event--current'})
    event_rows = event.find_all('td',{'class':'table__cell'})
    event_date = str(event_rows[0].contents[2])
    event_loc = str(event_rows[2].contents[2])
    dict["event_date"] = event_date
    dict["event_loc"] = event_loc
    return dict


app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Flask!"

sb = SkillBuilder()

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "Benvenuto in my tedx app. Come posso aiutarti?"

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("myTEDX", speech_text)).set_should_end_session(
        False)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("get_next_event"))
def get_next_event_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    translator = Translator()
    country_name = get_slot_value(handler_input=handler_input, slot_name="country_name")
    country_name_transl = translator.translate(country_name, src='it', dest='en').text
    print(country_name_transl)
    URL = f"https://www.ted.com/tedx/events?autocomplete_filter={country_name_transl}&when=upcoming"
    print(country_name)
    try:
        dict = extract_event_data(URL)
    except:
        speech_text = "Mi dispiace, al momento il sito di tedx non è raggiungibile"
        handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("myTEDX", speech_text)).set_should_end_session(
        True)
        return handler_input.response_builder.response
    
    event_date = dict["event_date"]
    event_loc = translator.translate(dict["event_loc"], src='en',dest='it').text
    event_date_split = event_date.split(',')
    month_it = translator.translate(event_date_split[0].split()[0], src='en', dest='it').text
    event_date = f"{event_date_split[0].split()[1]} {month_it} {event_date_split[1].strip()}"
    speech_text = f"Il prossimo evento in {country_name} si terrà a {event_loc} il {event_date}"

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("myTEDX", speech_text)).set_should_end_session(
        True)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "Puoi chiedermi quando si terrà il prossimo evento TEDX in un determinato paese"

    handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
        SimpleCard("myTEDX", speech_text))
    return handler_input.response_builder.response


@sb.request_handler(
    can_handle_func=lambda handler_input :
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "Ciao!"

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("myTEDx", speech_text)).set_should_end_session(
            True)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    # type: (HandlerInput) -> Response
    # any cleanup logic goes here

    return handler_input.response_builder.response


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    # type: (HandlerInput, Exception) -> Response
    # Log the exception in CloudWatch Logs
    print(exception)

    speech = "Mi dispiace, non ho capito! Puoi ripetere?"
    handler_input.response_builder.speak(speech).ask(speech)
    return handler_input.response_builder.response


handler = sb.lambda_handler()


skill_adapter = SkillAdapter(
                    skill=sb.create(), 
                    skill_id=1, 
                    app=app)

skill_adapter.register(app=app, route="/")

if __name__ == '__main__':
    app.run()