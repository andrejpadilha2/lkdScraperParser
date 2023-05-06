import os
from time import sleep
from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support import expected_conditions as EC
import pickle

with open('utils/referrer.txt') as f:
    website_list = f.read().splitlines()

cookies_dict = {}
for website in website_list:
    driver = webdriver.Chrome()
    sleep(5)
    driver.maximize_window()
    sleep(5)
    driver.get(website)
    sleep(5)

    for cookie in driver.get_cookies():
        cookies_dict.setdefault(website, {})[cookie['name']] = cookie['value']

    driver.close()
    sleep(5)

# Save cookies to a file
with open('utils/cookies.pkl', 'wb') as f:
    pickle.dump(cookies_dict, f)