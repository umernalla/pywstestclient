#|-----------------------------------------------------------------------------
#|            This source code is provided under the Apache 2.0 license      --
#|  and is provided AS IS with no warranty or guarantee of fit for purpose.  --
#|                See the project's LICENSE.md for details.                  --
#|           Copyright Thomson Reuters 2017. All rights reserved.            --
#|-----------------------------------------------------------------------------


#!/usr/bin/env python
""" Simple example of requesting Reuters domain Models using Websockets """

import sys
import time
import getopt
import socket
import json
import websocket
import threading
from threading import Thread, Event

# Global Default Variables for connection
hostname = 'localhost'  
port = '15000'   
ping_timeout_interval = 30  # How often do we expect to recieve Ping from server
ping_timeout_time = 0       # If not received a Ping by this time then timeout and exit
start_time = 0              # Time when first Market Data request made

# Other Global default variables
user = 'user'       # Default username for ADS login
app_id = '256'      # Default application ID for login
position = socket.gethostbyname(socket.gethostname())
ricList = []    # List of RICs to request
viewList = []   # List of Fields (FIDs or Names) to use in View Request
domainModel = None  # Websocket interface defaults to MarketPrice if not specified
snapshot = False    # Make Snapshot request (rather than the default streaming)
dumpRcvd = False    # Dump messages received from server
dumpPP = False      # Dump the incoming Ping and outgoing Pong messages
dumpSent = False    # Dump out the Requests to the SENT to the server
dumpStatus = False  # Dump out any Status Msgs received from server
autoExit = False    # Exit once Refresh (or Status closed) received for all requests

reqCnt = 0      # Number of Data Items requested
imgCnt = 0      # Data Refresh messages received
updCnt = 0      # Update messages received
statusCnt = 0   # Status messages received
pingCnt = 0     # Ping messages (= Pongs sent)
closedCnt = 0   # Specifically Closed status message (e.g. item not found)

web_socket_app = None
web_socket_open = False
shutdown_app = False

def print_stats():
    global imgCnt, updCnt, statusCnt, pingCnt, start_time
    elapsed = 0
    if (start_time!=0):
        elapsed = time.time() - start_time
    print("Stats; Refresh: {} \tUpdates: {} \tStatus: {} \tPings: {} \tElapsed Time: {:.2f}secs"
        .format(imgCnt,updCnt,statusCnt,pingCnt, elapsed))

def set_Login(u,a,p):
    global user, app_id, position
    app_id=a
    user=u
    position=p

def set_Request_Attr(rList,rdm,snap):
    global ricList,domainModel,snapshot
    ricList=rList
    domainModel=rdm
    snapshot=snap

def set_viewList(vList):
    global viewList
    viewList=vList
    print("Set viewList to", viewList, "from", vList)

def cleanup(ws):
    global shutdown_app
    send_login_close(ws)
    shutdown_app=True   # signal to main loop to exit
    #ws.close()     # Cannot use due to Websocket client issue/bug

def reset_ping_time():          # We can call this each time we send or receive a message 
    global ping_timeout_time    # to reset the timeout for the next ping
    ping_timeout_time = time.time() + ping_timeout_interval

def check_ping_timedout():    # Has it been too long since last ping
    global shutdown_app
    if (ping_timeout_time > 0) and (time.time() > ping_timeout_time):
        print("No ping from server, timing out")
        shutdown_app = True

def process_message(ws, message_json):
    global imgCnt, updCnt, statusCnt, pingCnt, closedCnt

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
        # Count Data Item Status msg received
        if message_domain != "Login":
            statusCnt += 1
            stream_state = message_json['State']['Stream']
            data_state = message_json['State']['Data']
            # Was the item request rejected by server & stream Closed?
            if stream_state=='Closed' and data_state=='Suspect':
                closedCnt += 1
            if dumpStatus:
                print(json.dumps(message_json))
        else:
            print("LOGIN STATUS:")      # We got a Login status (a problem ?) so report it
            print(json.dumps(message_json, sort_keys=True, indent=2, separators=(',', ':')))
    elif message_type == "Ping":
        pingCnt += 1
        pong_json = { 'Type':'Pong' }
        ws.send(json.dumps(pong_json))
        if (dumpPP):
            print("RCVD:", json.dumps(message_json),
                    " SENT:", json.dumps(pong_json))

    # Cleanup and exit - if autoExit and we have received response to all requests
    if (autoExit and (reqCnt==imgCnt+closedCnt)):
        cleanup(ws)


def process_login_response(ws, message_json):
    # Get Ping timeout interval from server
    global ping_timeout_interval, start_time
    ping_timeout_interval = int(message_json['Elements']['PingTimeout'])
    start_time = time.time()
    """ Send item request """
    send_market_price_request(ws)


def send_market_price_request(ws):
    global reqCnt
    """ Create and send simple Market Price request """

    reqCnt = len(ricList)

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

def send_login_close(ws):
    logout_json = {
        'Domain': 'Login',
        'ID': 1,
        'Type': 'Close'
    }
    ws.send(json.dumps(logout_json))
    if (dumpSent):
        print("SENT Logout Request:")
        print(json.dumps(logout_json, sort_keys=True, indent=2, separators=(',', ':')))


def on_message(ws, message):
    """ Called when message received, parse message into JSON for processing """
    message_json = json.loads(message)
    if dumpRcvd:
        print("RCVD: ")
        print(json.dumps(message_json, sort_keys=True, indent=2, separators=(',', ':')))

    for singleMsg in message_json:
        process_message(ws, singleMsg)
    # We have received a message from server - so reset the Ping timeout
    reset_ping_time()

def on_error(ws, error):
    """ Called when websocket error has occurred """
    print(error)


def on_close(ws):
    """ Called when websocket is closed """
    global web_socket_open, shutdown_app
    print("WebSocket Closed")
    web_socket_open = False
    shutdown_app = True

def on_open(ws):
    """ Called when handshake is complete and websocket is open, send login """

    print("WebSocket successfully connected!")
    print_stats()
    global web_socket_open
    web_socket_open = True
    reset_ping_time()
    send_login_request(ws)


