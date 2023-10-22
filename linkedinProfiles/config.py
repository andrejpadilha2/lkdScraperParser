from pathlib import Path

PROFILES_FOLDER_NAME = 'profilesSelenium25_8056'  # << change only this!!! profilesSelenium18_og_namesake
# PROFILES_FOLDER_NAME = 'test'
HEADLESS = True

# True if the scraper should continue from where it stopped last time,
# False if it should start from the beginning (it will retry failed name_variations 
# and skip already scrapped ones) 
CONTINUE_FROM_LAST_RUN = False


MANUAL_CAPTCHA = True # True: you will be prompted to solve captchas manually (browser will be started in HEADED mode, regardless of the HEADLESS option set above). False: you won't.


BASE_PATH = Path(__file__).resolve().parent
DATA_PATH = BASE_PATH / '..' / 'data' / 'linkedin_profiles' / PROFILES_FOLDER_NAME