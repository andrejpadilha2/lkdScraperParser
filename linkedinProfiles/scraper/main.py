import os
from timeit import default_timer as timer
import pandas as pd
import sys
import json

from .custom_chrome_driver import CustomChromeDriver
from .process_row import process_row
from .generate_linkedin_profiles import generate_linkedin_profiles_csv
from ..general_utils.methods import normalize_string, create_folder, sleep_print
from ..config import DATA_PATH

def main(linkedin_profiles_df, save_path, linkedin_profiles_path, unavailable_profiles_path, non_ufabc_students_path):
    start_total_time = timer()
    total_name_variations = len(linkedin_profiles_df)
    total_linkedin_requests = 0
    successful_linkedin_requests = 0
    total_profiles_scraped = 0
    successful_profiles_scraped = 0

    driver = CustomChromeDriver(headless=False)

    iter = 1
    for profile_row in linkedin_profiles_df.itertuples():
        start_iter_time = timer()

        if (total_linkedin_requests % 20 == 0 or total_linkedin_requests % 21 == 0) and total_linkedin_requests != 0:
            driver.restart()

        print("\n\n\n****************************************************************")
        print(f"Trying to find LinkedIn profile of {profile_row.full_name}\n")
        print("\n---------------------------------------------")
        print(f"Iter {iter}/{total_name_variations} - Testing name variation #{profile_row.uid}: {profile_row.name_variation}")

        full_path = f"{save_path}/{profile_row.name_id}_{normalize_string(profile_row.full_name)}"
        create_folder(full_path)

        with open(unavailable_profiles_path, 'r') as file:
            unavailable_profiles = json.load(file)

        with open(non_ufabc_students_path, 'r') as file:
            non_ufabc_students = json.load(file)

        linkedin_profiles_df, unavailable_profiles, non_ufabc_students, total_linkedin_requests, successful_linkedin_requests, \
            total_profiles_scraped, successful_profiles_scraped \
                = process_row(profile_row, driver, linkedin_profiles_df, unavailable_profiles, 
                              non_ufabc_students, full_path, 
                            total_linkedin_requests, successful_linkedin_requests,
                            total_profiles_scraped, successful_profiles_scraped)
        linkedin_profiles_df.to_csv(linkedin_profiles_path, index=False, sep=',')
        with open(f"{DATA_PATH / 'unavailable_profiles.json'}", 'w') as file:
            json.dump(unavailable_profiles, file)
        with open(f"{DATA_PATH / 'non_ufabc_students.json'}", 'w') as file:
            json.dump(non_ufabc_students, file)

        iter_time = timer() - start_iter_time
        print(f"→ Iteration elapsed time: {iter_time:.2f}")
        total_time = timer() - start_total_time
        print(f"Total elapsed time: {total_time:.2f}")
        iter += 1

    print("\n\n**************************\n")
    print("FINISHED LINKEDIN SCRAPING\n")
    print(f"Total requests to Linkedin: {total_linkedin_requests}. Successful requests: {successful_linkedin_requests}")
    print(f"Total profiles tried to scrape: {total_profiles_scraped}. Profiles successfully scraped: {successful_profiles_scraped}")
    print(f"Total time running the scraper: {total_time}")




if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__)) # we don't know where the user will run the script from
    names_list_path = DATA_PATH / 'names_list.txt'
    if not os.path.exists(names_list_path):
        raise Exception(f"No \"names_list.txt\" file to scrape on {DATA_PATH}.")

    print("\nBEGINNING LINKEDIN SCRAPING\n")


    unavailable_profiles_path = f"{DATA_PATH / 'unavailable_profiles.json'}"
    if not os.path.exists(unavailable_profiles_path):
        with open(unavailable_profiles_path, 'w') as file:
            json.dump([], file)

    non_ufabc_students_path = f"{DATA_PATH / 'non_ufabc_students.json'}"
    if not os.path.exists(non_ufabc_students_path):
        with open(non_ufabc_students_path, 'w') as file:
            json.dump([], file)

    # Check if linkedin_profiles.csv exists
    linkedin_profiles_path = DATA_PATH / 'linkedin_profiles.csv'
    linkedin_profiles_csv_exists = os.path.exists(linkedin_profiles_path)
    if not linkedin_profiles_csv_exists:
        generate_linkedin_profiles_csv(names_list_path, linkedin_profiles_path)       
        sleep_print(1, "sleeping 1 second...")
    else:
        user_input = input(f"Looks like a scrapping process already started on '{linkedin_profiles_path}'.\nWould you like to continue it? Type 'yes' to continue:\n> ")
        if user_input.lower() != 'yes':
            print('Exiting the scraper.')
            sys.exit(1)

    dtypes = {
                'uid': int,
                'name_id': int,
                'full_name': str,
                'name_variation': str,
                'to_scrape': int,
                'linkedin_url': str,
                'failed_cause': str,
                'html_path': str
            }
    linkedin_profiles_df = pd.read_csv(linkedin_profiles_path, sep=',', dtype=dtypes, parse_dates=['scraped_success_time'])

    main(linkedin_profiles_df, DATA_PATH, linkedin_profiles_path, unavailable_profiles_path, non_ufabc_students_path)
    


# Error Handling:
# It is always a good idea to anticipate potential issues and handle them appropriately. For instance, you have commented on a scenario where the internet connection may be lost during the execution. Python's exception handling allows you to handle these situations.

# In your case, you could add a try-except block around the request_website function call to handle any exceptions related to network errors.

# python
# Copy code
# try:
#     driver = request_website(driver, 'https://www.google.com.br')
# except Exception as e:
#     print(f"Error when trying to access the website: {str(e)}")
#     # Here you can add code to handle this error, like trying again, logging the error, or stopping the script




# Adding Logging:
# Logging is a very useful tool to track what's happening in your code. Python's built-in logging module makes it easy to add logging to your scripts. Here's a basic example of how to use it:

# python
# Copy code
# import logging

# logging.basicConfig(level=logging.INFO)

# def main():
#     logging.info("Starting script...")
#     # your code here...
#     logging.info("Script finished successfully.")

# if __name__ == "__main__":
#     main()
# With logging, you can also print debug messages that only show up when you're debugging:

# python
# Copy code
# logging.debug("This is a debug message.")
# To see debug messages, you need to set the logging level to DEBUG when configuring logging:

# python
# Copy code
# logging.basicConfig(level=logging.DEBUG)







# Commenting Your Code and Writing Docstrings:
# Good comments can be very helpful, but they can also be overused. As a general rule, your code should be self-explanatory. If you have to write a comment to explain what a piece of code does, it might be a sign that you should refactor that code into a function with a descriptive name.

# Here's an example:

# python
# Copy code
# # Before
# # Get the first 10 items (this is a hotfix, will be removed in the next version)
# items = all_items[:10]

# # After
# def get_first_n_items(items, n):
#     """Return the first n items from the given list."""
#     return items[:n]

# items = get_first_n_items(all_items, 10)
# You should also write docstrings for each function and class. Docstrings are a type of comment that explain what a function does, its parameters, and its return values. Here's an example:

# python
# Copy code
# def add(a, b):
#     """Add two numbers together.

#     Parameters:
#     a (int): The first number.
#     b (int): The second number.

#     Returns:
#     int: The sum of a and b.
#     """
#     return a + b
# Remember, these are suggestions. It's always a good idea to adapt guidelines to the needs and style of your specific project.