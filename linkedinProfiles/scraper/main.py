import random
from time import sleep
from timeit import default_timer as timer
from datetime import datetime
from linkedinProfiles.scraper.utils import add_failed_cause, check_name_subset, check_page_problems, check_studied_at_universities, initialize_webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from utils.methods import *
import pandas as pd
import sys

def search_linkedin_profiles(linkedin_profiles_df, save_path, filename):
    total_linkedin_requests = 0
    successful_linkedin_requests = 0

    total_profiles_scraped = 0
    successful_profiles_scraped = 0

    total_name_variations = len(linkedin_profiles_df)
    start_total_time = timer()

    iter = 1

    driver = initialize_webdriver()

    for profile_row in linkedin_profiles_df.itertuples():

        if total_linkedin_requests % 20 == 0 and total_linkedin_requests != 0: # restart webdriver
            print("\n\n\n========================")
            print(f"Restarting web browser.")
            print("========================\n\n\n")

            driver.close()
            driver = initialize_webdriver()

        start_iter_time = timer()

        print("\n\n\n****************************************************************")
        print(f"Trying to find LinkedIn profile of {profile_row.full_name}\n")

        full_path = f"{save_path}/{profile_row.name_id}_{normalize_string(profile_row.full_name)}"
        create_folder(full_path)

        print("\n---------------------------------------------")
        print(f"Iter {iter}/{total_name_variations} - Testing name variation #{profile_row.uid}: {profile_row.name_variation}")

        print(profile_row.failed_cause)

        if profile_row.to_scrape == 0 or not pd.isna(profile_row.failed_cause):  
            if profile_row.scraped_success_time:
                print("→ Name was already scraped, skipping...")
            else:
                print(f"→ Last Google search resulted in {profile_row.failed_cause}, skipping...")
        
        else:
            # 1 = TRUE

            sleep(2, '→ sleeping 2 seconds...')

            # TODO:
            # handle the exception: selenium.common.exceptions.WebDriverException: Message: unknown error: net::ERR_NAME_NOT_RESOLVED
            print("→ Requesting 'www.google.com.br'.")
            driver.get('https://www.google.com.br')
            sleep(random.uniform(2, 3), '→ sleeping between 2 and 3 seconds...')

            search_query = f'{profile_row.name_variation} ufabc linkedin'# using "ufabc" inside double quotes made some correct search results disappear, I really don't understand why

            print("→ Searching on Google.")
            search_box = driver.find_element(By.NAME, 'q')
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
            sleep(random.uniform(2, 3), '→ sleeping between 2 and 3 seconds...')

            links = driver.find_elements(By.TAG_NAME, 'a')

            # Select only linkedin.com/in links (which are Linkedin profiles)
            linkedin_links = [link for link in links if link.get_attribute('href') and 'linkedin.com/in/' in link.get_attribute('href')]

            # Select only the links whose profile name is a subset of the full name
            linkedin_links = [link for link in linkedin_links if check_name_subset(link.text.split(), profile_row.full_name)] 
            # TODO:
            # when we enter the webpage of that person, the name CAN BE DIFFERENT from what appeared on google search result!!!!!!
            # I need to handle this!!!
            # Example: name variation #1065, her name in the english profile is different than her name in the portuguese profile!!!!

            for link_idx, link in enumerate(linkedin_links):
                # Great, we found some Linkedin profiles to analyze!
                # But before we jump into it, we need to check one more thing:
                # If the profile URL was already scraped by ANOTHER name, we try the next link in linkedin_links (if it exists).
                
                linkedin_url = link.get_attribute('href')
                linkedin_id = linkedin_url.split("/in/")[-1].split("/")[0].split("?")[0]
                profile_already_scraped = (linkedin_profiles_df['linkedin_url'].str.contains(linkedin_id, na=False).any() and 
                                        profile_row.linkedin_url != linkedin_url)

                if profile_already_scraped:

                    if link_idx == len(linkedin_links)-1: 
                        print(f"→ Profile id '{linkedin_id}' was already scraped by another name, there are no other profiles to try, skipping...")
                        linkedin_profiles_df.loc[linkedin_profiles_df.loc[:, 'uid'] == profile_row.uid, 'to_scrape'] = 0

                        add_failed_cause(linkedin_profiles_df, profile_row.uid, 'no_linkedin_profile_available_for_namesake')
                    else:
                        print(f"→ Profile id '{linkedin_id}' was already scraped by another name, trying the next profile.")
                    continue
                    
                else:
                    # The profile URL wasn't scraped by any other name, so we can finally request it!
                    total_profiles_scraped += 1

                    # We will attempt to scrape it a few times.
                    for attempt in range(2):
                        print(f"→ Requesting '{linkedin_url}'.")
                        link.click()
                        total_linkedin_requests += 1
                        sleep(random.uniform(5, 7), '→ sleeping between 5 and 7 seconds...')

                        page_source = driver.page_source
                        problems, success = check_page_problems(page_source) 
                        # TODO
                        # If it's the xth unsucessful reply in a row, do something

                        if success:
                            # When it succeeds we want to save: the time it was scraped, linkedin URL, if the person studied at UFABC or not.
                            # The current name variation should be marked so that it doesn't get scraped again.
                            successful_linkedin_requests += 1
                            successful_profiles_scraped += 1

                            studied_at_ufabc = check_studied_at_universities(page_source, ['UFABC', 'Universidade Federal do ABC'])
                            
                            linkedin_profiles_df.loc[linkedin_profiles_df.loc[:, 'uid'] == profile_row.uid, 'to_scrape'] = 0
                            linkedin_profiles_df.loc[linkedin_profiles_df.loc[:, 'uid'] == profile_row.uid, 'linkedin_url'] = driver.current_url.split("?")[0]
                            linkedin_profiles_df.loc[linkedin_profiles_df.loc[:, 'uid'] == profile_row.uid, 'scraped_success_time'] = datetime.now()

                            if not studied_at_ufabc:
                                print("→ Succesful request, but the person did not study at UFABC.")
                                linkedin_profiles_df.loc[linkedin_profiles_df.loc[:, 'uid'] == profile_row.uid, 'failed_cause'] = f"(no_school_relationship)" 
                                # TODO: strange name and might need to add the failed cause to a list of previous failed causes
                            else:
                                # TODO:
                                # if it's the full name variation, we don't want to scrape any other name variations for that name
                                # because all other name variations are less specific than the full name, 
                                # hence they will bring more results which are LESS relevant!

                                print("→ Successful request and the person studied at UFABC!")
                                # linkedin_profiles_df.loc[linkedin_profiles_df.loc[:, 'name_id'] == profile_row.name_id, 'to_scrape'] = 0 didn't work as I expected

                            HtmlPath = f"{full_path}/{profile_row.uid}_{normalize_string(profile_row.name_variation)}_{problems}.html"
                            print(f"→ saving HTML to: '{HtmlPath}'.")
                            with open(HtmlPath, 'w', encoding='utf-8') as file:
                                file.write(page_source)

                            linkedin_profiles_df.loc[linkedin_profiles_df.loc[:, 'uid'] == profile_row.uid, 'html_path'] = HtmlPath
                            break # we don't to attempt to scrape the same profile again
                    
                        else:
                            if attempt == 0:
                                # If it fails, we return to the previous page and click on the link again.
                                # But the elements in the browser may have changed position (changed DOM), so we need to relocate the link
                                # with the href=linkedin_url that we just tried to access.

                                print("→ Failed request but will attempt again now!")
                                driver.execute_script("window.history.go(-1)")
                                sleep(random.uniform(2, 3), '→ sleeping between 2 and 3 seconds...')
                                link = driver.find_element(By.CSS_SELECTOR, f'a[href*="{linkedin_id}"]')
                                continue
                            else:
                                # When it fails for good we want to save some things: fail reason and the URL that it tried to access.
                                print("→ Failed request, not attempting again!")

                                linkedin_profiles_df.loc[linkedin_profiles_df.loc[:, 'uid'] == profile_row.uid, 'linkedin_url'] = linkedin_url

                                add_failed_cause(linkedin_profiles_df, profile_row.uid, problems)                                
                    
                    
                    print(f"→ So far {successful_linkedin_requests} out of {total_linkedin_requests} requests to Linkedin were successful.")
                    print(f"→ So far {successful_profiles_scraped} out of {total_profiles_scraped} profiles were succesfully scrapped.")
                    sleep(15, '→ sleeping 15 seconds...')
                    break
                
            if not linkedin_links:
                print("→ No LinkedIn search results to access.")

                linkedin_profiles_df.loc[linkedin_profiles_df.loc[:, 'uid'] == profile_row.uid, 'to_scrape'] = 0

                add_failed_cause(linkedin_profiles_df, profile_row.uid, 'no_linkedin_url')

            linkedin_profiles_df.to_csv(filename, index=False, sep=',')

        iter_time = timer() - start_iter_time
        print(f"→ Iteration elapsed time: {iter_time:.2f}")
        total_time = timer() - start_total_time
        print(f"Total elapsed time: {total_time:.2f}")
        iter += 1

    driver.close()

    return total_linkedin_requests, successful_linkedin_requests, total_profiles_scraped, successful_profiles_scraped, total_time

if __name__ == "__main__":
    print("\nBEGINNING LINKEDIN SCRAPING\n")
    save_path = 'people/profilesSelenium12'
    filename = f'{save_path}/linkedin_profiles.csv'

    if not os.path.exists(filename):
        create_folder(save_path)
        # Open the CSV file
        name_variations_df = pd.read_csv('people/name_variations.csv', sep=',')
        linkedin_profiles_df = name_variations_df

        linkedin_profiles_df['to_scrape'] = 1 # will track if it's still necessary to scrape this name variation
            # 0 will be False, 1 will be True
            # initially all name variations are going to be scraped, so they are naturally 1

        linkedin_profiles_df['linkedin_url'] = '' # stores linkedin_url
        linkedin_profiles_df['scraped_success_time'] = ''
        linkedin_profiles_df['failed_cause'] = '' # stores every fail attempt cause
        linkedin_profiles_df['html_path'] = '' # stores the path to the HTML file

        # Sort profiles so that more specific name variations are scraped first (full name -> first and last name -> etc)
        linkedin_profiles_df['Sort'] = linkedin_profiles_df.groupby('name_id').cumcount()
        linkedin_profiles_df.sort_values(['Sort', 'name_id'], inplace=True)
        linkedin_profiles_df.drop(columns=['Sort'], inplace=True)

        print(f"Creating file '{filename}'.\n")
        linkedin_profiles_df.to_csv(filename, index=False, sep=',')
        sleep(1)
    else:
        user_input = input(f"Looks like a scrapping process already started on '{save_path}'. Would you like to continue it? Type 'yes' to continue:\n> ")
        if user_input.lower() != 'yes':
            print('Exiting the scraper.')
            sys.exit(1)

    dtypes = {
                'uid': int,
                'name_id': int,
                'full_name': str,
                'name_variation': str,
                'to_scrape': int,
                'linkedin_url': str,
                'failed_cause': str,
                'html_path': str
            }
    linkedin_profiles_df = pd.read_csv(filename, sep=',', dtype=dtypes, parse_dates=['scraped_success_time'])
    # linkedin_profiles_df['to_scrape'] = linkedin_profiles_df['to_scrape'].replace(2, 0) # since we are beginning to scrape again, we can try to scrape the profiles marked with "Skip" again

    total_linkedin_requests, successful_linkedin_requests, \
    total_profiles_scraped, successful_profiles_scraped, \
    total_time = \
        search_linkedin_profiles(linkedin_profiles_df, save_path, filename)

    print("\n\n**************************\n")
    print("FINISHED LINKEDIN SCRAPING\n")
    print(f"Total requests to Linkedin: {total_linkedin_requests}. Successful requests: {successful_linkedin_requests}")
    print(f"Total profiles tried to scrape: {total_profiles_scraped}. Profiles successfully scraped: {successful_profiles_scraped}")
    print(f"Total time running the scraper: {total_time}")
