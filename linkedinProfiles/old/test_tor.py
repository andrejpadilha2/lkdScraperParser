import requests
from stem import Signal
from stem.control import Controller
import time

# signal TOR for a new connection 
def renew_connection():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="049049ab")
        controller.signal(Signal.NEWNYM)

def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5h://127.0.0.1:9050'}
    return session



# Following prints your normal public IP
print(requests.get('https://ident.me').text)


# Make a request through the Tor connection
# # IP visible through Tor
# session = get_tor_session()
# print(session.get('https://ident.me').text)
# # Above should print an IP different than your public IP

while True:
    # Make a request through the Tor connection
    # IP visible through Tor
    renew_connection()
    session = get_tor_session()
    print(session.get('https://ident.me').text)
    time.sleep(10)

