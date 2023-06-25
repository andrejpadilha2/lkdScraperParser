import unittest
from pathlib import Path
import json
from bs4 import BeautifulSoup

from ...parser.person import extract_person_info, get_identification_card, parse_about, parse_connections, parse_followers, parse_headline, parse_location, parse_linkedin_name

class CustomTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.write('OK\n')
        self.stream.write(f'Success: {str(test)} tested {test.num_profiles_tested()} profiles\n')
        self.stream.flush()

class CustomTestRunner(unittest.TextTestRunner):
    resultclass = CustomTestResult

class TestExtractPersonInfo(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.maxDiff = None
        self.test_data_path = Path(__file__).resolve().parent / 'test_data'
        expected_data_file = self.test_data_path / 'expected_data' / 'expected_person_data.json'

        with open(expected_data_file, 'r') as f:
            expected_data = json.load(f)
            self.profiles = expected_data['profiles']

        # load html content and parsed identification_card during setup
        for profile in self.profiles:
            html_path = self.test_data_path / 'input_data' / profile['file']
            with open(html_path, "r") as f:
                page_source = f.read()
            soup = BeautifulSoup(page_source, 'html.parser')
            profile['identification_card'] = get_identification_card(soup)
            profile['soup'] = soup
            profile['page_source'] = page_source

    def num_profiles_tested(self):
        return len(self.profiles)

    def test_parse_linkedin_name(self):
        """Test if name is parsed correctly."""
        for profile in self.profiles:
            parsed_name = parse_linkedin_name(profile['identification_card'])
            expected_name = profile['data']['linkedin_name']
            with self.subTest(profile=profile['file']):
                self.assertEqual(parsed_name, expected_name)

    def test_parse_headline(self):
        """Test if headline is parsed correctly."""
        for profile in self.profiles:
            parsed_headline = parse_headline(profile['identification_card'])
            expected_headline = profile['data']['headline']
            with self.subTest(profile=profile['file']):
                self.assertEqual(parsed_headline, expected_headline)

    def test_parse_location(self):
        """Test if location is parsed correctly."""
        for profile in self.profiles:
            parsed_location = parse_location(profile['identification_card'])
            expected_location = profile['data']['location']
            with self.subTest(profile=profile['file']):
                self.assertEqual(parsed_location, expected_location)

    def test_parse_followers(self):
        """Test if followers are parsed correctly."""
        for profile in self.profiles:
            parsed_followers = parse_followers(profile['identification_card'])
            expected_followers = profile['data']['followers']
            with self.subTest(profile=profile['file']):
                self.assertEqual(parsed_followers, expected_followers)

    def test_parse_connections(self):
        """Test if connections are parsed correctly."""
        for profile in self.profiles:
            parsed_connections = parse_connections(profile['identification_card'])
            expected_connections = profile['data']['connections']
            with self.subTest(profile=profile['file']):
                self.assertEqual(parsed_connections, expected_connections)

    def test_parse_about(self):
        """Test if about section is parsed correctly."""
        for profile in self.profiles:
            parsed_about = parse_about(profile['soup'])
            expected_about = profile['data']['about']
            with self.subTest(profile=profile['file']):
                self.assertEqual(parsed_about, expected_about)
    
    def test_extract_person_info(self):
        """Test if all person info is parsed and structured in a dictionary."""
        for profile in self.profiles:
            extracted_person_info = extract_person_info(profile['page_source'])
            expected_person_info = profile['data']
            with self.subTest(profile=profile['file']):
                self.assertEqual(extracted_person_info, expected_person_info)

if __name__ == '__main__':
    unittest.main(testRunner=CustomTestRunner())
