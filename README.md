# Python Websocket API Test Client  

Python example that uses the Refinitiv Websocket interface to facilitate the consumption of realtime data.
This example is meant to be a simplistic version of the 'rmdstestclient' tool and illustrates a variety of scenarios such as:  
* EDP or ADS connection
* Batch / View Request
* Streaming / Snapshot
* Reuters Domain Models

## Disclaimer  
The source code presented in this project has been written by Refinitiv solely for the purpose of illustrating the concepts of using the Websocket interface.  None of the code has been tested for a usage in production environments.

## Setup 
### Windows/Linux/macOS
1. __Install Python__
    - Go to: <https://www.python.org/downloads/>
    - Select the __Download tile__ for the Python 3 version
    - Run the downloaded `python-<version>` file and follow installation instructions
2. __Install libraries__
    - Run (in order):
      - `pip install requests`
      - `pip install websocket-client`
	  **The websocket-client must be version 0.49 or greater**



#### Optional arguments:  
  -h, --help         show this help message and exit  
  -S SERVICE         service name to request from (default: None - server typically has default)  
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
  -f RICFILE         filename of simple RICs - one per line (default: None)  
  -ef RICFILEEXT     filename of multi domain RICs - e.g. 6|VOD.L (default: None)  
  -md DOMAIN         domain model (default: MarketPrice)  
  -t                 Snapshot request (default: False)  
  -X                 Output Received JSON Data messages to console (default: False)  
  -l LOGFILENAME     Redirect console to filename (default: None)  
  -e                 Auto Exit after all items retrieved (default: False)  
  -et EXITTIME       Exit after time in minutes (0=indefinite) (default: 0)  
  -st STATSTIMESECS  Show Statistics interval in seconds (default: 10)  
  -ss                Output the JSON messages sent to server (default: False)  
  -sp                Output Ping and Pong heartbeat messages (default: False)  
  -sos               Output received Status messages (default: False)  

### Example runtime scenarios  
Below are a few example scenarios with sample arguments

**Connect to ADS, request MarketPrice items from ELEKTRON_DD service and display summary stats**  
    -S ELEKTRON_DD -H ads1 -items VOD.L,MSFT.O,TRI.N -u umer.nalla
    
**Connect to ADS, request MarketPrice items from default service and display summary stats**  
    -H ads1 -items VOD.L,MSFT.O,TRI.N -u umer.nalla

**As above and display received data**  
    -H ads1 -items VOD.L,MSFT.O,TRI.N -u umer.nalla -X

**As above with output redirected to file log.out**  
    -H ads1 -items VOD.L,MSFT.O,TRI.N -u umer.nalla -X -l log.out

**As above except RICs read from file srics.txt (one RIC per line)**  
    -H ads1 -f srics.txt -u umer.nalla -X -l log.out

**As above except mixed Domain RICs read from file extrics.txt (numeric domain|RIC per line)**  
    -H ads1 -ef extrics.txt -u umer.nalla -X -l log.out

**Connect to EDP, request MarketPrice items from default service and display summary stats**  
    -H emea-1.pricing.streaming.edp.thomsonreuters.com -p 443 -items VOD.L,BT.L -u GE-A-01103123-5-678 -pw *%GBiUSa16PsZHt5m2ufXyZAcg4ABC  


    

