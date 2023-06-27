import copy
import unittest
from pathlib import Path
import json
from bs4 import BeautifulSoup

from ...parser.experience import extract_experience_list, get_experience_list, parse_company_linkedin_url, parse_company_name, parse_description, parse_role, parse_location, parse_start_end_date

class CustomTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.write('OK\n')
        self.stream.write(f'Success: {str(test)} tested {test.num_profiles_tested()} profiles\n')
        self.stream.flush()

class CustomTestRunner(unittest.TextTestRunner):
    resultclass = CustomTestResult

class TestExtractExperienceList(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.maxDiff = None
        self.test_data_path = Path(__file__).resolve().parent / 'test_data'
        expected_data_file = self.test_data_path / 'expected_data' / 'expected_experience_data.json'

        with open(expected_data_file, 'r') as f:
            expected_data = json.load(f)
            self.profiles = expected_data['experiences']

        # load html content and parsed identification_card during setup
        for profile in self.profiles:
            html_path = self.test_data_path / 'input_data' / profile['file']
            with open(html_path, "r") as f:
                page_source = f.read()
            soup = BeautifulSoup(page_source, 'html.parser')
            profile['experience_list'] = get_experience_list(soup)
            profile['soup'] = soup
            profile['page_source'] = page_source

    def num_profiles_tested(self):
        return len(self.profiles)

    def test_parse_company_name(self):
        """Test if company name is parsed correctly."""
        for profile in self.profiles:
            for idx, experience_item in enumerate(profile['experience_list']):
                parsed_company_name = parse_company_name(experience_item)
                expected_company_name = profile['data'][idx]['company_name']
                with self.subTest(profile=profile['file'], experience_item=idx):
                    self.assertEqual(parsed_company_name, expected_company_name)

    def test_parse_company_linkedin_url(self):
        """Test if company Linkedin url is parsed correctly."""
        for profile in self.profiles:
            for idx, experience_item in enumerate(profile['experience_list']):
                parsed_company_linkedin_url = parse_company_linkedin_url(experience_item)
                expected_company_linkedin_url = profile['data'][idx]['company_linkedin_url']
                with self.subTest(profile=profile['file'], experience_item=idx):
                    self.assertEqual(parsed_company_linkedin_url, expected_company_linkedin_url)

    def test_parse_role(self):
        """Test if role is parsed correctly."""
        for profile in self.profiles:
            for idx, experience_item in enumerate(profile['experience_list']):
                parsed_role = parse_role(experience_item)
                expected_role = profile['data'][idx]['role']
                with self.subTest(profile=profile['file'], experience_item=idx):
                    self.assertEqual(parsed_role, expected_role)

    def test_parse_location(self):
        """Test if location is parsed correctly."""
        for profile in self.profiles:
            for idx, experience_item in enumerate(profile['experience_list']):
                parsed_location = parse_location(experience_item)
                expected_location = profile['data'][idx]['location']
                with self.subTest(profile=profile['file'], experience_item=idx):
                    self.assertEqual(parsed_location, expected_location)

    def test_parse_start_end_date(self):
        """Test if start and end date are parsed correctly."""
        for profile in self.profiles:
            for idx, experience_item in enumerate(profile['experience_list']):
                parsed_start_date, parsed_end_date = parse_start_end_date(experience_item)
                expected_start_date = profile['data'][idx]['start_date']
                expected_end_date = profile['data'][idx]['end_date']
                with self.subTest(profile=profile['file'], experience_item=idx):
                    self.assertEqual(parsed_start_date, expected_start_date)
                    self.assertEqual(parsed_end_date, expected_end_date)

    def test_parse_description(self):
        """Test if description is parsed correctly."""
        for profile in self.profiles:
            for idx, experience_item in enumerate(profile['experience_list']):
                parsed_description = parse_description(experience_item)
                expected_description = profile['data'][idx]['description']
                with self.subTest(profile=profile['file'], experience_item=idx):
                    self.assertEqual(parsed_description, expected_description)

    def test_extract_experience_list(self):
        """Test if all person info is parsed and structured in a dictionary."""
        for profile in self.profiles:
            extracted_experience_list = extract_experience_list(profile['page_source'])
            expected_experience_list = profile['data']

            with self.subTest(profile=profile['file']):
                self.assertEqual(extracted_experience_list, expected_experience_list)

if __name__ == '__main__':
    unittest.main(testRunner=CustomTestRunner())
