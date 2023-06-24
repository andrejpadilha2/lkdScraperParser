from bs4 import BeautifulSoup

def parse_linkedin_name(identification_list):
    name_item = identification_list.find('h1', class_='top-card-layout__title')
    return name_item.text.strip() if name_item else ""

def parse_headline(identification_list):
    headline_item = identification_list.find('h2', class_='top-card-layout__headline')
    return headline_item.text.strip() if headline_item else ""

def parse_location(identification_list):
    location_item = identification_list.find('div', class_='top-card__subline-item')
    return location_item.text.strip() if location_item else ""

def parse_followers(identification_list):
    followers_item = identification_list.find('span', class_='top-card__subline-item')
    return followers_item.text.strip() if followers_item else ""

def parse_connections(identification_list):
    connections_item = identification_list.find('span', class_='top-card__subline-item--bullet')
    return connections_item.text.strip() if connections_item else ""

def parse_about(soup):
    about_item = soup.find('section', class_='summary')
    return about_item.find('div', class_='core-section-container__content').text.strip() if about_item else ""

def get_identification_list(soup):
    return soup.find('section', class_='top-card-layout')

def extract_person_info(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')

    identification_list = get_identification_list(soup)

    name = parse_linkedin_name(identification_list)
    headline = parse_headline(identification_list)
    location = parse_location(identification_list)
    followers = parse_followers(identification_list)
    connections = parse_connections(identification_list)
    about = parse_about(soup)
    
    person_info = {
        'linkedin_name': name,
        'headline': headline,
        'location': location,
        'followers': followers,
        'connections': connections,
        'about': about
    }

    return person_info

