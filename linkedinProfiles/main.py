import os
import requests
from time import sleep
from selenium import webdriver
import chromedriver_binary
from generate_name_variations import generate_name_variations
from googleapiclient.discovery import build
from dotenv import load_dotenv


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




### ENVIRONMENT VARIABLES ###
#############################
load_dotenv()
GOOGLE_APY_KEY=os.environ['GOOGLE_API_KEY']
GOOGLE_SEARCH_ENGINE_ID=os.environ['GOOGLE_SEARCH_ENGINE_ID']

### COOKIES TO ACCESS LINKEDIN ###
######################################
driver = webdriver.Chrome()
sleep(5)
driver.maximize_window()
sleep(5)
driver.get("https://www.linkedin.com/")
sleep(5)

cookies_dict = {}
for cookie in driver.get_cookies():
        cookies_dict[cookie['name']] = cookie['value']
        
driver.close()
sleep(5)


### Names list ###
##################
name_list = ["André José de Queiroz Padilha", "João Carlos Duarte Caprera", "Gabriela Bertoni dos Santos", "Guilherme Ribeiro Portugal"]


### MAIN LOOP ###
#################

# while the profile on linkedin hasn't been matched
for name in name_list:
    for name_variation in generate_name_variations(name):
        print(f"\nTesting name variation: {name_variation}")
        query = f'"Universidade Federal do ABC" "{name_variation}"' # maybe create a variation for the university name as well -> e.g. UFABC and Universidade Federal do ABC

        try:
            results = google_search(query, GOOGLE_APY_KEY, GOOGLE_SEARCH_ENGINE_ID, num=10)
        except GoogleSearchError as e:
            print(f"No search results found for {name_variation}: {str(e)}")
        else:
            for result in results:
                print(result['link'])
                # give preference to the most complete profile between portuguese and english

                resp = requests.get(result['link'],
                     cookies=cookies_dict,
                     headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
                              'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                                                   'accept-encoding': 'gzip, deflate, br',
                                                   'accept-language': 'en-US,en;q=0.9',
                                                   'upgrade-insecure-requests': '1',
                                                   'scheme': 'https'})
        
                html = resp.text



                HtmlPath = f"profiles/{name_variation}.html"
                page_fun = open(HtmlPath,'w',encoding='utf-8')
                page_fun.write(html)
                page_fun.close()
                sleep(5)
        