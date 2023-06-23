from bs4 import BeautifulSoup
import pandas as pd

from ..general_utils.methods import normalize_string, sleep_print
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def add_failed_cause(linkedin_profiles_df, uid, new_failed_cause):
    df_index = linkedin_profiles_df['uid'] == uid

    if pd.isna(linkedin_profiles_df.loc[df_index, 'failed_cause']).bool():
        linkedin_profiles_df.loc[df_index, 'failed_cause'] = f"({new_failed_cause})"
    else:
        previous_failed_cause = linkedin_profiles_df.loc[df_index, 'failed_cause'].str.strip("()")
        linkedin_profiles_df.loc[df_index, 'failed_cause'] = f"({previous_failed_cause.item()}; {new_failed_cause})"

def check_name_subset(linkedin_link_title, full_name):
    hyphen_index = len(linkedin_link_title)
    if '-' in linkedin_link_title:
        hyphen_index = linkedin_link_title.index('-')

    names_in_linkedin_link = linkedin_link_title[:hyphen_index]
    names_in_linkedin_link = [normalize_string(name) for name in names_in_linkedin_link]

    names_in_full_name = full_name.split()
    names_in_full_name = [normalize_string(name) for name in names_in_full_name]

    is_subset = set(names_in_linkedin_link) <= set(names_in_full_name)
    
    return is_subset

def check_studied_at_universities(page_source, universities_to_check):
    # TODO:
    # I am thinking more and more about removing this on scraping and maintaining it only on parsing or directly on cleaning
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

def initialize_webdriver():
    options = webdriver.ChromeOptions()
    # options.add_argument("start-maximized")
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument("--headless")
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
    print("\n\n\n========================")
    print(f"Initializing web browser.")
    print("========================\n")
    sleep_print(1, '→ Sleeping 2 seconds before maximizing the window...')
    driver.maximize_window()
    return driver

def restart_browser(driver):
    print("\n\n\n========================")
    print(f"Restarting web browser.")
    print("========================\n\n\n")

    driver.close()
    driver = initialize_webdriver()

    return driver

# TODO:
# save the selenium find_element parameters in a config file, that way it's easier to configure the scraper if it changes
# also create some custom exceptions to indicate that maybe the position/name of the elements have changed
def search_google(driver, search_query):
    print("→ Searching on Google.")
    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)

def get_valid_linkedin_links(driver, profile_full_name):
    links = driver.find_elements(By.TAG_NAME, 'a')

    # Select only linkedin.com/in links (which are Linkedin profiles), and links whose profile name is a subset of the full name
    linkedin_links = [link for link in links if link.get_attribute('href') 
                      and ('linkedin.com/in/' in link.get_attribute('href')) 
                      and check_name_subset(link.text.split(), profile_full_name)]

    return linkedin_links

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

def click_link(driver, link, url):
    print(f"→ Requesting '{url}'.")
    link.click()
    page_source = driver.page_source

    return page_source

def save_html(full_path, page_source, profile_uid, profile_name_variation, problems):
    html_path = f"{full_path}/{profile_uid}_{normalize_string(profile_name_variation)}_{problems}.html"
    print(f"→ saving HTML to: '{html_path}'.")
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(page_source)

    return html_path

def prepare_next_attempt(driver, linkedin_id):
    print("→ Failed request but will attempt again now!")
    driver.execute_script("window.history.go(-1)")
    link = driver.find_element(By.CSS_SELECTOR, f'a[href*="{linkedin_id}"]')

    return link