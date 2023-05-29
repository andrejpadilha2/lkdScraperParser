from time import sleep
import random
import time
from selenium_stealth import stealth
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.generate_name_variations import generate_name_variations
# from utils.save_cookies import get_cookies
from utils.methods import *

print("\n\n\nBEGINNING LINKEDIN SCRAPPING\n\n\n")

save_path = 'profilesSelenium4'

### Names list ###
##################
with open('utils/names_list.txt') as f:
    name_list = f.read().splitlines()
    random.shuffle(name_list)

request_index = 1
succesful_requests = 0
name_dict = {}
print(f"Name variations:\n")
for name in name_list:
    name_dict[name] = generate_name_variations(name)
total_name_variations = sum(len(lst) for lst in name_dict.values())

# Determine the maximum length of the name variations
max_len = max(len(variations) for variations in name_dict.values())

start_total_time = time.time()
# Loop through the elements
for i in range(max_len):
    for name, variations in name_dict.items():
        print("\n\n\n****************************************************************")
        print(f"Trying to find Linkedin profile of {name}\n")

        full_path = normalize_string(f'{save_path}/{name}')
        create_folder(full_path)

        if i < len(variations):
            start_iter_time = time.time()
            name_variation = variations[i]
            print("\n---------------------------------------------")
            print(f"Iter {request_index}/{total_name_variations} - Testing name variation: {name_variation}")
            total_time = time.time() - start_total_time
            print(f"Total elapsed time: {total_time}")
            
            # open google
            options = webdriver.ChromeOptions()
            options.add_argument("start-maximized")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument(f'--proxy-server=socks5://127.0.0.1:9050')
            driver = webdriver.Chrome(options=options)  

            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    )
            
            sleep(random.uniform(1, 2))
            driver.get('https://www.google.com.br')
            page_source = driver.page_source
            while "Error 403" in page_source:
                renew_connection()
                driver.get('https://www.google.com.br')
                page_source = driver.page_source
            sleep(random.uniform(1, 2))
            
            # Search query
            search_box = driver.find_element(By.NAME, 'q')
            search_query = f'{name_variation} ufabc linkedin'
            for char in search_query:
                search_box.send_keys(char)
                delay = random.uniform(0.1, 0.3)
                sleep(delay)
            search_box.send_keys(Keys.RETURN)
            sleep(random.uniform(3, 5))
            page_source = driver.page_source
            print(page_source)

            # Find linkedin links and click on the first one (or maybe second, third etc)
            links = driver.find_elements(By.TAG_NAME, 'a') # Find all the anchor elements on the page

            # Filter anchor elements pointing to linkedin.com
            linkedin_links = []
            for link in links:
                href = link.get_attribute('href')
                if href and 'linkedin.com' in href:
                    linkedin_links.append(link)

            if len(linkedin_links) > 0:
                linkedin_links[0].click()
                sleep(random.uniform(5, 7))
            
                # Calculate the total duration and scrolling increments
                num_steps = random.randint(2,4)
                scroll_height = driver.execute_script("return document.body.scrollHeight")
                scroll_step = scroll_height / num_steps

                # Perform scrolling in increments
                for _ in range(num_steps):
                    # Scroll by the defined step size
                    driver.execute_script(f"window.scrollBy(0, {scroll_step})")
                    delay = random.uniform(3, 6)
                    sleep(delay)
                sleep(random.uniform(1, 2))


                # Get the page source
                page_source = driver.page_source

                success = 1
                if "authwall" in page_source:
                    print("You hit the authentication wall!")
                    problems = "authwall_"
                    success = 0
                else:
                    problems = ""

                if "captcha" in page_source:
                    print("You hit a captch page!")
                    problems = problems + "captcha_"
                    success = 0

                if page_source.startswith("<html><head>\n    <script type=\"text/javascript\">\n"):
                    print("You hit javascript obfuscated code!")
                    problems = problems + "obfuscatedJS_"
                    success = 0

                if success:
                    print("Successful request!")
                    succesful_requests += 1
                else:
                    print("Failed request!")
                print(f"So far {succesful_requests} out of {request_index} requests were succesful.")

                # Save the page source as an HTML file
                HtmlPath = f"{full_path}/{request_index}_{name_variation}_{problems}.html"
                print(f"- saving HTML to: {HtmlPath}")
                file = open(HtmlPath,'w',encoding='utf-8')
                file.write(page_source)
                file.close()
                
                request_index += 1
                sleep(10)
                iter_time = time.time() - start_iter_time
                print(f"Iteration elapsed time: {iter_time}")
            else:
                print("No linkedin.com search results.")
            driver.close()
            
        else:
            print(f"Element {i+1} for {name} doesn't exist")


# for name in name_list:    
#     print("\n\n\n****************************************************************")
#     print(f"Trying to find Linkedin profile of {name}\n")
    
#     full_path = normalize_string(f'{save_path}/{name}')
#     create_folder(full_path)

#     for name_variation in generate_name_variations(name):
#         print("\n---------------------------------------------")
#         print(f"Testing name variation: {name_variation}")

#         driver = webdriver.Chrome()
#         sleep(1.5)
#         driver.maximize_window()
#         sleep(2)
#         driver.get('https://www.google.com.br')
#         sleep(2)

#         # Find the search box element
#         search_box = driver.find_element(By.NAME, 'q')
#         search_query = f'"{name_variation}" ufabc linkedin'
#         delay = 0.2  # Delay in seconds between each character

#         for char in search_query:
#             search_box.send_keys(char)
#             sleep(delay)

#         search_box.send_keys(Keys.RETURN)
#         sleep(5)

#         # Find the element using XPath
#         element = driver.find_element(By.XPATH, '//*[@id="rso"]/div[1]/div/div/div[1]/div/a/h3') # make this more robust, so that it takes the first real link every time, and that link must be from linkedin, (it can try the second, third and so on, until it finds from linkedin)
#         # Click on the element
#         element.click()
#         sleep(20)
#         # Get the page source
#         page_source = driver.page_source

#         # Save the page source as an HTML file
#         HtmlPath = f"{full_path}/{result_index}_{name_variation}.html"
#         print(f"- saving HTML to: {HtmlPath}")
#         result_index += 1
#         file = open(HtmlPath,'w',encoding='utf-8')
#         file.write(page_source)
#         file.close()
#         driver.close()
