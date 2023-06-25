from typing import Tuple
import logging
import sys

import pandas as pd

from .education import extract_education_list, add_education_record
from .experience import extract_professional_experience, add_experience_record
from .person import extract_person_info
from .utils import get_or_add_id

from .config import LINKEDIN_PROFILES_COLUMNS, PERSON_COLUMNS, SCHOOL_COLUMNS, EDUCATION_COLUMNS, COMPANY_COLUMNS, EXPERIENCE_COLUMNS
from .config import DATA_PATH, LINKEDIN_PROFILES_PATH, PERSON_PATH, SCHOOL_PATH, EDUCATION_PATH, COMPANY_PATH, EXPERIENCE_PATH

# Set up logging
logging.basicConfig(level=logging.INFO)


def process_row(row, person_df, school_df, education_df, company_df, experience_df) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    """Processes a single row of LinkedIn profile data."""
    if pd.isna(row.html_path):
        return None
    info_text = f"\n\n*******************************************************\nParsing HTML file of name #{row.name_id}, variation #{row.uid}: {row.name_variation}.\n\n"
    logging.info(info_text)
    html_path = DATA_PATH / row.html_path
    with open(html_path, "r") as f:
        page_source = f.read()

    # Public person data
    person_info = extract_person_info(page_source)
    person_info['full_name'] = row.full_name
    person_info['name_variation'] = row.name_variation
    person_info['linkedin_url'] = row.linkedin_url
    person_id, person_df = get_or_add_id(person_info, person_df, 'name_variation', 'person_id')

    # Education data
    educations = extract_education_list(page_source)
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

    return person_df, school_df, education_df, company_df, experience_df



def main():
    """Main execution function."""
    
    linkedin_profiles_df = pd.read_csv(LINKEDIN_PROFILES_PATH, sep=',', 
                                       dtype=LINKEDIN_PROFILES_COLUMNS, 
                                       parse_dates=['scraped_success_time'])

    person_df = pd.DataFrame(columns=PERSON_COLUMNS.keys())\
    .astype(PERSON_COLUMNS)

    school_df = pd.DataFrame(columns=SCHOOL_COLUMNS.keys())\
        .astype(SCHOOL_COLUMNS)

    education_df = pd.DataFrame(columns=EDUCATION_COLUMNS.keys())\
        .astype(EDUCATION_COLUMNS)

    company_df = pd.DataFrame(columns=COMPANY_COLUMNS.keys())\
        .astype(COMPANY_COLUMNS)

    experience_df = pd.DataFrame(columns=EXPERIENCE_COLUMNS.keys())\
        .astype(EXPERIENCE_COLUMNS)

    for profile_row in linkedin_profiles_df.itertuples():
        try:
            result = process_row(profile_row, person_df, school_df, education_df, company_df, experience_df)
            if result is not None:
                person_df, school_df, education_df, company_df, experience_df = result
        except Exception as e:
            logging.error(f"Failed to process row {profile_row.Index}: {e}")

    print(education_df.dtypes)

    person_df.to_csv(PERSON_PATH, index=False, sep=',')
    school_df.to_csv(SCHOOL_PATH, index=False, sep=',')
    education_df.to_csv(EDUCATION_PATH, index=False, sep=',')
    company_df.to_csv(COMPANY_PATH, index=False, sep=',')
    experience_df.to_csv(EXPERIENCE_PATH, index=False, sep=',')

if __name__ == "__main__":
    print(f"Current DATA_PATH: {DATA_PATH}")
    user_input = input("Is this the correct DATA_PATH? Type 'yes' to continue or any other key to cancel: ")
    if user_input.lower() != 'yes':
        print("Operation canceled.")
        sys.exit(1)

    main()

# import hashlib

# def generate_new_id(df, unique_data):
#     return hashlib.sha256(unique_data.encode()).hexdigest()