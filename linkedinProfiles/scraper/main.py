import os
from linkedinProfiles.scraper.selenium_scraper import SeleniumScraper

from linkedinProfiles.scraper.config import NAMES_LIST_PATH

def main():
    
    selenium_scraper = SeleniumScraper()
    selenium_scraper.run()

if __name__ == "__main__":
    if not os.path.exists(NAMES_LIST_PATH):
        raise FileNotFoundError(f"File not found: {NAMES_LIST_PATH}")

    print("\nBEGINNING LINKEDIN SCRAPING\n")
    main()