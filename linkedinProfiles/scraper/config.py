from ..config import DATA_PATH

NAMES_LIST_PATH = DATA_PATH / 'names_list.txt'
UNAVAILABLE_PROFILES_PATH = DATA_PATH / 'unavailable_profiles.json'
NON_UFABC_STUDENTS_PATH = DATA_PATH / 'non_ufabc_students.json'
NAME_VARIATIONS_LINKEDIN_PATH = DATA_PATH / 'name_variations_linkedin.csv'

NAME_VARIATIONS_LINKEDIN_COLUMNS = {
    'uid': int,
    'name_id': int,
    'full_name': str,
    'name_variation': str,
    'to_scrape': int,
    'linkedin_url': str,
    'failed_cause': str,
    'html_path': str
}