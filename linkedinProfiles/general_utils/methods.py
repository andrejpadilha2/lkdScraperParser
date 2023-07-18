import os
from googleapiclient.discovery import build
from unidecode import unidecode
import re
from stem import Signal
from stem.control import Controller
import time

### FUNCTIONS ###
#################
class GoogleSearchError(Exception):
    pass

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()

    if 'items' not in res:
        raise GoogleSearchError("No search results found")
    
    return res['items']

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"→ Created folder: {folder_name}.")
    else:
        print(f"→ Folder already exists: {folder_name}.")

def normalize_string(input_string):
    # Remove accents
    normalized_string = unidecode(input_string)

    # Replace whitespaces with underscores
    normalized_string = re.sub(r'\s+', '_', normalized_string)

    # Convert to lower case
    normalized_string = normalized_string.lower()

    return normalized_string


def sleep_print(seconds, message=None):
    if message:
        print(message)
        time.sleep(seconds)
    else:
        time.sleep(seconds)

# signal TOR for a new connection 
def renew_connection():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="xxxx")
        controller.signal(Signal.NEWNYM)