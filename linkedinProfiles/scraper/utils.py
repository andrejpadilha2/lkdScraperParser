from bs4 import BeautifulSoup

from linkedinProfiles.parser.person import get_identification_card, parse_linkedin_name
from ..general_utils.methods import normalize_string

def is_subset(setA, setB):
    return set(setA) <= set(setB)

def check_link_title_name_subset_full_name(link_title_text, full_name):
    list_names_link_title = link_title_text.split('|')[0].split('-')[0].split()
    list_names_link_title = [normalize_string(name) for name in list_names_link_title]

    list_names_full_name = full_name.split()
    list_names_full_name = [normalize_string(name) for name in list_names_full_name]

    return is_subset(list_names_link_title, list_names_full_name)

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

def get_valid_linkedin_profile_elements(links, link_names, profile_full_name, unavailable_profiles, non_ufabc_student):
    """ Returns a list of linkedin link elements that:
    1) The name of person in the profile link title is a subset of the person's full name
    2) Is an available profile
    3) Isn't a non-ufabc student"""
    # Select only linkedin.com/in links (which are Linkedin profiles), and links whose profile name is a subset of the full name
    linkedin_link_elements = [link_element for link_element, link_name in zip(links, link_names) if 
                              check_link_title_name_subset_full_name(link_name, profile_full_name)
                              and not check_unavailable_profile(link_element.get_attribute('href'), unavailable_profiles)
                              and not check_non_ufabc_student(link_element.get_attribute('href'), non_ufabc_student)]

    return linkedin_link_elements

def check_non_ufabc_student(url, non_ufabc_student):
    """Returns True if link is a non-UFABC student profile or False otherwise"""
    url_clean = url.split("?")[0]
    return url_clean in non_ufabc_student

def check_unavailable_profile(url, unavailable_profiles):
    """Returns True if link is an unavailable profile or False otherwise.
    Unavailable profiles: list of profile links that are not available"""
    url_clean = url.split("?")[0]
    return url_clean in unavailable_profiles

def get_linkedin_url_id(link):
    linkedin_url = link.get_attribute('href').split("?")[0]
    profile_id = linkedin_url.split("/in/")[-1].split("/")[0].split("?")[0]
    return linkedin_url, profile_id

def check_profile_already_scraped(link, list_already_scraped_profiles, 
                                  profile_linkedin_url):
    # TODO: maybe I need to adjust "profile_linkedin_url != linkedin_url" depending on scraper workflow
    linkedin_url, profile_id = get_linkedin_url_id(link)
    combined_list = '\t'.join(list_already_scraped_profiles)
    profile_already_scraped = (profile_id in combined_list and
                               profile_linkedin_url != linkedin_url)
    
    return profile_already_scraped

def check_profile_availability(page_source):
    """Returns true if profile is available or false otherwise"""
    return not "page-not-found" in page_source

def save_html(html_path, page_source):
    print(f"→ saving HTML to: '{html_path}'.")
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(page_source)