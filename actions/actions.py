from dotenv import dotenv_values
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import requests

config = dotenv_values(".env")
API_KEY = config['API_KEY']
# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
class ActionCheckWeather(Action):

    def name(self)-> Text:
        return "action_get_weather"
    
    def run(self, dispatcher, tracker, domain):
        loc = tracker.get_slot('location')
        current = requests.get('http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(loc, API_KEY)).json()
        print(current)
        country = current['sys']['country']
        city = current['name']
        condition = current['weather'][0]['main']
        temperature_c = current['main']['temp']
        humidity = current['main']['humidity']
        wind_mph = current['wind']['speed']
        response = """It is currently {} in {} at the moment. The temperature is {} degrees, the humidity is {}% and the wind speed is {} mph.""".format(condition, city, temperature_c, humidity, wind_mph)
        dispatcher.utter_message(response)
        dispatcher.utter_message(template='utter_continue')
        # dispatcher.utter_message("I can tell you vacation planning details")
        return [SlotSet('location', loc)]

class ActionCheckHotels(Action):

    def name(self)-> Text:
        return "action_get_hotels"
    
    def run(self, dispatcher, tracker, domain):
        loc = tracker.get_slot('location')
        querystring = {"query":loc}
        url = "https://hotels4.p.rapidapi.com/locations/v2/search"
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': "b2b8df2c4emsh55932ebbbefe351p11f903jsn956c777b38ca"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)

        hotel_details = response.json()

        dispatcher.utter_message(f"Showing Hotel Suggestions in {hotel_details['term']}....")
        for group in hotel_details['suggestions']:
            if group['group'] == "HOTEL_GROUP":
                for entity in group['entities']:
                    dispatcher.utter_message(entity['name'])
        dispatcher.utter_message(template='utter_continue')
        return [SlotSet('location', loc)]

class ActionCheckStations(Action):

    def name(self)-> Text:
        return "action_get_stations"
    
    def run(self, dispatcher, tracker, domain):
        loc = tracker.get_slot('location')
        querystring = {"query":loc}
        url = "https://hotels4.p.rapidapi.com/locations/v2/search"
        headers = {
            'x-rapidapi-host': "hotels4.p.rapidapi.com",
            'x-rapidapi-key': "b2b8df2c4emsh55932ebbbefe351p11f903jsn956c777b38ca"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)

        hotel_details = response.json()

        dispatcher.utter_message(f"Listing Suggestions for transportation stations in {hotel_details['term']}....")
        for group in hotel_details['suggestions']:
            if group['group'] == "TRANSPORT_GROUP":
                for entity in group['entities']:
                    type = ' '.join(entity['type'].split("_")).title()
                    dispatcher.utter_message(f"{type}:{entity['name']}")
        dispatcher.utter_message(template='utter_continue')
        return [SlotSet('location', loc)]

class ActionCheckTrain(Action):

    def name(self)-> Text:
        return "action_get_train"
    
    def run(self, dispatcher, tracker, domain):
        train = tracker.get_slot('train_name')
        url = "https://trains.p.rapidapi.com/"

        payload = {"search": train}
        headers = {
            'content-type': "application/json",
            'x-rapidapi-host': "trains.p.rapidapi.com",
            'x-rapidapi-key': "b2b8df2c4emsh55932ebbbefe351p11f903jsn956c777b38ca"
            }

        response = requests.request("POST", url, json=payload, headers=headers)
        train_details = response.json()
        print("Response: ", train_details)
        
        dispatcher.utter_message(f"Listing details for {train}...")
        for idx, train in enumerate(train_details):
            days = []
            for day in train['data']['days']:
                if int(train['data']['days'][day]):
                    days.append(day)
            available_days = ', '.join(days)
            details = f"{idx+1}. Train Number: {train['train_num']}, Train Name: {train['name']}, Available on {available_days}. Arrival Time: {train['data']['arriveTime']}, Departure Time: {train['data']['departTime']}"
            dispatcher.utter_message(details)

        dispatcher.utter_message(template='utter_continue')
        return [SlotSet('location', train)]


class ActionBestHotel(Action):

    def name(self)-> Text:
        return "action_best_hotel"
    
    def run(self, dispatcher, tracker, domain):
        loc = tracker.get_slot('location')
        querystring = {"cityName":loc,"countryName":"India"}

        url = "https://best-booking-com-hotel.p.rapidapi.com/booking/best-accommodation"

        headers = {
            'x-rapidapi-host': "best-booking-com-hotel.p.rapidapi.com",
            'x-rapidapi-key': "b2b8df2c4emsh55932ebbbefe351p11f903jsn956c777b38ca"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)

        hotel_details = response.json()

        dispatcher.utter_message(f"The best rated hotel in {loc}....")
        dispatcher.utter_message(f"Name: {hotel_details['name']}")
        dispatcher.utter_message(f"Link: {hotel_details['link']}")
        dispatcher.utter_message(f"Rating: {hotel_details['rating']}")
        
        dispatcher.utter_message(template='utter_continue')
        return [SlotSet('location', loc)]



