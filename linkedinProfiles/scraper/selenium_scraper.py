import random
from datetime import datetime
from collections import deque
from timeit import default_timer as timer
from linkedinProfiles.config import HEADLESS, MANUAL_CAPTCHA

from linkedinProfiles.general_utils.methods import sleep_print
from linkedinProfiles.scraper.custom_chrome_driver import CustomChromeDriver
from linkedinProfiles.scraper.data_manager import DataManager
from linkedinProfiles.scraper.utils import (
    check_profile_already_scraped, check_profile_availability, 
    check_profile_name_subset_full_name, check_studied_at_universities, 
    get_linkedin_url_id, get_page_problems, get_valid_linkedin_profile_elements, 
)

class SeleniumScraper:
    def __init__(self):
        self.start_total_time = timer()

        self.data_manager = DataManager()
        
        self.total_linkedin_requests = 0
        self.successful_linkedin_requests = 0
        self.total_profiles_scraped = 0
        self.successful_profiles_scraped = 0
        self.success_queue = deque(maxlen=4)
        self.last_failed_scraped_entries = deque(maxlen=2)
        self.try_next_link = True

        if MANUAL_CAPTCHA:
            headless=False
            load_images=True
        else:
            headless=HEADLESS
            load_images=False
        self.driver = CustomChromeDriver(load_images, headless=headless)

    def start_scraper(self):
        self.run()        
    
    def run(self):
        for scraped_entry in self.data_manager.get_scraped_entries():         
            ip_blocked = self.check_ip_blocked()
            if ip_blocked:
                pass
                # self.run_last_scraped_entries()
                
            print("\n\n\n****************************************************************")
            print(f"Trying to find LinkedIn profile of {scraped_entry.full_name}\n")
            print("\n---------------------------------------------")
            print(f"Iter {self.data_manager.name_variation_idx}/{self.data_manager.total_name_variations} - Testing name variation #{scraped_entry.uid}: {scraped_entry.name_variation}")
           
            self.process_entry(scraped_entry)

            # self.driver.restart()

    def run_last_scraped_entries(self):
        for scraped_entry in self.last_failed_scraped_entries.copy():         
            print("\n\n\n****************************************************************")
            print(f"Trying to find LinkedIn profile of {scraped_entry.full_name}\n")
            print("\n---------------------------------------------")
            print(f"Repeated iteration - Testing name variation #{scraped_entry.uid}: {scraped_entry.name_variation}")
            self.process_entry(scraped_entry)

        # I don't to retry the "last_failed_scraped_entries" if they fail yet again, so we will restart it
        self.success_queue = deque(maxlen=4)
        self.last_failed_scraped_entries = deque(maxlen=2)

    def process_entry(self, scraped_entry):
        start_iter_time = timer()

        self.process_name_variation(scraped_entry)
        self.data_manager.save(scraped_entry)

        iter_time = timer() - start_iter_time
        print(f"→ Iteration elapsed time: {iter_time:.2f}")
        total_time = timer() - self.start_total_time
        print(f"→ Total elapsed time: {total_time:.2f}")

    def process_name_variation(self, scraped_entry):
        if scraped_entry.to_scrape == 0:
            self.handle_already_scraped_name_variation(scraped_entry)
        else:
            self.search_name_variation_online(scraped_entry)

    def search_name_variation_online(self, scraped_entry):
        sleep_print(2, '→ sleeping 2 seconds...')

        self.driver.request_website('https://www.google.com.br')
        sleep_print(random.uniform(0.5, 1.5), '→ sleeping between 0.5 and 1.5 seconds...')

        # using "ufabc" inside double quotes made some correct search results disappear, 
        # I really don't understand why
        search_query = f'{scraped_entry.name_variation} ufabc linkedin'
        self.driver.search_google(search_query)
        sleep_print(random.uniform(0.5, 1.5), '→ sleeping between 0.5 and 1.5 seconds...')

        lp_link_elements, lp_link_names = self.driver.find_linkedin_profile_link_elements()
        valid_lp_link_elements = get_valid_linkedin_profile_elements(
            lp_link_elements, lp_link_names, scraped_entry.full_name,
            self.data_manager.get_unavailable_profiles(),
            self.data_manager.get_non_ufabc_student_profiles()
        )

        self.try_next_link = True
        for link_idx, link in enumerate(valid_lp_link_elements):
            # Great, we found some Linkedin profiles to analyze!
            # But before we jump into it, we need to check one more thing:
            # If the profile URL was already scraped by ANOTHER name, we try the next link in linkedin_link_elements (if it exists).
            list_already_scraped_url = self.data_manager.get_list_already_scraped_url()    
            profile_already_scraped = check_profile_already_scraped(link, list_already_scraped_url, scraped_entry.linkedin_url)
            linkedin_url, linkedin_id = get_linkedin_url_id(link)

            if profile_already_scraped:
                self.handle_already_scraped_profile(link_idx, valid_lp_link_elements,
                                                    linkedin_id, scraped_entry)

            else:
                # The profile URL wasn't scraped by any other name, so we can finally request it!
                self.total_profiles_scraped += 1
                self.request_linkedin_profile(link, linkedin_url, scraped_entry)


                print(f"→ So far {self.successful_linkedin_requests} out of {self.total_linkedin_requests} requests to Linkedin were successful.")
                print(f"→ So far {self.successful_profiles_scraped} out of {self.total_profiles_scraped} profiles were succesfully scrapped.")
                sleep_print(random.uniform(4, 6), '→ sleeping between 4 and 6 seconds...')

                if not self.try_next_link:
                    break
                print("→ Trying next available profile.")
            
        if not valid_lp_link_elements:
            print("→ No LinkedIn profile to access.")
            scraped_entry.update_results(to_scrape=0, new_failed_cause='no_linkedin_url')

        elif self.try_next_link:
            print("→ No Linkedin profile found. No other Linkedin profiles to try.")
            scraped_entry.update_results(to_scrape=0, new_failed_cause='no_suitable_linkedin_profile')

    def handle_already_scraped_name_variation(self, scraped_entry):
        if scraped_entry.scraped_success_time:
            print("→ Name was already scraped, skipping...")
        else:
            print(f"→ Last Google search resulted in {scraped_entry.failed_cause}, skipping...")


    def handle_already_scraped_profile(self, link_idx, valid_lp_link_elements, linkedin_id, scraped_entry):
        if link_idx == len(valid_lp_link_elements)-1: 
            print(f"→ Profile id '{linkedin_id}' was already scraped by another name, there are no other profiles to try, skipping...")
            scraped_entry.update_results(to_scrape=0, new_failed_cause='no_linkedin_profile_available_for_namesake')
        else:
            print(f"→ Profile id '{linkedin_id}' was already scraped by another name, trying the next profile.")


    def request_linkedin_profile(self, link, linkedin_url, scraped_entry):
        page_source = self.data_manager.get_saved_for_later_profile(linkedin_url)
        if page_source:
            print("→ Profile was 'saved for later'. Fetching it now!")
            self.handle_successful_request(page_source, scraped_entry, linkedin_url)
        else:
            for attempt in range(2):
                self.total_linkedin_requests += 1

                self.driver.open_link_new_tab(link, linkedin_url)
                sleep_print(random.uniform(5, 7), '→ sleeping between 1 and 2 seconds...')
                print("→ Scrolling to bottom.")
                self.driver.scroll_to_bottom()

                page_source = self.driver.page_source
                is_successful_request, problems = get_page_problems(page_source)
                page_source = self.driver.page_source

                if is_successful_request:
                    print("→ Successful request!")
                    self.successful_linkedin_requests += 1
                    self.handle_successful_request(page_source, scraped_entry, linkedin_url)
                    self.success_queue.append(is_successful_request)
                    self.driver.close_new_tab()
                    break
                    
                else:
                    if attempt == 0:
                        # If it fails, we return to the main tab and click on the link again.
                        print("→ Failed request but will attempt again now!")
                    else:
                        self.success_queue.append(is_successful_request)
                        self.last_failed_scraped_entries.append(scraped_entry)
                        # When it fails for good we want to save some things: fail reason and the URL that it tried to access.
                        print("→ Failed request, not attempting again!")    
                        scraped_entry.update_results(to_scrape=1, new_failed_cause=problems)
                        self.try_next_link = False                           
            
                    self.driver.close_new_tab()


    def handle_successful_request(self, page_source, scraped_entry, linkedin_url):       
        is_profile_available = check_profile_availability(page_source)
        if is_profile_available:
            is_ufabc_student = check_studied_at_universities(page_source, ['UFABC', 'Universidade Federal do ABC'])
            if is_ufabc_student:
            
                is_profile_name_subset_full_name = check_profile_name_subset_full_name(page_source, scraped_entry.full_name)
                if is_profile_name_subset_full_name:
                    self.successful_profiles_scraped += 1
                    self.try_next_link = False
                    print("→ It's a match!\n\tProfile name is a subset of the full name and the person studied at UFABC!")
                    # TODO:
                    # if it's the full name variation, MAYBE we don't want to scrape any other name variations for that name
                    # because all other name variations are less specific than the full name, 
                    # hence they will bring more results which are LESS relevant!
                    html_path = scraped_entry.generate_html_path(self.data_manager.data_path)
                    scraped_entry.update_results(to_scrape=0, linkedin_url=linkedin_url, 
                                                  scraped_success_time=datetime.now(), html_path=html_path,
                                                  page_source=page_source)
                else:
                    print("→ Profile name is not a subset of the person full name, will try next available link.")
                    self.data_manager.save_profile_for_later(linkedin_url, page_source, scraped_entry.uid)
                    
            else:
                print("→ Person did not study at UFABC; will try next available link.")
                self.data_manager.update_non_ufabc_student_profiles(linkedin_url)
        else:
            print("→ Profile is not available, will try next available link.")
            self.data_manager.update_unavailable_profiles(linkedin_url)         

    def check_ip_blocked(self):
        if len(self.success_queue) == 4 and sum(self.success_queue) < 3:
            print("\n\n→ High failure rate in the last 4 requests, rotating IP and restarting driver!")
            self.driver.restart()
            self.success_queue = deque(maxlen=4)
            self.last_failed_scraped_entries = deque(maxlen=2)
            return True
        else:
            return False



# Use Logging Instead of Print:
# Instead of using print statements to track the progress, consider using the logging library. This would allow you to easily control the level of output (DEBUG, INFO, WARN, etc.), as well as write logs to a file, which can be very helpful for post-execution analysis.

# Error Handling Class:
# You may consider creating an ErrorHandling class that can take care of all the error checking. For example, you can move the error-checking methods such as get_page_problems or check_profile_availability to this class.

# Separate Scrape Management Class:
# Some methods in SeleniumScraper seem to be more about managing the overall scrape, like run and process_row. It might be helpful to create a ScrapeManager class to take care of these. Then, SeleniumScraper can focus on actual scraping logic.

# Commenting and Documentation:
# Although your code has some comments, you can improve it by adding docstrings to your classes and methods to describe what they do. This will make it easier for others (and for future you) to understand what each part of the code is meant to do.