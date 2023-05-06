import os
import requests
from time import sleep
from generate_name_variations import generate_name_variations
from dotenv import load_dotenv
import random
import pickle
from utils.methods import *
from torrequest import TorRequest

### ENVIRONMENT VARIABLES ###
#############################
load_dotenv()
GOOGLE_APY_KEY=os.environ['GOOGLE_API_KEY']
GOOGLE_SEARCH_ENGINE_ID=os.environ['GOOGLE_SEARCH_ENGINE_ID']

### Names list ###
##################
with open('utils/names_list.txt') as f:
    name_list = f.read().splitlines()

### User-agent list ###
#####################
with open('utils/user_agents.txt') as f:
    user_agents = f.read().splitlines()

### Referrer list ###
#####################
with open('utils/referrer.txt') as f:
    referrer_list = f.read().splitlines()

### Cookies list ###
#####################
with open('utils/cookies.pkl', 'rb') as f:
    cookies_dict = pickle.load(f)
                 
### Add random pause in the software ###


### MAIN LOOP ###
#################

# while the profile on linkedin hasn't been matched
# to match I would need to obviously check the name of the person, the school they went, graduation they got
# if more than one result matches all three characteristics, it's a draw and should be solved by a human
with TorRequest(proxy_port=9050, ctrl_port=9051, password=None) as tr:
    for name in name_list:
        print("\n\n\n****************************************************************")
        print(f"Trying to find Linkedin profile of {name}\n")
        
        path = normalize_string(f'profilesTor/{name}')
        create_folder(path)

        for name_variation in generate_name_variations(name):
            print("\n---------------------------------------------")
            print(f"Testing name variation: {name_variation}")
            

            query = f'"Universidade Federal do ABC" "{name_variation}"' # maybe create a variation for the university name as well -> e.g. UFABC and Universidade Federal do ABC

            try:
                results = google_search(query, GOOGLE_APY_KEY, GOOGLE_SEARCH_ENGINE_ID, num=10)
            except GoogleSearchError as e:
                print(f"No search results found for {name_variation}: {str(e)}")
            else:
                result_index = 0
                for result in results:

                    user_agent = random.choice(user_agents)
                    referrer = random.choice(referrer_list)
                    cookies = cookies_dict[referrer]

                    print(f"\nTrying to GET: {result['link']}")
                    print(f"- referrer: {referrer}")
                    print(f"- user-agent: {user_agent}")
                    print(cookies)

                    
                    # give preference to the most complete profile between portuguese and english

                    resp = tr.get(result['link'],
                                        cookies=cookies,
                                        headers={'user-agent': user_agent,
                                                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                                                'accept-encoding': 'gzip, deflate, br',
                                                'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                                                'upgrade-insecure-requests': '1',
                                                'scheme': 'https',
                                                'referer': referrer})
            
                    html = resp.text

                    HtmlPath = f"{path}/{name_variation}_{result_index}.html"
                    result_index += 1
                    page_fun = open(HtmlPath,'w',encoding='utf-8')
                    page_fun.write(html)
                    page_fun.close()

                    delay = random.gauss(15,3)
                    if delay < 0:
                        delay = 10
                    sleep(delay)

                    tr.reset_identity()