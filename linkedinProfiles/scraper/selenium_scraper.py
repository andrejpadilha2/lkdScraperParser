from datetime import datetime
import json
import os
import random
import sys
import pandas as pd
from timeit import default_timer as timer
from linkedinProfiles.config import DATA_PATH

from linkedinProfiles.general_utils.methods import create_folder, normalize_string, sleep_print
from linkedinProfiles.scraper.custom_chrome_driver import CustomChromeDriver
from linkedinProfiles.scraper.generate_name_variations import generate_name_variations_linkedin_csv
from linkedinProfiles.scraper.utils import check_profile_already_scraped, check_profile_availability, check_profile_name_subset_full_name, check_studied_at_universities, get_linkedin_url_id, get_page_problems, get_valid_linkedin_link_elements, save_html, update_results

from linkedinProfiles.scraper.config import NAME_VARIATIONS_LINKEDIN_COLUMNS, NAME_VARIATIONS_LINKEDIN_PATH, NAMES_LIST_PATH, NON_UFABC_STUDENTS_PATH, UNAVAILABLE_PROFILES_PATH

class SeleniumScraper:
    def __init__(self):
        self.start_total_time = timer()

        self.NAME_VARIATIONS_LINKEDIN_PATH = NAME_VARIATIONS_LINKEDIN_PATH
        self.UNAVAILABLE_PROFILES_PATH = UNAVAILABLE_PROFILES_PATH
        self.NON_UFABC_STUDENTS_PATH = NON_UFABC_STUDENTS_PATH
        self.NAMES_LIST_PATH = NAMES_LIST_PATH

        # Load files
        linkedin_profiles_csv_exists = os.path.exists(self.NAME_VARIATIONS_LINKEDIN_PATH)
        if not linkedin_profiles_csv_exists:
            generate_name_variations_linkedin_csv(self.NAMES_LIST_PATH, self.NAME_VARIATIONS_LINKEDIN_PATH)       
            sleep_print(1, "sleeping 1 second...")
        else:
            user_input = input(f"Looks like a scrapping process already started on '{self.NAME_VARIATIONS_LINKEDIN_PATH}'.\nWould you like to continue it? Type 'yes' to continue:\n> ")
            if user_input.lower() != 'yes':
                print('Exiting the scraper.')
                sys.exit(1)
        name_variations_linkedin_df = pd.read_csv(self.NAME_VARIATIONS_LINKEDIN_PATH, sep=',', dtype=NAME_VARIATIONS_LINKEDIN_COLUMNS, parse_dates=['scraped_success_time'])
        self.name_variations_linkedin_df = name_variations_linkedin_df
        
        if not os.path.exists(self.UNAVAILABLE_PROFILES_PATH):
            with open(self.UNAVAILABLE_PROFILES_PATH, 'w') as file:
                json.dump([], file)

        with open(self.UNAVAILABLE_PROFILES_PATH, 'r') as file:
                self.unavailable_profiles = json.load(file)

        if not os.path.exists(self.NON_UFABC_STUDENTS_PATH):
            with open(self.NON_UFABC_STUDENTS_PATH, 'w') as file:
                json.dump([], file)

        with open(self.NON_UFABC_STUDENTS_PATH, 'r') as file:
                self.non_ufabc_students = json.load(file)

        

        self.total_name_variations = len(self.name_variations_linkedin_df)
        self.total_linkedin_requests = 0
        self.successful_linkedin_requests = 0
        self.total_profiles_scraped = 0
        self.successful_profiles_scraped = 0
        # self.linkedin_requests_count = 0
        self.name_variation_idx = 0
        self.try_next_link = True

        self.driver = CustomChromeDriver(headless=False)
        
        


    def run(self):
        # !!!!!!!!!!!!!
        # TODO: maybe each name_variation could be an instance of a NameVariation class
        # that instance would have its own attributes, like "full_path" to save files and so on
        for name_variation in self.name_variations_linkedin_df.itertuples():
            start_iter_time = timer()
            self.name_variation_idx += 1
            
            self.check_driver_restart()

            print("\n\n\n****************************************************************")
            print(f"Trying to find LinkedIn profile of {name_variation.full_name}\n")
            print("\n---------------------------------------------")
            print(f"Iter {self.name_variation_idx}/{self.total_name_variations} - Testing name variation #{name_variation.uid}: {name_variation.name_variation}")

            # TODO: make full_path an instance variable of name_variation
            full_path = f"{DATA_PATH}/{name_variation.name_id}_{normalize_string(name_variation.full_name)}"
            create_folder(full_path)

            self.process_row(name_variation, full_path)
            
            # Save all three files
            self.name_variations_linkedin_df.to_csv(self.NAME_VARIATIONS_LINKEDIN_PATH, index=False, sep=',')
            with open(self.UNAVAILABLE_PROFILES_PATH, 'w') as file:
                json.dump(self.unavailable_profiles, file)
            with open(self.NON_UFABC_STUDENTS_PATH, 'w') as file:
                json.dump(self.non_ufabc_students, file)

            iter_time = timer() - start_iter_time
            print(f"→ Iteration elapsed time: {iter_time:.2f}")
            total_time = timer() - self.start_total_time
            print(f"Total elapsed time: {total_time:.2f}")

    def process_row(self, name_variation, full_path):
        
        if name_variation.to_scrape == 0 or not pd.isna(name_variation.failed_cause):
            self.handle_already_scraped_name_variation(name_variation)
        else:
            self.process_name_variation(name_variation, full_path)

    def process_name_variation(self, name_variation, full_path):
        
        sleep_print(2, '→ sleeping 2 seconds...')

        self.driver.request_website('https://www.google.com.br')
        sleep_print(random.uniform(2, 3), '→ sleeping between 2 and 3 seconds...')

        # using "ufabc" inside double quotes made some correct search results disappear, 
        # I really don't understand why
        search_query = f'{name_variation.name_variation} ufabc linkedin'
        self.driver.search_google(search_query)
        sleep_print(random.uniform(2, 3), '→ sleeping between 2 and 3 seconds...')

        links = self.driver.find_linkedin_links()
        linkedin_link_elements = (
            get_valid_linkedin_link_elements(links, name_variation.full_name,
                                                self.unavailable_profiles, 
                                                self.non_ufabc_students)
        )

        self.try_next_link = True
        for link_idx, link in enumerate(linkedin_link_elements):
            # Great, we found some Linkedin profiles to analyze!
            # But before we jump into it, we need to check one more thing:
            # If the profile URL was already scraped by ANOTHER name, we try the next link in linkedin_link_elements (if it exists).
                
            profile_already_scraped = check_profile_already_scraped(link, self.name_variations_linkedin_df, name_variation.linkedin_url)
            linkedin_url, linkedin_id = get_linkedin_url_id(link)

            if profile_already_scraped:
                self.handle_already_scraped_profile(link_idx, linkedin_link_elements,
                                                    linkedin_id, name_variation)

            else:
                # The profile URL wasn't scraped by any other name, so we can finally request it!
                self.total_profiles_scraped += 1
                self.request_linkedin_profile(link, linkedin_url,
                                                name_variation, full_path)

                print(f"→ So far {self.successful_linkedin_requests} out of {self.total_linkedin_requests} requests to Linkedin were successful.")
                print(f"→ So far {self.successful_profiles_scraped} out of {self.total_profiles_scraped} profiles were succesfully scrapped.")
                sleep_print(15, '→ sleeping 15 seconds...')

                if not self.try_next_link:
                    break
                print("→ Trying next available profile.")
            
        if not linkedin_link_elements:
            print("→ No LinkedIn search results to access.")
            update_results(self.name_variations_linkedin_df, name_variation.uid, 0, failed_cause='no_linkedin_url')

        elif self.try_next_link:
            print("→ No Linkedin profile found. No other Linkedin profiles to try.")
            update_results(self.name_variations_linkedin_df, name_variation.uid, 0, failed_cause='no_suitable_linkedin_profile')

    def handle_already_scraped_name_variation(self, name_variation):
        if name_variation.scraped_success_time:
            print("→ Name was already scraped, skipping...")
        else:
            print(f"→ Last Google search resulted in {name_variation.failed_cause}, skipping...")


    def handle_already_scraped_profile(self, link_idx, linkedin_link_elements, linkedin_id, name_variation):
        if link_idx == len(linkedin_link_elements)-1: 
            print(f"→ Profile id '{linkedin_id}' was already scraped by another name, there are no other profiles to try, skipping...")
            update_results(self.name_variations_linkedin_df, name_variation.uid, 0, failed_cause='no_linkedin_profile_available_for_namesake')
        else:
            print(f"→ Profile id '{linkedin_id}' was already scraped by another name, trying the next profile.")


    def request_linkedin_profile(self, link, linkedin_url, 
                                 name_variation, full_path):
        for attempt in range(2):
            self.total_linkedin_requests += 1

            self.driver.open_link_new_tab(link, linkedin_url) # TODO: what if the internet connection is lost in this step?
            sleep_print(random.uniform(5, 7), '→ sleeping between 5 and 7 seconds...')
            page_source = self.driver.page_source
            is_successful_request, problems = get_page_problems(page_source)

            # TODO
            # If it's the xth unsucessful reply in a row, do something (maybe change IP)

            if is_successful_request:
                self.successful_linkedin_requests += 1
                self.handle_successful_request(page_source, name_variation,
                                               problems, full_path)
                self.driver.close_new_tab()
                break
                
            else:
                if attempt == 0:
                    # If it fails, we return to the main tab and click on the link again.
                    print("→ Failed request but will attempt again now!")
                    sleep_print(random.uniform(2, 3), '→ sleeping between 2 and 3 seconds...')
                else:
                    # When it fails for good we want to save some things: fail reason and the URL that it tried to access.
                    print("→ Failed request, not attempting again!")    
                    update_results(self.name_variations_linkedin_df, name_variation.uid, 1, failed_cause=problems)
                    self.try_next_link = False                           
        
                self.driver.close_new_tab()


    def handle_successful_request(self, page_source, name_variation, 
                                  problems, full_path):
        
        current_url = self.driver.current_url.split("?")[0]
        
        is_profile_available = check_profile_availability(page_source)
        if is_profile_available:

            is_profile_name_subset_full_name = check_profile_name_subset_full_name(page_source, name_variation.full_name)
            if is_profile_name_subset_full_name:

                is_ufabc_student = check_studied_at_universities(page_source, ['UFABC', 'Universidade Federal do ABC'])
                if is_ufabc_student:
                    self.successful_profiles_scraped += 1
                    self.try_next_link = False
                    print("→ Successful request and the person studied at UFABC!")
                    # TODO:
                    # if it's the full name variation, we don't want to scrape any other name variations for that name
                    # because all other name variations are less specific than the full name, 
                    # hence they will bring more results which are LESS relevant!
                    saved_html_path = save_html(full_path, page_source, name_variation.uid, name_variation.name_variation, problems)
                    update_results(self.name_variations_linkedin_df, name_variation.uid, 0, current_url, datetime.now(), saved_html_path)
                else:
                    print("→ Succesful request, but the person did not study at UFABC; will try next available link.")
                    self.non_ufabc_students.append(current_url)
                    
            else:
                # TODO: this profile could be a UFABC student, so it would be great to save the profile in a "saved for later" folder so that we don't request the same profile twice
                print("→ Succesful request, but profile name is not a subset of the person full name, will try next available link.")
        else:
            print("→ Succesful request, but profile is not available, will try next available link.")
            self.unavailable_profiles.append(current_url)


    def check_driver_restart(self):
        if (self.total_linkedin_requests % 20 == 0 or self.total_linkedin_requests % 21 == 0) and self.total_linkedin_requests != 0:
                self.driver.restart()



# Use Logging Instead of Print:
# Instead of using print statements to track the progress, consider using the logging library. This would allow you to easily control the level of output (DEBUG, INFO, WARN, etc.), as well as write logs to a file, which can be very helpful for post-execution analysis.

# Error Handling Class:
# You may consider creating an ErrorHandling class that can take care of all the error checking. For example, you can move the error-checking methods such as get_page_problems or check_profile_availability to this class.

# Data Management Class:
# Consider creating a DataManagement class that would handle tasks like reading and writing to files, validating and cleaning data. This could include methods that currently exist in your SeleniumScraper class like reading and writing the unavailable_profiles and non_ufabc_students.

# Separate Scrape Management Class:
# Some methods in SeleniumScraper seem to be more about managing the overall scrape, like run and process_row. It might be helpful to create a ScrapeManager class to take care of these. Then, SeleniumScraper can focus on actual scraping logic.

# Driver Management Class:
# You could also create a separate class, say DriverManager, to handle the web driver (ChromeDriver) lifecycle, including starting, stopping, and restarting the driver. This would simplify the SeleniumScraper class and help make the driver's lifecycle management more robust.

# Commenting and Documentation:
# Although your code has some comments, you can improve it by adding docstrings to your classes and methods to describe what they do. This will make it easier for others (and for future you) to understand what each part of the code is meant to do.