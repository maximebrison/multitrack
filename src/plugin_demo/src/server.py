import os
import requests
import json
import time
import random
import threading

PUBLISH_IP = os.getenv('PUBLISH_IP', '127.0.0.1')
PUBLISH_PORT = os.getenv('PUBLISH_PORT', '8081')
LISTEN_PORT = os.getenv('LISTEN_PORT', '80')

print(f"PUBLISH_PORT: {PUBLISH_PORT}")
print(f"LISTEN_PORT: {LISTEN_PORT}")

# Create a HTTP server that Posts data to the PUBLISH_IP:PUBLISH_PORT
# and listens on LISTEN_PORT

url = 'http://'+PUBLISH_IP+':'+PUBLISH_PORT+'/'
myobj = {}

with open("datasource.json", "r") as f:
    raw = f.read()
    # convert raw to json object
    dataSource = json.loads(raw)

def post_identify_plugin():
    # The posted data should look like this :
    # {
    #     "type": "identify_plugin",
    #     "main_ID": <main_ID>,
    #     "actions": [<actions>],
    #     "text": <true/false>,
    #     "position": <true/false>,
    #     "status": <true/false>
    # }
    myobj = {
        "type": "identify_plugin",
        "main_ID": "dummy_source",
        "actions": ["stun", "kill", "revive"],
        "text": True,
        "position": True,
        "status": True,
        "listen_port": LISTEN_PORT
    }
    x = requests.post(url+"subscribe", json = myobj)
    print(x.text)

def post_data():
    for key in dataSource:
        # The posted data should look like this for a new position :
        # {
        #     "type": "device",
        #     "main_ID": <main_ID>,
        #     "model": <model>,
        #     "serial": <serial>,
        #     "last_updated": <last_updated>,
        #     "position": {
        #         "timestamp": <timestamp>,
        #         "latitude": <latitude>,
        #         "longitude": <longitude>
        #     }
        # }
        #
        # And this for a new text message :
        # {
        #     "type": "device",
        #     "main_ID": <main_ID>,
        #     "model": <model>,
        #     "serial": <serial>,
        #     "last_updated": <last_updated>,
        #     "text": <text>
        # }
        #
        # And this for a new status :
        # {
        #     "type": "device",
        #     "main_ID": <main_ID>,
        #     "model": <model>,
        #     "serial": <serial>,
        #     "status": <status>,
        #     "last_updated": <last_updated>
        # }
        print(key)
        for position in dataSource[key]["positions"]:
            myobj = {
                "type": "device",
                "main_ID": key,
                "model": dataSource[key]["model"],
                "serial": dataSource[key]["serial"],
                "last_updated": int(time.time()),
                "status": dataSource[key]["status"],
                "position": {
                    "timestamp": int(time.time()),
                    "latitude": position["latitude"],
                    "longitude": position["longitude"]
                }
            }
            x = requests.post(url+"data", json = myobj)
            print(x.text)
            time.sleep(2)
        for text in dataSource[key]["texts"]:
            myobj = {
                "type": "device",
                "main_ID": key,
                "model": dataSource[key]["model"],
                "serial": dataSource[key]["serial"],
                "last_updated": int(time.time()),
                "status": dataSource[key]["status"],
                "text": text
            }
            x = requests.post(url+"data", json = myobj)
            print(x.text)
            time.sleep(2)
        # for status in dataSource[key]["statuses"]:
        #     myobj = {
        #         "type": "device",
        #         "main_ID": key,
        #         "model": dataSource[key]["model"],
        #         "serial": dataSource[key]["serial"],
        #         "status": status,
        #         "last_updated": int(time.time())
        #     }
        #     x = requests.post(url+"data", json = myobj)
        #     print(x.text)
        #     time.sleep(2)


# create flask server that listens on LISTEN_PORT
from flask import Flask, request
app = Flask(__name__)

@app.route('/', methods=['POST'])
def data():
    # print the data received
    print(request.json)
    return 'OK', 200

@app.route('/text', methods=['POST'])
def text():
    # print the data received
    print(request.json)
    return 'OK', 200

@app.route('/action', methods=['POST'])
def action():
    # print the data received
    print(request.json)

    main_ID = request.json["main_ID"]
    serial = request.json["serial"]
    action = request.json["action"]

    if main_ID == "dummy_source":
        if action == "stun":
            print(f"Stunning {serial}")
            dataSource[main_ID]["status"] = "stun"
        elif action == "kill":
            print(f"Killing {serial}")
            dataSource[main_ID]["status"] = "kill"
        elif action == "revive":
            print(f"Reviving {serial}")
            dataSource[main_ID]["status"] = "alive"
        else:
            print(f"Unknown action {action} for {serial}")

    return 'OK', 200

@app.route('/', methods=['GET'])
def main():
    # print the data received
    print(request.json)
    return 'OK', 200


def create_flask_app():
    app.run(host='0.0.0.0', port=LISTEN_PORT)

def send_data():
    post_identify_plugin()
    post_data()


if __name__ == '__main__':
    # start flask app in background thread
    threading.Thread(target=create_flask_app).start()

    # keep the main thread alive
    while True:
        time.sleep(1)
        send_data()