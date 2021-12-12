from os import access
from dotenv import dotenv_values
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.types import DomainDict
import csv
import re
from datetime import date
from datetime import datetime
import requests
from requests.structures import CaseInsensitiveDict


config = dotenv_values(".env")
API_KEY = config['API_KEY']
RAPID_API_KEY = config['RAPID_API_KEY']
AMADEUS_CLIENT_ID = config['AMADEUS_CLIENT_ID']
AMADEUS_CLIENT_SECRET = config['AMADEUS_CLIENT_SECRET']

IATA_MAPPER = {}
filename ="./EasyPNR-Airports.csv"
with open(filename, 'r') as data:
	for line in csv.DictReader(data):
		IATA_MAPPER[line['iataCode']] = line['Airport name']
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
        response = """It is currently <b>{}</b> in {} at the moment. The temperature is <b>{}</b> degrees, the humidity is <b>{}%</b> and the wind speed is <b>{}</b> mph.""".format(condition, city, temperature_c, humidity, wind_mph)
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
            'x-rapidapi-key': RAPID_API_KEY
            }

        response = requests.request("GET", url, headers=headers, params=querystring)

        hotel_details = response.json()

        dispatcher.utter_message(f"Showing Hotel Suggestions in {hotel_details['term']}....")
        for group in hotel_details['suggestions']:
            if group['group'] == "HOTEL_GROUP":
                for entity in group['entities']:
                    dispatcher.utter_message(f"<b>{entity['name']}</b>")
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
            'x-rapidapi-key': RAPID_API_KEY
            }

        response = requests.request("GET", url, headers=headers, params=querystring)

        hotel_details = response.json()

        dispatcher.utter_message(f"Listing Suggestions for transportation stations in {hotel_details['term']}....")
        for group in hotel_details['suggestions']:
            if group['group'] == "TRANSPORT_GROUP":
                for entity in group['entities']:
                    type = ' '.join(entity['type'].split("_")).title()
                    dispatcher.utter_message(f"<b>{type}:</b>{entity['name']}")
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
            'x-rapidapi-key': RAPID_API_KEY
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
            details = f"{idx+1}. <b>Train Number:</b> {train['train_num']}, <b>Train Name:</b> {train['name']}, <b>Available on</b> {available_days}. <b>Arrival Time:</b> {train['data']['arriveTime']}, <b>Departure Time:</b> {train['data']['departTime']}"
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
            'x-rapidapi-key': RAPID_API_KEY
            }

        response = requests.request("GET", url, headers=headers, params=querystring)

        hotel_details = response.json()

        dispatcher.utter_message(f"The best rated hotel in {loc}....")
        dispatcher.utter_message(f"<b>Name:</b> {hotel_details['name']}")
        dispatcher.utter_message(f"<a href = {hotel_details['link']} target='_blank'>Click Here to Book</a>")
        dispatcher.utter_message(f"Rating: {hotel_details['rating']}")
        
        dispatcher.utter_message(template='utter_continue')
        return [SlotSet('location', loc)]



class ValidateFlightForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_flight_form"

    def validate_origin_location(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `origin_location` value."""

        # Check if origin Location is valid
        print(f"origin location given = {slot_value}")
        filename ="./EasyPNR-Airports.csv"

        with open(filename, 'r') as data:
            for line in csv.DictReader(data):
                print("slot_value", slot_value.lower())
                print("Location", line['Location'].lower())
                if slot_value.lower() in line['Location'].lower():
                    dispatcher.utter_message(f"I found {line['Airport name']} for {slot_value}")
                    return {"origin_location": line['iataCode']}
        dispatcher.utter_message(f"I couldn't find an airport for the location <b>{slot_value}</b>, Please Enter proper location.")
        return {"origin_location": None}

    def validate_destination_location(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `destination_location` value."""

        # Check if origin Location is valid
        print(f"destination location given = {slot_value}")
        filename ="./EasyPNR-Airports.csv"

        with open(filename, 'r') as data:
            for line in csv.DictReader(data):
                if slot_value.lower() in line['Location'].lower():
                    dispatcher.utter_message(f"I found {line['Airport name']} for {slot_value}")
                    return {"destination_location": line['iataCode']}
        dispatcher.utter_message(f"I couldn't find an airport for the location <b>{slot_value}</b>, Please Enter proper location.")
        return {"destination_location": None}

    def validate_departure_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `departure_date` value."""
        regex = r'\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$'

        if re.match(regex, slot_value) == None:
            dispatcher.utter_message("I'm assuming you mis-spelled the departure date. Here's the format of date: yyyy-mm-dd")
            return {"departure_date": None}
        elif datetime.strptime(str(date.today()), '%Y-%m-%d')>datetime.strptime(slot_value, '%Y-%m-%d'):
            dispatcher.utter_message("Hey, I'm sorry to inform that time travel is yet to be discovered 🙁! Untill then, please Enter a date either in future or today's date.")
        else:
            return {"departure_date": slot_value}

    def validate_noof_adults(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `noof_adults` value."""
        regex = r'\b[1-9]\b'

        if re.match(regex, slot_value) == None:
            dispatcher.utter_message("You can book tickets for 1-9 adults. Please Enter numbers in only range of 1 to 9.")
            return {"noof_adults": None}
        else:
            return {"noof_adults": slot_value}


class ActionSubmit(Action):
    def name(self) -> Text:
        return "action_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        origin_location = tracker.get_slot("origin_location")
        destination_location = tracker.get_slot("destination_location")
        departure_date = tracker.get_slot("departure_date")
        noof_adults = tracker.get_slot("noof_adults")

        # First, we generate the access token
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

        data = "grant_type=client_credentials&client_id={}&client_secret={}".format(AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET)


        resp = requests.post(url, headers=headers, data=data)

        access_token = resp.json()['access_token']

        # Now, we call flight search API
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers?originLocationCode={}&destinationLocationCode={}&departureDate={}&adults={}&currencyCode=INR&nonStop=false&max=250".format(origin_location, destination_location, departure_date, noof_adults)

        headers = CaseInsensitiveDict()
        headers["accept"] = "application/vnd.amadeus+json"
        headers["Authorization"] = "Bearer {}".format(access_token)


        resp = requests.get(url, headers=headers)

        data = resp.json()

        # Now, respond to user
        dispatcher.utter_message(f"<b>{data['meta']['count']}</b> flights found ....")
        for flight in data['data']:
            id = flight['id']
            lastTicketingDate = flight['lastTicketingDate']
            price = flight['price']['total']
            duration = flight['itineraries'][0]['duration']

            segments = flight['itineraries'][0]['segments']
            departure = segments[0]['departure']
            departure_location = IATA_MAPPER[departure['iataCode']]
            departure_time = departure['at']

            arrival = segments[0]['arrival']
            arrival_location = IATA_MAPPER[arrival['iataCode']]
            arrival_time = arrival['at']
            text = f"<b>Filght #{id}</b></br><b>Last Ticketing Date: </b>{lastTicketingDate}</br><b>Total Price:</b> ₹{price} </br><b>Duration:</b>{duration}</br>Departure from {departure_location} at {departure_time}.</br> Arrival at {arrival_location} at {arrival_time}."
            dispatcher.utter_message(text)

        return []