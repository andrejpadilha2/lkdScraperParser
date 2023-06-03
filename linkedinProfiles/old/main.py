import os
from time import sleep
import random
from dotenv import load_dotenv
import requests
from utils.generate_name_variations import generate_name_variations
from linkedinProfiles.old.utisl.save_cookies import get_cookies
from utils.methods import *

def run_scrapper(save_path, use_cookies=True, tor=False):   

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
    # with open('utils/cookies.pkl', 'rb') as f:
    #     cookies_dict = pickle.load(f)
    cookie_jar = None
    if use_cookies:
        cookie_jar = get_cookies()
                    
    print(cookie_jar)
    ### Add random pause in the software ###


    ### MAIN LOOP ###
    #################

    # while the profile on linkedin hasn't been matched
    # to match I would need to obviously check the name of the person, the school they went, graduation they got
    # if more than one result matches all three characteristics, it's a draw and should be solved by a human
    result_index = 0
    for name in name_list:
        print("\n\n\n****************************************************************")
        print(f"Trying to find Linkedin profile of {name}\n")
        
        full_path = normalize_string(f'{save_path}/{name}')
        create_folder(full_path)

        for name_variation in generate_name_variations(name):
            print("\n---------------------------------------------")
            print(f"Testing name variation: {name_variation}")
            
            query = f'"Universidade Federal do ABC" "{name_variation}"' # maybe create a variation for the university name as well -> e.g. UFABC and Universidade Federal do ABC

            try:
                results = google_search(query, GOOGLE_APY_KEY, GOOGLE_SEARCH_ENGINE_ID, num=10)
            except GoogleSearchError as e:
                print(f"No search results found for {name_variation}: {str(e)}")
            else:
                
                for result in results:
                    with requests.session() as s:
                        if tor:
                            renew_connection()
                            # Tor uses the 9050 port as the default socks port
                            s.proxies = {'http':  'socks5://127.0.0.1:9050',
                                         'https': 'socks5h://127.0.0.1:9050'}

                        user_agent = random.choice(user_agents)
                        referrer = random.choice(referrer_list)
                        headers = { 
                            'Connection': 'keep-alive',
                            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                            'sec-ch-ua-mobile': '?0',
                            'sec-ch-ua-platform': 'Windows',
                            'Upgrade-Insecure-Requests': '1',
                            'User-Agent': user_agent,
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-User': '?1',
                            'Sec-Fetch-Dest': 'document',
                            'Referer': referrer,
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'                            
                        }

                        # give preference to the most complete profile between portuguese and english

                        resp = s.get(
                            result['link'],
                            cookies=cookie_jar,
                            headers=headers
                        )

                        print(f"\n{result_index} - Trying to GET: {result['link']}")
                        print(f"- referrer: {referrer}")
                        print(f"- user-agent: {user_agent}")
                        print(f"- cookies: {cookie_jar}")
                        print(f"- current IP making the request: {s.get('https://ident.me').text}")
                        
                
                        html = resp.text

                        HtmlPath = f"{full_path}/{result_index}_{name_variation}.html"
                        print(f"- saving HTML to: {HtmlPath}")
                        result_index += 1
                        page_fun = open(HtmlPath,'w',encoding='utf-8')
                        page_fun.write(html)
                        page_fun.close()

                        delay = random.gauss(15,3)
                        if delay < 0:
                            delay = 10
                        sleep(delay)