# Base path
BASE_PATH = 'data/linkedin_profiles/profilesSelenium11_og_namesake/'

# File paths
LINKEDIN_PROFILES_PATH = BASE_PATH + 'linkedin_profiles.csv'
PERSON_PATH = BASE_PATH + 'person.csv'
SCHOOL_PATH = BASE_PATH + 'school.csv'
EDUCATION_PATH = BASE_PATH + 'education.csv'
COMPANY_PATH = BASE_PATH + 'company.csv'
EXPERIENCE_PATH = BASE_PATH + 'experience.csv'

# Column definitions

LINKEDIN_PROFILES_COLUMNS = {
    'uid': int,
    'name_id': int,
    'full_name': str,
    'name_variation': str,
    'to_scrape': int,
    'linkedin_url': str,
    'failed_cause': str,
    'html_path': str
}

PERSON_COLUMNS = {
    'person_id': int,
    'full_name': str,
    'name_variation': str,
    'linkedin_name': str,
    'linkedin_url': str,
    'headline': str,
    'location': str,
    'followers': str,
    'connections': str,
    'about': str
}

SCHOOL_COLUMNS = {
    'school_id': int,
    'name': str,
    'linkedin_url': str
}

EDUCATION_COLUMNS = {
    'person_id': int,
    'school_id': int,
    'degree': str,
    'field_of_study': str,
    'start_date': str, # actually should be date
    'end_date': str, # actually should be date
    'description': str,
    'grade': str,
    'activities_societies': str}

COMPANY_COLUMNS = {
    'company_id': int,
    'name': str,
    'linkedin_url': str}

EXPERIENCE_COLUMNS = {
    'person_id': int,
    'company_id': int,
    'role': str,
    'location': str,
    'start_date': str, # actually should be date
    'end_date': str, # actually should be date
    'description': str}