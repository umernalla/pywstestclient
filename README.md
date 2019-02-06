# pywstestclient
Python Websocket API Test Client

Python example that uses the Refinitiv Websocket interface to facilitate the consumption of realtime data.
This example is meant to be a simplistic version of the 'rmdstestclient' tool

Mandatory arguments:  
  -S SERVICE         service name to request from (default: None)  
  
Optional arguments:  
  -h, --help         show this help message and exit  
  -H HOST            hostname of ADS server or EDP endpoint (default: ads1)  
  -ah AUTHHOSTNAME   authorization server (default: api.edp.thomsonreuters.com)  
  -p PORT            port of the ADS server or EDP (default: 15000)  
  -ap AUTHPORT       port of the authorisation server (default: 443)  
  -u USER            login user name (default: your local os username)  
  -pw PASSWORD       Specify EDP user password to connect to EDP (default: None)  
  -pos POSITION      application position (default: your local IP address)  
  -aid APPID         application Identifier (default: 256)  
  -items ITEMLIST    comma-separated list of RICs (default: None)  
  -vfids VIEWFIDS    comma-separated list of Field IDs for View (default: None)  
  -vnames VIEWNAMES  comma-separated list of Field Names for View (default: None)  
  -f RICFILE         simple file of RICs (default: None)  
  -md DOMAIN         domain model (default: None)  
  -t                 Snapshot request (default: False)  
  -X                 Output Received JSON Data messages to console (default: False)  
  -l LOGFILENAME     Redirect console to filename (default: None)  
  -e                 Auto Exit after all items retrieved (default: False)  
  -et EXITTIME       Exit after time in minutes (0=indefinite) (default: 0)  
  -st STATSTIMESECS  Show Statistics interval in seconds (default: 10)  
  -ss                Output the JSON messages sent to server (default: False)  
  -sp                Output Ping and Pong heartbeat messages (default: False)  
  -sos               Output received Status messages (default: False)  
  
NOT YET IMPLEMENTED  
  -ef RICFILEEXT     multi domain file of RICs - e.g. 6|VOD.L (default: None)  
  
  
