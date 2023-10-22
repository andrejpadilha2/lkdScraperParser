import json
import os
import sys
import pandas as pd

from .utils import save_html
from .scraped_entry import ScrapedEntry
from ..general_utils.methods import create_folder, normalize_string, sleep_print
from .generate_name_variations import generate_all_name_variations
from ..config import DATA_PATH, CONTINUE_FROM_LAST_RUN
from .config import SCRAPED_DATA_COLUMNS, SCRAPED_DATA_PATH, NAMES_LIST_PATH, NON_UFABC_STUDENT_PROFILES_PATH, UNAVAILABLE_PROFILES_PATH, SAVED_FOR_LATER_PROFILES_PATH


class DataManager():
    def __init__(self, format='csv'):
        self.format = format
        self.data_path = DATA_PATH
        self.continue_from_last_run = CONTINUE_FROM_LAST_RUN
        self.name_variation_idx = 0
        self.total_name_variations = 0

        if self.format == 'csv':
            self.SCRAPED_DATA_PATH = SCRAPED_DATA_PATH
            self.UNAVAILABLE_PROFILES_PATH = UNAVAILABLE_PROFILES_PATH
            self.NON_UFABC_STUDENT_PROFILES_PATH = NON_UFABC_STUDENT_PROFILES_PATH
            self.SAVED_FOR_LATER_PROFILES_PATH = SAVED_FOR_LATER_PROFILES_PATH
            self.NAMES_LIST_PATH = NAMES_LIST_PATH

            if not os.path.exists(self.UNAVAILABLE_PROFILES_PATH):
                with open(self.UNAVAILABLE_PROFILES_PATH, 'w') as file:
                    json.dump([], file)

            with open(self.UNAVAILABLE_PROFILES_PATH, 'r') as file:
                    self.unavailable_profiles = json.load(file)

            if not os.path.exists(self.NON_UFABC_STUDENT_PROFILES_PATH):
                with open(self.NON_UFABC_STUDENT_PROFILES_PATH, 'w') as file:
                    json.dump([], file)

            with open(self.NON_UFABC_STUDENT_PROFILES_PATH, 'r') as file:
                    self.non_ufabc_student_profiles = json.load(file)

            if not os.path.exists(self.SAVED_FOR_LATER_PROFILES_PATH):
                with open(self.SAVED_FOR_LATER_PROFILES_PATH, 'w') as file:
                    json.dump({}, file)

            with open(self.SAVED_FOR_LATER_PROFILES_PATH, 'r') as file:
                    self.saved_for_later_profiles = json.load(file)

            # Load files
            scraped_data_csv_exists = os.path.exists(self.SCRAPED_DATA_PATH)
            if not scraped_data_csv_exists:
                self.create_scraped_data_csv()       
                sleep_print(1, "sleeping 1 second...")
            else:
                user_input = input(f"Looks like a scrapping process already started on '{self.SCRAPED_DATA_PATH}'.\nIs this the correct path? Type 'yes' to continue:\n> ")
                if user_input.lower() != 'yes':
                    print('Exiting the scraper.')
                    sys.exit(1)
            self.scraped_data = pd.read_csv(self.SCRAPED_DATA_PATH, sep=',', dtype=SCRAPED_DATA_COLUMNS, parse_dates=['scraped_success_time'])
            self.total_name_variations = len(self.scraped_data)

    def create_scraped_data_csv(self):

        name_variations = generate_all_name_variations(self.NAMES_LIST_PATH)
        scraped_data = pd.DataFrame(
            name_variations, columns=['uid', 'name_variation', 'name_id', 'full_name'])

        scraped_data['to_scrape'] = 1 # will track if it's still necessary to scrape this name variation
        scraped_data['scraped_success_time'] = ''
        scraped_data['linkedin_url'] = '' # stores linkedin_url
        scraped_data['html_path'] = '' # stores the path to the HTML file
        scraped_data['failed_cause'] = '' # stores every fail attempt cause

        # Sort profiles so that more specific name variations are scraped first (full name -> first and last name -> etc)
        scraped_data['Sort'] = scraped_data.groupby('name_id').cumcount()
        scraped_data.sort_values(['Sort', 'name_id'], inplace=True)
        scraped_data.drop(columns=['Sort'], inplace=True)

        print(f"Creating file '{self.SCRAPED_DATA_PATH}'.\n")
        scraped_data.to_csv(self.SCRAPED_DATA_PATH, index=False, sep=',')

    def save(self, scraped_entry):
         if self.format == 'csv':
            def update_results(scraped_data, scraped_entry):
                scraped_data.loc[scraped_data.loc[:, 'uid'] == scraped_entry.uid, 'to_scrape'] = scraped_entry.to_scrape
                scraped_data.loc[scraped_data.loc[:, 'uid'] == scraped_entry.uid, 'scraped_success_time'] = scraped_entry.scraped_success_time
                scraped_data.loc[scraped_data.loc[:, 'uid'] == scraped_entry.uid, 'linkedin_url'] = scraped_entry.linkedin_url
                scraped_data.loc[scraped_data.loc[:, 'uid'] == scraped_entry.uid, 'html_path'] = scraped_entry.html_path
                scraped_data.loc[scraped_data.loc[:, 'uid'] == scraped_entry.uid, 'failed_cause'] = scraped_entry.failed_cause

            update_results(self.scraped_data, scraped_entry)
            # Save all three files
            self.scraped_data.to_csv(self.SCRAPED_DATA_PATH, index=False, sep=',')
            with open(self.UNAVAILABLE_PROFILES_PATH, 'w') as file:
                json.dump(self.unavailable_profiles, file)
            with open(self.NON_UFABC_STUDENT_PROFILES_PATH, 'w') as file:
                json.dump(self.non_ufabc_student_profiles, file)
            with open(self.SAVED_FOR_LATER_PROFILES_PATH, 'w') as file:
                json.dump(self.saved_for_later_profiles, file)
            
            if scraped_entry.page_source:
                folder_name = f"{DATA_PATH}/{scraped_entry.name_id}_{normalize_string(scraped_entry.full_name)}"
                create_folder(folder_name)
                save_html(scraped_entry.html_path, scraped_entry.page_source)

    def save_profile_for_later(self, url, page_source, uid):
        folder_name = f"{DATA_PATH}/saved_for_later"
        create_folder(folder_name)
        html_path = f"{folder_name}/{uid}.html"
        save_html(html_path, page_source)
        self.saved_for_later_profiles[url] = html_path

    def update_non_ufabc_student_profiles(self, url):
        self.non_ufabc_student_profiles.append(url)

    def update_unavailable_profiles(self, url):
        self.unavailable_profiles.append(url)

    def get_saved_for_later_profile(self, url):
        html_path = self.saved_for_later_profiles.get(url)
        page_source = None
        if html_path:
            with open(html_path, "r") as f:
                    page_source = f.read()
        return page_source

    def get_list_already_scraped_url(self):
        if self.format == 'csv':
            return self.scraped_data.linkedin_url.dropna().unique().tolist()
        
    def get_unavailable_profiles(self):
        if self.format == 'csv':
            return self.unavailable_profiles
    
    def get_non_ufabc_student_profiles(self):
        if self.format == 'csv':
            return self.non_ufabc_student_profiles
    
    def get_scraped_entries(self):
        """ Generator that reads one row of "scrape data" (either
        in CSV or in SQLite) and yields an instance of ScrapeEntry
        at a time. """

        if self.format == 'csv':
            if self.continue_from_last_run:
                for scraped_tuple in self.scraped_data.itertuples():
                    self.name_variation_idx += 1
                    if scraped_tuple.to_scrape == 1 and pd.isna(scraped_tuple.failed_cause):
                        scraped_entry = ScrapedEntry(
                            scraped_tuple.uid, scraped_tuple.name_variation,
                            scraped_tuple.full_name, scraped_tuple.name_id,
                            scraped_tuple.to_scrape, scraped_tuple.scraped_success_time,
                            scraped_tuple.linkedin_url, scraped_tuple.html_path,
                            "", scraped_tuple.failed_cause
                        )
                        yield scraped_entry
                    else:
                        print(f"Skipping uid {scraped_tuple.uid} - {scraped_tuple.name_variation} - to_scrape = {scraped_tuple.to_scrape} - failed_cause = {scraped_tuple.failed_cause}")
            else:

                for scraped_tuple in self.scraped_data.itertuples():
                    self.name_variation_idx += 1
                    scraped_entry = ScrapedEntry(
                        scraped_tuple.uid, scraped_tuple.name_variation,
                        scraped_tuple.full_name, scraped_tuple.name_id,
                        scraped_tuple.to_scrape, scraped_tuple.scraped_success_time,
                        scraped_tuple.linkedin_url, scraped_tuple.html_path,
                        "", scraped_tuple.failed_cause
                    )
                    yield scraped_entry