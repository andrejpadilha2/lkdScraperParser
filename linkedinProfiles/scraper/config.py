from ..config import DATA_PATH

NAMES_LIST_PATH = DATA_PATH / 'names_list.txt'
UNAVAILABLE_PROFILES_PATH = DATA_PATH / 'unavailable_profiles.json'
NON_UFABC_STUDENT_PROFILES_PATH = DATA_PATH / 'non_ufabc_student_profiles.json'
SCRAPED_DATA_PATH = DATA_PATH / 'scraped_data.csv'
SAVED_FOR_LATER_PROFILES_PATH = DATA_PATH / 'saved_for_later_profiles.json'

SCRAPED_DATA_COLUMNS = {
    'uid': int,
    'name_variation': str,
    'name_id': int,
    'full_name': str,
    'to_scrape': int,
    'linkedin_url': str,
    'html_path': str,
    'failed_cause': str
}