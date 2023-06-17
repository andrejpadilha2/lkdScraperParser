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