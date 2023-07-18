from linkedinProfiles.general_utils.methods import normalize_string

class ScrapedEntry():

    def __init__(self, uid, name_variation, full_name, name_id, to_scrape,
                 scraped_success_time, linkedin_url, html_path, page_source, 
                 failed_cause):
        self.uid = uid
        self.name_variation = name_variation
        self.full_name = full_name
        self.name_id = name_id
        self.to_scrape = to_scrape
        self.scraped_success_time = scraped_success_time
        self.linkedin_url = linkedin_url
        self.html_path = html_path
        self.page_source = page_source
        self.failed_cause = failed_cause

    def update_results(self, to_scrape, linkedin_url=None, scraped_success_time=None, 
                       html_path=None, page_source=None, new_failed_cause=None):
        self.to_scrape = to_scrape
        if linkedin_url is not None:
            self.linkedin_url = linkedin_url
        if scraped_success_time is not None:
            self.scraped_success_time = scraped_success_time
        if html_path is not None:
            self.html_path = html_path
        if page_source is not None:
            self.page_source = page_source
        if new_failed_cause is not None:
            self.add_failed_cause(new_failed_cause)
        
    def add_failed_cause(self, new_failed_cause):
        if isinstance(self.failed_cause, str):
            previous_failed_cause = self.failed_cause.strip("()")
            self.failed_cause = f"({previous_failed_cause}; {new_failed_cause})"
        else:
            self.failed_cause = f"({new_failed_cause})"

    def generate_html_path(self, data_path):
        full_name_folder = f"{data_path}/{self.name_id}_{normalize_string(self.full_name)}"
        html_path = f"{full_name_folder}/{self.uid}_{normalize_string(self.name_variation)}.html"
        return html_path