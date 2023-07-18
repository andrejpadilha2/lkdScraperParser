from pathlib import Path

PROFILES_FOLDER_NAME = 'profilesSelenium19_1000'  # << change only this!!! profilesSelenium18_og_namesake
# PROFILES_FOLDER_NAME = 'test'
HEADLESS = True

# True if the scraper should retry profiles that failed in a previous run 
# because a Captcha was raised. 
RETRY_CAPTCHA_WHEN_RESUMING = False 





BASE_PATH = Path(__file__).resolve().parent
DATA_PATH = BASE_PATH / 'data' / 'linkedin_profiles' / PROFILES_FOLDER_NAME