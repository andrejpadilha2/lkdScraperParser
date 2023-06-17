from bs4 import BeautifulSoup

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