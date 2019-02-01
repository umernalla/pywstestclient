#|-----------------------------------------------------------------------------
#|            This source code is provided under the Apache 2.0 license      --
#|  and is provided AS IS with no warranty or guarantee of fit for purpose.  --
#|                See the project's LICENSE.md for details.                  --
#|           Copyright Thomson Reuters 2017. All rights reserved.            --
#|-----------------------------------------------------------------------------


#!/usr/bin/env python
""" Simple example of outputting Market Price JSON data using Websockets """

import sys
import time
import getopt
import socket
import json
import websocket
import threading
from threading import Thread, Event

# Global Default Variables use by __main__
hostname = 'localhost'  
port = '15000'   

# Other Global default variables
user = 'user'
app_id = '256'
position = socket.gethostbyname(socket.gethostname())
ricList = []    # List of RICs to request
viewList = []   # List of Fields (FIDs or Names) to use in View Request
domainModel = None  # Websocket interface defaults to MarketPrice if not specified
snapshot = False    # Make Snapshot request (rather than the default streaming)
dumpRcvd = False    # Dump messages received from server
dumpPP = False      # Dump the incoming Ping and outgoing Pong messages
dumpSent = False    # Dump out the Requests to the SENT to the server

imgCnt = 0
updCnt = 0
statusCnt = 0
pingCnt = 0

web_socket_app = None
web_socket_open = False

def print_stats():
    global imgCnt, updCnt, statusCnt, pingCnt
    print("Stats; Refresh:",imgCnt," Updates:",updCnt," Status:",statusCnt,"Pings:",pingCnt)

def setLogin(u,a,p):
    global user, app_id, position
    app_id=a
    user=u
    position=p

def setRequestAttr(rList,rdm,snap):
    global ricList,domainModel,snapshot
    ricList=rList
    domainModel=rdm
    snapshot=snap

def set_viewList(vList):
    global viewList
    viewList=vList
    print("Set viewList to", viewList, "from", vList)


def process_message(ws, message_json):
    global imgCnt, updCnt, statusCnt, pingCnt

    """ Parse at high level and output JSON of message """
    message_type = message_json['Type']
    
    message_domain = "MarketPrice"  # Dont get Domain in MarketPrice message
    if 'Domain' in message_json:
        message_domain = message_json['Domain']

    if message_type == "Refresh":
        if message_domain == "Login":
            process_login_response(ws, message_json)
        else:
            imgCnt += 1     # Refresh for a non-Login i.e. Data Domain
    elif message_type == "Update":
        updCnt += 1
    elif message_type == "Status":
        if message_domain != "Login":
            statusCnt += 1
        else:
            print("LOGIN STATUS:")      # We got a Login status so report it
            print(json.dumps(message_json, sort_keys=True, indent=2, separators=(',', ':')))
    elif message_type == "Ping":
        pingCnt += 1
        pong_json = { 'Type':'Pong' }
        ws.send(json.dumps(pong_json))
        if (dumpPP):
            print("RCVD:", json.dumps(message_json),
                    " SENT:", json.dumps(pong_json))


def process_login_response(ws, message_json):
    """ Send item request """
    send_market_price_request(ws)


def send_market_price_request(ws):
    """ Create and send simple Market Price request """

    mp_req_json = {
        'ID': 2,
        'Key': {
            'Name': ricList,
        },
    }
    if (len(viewList)>0):
        mp_req_json['View'] = viewList
    if (domainModel!=None):
        mp_req_json['Domain'] = domainModel
    if snapshot:
        mp_req_json['Streaming'] = False

    ws.send(json.dumps(mp_req_json))
    if (dumpSent):
        print("SENT MP Request:")
        print(json.dumps(mp_req_json, sort_keys=True, indent=2, separators=(',', ':')))


def send_login_request(ws):
    """ Generate a login request from command line data (or defaults) and send """
    login_json = {
        'ID': 1,
        'Domain': 'Login',
        'Key': {
            'Name': '',
            'Elements': {
                'ApplicationId': '',
                'Position': ''
            }
        }
    }

    login_json['Key']['Name'] = user
    login_json['Key']['Elements']['ApplicationId'] = app_id
    login_json['Key']['Elements']['Position'] = position

    ws.send(json.dumps(login_json))
    if (dumpSent):
        print("SENT Login Request:")
        print(json.dumps(login_json, sort_keys=True, indent=2, separators=(',', ':')))


def on_message(ws, message):
    """ Called when message received, parse message into JSON for processing """
    message_json = json.loads(message)
    if dumpRcvd:
        print("RCVD: ")
        print(json.dumps(message_json, sort_keys=True, indent=2, separators=(',', ':')))

    for singleMsg in message_json:
        process_message(ws, singleMsg)


def on_error(ws, error):
    """ Called when websocket error has occurred """
    print(error)


def on_close(ws):
    """ Called when websocket is closed """
    global web_socket_open
    print("WebSocket Closed")
    web_socket_open = False


def on_open(ws):
    """ Called when handshake is complete and websocket is open, send login """

    print("WebSocket successfully connected!")
    print_stats()
    global web_socket_open
    web_socket_open = True
    send_login_request(ws)


if __name__ == "__main__":

    # Get command line parameters
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["help", "hostname=", "port=", "app_id=", "user=", "position="])
    except getopt.GetoptError:
        print('Usage: market_price.py [--hostname hostname] [--port port] [--app_id app_id] [--user user] [--position position] [--help]')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("--help"):
            print('Usage: market_price.py [--hostname hostname] [--port port] [--app_id app_id] [--user user] [--position position] [--help]')
            sys.exit(0)
        elif opt in ("--hostname"):
            hostname = arg
        elif opt in ("--port"):
            port = arg
        elif opt in ("--app_id"):
            app_id = arg
        elif opt in ("--user"):
            user = arg
        elif opt in ("--position"):
            position = arg

    # Start websocket handshake
    ws_address = "ws://{}:{}/WebSocket".format(hostname, port)
    print("Connecting to WebSocket " + ws_address + " ...")
    web_socket_app = websocket.WebSocketApp(ws_address, header=['User-Agent: Python'],
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close,
                                        subprotocols=['tr_json2'])
    web_socket_app.on_open = on_open

    # Event loop
    wst = threading.Thread(target=web_socket_app.run_forever)
    wst.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        web_socket_app.close()
