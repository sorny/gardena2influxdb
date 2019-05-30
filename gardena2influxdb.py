#!/usr/bin/python3 -u
# Parsing GARDENA smart system events and forwarding it InfluxDB
# Gerald Reisinger 2019

import os
import sys
import time
import json
import requests
import websocket
import configparser
import dateutil.parser
from datetime import datetime
from threading import Thread
from influxdb import InfluxDBClient


class Client:
    def __init__(self, idb):
        self.idb = idb

    def on_message(self, message):
        print("msg", message)
        sys.stdout.flush()

        # Parse and reading point as JSON data to InfluxDB
        influxdata = eventparse(message)
        if influxdata:
            self.idb.write_points(influxdata)

    def on_error(self, error):
        print("error", error)
        print("### exit ###")
        sys.exit(-1)

    def on_close(self):
        self.live = False
        print("### closed ###")
        sys.exit(0)

    def on_open(self):
        print("### connected ###")

        self.live = True

        def run(*args):
            while self.live:
                time.sleep(1)

        Thread(target=run).start()


def eventparse(message):
    try:
        # Process event data
        # If an attribute contains a timestamp, we will use that one as data creation timestamp
        iso = datetime.utcnow().ctime()
        data = json.loads(message)
        device_id = data["id"]
        event_type = data["type"]
        influxdata = []

        # Ignore LOCATION and DEVICE type events as they contain no statistic data
        if (event_type == "LOCATION") or (event_type == "DEVICE"):
            return

        event_attributes = data["attributes"]
        for event_attribute in event_attributes:
            influx_event = {
                "measurement": device_id,
                "tags": {
                    "event_type": event_type
                },
                "fields": {
                }
            }

            # event timestamp handling
            try:
                if event_attributes[event_attribute]["timestamp"]:
                    parsed_date = dateutil.parser.parse(event_attributes[event_attribute]["timestamp"])
                    influx_event["time"] = parsed_date.ctime()

            except KeyError:
                influx_event["time"] = iso

            # event field value handling
            event_field_value = event_attributes[event_attribute]["value"]

            # convert ONLINE/OFFLINE to boolean
            if event_attribute == "rfLinkState":
                if event_field_value == "ONLINE":
                    event_field_value = 1
                else:
                    event_field_value = 0

            influx_event["fields"][event_attribute] = event_field_value
            influxdata.append(influx_event)

        return influxdata

    except Exception as e:
        print("Exception", e)
        return


def main():
    # Preparing for reading config file
    PWD = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    CONFIG = configparser.ConfigParser()
    CONFIG.read('%s/settings.ini' % PWD)

    # Getting params from config
    INFLUX_HOST = CONFIG.get('INFLUXDB', 'host')
    INFLUX_PORT = CONFIG.get('INFLUXDB', 'port')
    INFLUX_DB = CONFIG.get('INFLUXDB', 'database')
    INFLUX_USER = CONFIG.get('INFLUXDB', 'username')
    INFLUX_PASSWORD = CONFIG.get('INFLUXDB', 'password')

    USERNAME = CONFIG.get('GARDENA', 'username')
    PASSWORD = CONFIG.get('GARDENA', 'password')
    API_KEY = CONFIG.get('GARDENA', 'application_api_key')

    AUTHENTICATION_ENDPOINT = CONFIG.get('GARDENA', 'authentication_endpoint')
    GARDENA_API_ENDPOINT = CONFIG.get('GARDENA', 'gardena_api_endpoint')

    # Setup InfluxDB client
    idb = InfluxDBClient(INFLUX_HOST, INFLUX_PORT, INFLUX_USER, INFLUX_PASSWORD, INFLUX_DB)

    # Authenticate and connect to Gardena Websocket Endpoint
    payload = {'grant_type': 'password', 'username': USERNAME, 'password': PASSWORD,
               'client_id': API_KEY}

    print("Logging into authentication system...")
    r = requests.post(f'{AUTHENTICATION_ENDPOINT}/v1/oauth2/token', data=payload)
    assert r.status_code == 200, r
    auth_token = r.json()["access_token"]

    headers = {
        "Content-Type": "application/vnd.api+json",
        "x-api-key": API_KEY,
        "Authorization-Provider": "husqvarna",
        "Authorization": "Bearer " + auth_token
    }

    r = requests.get(f'{GARDENA_API_ENDPOINT}/v1/locations', headers=headers)
    assert r.status_code == 200, r
    assert len(r.json()["data"]) > 0, 'location missing - user has not setup system'
    location_id = r.json()["data"][0]["id"]

    payload = {
        "data": {
            "type": "WEBSOCKET",
            "attributes": {
                "locationId": location_id
            },
            "id": "does-not-matter"
        }
    }
    print("Logged in (%s), getting WebSocket ID..." % auth_token)
    r = requests.post(f'{GARDENA_API_ENDPOINT}/v1/websocket', json=payload, headers=headers)

    assert r.status_code == 201, r
    print("WebSocket ID obtained, connecting...")
    response = r.json()
    websocket_url = response["data"]["attributes"]["url"]

    # websocket.enableTrace(True)
    client = Client(idb)
    ws = websocket.WebSocketApp(
        websocket_url,
        on_message=client.on_message,
        on_error=client.on_error,
        on_close=client.on_close)
    ws.on_open = client.on_open
    ws.run_forever(ping_interval=150, ping_timeout=1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
