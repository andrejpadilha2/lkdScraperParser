from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


from ..general_utils.methods import sleep_print
from linkedinProfiles.scraper.wingle import rotate_ip

class CustomChromeDriver(webdriver.Chrome):

    def __init__(self, headless=False, *args, **kwargs):
        self.headless = headless

        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument('--blink-settings=imagesEnabled=false')
        if headless:
            options.add_argument("--headless")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        super().__init__(*args, **kwargs, options=options)
        self.implicitly_wait(5)
        stealth(self,
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
        self.maximize_window()

    def restart(self):
        print("\n\n\n========================")
        print(f"Restarting web browser.")
        print("========================\n\n\n")

        self.quit()
        self.__init__(self.headless)

    def request_website(self, website):
        while True:
            try:
                print(f"→ Requesting '{website}'.")
                self.get(website)
                break
            except WebDriverException as e:
                if "net::ERR_NAME_NOT_RESOLVED" in str(e):
                    print(f"→ Error: couldn't resolve '{website}', maybe there's no internet connection.")
                    sleep_print(5, '→ Trying again in 5 seconds.')
                else:
                    print("→ Error:", str(e))

    def search_google(self, search_query):
        print("→ Searching on Google.")
        search_box = self.find_element(By.NAME, 'q')
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        while True:
            try:
                WebDriverWait(self, 10).until(EC.title_contains(search_query))
                break
            except TimeoutException as e:                   
                print("→ Error: waited 10s and couldn't get search query results, maybe there's no internet connection.")
                print("→ Trying again.")
                self.refresh()

    def open_link_new_tab(self, link_element, url):
        print(f"→ Clicking on '{url}'.")
        actions = ActionChains(self)
        actions.key_down(Keys.CONTROL).click(link_element).key_up(Keys.CONTROL).perform()
        try:
            WebDriverWait(self, 10).until(EC.number_of_windows_to_be(2))
            self.switch_to.window(self.window_handles[1])
            while True:
                try:
                    WebDriverWait(self, 10).until(EC.invisibility_of_element_located((By.ID, "main-frame-error")))
                    break
                except TimeoutException as e:
                    print(f"→ Error: couldn't resolve {url}, maybe there's no internet connection.")
                    print("→ Trying again.")
                    self.refresh()
        except TimeoutException as e:
            print("→ Error: Driver didn't open the link in a new tab.")

    def close_new_tab(self):
        print(f"→ Closing current tab.")
        self.close()
        self.switch_to.window(self.window_handles[0])

    def find_linkedin_profile_link_elements(self):
        """The idea here is that we find all clickable elements with a
        <a> tag (which are hyperlinks), but the hyperlink should be pointing
        to a link starting with 'https://xx.linkedin.com/in/', where
        'xx' stands for the country code of the profile. Some links 
        contain the "https://xx.linkedin.com/in/" in the end, like 
        translation pages of a given profile, which we don't want to 
        return, this is why we only select the first 40 characters."""

        linkedin_profile_link_elements = (
            [link_element
             for link_element in self.find_elements(By.TAG_NAME, 'a') if
             link_element.is_displayed() and
             link_element.get_attribute('href')
             and 'linkedin.com/in/' in link_element.get_attribute('href')[:40]])
        
        linkedin_profile_link_name = [link_element.find_element(By.TAG_NAME, 'h3').text
                                      for link_element in linkedin_profile_link_elements]
        return linkedin_profile_link_elements, linkedin_profile_link_name
    
    def rotate_ip(self):
        rotate_ip()