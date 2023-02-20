import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = "foobar"
# you can get API keys for free here - https://www.weatherapi.com/
WEATHERAPI_KEY = ""

app = Flask(__name__)


def generate_weather(location: str, date: str):
    url_base_url = "http://api.weatherapi.com/v1"
    url_api = "history.json"
    url_q = f"?key={WEATHERAPI_KEY}&q={location}&dt={date}"

    url = f"{url_base_url}/{url_api}{url_q}"


    response = requests.request("GET", url)
    resp_json = json.loads(response.text)
    day_data = resp_json["forecast"]["forecastday"][0]["day"]
    hourly_data = resp_json["forecast"]["forecastday"][0]["hour"]
    return {
        "temp_c" : day_data["avgtemp_c"],
        "humidity": day_data["avghumidity"],
        "wind_kph": day_data["maxwind_kph"],
        "pressure_mb": hourly_data[0]["pressure_mb"]
    }


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: Python Saas.</h2></p>"


@app.route(
    "/content/api/v1/integration/generate",
    methods=["POST"],
)

def weather_endpoint():
    json_data = request.get_json()

    token = json_data.get("token")
    location = json_data.get("location")
    requester_name = json_data.get("requester_name")
    date = json_data.get("date")

    if token is None:
        raise InvalidUsage("token is required", status_code=400)
    if requester_name is None:
        raise InvalidUsage("requester_name is required", status_code=400)
    if date is None:
        raise InvalidUsage("location is required", status_code=400)
    if location is None:
        raise InvalidUsage("date is required", status_code=400)
    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    weather = generate_weather(location, date)

    end_dt = dt.datetime.now()

    result = {
        "requester_name": requester_name,
        "timestamp": end_dt.isoformat(),
        "location": location,
        "date": date,
        "weather": weather,
    }

    return result