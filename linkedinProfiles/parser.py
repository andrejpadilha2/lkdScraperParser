import pandas as pd
from bs4 import BeautifulSoup

def extract_professional_experience(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')

    experiences = []

    # Find all experience items
    experience_list = soup.find('ul', class_='experience__list')

    if experience_list:
        experience_items = experience_list.find_all('li', class_='profile-section-card')

        if len(experience_items) > 0:

            # Iterate over each experience item
            for item in experience_items:
                # Extract the role name
                role = item.find('h3', class_='profile-section-card__title').text.strip()

                
                # Extract the location (if available)
                location = None
                location_element = item.find('p', class_='experience-item__location')
                if not location_element:
                    location_element = item.find('p', class_='experience-group-position__location')
                if location_element:
                    location = location_element.text.strip()


                # Extract the company name (if available)
                company_element = item.find('h4', class_='profile-section-card__subtitle')
                company_name = company_element.text.strip() if company_element else None

                # Find the date range element
                date_range_element = item.find('span', class_='date-range')

                # Extract the start time, end time, and duration
                start_date = None
                end_date = None
                if date_range_element:
                    # TODO: 
                    # Convert date string to DATE
                    time_elements = date_range_element.find_all('time')

                    if time_elements and len(time_elements) >= 1:
                        start_date = time_elements[0].text.strip()

                        if len(time_elements) == 2:
                            end_date = time_elements[1].text.strip()
                        else:
                            end_date = "Ongoing"
                    

                    # duration_element = date_range_element.find('span', class_='before:middot')
                    # if duration_element:
                    #     duration = duration_element.text.strip()
                    # else:
                    #     duration = None


                # Extract the description (if available)
                description = None
                description_element = item.find('div', class_='experience-item__description')
                if not description_element:
                    description_element = item.find('div', class_='experience-group-position__description')
                
                if description_element:
                    description_big = description_element.find('p', class_='show-more-less-text__text--more')
                    if description_big:
                        description = description_big.get_text(strip=True).replace('Exibir menos', '')
                    else:
                        description = description_element.find('p', class_='show-more-less-text__text--less').get_text(strip=True)


                experiences.append({
                    'company_name': company_name,
                    'company_linkedin_url': 'url_of_company_here',
                    'role': role,
                    'location': location,
                    'start_date': start_date, 
                    'end_date': end_date,
                    'description': description})

    return experiences

def extract_education_info(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')

    education_items = soup.find_all('li', class_='education__list-item')

    educations = []
    if len(education_items) > 0:

        for item in education_items:
            school_element = item.find('h3', class_='profile-section-card__title')
            school_name = school_element.text.strip() if school_element else None

            a_tag = school_element.find('a')
            school_url = a_tag['href'] if a_tag else None
            
            degree_info_elements = item.find_all('span', class_='education__item--degree-info')
            degree_info = [degree_info_element.text.strip() for degree_info_element in degree_info_elements]

            # Extract degree (bachelor's, master, doctoral, etc.)
            degree = None
            if len(degree_info) >= 1:
                degree = degree_info[0]
            
            # Extract field_of_stydy: management engineering, mechanical engineering, computer science, etc.
            field_of_study = None
            if len(degree_info) >= 2:
                field_of_study = degree_info[1]

            grade = None
            if len(degree_info) >= 3:
                # TODO:
                # I need to extract the grade and the maximum grade from this string field (maybe not here, but definitely in the analysis)
                grade = degree_info[2]

            duration_element = item.find('p', class_='education__item--duration')

            # Extract the start time, end time, and duration
            if duration_element:
                # TODO: 
                # Convert date string to DATE
                time_elements = duration_element.find_all('time')

                if time_elements and len(time_elements) >= 1:
                    start_date = time_elements[0].text.strip()

                    if len(time_elements) == 2:
                        end_date = time_elements[1].text.strip()
                    else:
                        end_date = "Ongoing"
                else:
                    start_date = None
                    end_date = None

            description_element = item.find('div', class_='show-more-less-text')
            description = description_element.text.strip() if description_element else None

            activities_societies_element = item.find('p', class_='education__item--activities-and-societies')
            activities_societies = activities_societies_element.text.strip() if activities_societies_element else None

            educations.append({
                'school_name': school_name,
                'school_linkedin_url': school_url,
                'degree': degree,
                'field_of_study': field_of_study,
                'start_date': start_date, # actually should be date type
                'end_date': end_date, # actually should be date type
                'description': description,
                'grade': grade,
                'activities_societies': activities_societies})


    return educations

# open the file "linkedin_profiles.csv" to get all HTML that will be parsed
dtypes = {
                'uid': int,
                'name_id': int,
                'full_name': str,
                'name_variation': str,
                'to_scrape': int,
                'linkedin_url': str,
                'failed_cause': str,
                'html_path': str}
linkedin_profiles_df = pd.read_csv('people/profilesSelenium12/linkedin_profiles.csv', sep=',', dtype=dtypes, parse_dates=['scraped_success_time'])

school_columns = {
            'school_id': int,
            'name': str,
            'linkedin_url': str}
school_df = pd.DataFrame(columns=school_columns.keys())\
    .astype(school_columns)


education_columns = {
            'person_id': int,
            'school_id': int,
            'degree': str,
            'field_of_study': str,
            'start_date': str, # actually should be date
            'end_date': str, # actually should be date
            'description': str,
            'grade': str,
            'activities_societies': str}
education_df = pd.DataFrame(columns=education_columns.keys())\
    .astype(education_columns)


company_columns = {
            'company_id': int,
            'name': str,
            'linkedin_url': str}
company_df = pd.DataFrame(columns=company_columns.keys())\
    .astype(company_columns)

experience_columns = {
            'person_id': int,
            'company_id': int,
            'role': str,
            'location': str,
            'start_date': str, # actually should be date
            'end_date': str, # actually should be date
            'description': str}
experience_df = pd.DataFrame(columns=experience_columns.keys())\
    .astype(experience_columns)



def generate_new_id(df, id_column):
    if df.empty:
        return 0
    else:
        return df[id_column].max() + 1

def get_or_add_id(entity, df, id_column):
    # check if entity already exists in the DataFrame
    existing_entity = df.loc[df['name'] == entity['name']]

    if not existing_entity.empty:
        # if entity exists, return its ID
        return existing_entity.iloc[0][id_column], df
    else:
        # if entity doesn't exist, generate a new ID, add them to DataFrame, and return the ID
        new_id = generate_new_id(df, id_column)  # function to generate new unique id
        entity[id_column] = new_id
        df = df.append(entity, ignore_index=True)
        return new_id, df
    
def add_education_record(education_data, person_id, school_id, education_df):
    # Create a new dictionary with education data, person_id and school_id
    education = {
        'person_id': person_id,
        'school_id': school_id,
        'degree': education_data['degree'],
        'field_of_study': education_data['field_of_study'],
        'start_date': education_data['start_date'],
        'end_date': education_data['end_date'],
        'description': education_data['description'],
        'grade': education_data['grade'],
        'activities_societies': education_data['activities_societies'],}
    
    # Append the new education record to the DataFrame
    education_df = education_df.append(education, ignore_index=True)

    # return updated education_df
    return education_df

def add_experience_record(experience_data, person_id, company_id, experience_df):
    # Create a new dictionary with education data, person_id and company_id
    experience = {
        'person_id': person_id,
        'company_id': company_id,
        'role': experience_data['role'],
        'location': experience_data['location'],
        'start_date': experience_data['start_date'],
        'end_date': experience_data['end_date'],
        'description': experience_data['description']}
        
    # Append the new education record to the DataFrame
    experience_df = experience_df.append(experience, ignore_index=True)

    # return updated experience_df
    return experience_df

linkedin_profiles_df = linkedin_profiles_df.head(50)
for row in linkedin_profiles_df.itertuples():

    if not pd.isna(row.html_path):
        print(f"\n\n*******************************************************")
        print(f"Parsing HTML file of name #{row.name_id}, variation #{row.uid}: {row.name_variation}.\n\n")
        
        page_source = open(row.html_path, "r").read()

        # Public person data


        # Education data
        educations = extract_education_info(page_source)
        for education in educations:
            school = {
                'name': education['school_name'],
                'linkedin_url': education['school_linkedin_url']
            }
            school_id, school_df = get_or_add_id(school, school_df, 'school_id')
            education_df = add_education_record(education, row.uid, school_id, education_df)

            
        # Professional experience data
        experiences = extract_professional_experience(page_source)
        for experience in experiences:
            company = {
                'name': experience['company_name'],
                'linkedin_url': experience['company_linkedin_url']
            }
            company_id, company_df = get_or_add_id(company, company_df, 'company_id')
            experience_df = add_experience_record(experience, row.uid, company_id, experience_df)

        

# school_df.reset_index(inplace=True)
# school_df.rename(columns={'index': 'uid'}, inplace=True)
school_df.to_csv('people/profilesSelenium12/school.csv', index=False, sep=',')

# experience_df.reset_index(inplace=True)
# experience_df.rename(columns={'index': 'uid'}, inplace=True)
experience_df.to_csv('people/profilesSelenium12/experience.csv', index=False, sep=',')

# education_df.reset_index(inplace=True)
# education_df.rename(columns={'index': 'uid'}, inplace=True)
education_df.to_csv('people/profilesSelenium12/education.csv', index=False, sep=',')

print("school_df")
print(school_df)

print()
print("education_df")
print(education_df)

print()
print("company_df")
print(company_df)

print()
print("experience_df")
print(experience_df)




# for filename in os.listdir(directory):
#     with open(filename, 'r') as f:
#         contents = f.read()

#     soup = BeautifulSoup(contents, 'html.parser')
    
#     # Parse main information
#     person = parse_person(soup)
#     person_id = get_or_create_person_id(person, person_df)

#     # Parse education
#     educations = parse_educations(soup)
#     for education in educations:
#         school_id = get_or_create_school_id(education['school'], school_df)
#         create_education_record(education, person_id, school_id, education_df)

#     # Parse experiences
#     experiences = parse_experiences(soup)
#     for experience in experiences:
#         company_id = get_or_create_company_id(experience['company'], company_df)
#         create_experience_record(experience, person_id, company_id, experience_df)

# # Save to CSV
# person_df.to_csv('person.csv')
# experience_df.to_csv('experience.csv')
# company_df.to_csv('company.csv')
# education_df.to_csv('education.csv')
# school_df.to_csv('school.csv')


# def get_or_create_person_id(person, person_df):
#     # check if person already exists in the DataFrame
#     existing_person = person_df.loc[person_df['name'] == person['name']]

#     if not existing_person.empty:
#         # if person exists, return their ID
#         return existing_person.iloc[0]['person_id']
#     else:
#         # if person doesn't exist, generate a new ID, add them to DataFrame, and return the ID
#         new_person_id = generate_new_id(person_df)  # function to generate new unique id
#         person['person_id'] = new_person_id
#         person_df = person_df.append(person, ignore_index=True)
#         return new_person_id




# import hashlib

# def generate_new_id(df, unique_data):
#     return hashlib.sha256(unique_data.encode()).hexdigest()