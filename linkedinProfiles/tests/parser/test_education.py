import copy
import unittest
from pathlib import Path
import json
from bs4 import BeautifulSoup

from ...parser.education import extract_education_list, get_degree, get_education_list, get_field_of_study, get_grade, parse_activities_societies, parse_degree_info, parse_description, parse_school_name, parse_school_url, parse_start_end_date

class CustomTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.write('OK\n')
        self.stream.write(f'Success: {str(test)} tested {test.num_profiles_tested()} profiles\n')
        self.stream.flush()

class CustomTestRunner(unittest.TextTestRunner):
    resultclass = CustomTestResult

class TestExtractEducationList(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.maxDiff = None
        self.test_data_path = Path(__file__).resolve().parent / 'test_data'
        expected_data_file = self.test_data_path / 'expected_data' / 'expected_education_data.json'

        with open(expected_data_file, 'r') as f:
            expected_data = json.load(f)
            self.profiles = expected_data['educations']

        # load html content and parsed identification_card during setup
        for profile in self.profiles:
            html_path = self.test_data_path / 'input_data' / profile['file']
            with open(html_path, "r") as f:
                page_source = f.read()
            soup = BeautifulSoup(page_source, 'html.parser')
            profile['education_list'] = get_education_list(soup)
            profile['soup'] = soup
            profile['page_source'] = page_source

    def num_profiles_tested(self):
        return len(self.profiles)

    def test_parse_school_name(self):
        """Test if school name is parsed correctly."""
        for profile in self.profiles:
            for idx, education_item in enumerate(profile['education_list']):
                parsed_school_name = parse_school_name(education_item)
                expected_school_name = profile['data'][idx]['school_name']
                with self.subTest(profile=profile['file'], education_item=idx):
                    self.assertEqual(parsed_school_name, expected_school_name)

    def test_parse_school_url(self):
        """Test if school URL is parsed correctly."""
        for profile in self.profiles:
            for idx, education_item in enumerate(profile['education_list']):
                parsed_school_url = parse_school_url(education_item)
                expected_school_url = profile['data'][idx]['school_linkedin_url']
                with self.subTest(profile=profile['file'], education_item=idx):
                    self.assertEqual(parsed_school_url, expected_school_url)

    def test_parse_degree_info(self):
        """Test if degree info is parsed correctly, that is, a list of degree information."""
        for profile in self.profiles:
            for idx, education_item in enumerate(profile['education_list']):
                parsed_degree_info = parse_degree_info(education_item)
                expected_degree_info = profile['data'][idx]['degree_info']
                with self.subTest(profile=profile['file'], education_item=idx):
                    self.assertEqual(parsed_degree_info, expected_degree_info)

    def test_get_degree(self):
        """Test if degree is parsed correctly."""
        for profile in self.profiles:
            for idx, education_item in enumerate(profile['education_list']):
                parsed_degree = get_degree(parse_degree_info(education_item))
                expected_degree = profile['data'][idx]['degree']
                with self.subTest(profile=profile['file'], education_item=idx):
                    self.assertEqual(parsed_degree, expected_degree)

    def test_get_field_of_study(self):
        """Test if field of study is parsed correctly."""
        for profile in self.profiles:
            for idx, education_item in enumerate(profile['education_list']):
                parsed_field_of_study = get_field_of_study(parse_degree_info(education_item))
                expected_field_of_study = profile['data'][idx]['field_of_study']
                with self.subTest(profile=profile['file'], education_item=idx):
                    self.assertEqual(parsed_field_of_study, expected_field_of_study)

    def test_get_grade(self):
        """Test if grade is parsed correctly."""
        for profile in self.profiles:
            for idx, education_item in enumerate(profile['education_list']):
                parsed_grade = get_grade(parse_degree_info(education_item))
                expected_grade = profile['data'][idx]['grade']
                with self.subTest(profile=profile['file'], education_item=idx):
                    self.assertEqual(parsed_grade, expected_grade)

    def test_parse_start_end_date(self):
        """Test if start and end date are parsed correctly."""
        for profile in self.profiles:
            for idx, education_item in enumerate(profile['education_list']):
                parsed_start_date, parsed_end_date = parse_start_end_date(education_item)
                expected_start_date = profile['data'][idx]['start_date']
                expected_end_date = profile['data'][idx]['end_date']
                with self.subTest(profile=profile['file'], education_item=idx):
                    self.assertEqual(parsed_start_date, expected_start_date)
                    self.assertEqual(parsed_end_date, expected_end_date)

    def test_parse_description(self):
        """Test if description is parsed correctly."""
        for profile in self.profiles:
            for idx, education_item in enumerate(profile['education_list']):
                parsed_description = parse_description(education_item)
                expected_description = profile['data'][idx]['description']
                with self.subTest(profile=profile['file'], education_item=idx):
                    self.assertEqual(parsed_description, expected_description)

    def test_parse_activities_societies(self):
        """Test if activities and societies are parsed correctly."""
        for profile in self.profiles:
            for idx, education_item in enumerate(profile['education_list']):
                parsed_activities_societies = parse_activities_societies(education_item)
                expected_activities_societies = profile['data'][idx]['activities_societies']
                with self.subTest(profile=profile['file'], education_item=idx):
                    self.assertEqual(parsed_activities_societies, expected_activities_societies)

    def test_extract_education_list(self):
        """Test if all person info is parsed and structured in a dictionary."""
        for profile in self.profiles:
            extracted_education_list = extract_education_list(profile['page_source'])
            expected_education_list = copy.deepcopy(profile['data'])

            # Remove the "degree_info" field from the expected data
            for education_item in expected_education_list:
                del education_item['degree_info']

            with self.subTest(profile=profile['file']):
                self.assertEqual(extracted_education_list, expected_education_list)



if __name__ == '__main__':
    unittest.main(testRunner=CustomTestRunner())
