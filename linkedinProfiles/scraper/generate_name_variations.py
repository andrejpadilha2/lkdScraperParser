from nameparser import HumanName
import pandas as pd

def generate_name_variations(name_str):
    # Remove specified words from name string
    name_str = name_str.replace(" de ", " ").replace(" do ", " ").replace(" da ", " ").replace(" dos ", " ").replace(" das ", " ")

    def append_variation(variation, variations):

        if variation not in variations:
            variations.append(variation)
        
        return variations

    # Full name variation
    variations = []
    variations.append(f"{name_str}") # full name

    # Extract individual name components
    name = HumanName(name_str)
    first_name = name.first
    middle_name = name.middle
    last_name = name.last

    ### Generate name variations ###
    ################################
    variation = f"{first_name} {last_name.split()[-1]}" # first and last name
    variations = append_variation(variation, variations)

    if len(middle_name.split()) > 0:
        variation = f"{first_name} {middle_name.split()[0]}" # first and second name
        variations = append_variation(variation, variations)

        variation = f"{first_name} {middle_name.split()[0]} {last_name.split()[-1]}" # first, second and last name
        variations = append_variation(variation, variations)

    if len(middle_name.split()) > 1:
        variation = f"{first_name} {middle_name.split()[1]} {last_name}" # all names except the second
        variations = append_variation(variation, variations)

    print(variations)

    return variations

def generate_all_name_variations(input_names_path): #, output_names_path):
    # Read the names from the file
    with open(input_names_path, 'r') as file:
        names = file.readlines()

    # Process names, generate name variations and add unique ID to each NAME
    processed_names = []
    uid = 0
    for name_id, name in enumerate(names):
        name = name.strip()

        # Generate name variations for the current full_name
        name_variations = generate_name_variations(name)
        # Append each name variation to the output rows
        for name_variation in name_variations:
            processed_names.append([uid, name_id, name, name_variation])
            uid += 1

    return processed_names

def generate_name_variations_linkedin_csv(input_names_path, name_variations_linkedin_path):

    name_variations = generate_all_name_variations(input_names_path)
    name_variations_linkedin_df = pd.DataFrame(name_variations, columns=['uid', 'name_id', 'full_name', 'name_variation'])

    name_variations_linkedin_df['to_scrape'] = 1 # will track if it's still necessary to scrape this name variation
    name_variations_linkedin_df['linkedin_url'] = '' # stores linkedin_url
    name_variations_linkedin_df['scraped_success_time'] = ''
    name_variations_linkedin_df['failed_cause'] = '' # stores every fail attempt cause
    name_variations_linkedin_df['html_path'] = '' # stores the path to the HTML file

    # Sort profiles so that more specific name variations are scraped first (full name -> first and last name -> etc)
    name_variations_linkedin_df['Sort'] = name_variations_linkedin_df.groupby('name_id').cumcount()
    name_variations_linkedin_df.sort_values(['Sort', 'name_id'], inplace=True)
    name_variations_linkedin_df.drop(columns=['Sort'], inplace=True)

    print(f"Creating file '{name_variations_linkedin_path}'.\n")
    name_variations_linkedin_df.to_csv(name_variations_linkedin_path, index=False, sep=',')