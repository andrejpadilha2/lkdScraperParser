import random
from time import sleep
from timeit import default_timer as timer
from datetime import datetime

from selenium_stealth import stealth
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.generate_name_variations import generate_name_variations
from utils.methods import *
import pandas as pd
import numpy as np
import sys

def check_page_problems(page_source):
    problems = ""
    success = 1

    if "authwall" in page_source:
        print("You hit the authentication wall!")
        problems = "authwall_"
        success = 0

    if "captcha" in page_source:
        print("You hit a captcha page!")
        problems += "captcha_"
        success = 0

    if page_source.startswith("<html><head>\n    <script type=\"text/javascript\">\n"):
        print("You hit javascript obfuscated code!")
        problems += "obfuscatedJS_"
        success = 0
    
    return problems, success

def initialize_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument('--blink-settings=imagesEnabled=false')
    # options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(60)
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    return driver

def search_linkedin_profiles(linkedin_profiles_df, save_path, filename):
    total_requests = 0
    successful_requests = 0

    total_name_variations = len(linkedin_profiles_df)
    start_total_time = timer()

    shuffled_indices = np.random.permutation(linkedin_profiles_df.index)

    iter = 1
    for index in shuffled_indices:
        start_iter_time = timer()

        row = linkedin_profiles_df.loc[index]
        print("\n\n\n****************************************************************")
        print(f"Trying to find LinkedIn profile of {row['full_name']}\n")

        full_path = f"{save_path}/{normalize_string(row['full_name'])}"
        create_folder(full_path)

        print("\n---------------------------------------------")
        print(f"Iter {iter}/{total_name_variations} - Testing name variation #{index}: {row['name_variation']}")
        

        if pd.isna(row['scrapped_success_time']):
            driver = initialize_webdriver()
            sleep(random.uniform(1, 2))
            driver.get('https://www.google.com.br')
            sleep(random.uniform(1, 2))

            search_box = driver.find_element(By.NAME, 'q')
            search_query = f"{row['name_variation']} ufabc linkedin"
            search_box.send_keys(search_query)
            # for char in search_query:
            #     search_box.send_keys(char)
            #     delay = random.uniform(0.1, 0.3)
            #     sleep(delay)
            search_box.send_keys(Keys.RETURN)
            sleep(random.uniform(3, 5), 'sleeping between 3 and 5 seconds...')

            links = driver.find_elements(By.TAG_NAME, 'a')
            linkedin_links = [link for link in links if link.get_attribute('href') and 'linkedin.com/in/' in link.get_attribute('href')]

            if linkedin_links:
                # TODO
                # 1) check if the link that I am about to click was already scrapped
                # 2) check if the person studied at UFABC


                linkedin_links[0].click()
                total_requests += 1
                sleep(random.uniform(5, 7), 'sleeping between 5 and 7 seconds...')

                page_source = driver.page_source
                problems, success = check_page_problems(page_source) 
                # TODO
                # If it's the xth unsucessful reply in a row, do something

                if success:
                    print("Successful request!")
                    successful_requests += 1
                    linkedin_profiles_df.at[index, 'linkedin_profile'] = driver.current_url
                    
                    linkedin_profiles_df.at[index, 'scrapped_success_time'] = datetime.now()

                    # num_steps = random.randint(2, 4)
                    # scroll_height = driver.execute_script("return document.body.scrollHeight")
                    # scroll_step = scroll_height / num_steps

                    # for _ in range(num_steps):
                    #     driver.execute_script(f"window.scrollBy(0, {scroll_step})")
                    #     delay = random.uniform(3, 6)
                    #     sleep(delay)
                    # sleep(random.uniform(1, 2), 'sleeping between 1 and 2 seconds...')
                else:
                    print("Failed request!")
                    if pd.isna(linkedin_profiles_df.at[index, 'failed_reason']):
                        linkedin_profiles_df.at[index, 'failed_reason'] = f"({problems})"
                    else:
                        previous_failed_reason = linkedin_profiles_df.at[index, 'failed_reason'].strip("()")
                        linkedin_profiles_df.at[index, 'failed_reason'] = f"({previous_failed_reason};{problems})"
                              

                HtmlPath = f"{full_path}/{index}_{normalize_string(row['name_variation'])}_{problems}.html"
                print(f"- saving HTML to: {HtmlPath}")
                with open(HtmlPath, 'w', encoding='utf-8') as file:
                    file.write(page_source)

                linkedin_profiles_df.at[index, 'html_path'] = HtmlPath
                linkedin_profiles_df.to_csv(filename, index=False, sep=',')

                print(f"So far {successful_requests} out of {total_requests} requests to Linkedin were successful.")
            
                sleep(15, 'sleeping 15 seconds...')
                iter_time = timer() - start_iter_time
                print(f"Iteration elapsed time: {iter_time:.2f}")
                
            else:
                print("No LinkedIn search results to access.")
                if pd.isna(linkedin_profiles_df.at[index, 'failed_reason']):
                    linkedin_profiles_df.at[index, 'failed_reason'] = f"(no_linkedin_url)"
                else:
                    previous_failed_reason = linkedin_profiles_df.at[index, 'failed_reason'].strip("()")
                    linkedin_profiles_df.at[index, 'failed_reason'] = f"({previous_failed_reason};no_linkedin_url)"

            driver.close()
        else:
            print("Name variation was already scrapped, skipping...")

        iter += 1
        
        total_time = timer() - start_total_time
        print(f"Total elapsed time: {total_time:.2f}")

        # print(linkedin_profiles_df[['name_variation', 'linkedin_profile', 'last_scrapped']])
    return total_requests, successful_requests, total_time

if __name__ == "__main__":
    print("\nBEGINNING LINKEDIN SCRAPING\n")
    save_path = 'people/profilesSelenium7'
    filename = f'{save_path}/linkedin_profiles.csv'

    # Check if the file already exists
    if not os.path.exists(filename):
        create_folder(save_path)
        # Open the CSV file
        name_variations_df = pd.read_csv('people/name_variations.csv', sep=',')
        linkedin_profiles_df = name_variations_df
        linkedin_profiles_df['linkedin_profile'] = ''
        linkedin_profiles_df['scrapped_success_time'] = ''
        linkedin_profiles_df['failed_reason'] = ''
        linkedin_profiles_df['html_path'] = ''
        print(f"Creating file '{filename}'.\n")
        linkedin_profiles_df.to_csv(filename, index=False, sep=',')
        sleep(1)
    else:
        user_input = input(f"Looks like a scrapping process already started on '{save_path}'. Would you like to continue it? Type 'yes' to continue:\n> ")
        if user_input.lower() != 'yes':
            print('Exiting the scrapper.')
            sys.exit(1)

    dtypes = {
                'uid': int,
                'name_id': int,
                'full_name': str,
                'name_variation': str,
                'linkedin_profile': str,
                'failed_reason': str,
                'html_path': str
            }
    linkedin_profiles_df = pd.read_csv(filename, sep=',', dtype=dtypes, parse_dates=['scrapped_success_time'])
    total_requests, successful_requests, total_time = search_linkedin_profiles(linkedin_profiles_df, save_path, filename)

    print(f"Total requests to Linkedin: {total_requests}. Successful requests: {successful_requests}")
    print(f"Total time running the scrapper: {total_time}")
