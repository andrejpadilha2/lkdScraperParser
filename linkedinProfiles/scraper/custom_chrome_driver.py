from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains

from ..general_utils.methods import sleep_print

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
        self.implicitly_wait(60)
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
                    print("→ An error occurred: couldn't resolve '{website}', maybe there's no internet connection.")
                    sleep_print(5, '→ Trying again in 5 seconds.')
                else:
                    print("→ An error occurred:", str(e))

    def search_google(self, search_query):
        print("→ Searching on Google.")
        search_box = self.find_element(By.NAME, 'q')
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)

    def open_link_new_tab(self, link_element, url):
        print(f"→ Requesting '{url}'.")
        actions = ActionChains(self)
        actions.key_down(Keys.CONTROL).click(link_element).key_up(Keys.CONTROL).perform()
        self.switch_to.window(self.window_handles[1])

    def close_new_tab(self):
        print(f"→ Closing current tab.")
        self.close()
        self.switch_to.window(self.window_handles[0])

    def find_linkedin_links(self):
        links = self.find_elements(By.TAG_NAME, 'a')
        return links