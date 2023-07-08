from bs4 import BeautifulSoup
import pandas as pd

from linkedinProfiles.parser.person import get_identification_card, parse_linkedin_name
from ..general_utils.methods import normalize_string


def add_failed_cause(linkedin_profiles_df, uid, new_failed_cause):
    df_index = linkedin_profiles_df['uid'] == uid

    if pd.isna(linkedin_profiles_df.loc[df_index, 'failed_cause']).bool():
        linkedin_profiles_df.loc[df_index, 'failed_cause'] = f"({new_failed_cause})"
    else:
        previous_failed_cause = linkedin_profiles_df.loc[df_index, 'failed_cause'].str.strip("()")
        linkedin_profiles_df.loc[df_index, 'failed_cause'] = f"({previous_failed_cause.item()}; {new_failed_cause})"

def is_subset(setA, setB):
    return set(setA) <= set(setB)

def check_link_title_name_subset_full_name(linkedin_link_title, full_name):
    title_divider = len(linkedin_link_title)
    if '-' in linkedin_link_title:
        title_divider = linkedin_link_title.index('-')
    elif '|' in linkedin_link_title:
        title_divider = linkedin_link_title.index('|')

    names_in_linkedin_link = linkedin_link_title[:title_divider]
    names_in_linkedin_link = [normalize_string(name) for name in names_in_linkedin_link]

    names_in_full_name = full_name.split()
    names_in_full_name = [normalize_string(name) for name in names_in_full_name]

    return is_subset(names_in_linkedin_link, names_in_full_name)

def check_profile_name_subset_full_name(page_source, full_name):
    soup = BeautifulSoup(page_source, 'html.parser')
    identification_card = get_identification_card(soup)
    linkedin_name = parse_linkedin_name(identification_card)
    return is_subset(normalize_string(linkedin_name), normalize_string(full_name))

def check_studied_at_universities(page_source, universities_to_check):
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find the script tag containing the JSON-LD data
    education_items = soup.find_all('li', class_='education__list-item')

    if education_items:

        universities_studied = []
        for item in education_items:
            university_element = item.find('h3', class_='profile-section-card__title')
            university = university_element.text.strip() if university_element else None
            universities_studied.append(university)

        for university_to_check in universities_to_check:
            for university_studied in universities_studied:
                if normalize_string(university_to_check) in normalize_string(university_studied):
                    return True

    return False

def get_page_problems(page_source):
    problems = ""
    success = 1

    if "authwall" in page_source:
        print("→ You hit the authentication wall!")
        problems = "authwall_"
        success = 0

    if "captcha" in page_source:
        print("→ You hit a captcha page!")
        problems += "captcha_"
        success = 0

    if page_source.startswith("<html><head>\n    <script type=\"text/javascript\">\n"):
        print("→ You hit javascript obfuscated code!")
        problems += "obfuscatedJS_"
        success = 0
    
    return success, problems

def get_valid_linkedin_link_elements(links, profile_full_name, unavailable_profiles, non_ufabc_student):
    """ Returns a list of linkedin link elements that:
    1) Are Linkedin profiles (linkedin.com/in/)
    2) The name of person in the profile link title is a subset of the person's full name
    3) Is an available profile
    4) Isn't a non-ufabc student"""

    # Select only linkedin.com/in links (which are Linkedin profiles), and links whose profile name is a subset of the full name
    linkedin_link_elements = [link_element for link_element in links if 
                              link_element.get_attribute('href')
                              and ('linkedin.com/in/' in link_element.get_attribute('href'))
                              and check_link_title_name_subset_full_name(link_element.text.split(), profile_full_name)
                              and check_available_profile(link_element.get_attribute('href'), unavailable_profiles)
                              and check_ufabc_student(link_element.get_attribute('href'), non_ufabc_student)]

    return linkedin_link_elements

def check_ufabc_student(link, non_ufabc_student):
    """Returns True if link is a UFABC student profile or False otherwise"""
    return not link in non_ufabc_student

def check_available_profile(link, unavailable_profiles):
    """Returns True if link is an available profile or False otherwise.
    Unavailable profiles: list of profile links that are not available"""
    return not link in unavailable_profiles

def get_linkedin_url_id(link):
    linkedin_url = link.get_attribute('href')
    linkedin_id = linkedin_url.split("/in/")[-1].split("/")[0].split("?")[0]
    return linkedin_url, linkedin_id

def check_profile_already_scraped(link, linkedin_profiles_df, profile_linkedin_url):
    # TODO: maybe I need to adjust "profile_linkedin_url != linkedin_url" depending on scraper workflow
    linkedin_url, linkedin_id = get_linkedin_url_id(link)
    profile_already_scraped = (linkedin_profiles_df['linkedin_url'].str.contains(linkedin_id, na=False).any() and 
                            profile_linkedin_url != linkedin_url)
    
    return profile_already_scraped

def check_profile_availability(page_source):
    """Returns true if profile is available or false otherwise"""
    return not "page-not-found" in page_source

def save_html(full_path, page_source, profile_uid, profile_name_variation, problems):
    html_path = f"{full_path}/{profile_uid}_{normalize_string(profile_name_variation)}_{problems}.html"
    print(f"→ saving HTML to: '{html_path}'.")
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(page_source)

    return html_path

def update_results(linkedin_profiles_df, uid, to_scrape, linkedin_url=None, scraped_success_time=None, html_path=None, failed_cause=None):
    linkedin_profiles_df.loc[linkedin_profiles_df.loc[:, 'uid'] == uid, 'to_scrape'] = to_scrape
    if linkedin_url is not None:
        linkedin_profiles_df.loc[linkedin_profiles_df.loc[:, 'uid'] == uid, 'linkedin_url'] = linkedin_url
    if scraped_success_time is not None:
        linkedin_profiles_df.loc[linkedin_profiles_df.loc[:, 'uid'] == uid, 'scraped_success_time'] = scraped_success_time
    if html_path is not None:
        linkedin_profiles_df.loc[linkedin_profiles_df.loc[:, 'uid'] == uid, 'html_path'] = html_path
    if failed_cause is not None:
        add_failed_cause(linkedin_profiles_df, uid, failed_cause)