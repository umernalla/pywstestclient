import time
import argparse
import sys
import socket
import getpass
import market_price
import websocket
import threading
from threading import Thread, Event

# Global Variables
simpleRics=None
extRics=None
opts=None
ws_app=None

def readSimpleRicsFile():
    global simpleRics
    with open(opts.ricFile, 'r') as f:
        simpleRics = f.read().splitlines()  # using read.splitlines to avoid \n on end of each RIC
    print(simpleRics)

def readExtRicsFile():
    with open(opts.ricFileExt, 'r') as f:
        tmpExtRics = f.read().splitlines() # using read.splitlines to strip \n on end of each RIC
    extRics=[]
    for xRic in tmpExtRics:
        tmp = xRic.split("|")
        try:
            extRics.append((int(tmp[0]), str(tmp[1])))
        except:pass
    print(extRics)

def parse_rics():
    global simpleRics
    if (opts.itemList!=None):
        simpleRics = opts.itemList.split(',')
        print(simpleRics)
    elif (opts.ricFile!=None):
        readSimpleRicsFile()
    elif (opts.ricFileExt!=None):
        readExtRicsFile()

def validate_options():
    global opts
    # Dont allow both FIDS and Field Names to be specifed for View request
    if ((opts.viewFIDs!=None) and (opts.viewNames!=None)):  
        print('Only one type of View allowed; -vfids or -vnames')
        return False

    ricLists = (opts.itemList, opts.ricFile, opts.ricFileExt)
    ricListCnt=0
    for rics in ricLists:
        if (rics!=None):
            ricListCnt+=1

    if (ricListCnt>1):
        print('Only one RIC list specifier allowed; -items, -f or -ef')
        return False
    elif (ricListCnt==0):
        print('Must specify some RICs using one of the following; -items, -f or -ef')
        return False
    else:
        parse_rics()

    if (opts.exitTimeMins>0) and (opts.statsTimeSecs > (opts.exitTimeMins*60)):
        opts.statsTimeSecs ==  opts.exitTimeMins*60

    return True

def parse_args(args=None):
    parser = argparse.ArgumentParser(description='rmdstestclient python websocket version',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
                       
    parser.add_argument('-S', dest='service',
                        help='service name to request from',
                        required='True')
    parser.add_argument('-H', dest='host',
                        help='hostname / ip of server',
                        default='ads1')
    parser.add_argument('-p', dest='port',
                        help='port of the server',
                        type=int,
                        default=15000)
    parser.add_argument('-u', dest='user',
                        help='login user name',
                        default=getpass.getuser())
    parser.add_argument('-pw', dest='password',
                        help='EDP user password')
    parser.add_argument('-pos', dest='position',
                        help='application position',
                        default=socket.gethostbyname(socket.gethostname()))
    parser.add_argument('-aid', dest='appID',
                        help='application Identifier',
                        default='256')
    parser.add_argument('-items', dest='itemList',
                        help='comma-separated list of RICs')
    parser.add_argument('-vfids', dest='viewFIDs',
                        help='comma-separated list of Field IDs for View')
    parser.add_argument('-vnames', dest='viewNames',
                        help='comma-separated list of Field Names for View')
    parser.add_argument('-f', dest='ricFile',
                        help='simple file of RICs')
    parser.add_argument('-ef', dest='ricFileExt',
                        help='multi domain file of RICs - e.g. 6|VOD.L')
    parser.add_argument('-md', dest='domain',
                        help='domain model')
    parser.add_argument('-t', dest='snapshot',
                        help='Snapshot request',
                        default=False,
                        action='store_true')
    parser.add_argument('-X', dest='dump',
                        help='Dump to console',
                        default=False,
                        action='store_true')
    parser.add_argument('-e', dest='autoExit',
                        help='Auto Exit after all items retrieved',
                        default=False,
                        action='store_true')
    parser.add_argument('-et', dest='exitTimeMins',
                        help='Exit after time in minutes (0=indefinite)',
                        type=int,
                        default=0)
    parser.add_argument('-st', dest='statsTimeSecs',
                        help='Show Statistics interval in seconds',
                        type=int,
                        default=10)
    parser.add_argument('-ss', dest='showSentMsgs',
                        help='Output the JSON messages sent to server',
                        default=False,
                        action='store_true')
    parser.add_argument('-sp', dest='showPingPong',
                        help='Output Ping and Pong heartbeat messages',
                        default=False,
                        action='store_true')
    
    return (parser.parse_args(args))

if __name__ == '__main__':
    opts = parse_args(sys.argv[1:])
    print(opts)
    if not validate_options():
        print('Exit due to invalid parameters')
        sys.exit(2)

    #print('Valid parameters', simpleRics) 
    market_price.setLogin(opts.user,
                        opts.appID,
                        opts.position)

    market_price.dumpRcvd = opts.dump
    market_price.dumpPP = opts.showPingPong
    market_price.dumpSent = opts.showSentMsgs

    market_price.setRequestAttr(simpleRics,opts.domain,opts.snapshot)

    if (opts.viewNames!=None):
        vList = opts.viewNames.split(',')
        market_price.set_viewList(vList)
    elif (opts.viewFIDs!=None):
        vList = list(map(int, opts.viewFIDs.split(',')))
        market_price.set_viewList(vList)

    # Start websocket handshake
    ws_address = "ws://{}:{}/WebSocket".format(opts.host, opts.port)
    print("Connecting to WebSocket " + ws_address + " ...")
    ws_app = websocket.WebSocketApp(ws_address, header=['User-Agent: Python'],
                                        on_message=market_price.on_message,
                                        on_error=market_price.on_error,
                                        on_close=market_price.on_close,
                                        subprotocols=['tr_json2'])
    ws_app.on_open = market_price.on_open
    # Event loop
    wst = threading.Thread(target=ws_app.run_forever)
    wst.start()

    try:
        if (opts.exitTimeMins>0):   # Loop for x minutes
            end_time = time.time() + 60*opts.exitTimeMins
            print("Run for", opts.exitTimeMins, "minute(s)")
            while time.time() < end_time:
                time.sleep(opts.statsTimeSecs)
                market_price.print_stats()
        else:                   
            print("Run indefinitely - CTRL+C to break")
            while True:         # Loop for ever     
                time.sleep(opts.statsTimeSecs)
                market_price.print_stats()
    except KeyboardInterrupt:
       pass
    finally:
        ws_app.close()
        
    market_price.print_stats()

#    mydict = vars(opts)
#    print('Invoked with the following options')
#    for myarg in mydict:
#        print (myarg, ':', mydict[myarg])
#
# python pwtestclient -S ELEKTRON_DD -h ads1 -p 5900 -items VOD.L,BT.L,BP.L