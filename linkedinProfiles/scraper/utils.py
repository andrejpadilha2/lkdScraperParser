from bs4 import BeautifulSoup

from linkedinProfiles.utils.methods import normalize_string
from selenium import webdriver
from selenium_stealth import stealth

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
    # normalize the names when comparing, some people write "Universidade federal do Abc", or "ufabc", or even "universidade federal do abc - santo andré"
    # I am thinking more and more about removing this in this step and maintaining it only on parsing or directly on cleaning
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
                if university_to_check in university_studied:
                    return True

    return False

def check_page_problems(page_source):
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
    
    return problems, success

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
    sleep(1, '→ sleeping 2 seconds before maximizing the window...')
    driver.maximize_window()
    return driver