import pandas as pd

from .education import extract_education_info, add_education_record
from .experience import extract_professional_experience, add_experience_record
from .person import extract_person_info
from .utils import get_or_add_id

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
linkedin_profiles_df = pd.read_csv('data/linkedin_profiles/profilesSelenium11_og_namesake/linkedin_profiles.csv', sep=',', dtype=dtypes, parse_dates=['scraped_success_time'])

person_columns = {
    'person_id': int,
    'full_name': str,
    'name_variation': str,
    'linkedin_name': str,
    'linkedin_url': str,
    'headline': str,
    'location': str,
    'followers': str,
    'connections': str,
    'about': str
}
person_df = pd.DataFrame(columns=person_columns.keys())\
    .astype(person_columns)


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



# linkedin_profiles_df = linkedin_profiles_df.head(5)
for row in linkedin_profiles_df.itertuples():

    if not pd.isna(row.html_path):
        print(f"\n\n*******************************************************")
        print(f"Parsing HTML file of name #{row.name_id}, variation #{row.uid}: {row.name_variation}.\n\n")
        
        page_source = open(row.html_path, "r").read()

        # Public person data
        person_info = extract_person_info(page_source)
        person_info['full_name'] = row.full_name
        person_info['name_variation'] = row.name_variation
        person_info['linkedin_url'] = row.linkedin_url
        person_id, person_df = get_or_add_id(person_info, person_df, 'name_variation', 'person_id')

        # Education data
        educations = extract_education_info(page_source)
        for education in educations:
            school = {
                'name': education['school_name'],
                'linkedin_url': education['school_linkedin_url']
            }
            school_id, school_df = get_or_add_id(school, school_df, 'name', 'school_id')
            education_df = add_education_record(education, person_id, school_id, education_df)

            
        # Professional experience data
        experiences = extract_professional_experience(page_source)
        for experience in experiences:
            company = {
                'name': experience['company_name'],
                'linkedin_url': experience['company_linkedin_url']
            }
            company_id, company_df = get_or_add_id(company, company_df, 'name', 'company_id')
            experience_df = add_experience_record(experience, person_id, company_id, experience_df)

        


person_df.to_csv('data/linkedin_profiles/profilesSelenium11_og_namesake/person.csv', index=False, sep=',')

# school_df.reset_index(inplace=True)
# school_df.rename(columns={'index': 'uid'}, inplace=True)
school_df.to_csv('data/linkedin_profiles/profilesSelenium11_og_namesake/school.csv', index=False, sep=',')

# education_df.reset_index(inplace=True)
# education_df.rename(columns={'index': 'uid'}, inplace=True)
education_df.to_csv('data/linkedin_profiles/profilesSelenium11_og_namesake/education.csv', index=False, sep=',')


company_df.to_csv('data/linkedin_profiles/profilesSelenium11_og_namesake/company.csv', index=False, sep=',')

# experience_df.reset_index(inplace=True)
# experience_df.rename(columns={'index': 'uid'}, inplace=True)
experience_df.to_csv('data/linkedin_profiles/profilesSelenium11_og_namesake/experience.csv', index=False, sep=',')

print("\n\n************************************************************************")
print("person_df")
print(person_df[person_df['person_id']==18]['headline'])



print("\n\n************************************************************************")
print("school_df")
print(school_df)

print("\n\n************************************************************************")
print("education_df")
print(education_df)

print("\n\n************************************************************************")
print("company_df")
print(company_df)

print("\n\n************************************************************************")
print("experience_df")
print(experience_df)





# import hashlib

# def generate_new_id(df, unique_data):
#     return hashlib.sha256(unique_data.encode()).hexdigest()