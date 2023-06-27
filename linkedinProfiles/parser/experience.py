from bs4 import BeautifulSoup
import pandas as pd

def add_experience_record(experience_data, person_id, company_id, experience_df):
    # Create a new dictionary with experience data, person_id, and company_id
    person_experience_dict = {
        'person_id': [person_id],
        'company_id': [company_id],
        'role': [experience_data['role']],
        'location': [experience_data['location']],
        'start_date': [experience_data['start_date']],
        'end_date': [experience_data['end_date']],
        'description': [experience_data['description']]
    }
    
    # Convert the new experience dictionary into a DataFrame
    person_experience_df = pd.DataFrame(person_experience_dict)

    # Concatenate the new experience DataFrame with the existing experience_df
    experience_df = pd.concat([experience_df, person_experience_df], ignore_index=True)

    # Return the updated experience_df
    return experience_df

def get_experience_list(soup):
    experience = soup.find('ul', class_='experience__list')
    experience_list = experience.find_all('li', class_='profile-section-card') if experience else []
    return experience_list

def parse_company_name(experience_item):
    company_element = experience_item.find('h4', class_='profile-section-card__subtitle')
    return company_element.text.strip() if company_element else ""

def parse_company_linkedin_url(experience_item):
    company_element = experience_item.find('a', class_='profile-section-card__subtitle-link')
    return company_element['href'].split('?')[0] if company_element else ""

def parse_role(experience_item):
    role_item = experience_item.find('h3', class_='profile-section-card__title')
    return role_item.text.strip() if role_item else ""

def parse_location(experience_item):
    """Parse the location of the company. This method already accounts for two possibilities: 
        if the experience is a single experience within a company or 
        if it's part of multiple experiences within the same company."""
    
    location = ""
    location_element = experience_item.find('p', class_='experience-item__location')
    if not location_element:
        location_element = experience_item.find('p', class_='experience-group-position__location')
    if location_element:
        location = location_element.text.strip()
        
    return location

def parse_start_end_date(experience_item):
    start_date = ""
    end_date = ""

    date_range_element = experience_item.find('span', class_='date-range')
    if date_range_element:
        time_elements = date_range_element.find_all('time')

        if time_elements and len(time_elements) >= 1:
            start_date = time_elements[0].text.strip()

            if len(time_elements) == 2:
                end_date = time_elements[1].text.strip()
            else:
                end_date = "Ongoing"
    
    return start_date, end_date

def parse_description(experience_item):
    """Parse the description of the company. This method already accounts for two possibilities: 
    if the experience is a single experience within a company or 
    if it's part of multiple experiences within the same company."""

    description = ""
    description_element = experience_item.find('div', class_='experience-item__description')
    if not description_element:
        description_element = experience_item.find('div', class_='experience-group-position__description')
    
    if description_element:
        description_big = description_element.find('p', class_='show-more-less-text__text--more')
        if description_big:
            description = description_big.get_text(strip=True).replace('Exibir menos', '').replace('Show less', '')
        else:
            description = description_element.find('p', class_='show-more-less-text__text--less').get_text(strip=True)
    
    return description

def extract_experience_list(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    experience_list = get_experience_list(soup)
    
    experiences = []
    if len(experience_list) > 0:
        for experience_item in experience_list:
            
            company_name = parse_company_name(experience_item)
            company_linkedin_url = parse_company_linkedin_url(experience_item)
            role = parse_role(experience_item)
            location = parse_location(experience_item)
            start_date, end_date = parse_start_end_date(experience_item)
            description = parse_description(experience_item)

            experiences.append({
                'company_name': company_name,
                'company_linkedin_url': company_linkedin_url,
                'role': role,
                'location': location,
                'start_date': start_date, 
                'end_date': end_date,
                'description': description})

    return experiences