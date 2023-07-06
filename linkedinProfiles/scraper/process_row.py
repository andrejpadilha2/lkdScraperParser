import random
from datetime import datetime
import pandas as pd

from .utils import (
    check_profile_name_subset_full_name, check_profile_already_scraped, 
    check_profile_availability, check_studied_at_universities, 
    get_linkedin_url_id, get_page_problems, 
    get_valid_linkedin_link_elements, save_html, update_results
)
from ..general_utils.methods import sleep_print


def process_row(profile_row, driver, linkedin_profiles_df, 
                unavailable_profiles, non_ufabc_students, 
                full_path, total_linkedin_requests, 
                successful_linkedin_requests, total_profiles_scraped, 
                successful_profiles_scraped):

    if profile_row.to_scrape == 0 or not pd.isna(profile_row.failed_cause):
        handle_already_scraped_name_variation(profile_row)
    
    else:
        sleep_print(2, '→ sleeping 2 seconds...')

        driver.request_website('https://www.google.com.br')
        sleep_print(random.uniform(2, 3), '→ sleeping between 2 and 3 seconds...')

        search_query = f'{profile_row.name_variation} ufabc linkedin' # using "ufabc" inside double quotes made some correct search results disappear, I really don't understand why
        driver.search_google(search_query)
        sleep_print(random.uniform(2, 3), '→ sleeping between 2 and 3 seconds...')

        links = driver.find_linkedin_links()
        linkedin_link_elements = get_valid_linkedin_link_elements(links, profile_row.full_name, unavailable_profiles, non_ufabc_students)

        try_next_link = True
        for link_idx, link in enumerate(linkedin_link_elements):
            # Great, we found some Linkedin profiles to analyze!
            # But before we jump into it, we need to check one more thing:
            # If the profile URL was already scraped by ANOTHER name, we try the next link in linkedin_link_elements (if it exists).
            
            
            profile_already_scraped = check_profile_already_scraped(link, linkedin_profiles_df, profile_row.linkedin_url)
            linkedin_url, linkedin_id = get_linkedin_url_id(link)

            if profile_already_scraped:
                handle_already_scraped_profile(link_idx, linkedin_link_elements, 
                                               linkedin_id, linkedin_profiles_df, profile_row)

            else:
                # The profile URL wasn't scraped by any other name, so we can finally request it!
                total_profiles_scraped += 1
                try_next_link, total_linkedin_requests,\
                    successful_linkedin_requests, successful_profiles_scraped = (
                    request_linkedin_profile(driver, link, linkedin_url, 
                                             profile_row, full_path,
                                             total_linkedin_requests,
                                             successful_linkedin_requests,
                                             successful_profiles_scraped,
                                             linkedin_profiles_df, non_ufabc_students,
                                             unavailable_profiles)
                )

                print(f"→ So far {successful_linkedin_requests} out of {total_linkedin_requests} requests to Linkedin were successful.")
                print(f"→ So far {successful_profiles_scraped} out of {total_profiles_scraped} profiles were succesfully scrapped.")
                sleep_print(15, '→ sleeping 15 seconds...')

                if not try_next_link:
                    break
                print("→ Trying next available profile.")
            
        if not linkedin_link_elements:
            print("→ No LinkedIn search results to access.")
            update_results(linkedin_profiles_df, profile_row.uid, 0, failed_cause='no_linkedin_url')

        elif try_next_link:
            print("→ No Linkedin profile found. No other Linkedin profiles to try.")
            update_results(linkedin_profiles_df, profile_row.uid, 0, failed_cause='no_suitable_linkedin_profile')
            
    return linkedin_profiles_df, unavailable_profiles, non_ufabc_students, total_linkedin_requests, successful_linkedin_requests, total_profiles_scraped, successful_profiles_scraped


def handle_already_scraped_name_variation(profile_row):
    if profile_row.scraped_success_time:
        print("→ Name was already scraped, skipping...")
    else:
        print(f"→ Last Google search resulted in {profile_row.failed_cause}, skipping...")


def handle_already_scraped_profile(link_idx, linkedin_link_elements, linkedin_id, linkedin_profiles_df, profile_row):
    if link_idx == len(linkedin_link_elements)-1: 
        print(f"→ Profile id '{linkedin_id}' was already scraped by another name, there are no other profiles to try, skipping...")
        update_results(linkedin_profiles_df, profile_row.uid, 0, failed_cause='no_linkedin_profile_available_for_namesake')
    else:
        print(f"→ Profile id '{linkedin_id}' was already scraped by another name, trying the next profile.")


def request_linkedin_profile(driver, link, linkedin_url, profile_row, full_path,
                             total_linkedin_requests, successful_linkedin_requests,
                             successful_profiles_scraped, linkedin_profiles_df,
                             non_ufabc_students, unavailable_profiles):
    for attempt in range(2):
        total_linkedin_requests += 1

        driver.open_link_new_tab(link, linkedin_url) # TODO: what if the internet connection is lost in this step?
        sleep_print(random.uniform(5, 7), '→ sleeping between 5 and 7 seconds...')
        page_source = driver.page_source
        is_successful_request, problems = get_page_problems(page_source)

        # TODO
        # If it's the xth unsucessful reply in a row, do something (maybe change IP)

        if is_successful_request:
            successful_linkedin_requests += 1
            try_next_link, successful_profiles_scraped = (
                handle_successful_request(page_source, linkedin_profiles_df,
                                          profile_row, driver, problems,
                                          successful_profiles_scraped,
                                          unavailable_profiles, non_ufabc_students,
                                          full_path)
            )
            driver.close_new_tab()
            break
            
        else:
            if attempt == 0:
                # If it fails, we return to the main tab and click on the link again.
                print("→ Failed request but will attempt again now!")
                sleep_print(random.uniform(2, 3), '→ sleeping between 2 and 3 seconds...')
            else:
                # When it fails for good we want to save some things: fail reason and the URL that it tried to access.
                print("→ Failed request, not attempting again!")    
                update_results(linkedin_profiles_df, profile_row.uid, 1, failed_cause=problems)
                try_next_link = False                           
    
            driver.close_new_tab()

    return try_next_link, total_linkedin_requests, successful_linkedin_requests, successful_profiles_scraped


def handle_successful_request(page_source, linkedin_profiles_df, profile_row,
                              driver, problems, successful_profiles_scraped,
                              unavailable_profiles, non_ufabc_students, full_path):
    
    try_next_link = True
    current_url = driver.current_url.split("?")[0]
    
    is_profile_available = check_profile_availability(page_source)
    if is_profile_available:

        is_profile_name_subset_full_name = check_profile_name_subset_full_name(page_source, profile_row.full_name)
        if is_profile_name_subset_full_name:

            is_ufabc_student = check_studied_at_universities(page_source, ['UFABC', 'Universidade Federal do ABC'])
            if is_ufabc_student:
                successful_profiles_scraped += 1
                try_next_link = False
                print("→ Successful request and the person studied at UFABC!")
                # TODO:
                # if it's the full name variation, we don't want to scrape any other name variations for that name
                # because all other name variations are less specific than the full name, 
                # hence they will bring more results which are LESS relevant!
                saved_html_path = save_html(full_path, page_source, profile_row.uid, profile_row.name_variation, problems)
                update_results(linkedin_profiles_df, profile_row.uid, 0, current_url, datetime.now(), saved_html_path)
            else:
                print("→ Succesful request, but the person did not study at UFABC; will try next available link.")
                non_ufabc_students.append(current_url)
                
        else:
            # TODO: this profile could be a UFABC student, so it would be great to save the profile in a "saved for later" folder so that we don't request the same profile twice
            print("→ Succesful request, but profile name is not a subset of the person full name, will try next available link.")
    else:
        print("→ Succesful request, but profile is not available, will try next available link.")
        unavailable_profiles.append(current_url)
            
    return try_next_link, successful_profiles_scraped