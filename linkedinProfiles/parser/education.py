from bs4 import BeautifulSoup
import pandas as pd

def add_education_record(education_data, person_id, school_id, education_df):
    # Create a new dictionary with education data, person_id, and school_id
    person_education = {
        'person_id': [person_id],
        'school_id': [school_id],
        'degree': [education_data['degree']],
        'field_of_study': [education_data['field_of_study']],
        'start_date': [education_data['start_date']],
        'end_date': [education_data['end_date']],
        'description': [education_data['description']],
        'grade': [education_data['grade']],
        'activities_societies': [education_data['activities_societies']]
    }
    
    # Convert the new education dictionary into a DataFrame
    person_education_df = pd.DataFrame(person_education)

    # Concatenate the new education DataFrame with the existing education_df
    education_df = pd.concat([education_df, person_education_df], ignore_index=True)

    # Return the updated education_df
    return education_df

def get_education_list(soup):
    return soup.find_all('li', class_='education__list-item')

def parse_school_name(education_item):
    school_element = education_item.find('h3', class_='profile-section-card__title')
    return school_element.text.strip() if school_element else ""

def parse_school_linkedin_url(education_item):
    school_element = education_item.find('h3', class_='profile-section-card__title')
    a_tag = school_element.find('a')
    return a_tag['href'].split('?')[0] if a_tag else ""

def parse_degree_info(education_item):
    degree_info_elements = education_item.find_all('span', class_='education__item--degree-info')
    return [degree_info_element.text.strip() for degree_info_element in degree_info_elements]

def get_degree(degree_info):
    """ Extract degree (bachelor's, master, doctoral, etc.) """
    degree = ""
    if len(degree_info) >= 1:
        degree = degree_info[0]
    return degree

def get_field_of_study(degree_info):
    """ Extract field_of_study: management engineering, mechanical engineering, computer science, etc. """
    field_of_study = ""
    if len(degree_info) >= 2:
        field_of_study = degree_info[1]
    return field_of_study

def get_grade(degree_info):
    """Extract the grade (GPA) of the corresponding degree info. It can come in multiple formats: just grade, or grade + max. grade etc."""
    grade = ""
    if len(degree_info) >= 3:
        # TODO:
        # I need to extract the grade and the maximum grade from this string field (maybe not here, but definitely in the analysis)
        grade = degree_info[2]
    return grade

def parse_start_end_date(education_item):
    """ Extract the start time, end time, and duration """
    duration_element = education_item.find('p', class_='education__item--duration')
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
            start_date = ""
            end_date = ""
    return start_date, end_date

def parse_description(education_item):
    """ Extract the description (if available) """
    description = ""
    description_big = education_item.find('p', class_='show-more-less-text__text--more')
    if description_big:
        description = description_big.get_text(strip=True).replace('Exibir menos', '')
    else:
        description_small = education_item.find('p', class_='show-more-less-text__text--less')
        if description_small:
            description = description_small.get_text(strip=True).replace('Exibir mais', '')
    return description

def parse_activities_societies(education_item):
    activities_societies_element = education_item.find('p', class_='education__item--activities-and-societies')
    return activities_societies_element.text.strip() if activities_societies_element else ""

def extract_education_list(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    education_list = get_education_list(soup)

    educations = []
    if len(education_list) > 0:
        for education_item in education_list:
            
            school_name = parse_school_name(education_item)
            school_url = parse_school_linkedin_url(education_item)
            degree_info = parse_degree_info(education_item)
            degree = get_degree(degree_info)
            field_of_study = get_field_of_study(degree_info)
            grade = get_grade(degree_info)
            start_date, end_date = parse_start_end_date(education_item)
            description = parse_description(education_item)
            activities_societies = parse_activities_societies(education_item)
            
            educations.append({
                'school_name': school_name,
                'school_linkedin_url': school_url,
                'degree': degree,
                'field_of_study': field_of_study,
                'grade': grade,
                'start_date': start_date,
                'end_date': end_date,
                'description': description,
                'activities_societies': activities_societies})

    return educations