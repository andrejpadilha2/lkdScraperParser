import os
from generate_name_variations import generate_name_variations
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
GOOGLE_APY_KEY=os.environ['GOOGLE_API_KEY']
GOOGLE_SEARCH_ENGINE_ID=os.environ['GOOGLE_SEARCH_ENGINE_ID']

class GoogleSearchError(Exception):
    pass

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()

    if 'items' not in res:
        raise GoogleSearchError("No search results found")
    
    return res['items']

name_list = ["André José de Queiroz Padilha"]#, "João Carlos Duarte Caprera", "Gabriela Bertoni dos Santos", "Guilherme Ribeiro Portugal"]

# while the profile on linkedin hasn't been matched
for name in name_list:
    for name_variation in generate_name_variations(name):
        print(f"\nTesting name variation: {name_variation}")
        query = f'"Universidade Federal do ABC" "{name_variation}"' # maybe create a variation -> UFABC 

        try:
            results = google_search(query, GOOGLE_APY_KEY, GOOGLE_SEARCH_ENGINE_ID, num=10)
        except GoogleSearchError as e:
            print(f"No search results found for {name_variation}: {str(e)}")
        else:
            for result in results:
                print(result['link'])
                

            # give preference for the most complete profile between portuguese and english
            # enter in the link using selenium or beautiful soup
            # check if the Linkedin profile match the information of the people we are looking for
            # if it does, go to the next person, if it doesn't, try the next link
        
        # if none of the links worked, try a different name combination of that same person