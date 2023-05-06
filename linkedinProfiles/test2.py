import pickle
import random
import requests

# Load cookies from file
with open('utils/cookies.pkl', 'rb') as f:
    cookies_dict = pickle.load(f)

# Select a random website URL
website = random.choice(list(cookies_dict.keys()))
print(website)

# Retrieve cookies for the selected website
cookies = cookies_dict[website]
print(cookies)

# Use cookies to make a request
resp = requests.get(website, cookies=cookies)