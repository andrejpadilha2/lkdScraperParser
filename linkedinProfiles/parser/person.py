from bs4 import BeautifulSoup

def parse_linkedin_name(identification_card):
    name_item = identification_card.find('h1', class_='top-card-layout__title')
    return name_item.text.strip() if name_item else ""

def parse_headline(identification_card):
    headline_item = identification_card.find('h2', class_='top-card-layout__headline')
    return headline_item.text.strip() if headline_item else ""

def parse_location(identification_card):
    location_item = identification_card.find('div', class_='top-card__subline-item')
    return location_item.text.strip() if location_item else ""

def parse_followers(identification_card):
    followers_item = identification_card.find('span', class_='top-card__subline-item')
    return followers_item.text.strip() if followers_item else ""

def parse_connections(identification_card):
    connections_item = identification_card.find('span', class_='top-card__subline-item--bullet')
    return connections_item.text.strip() if connections_item else ""

def parse_about(soup):
    about_item = soup.find('section', class_='summary')
    return about_item.find('div', class_='core-section-container__content').text.strip() if about_item else ""

def get_identification_card(soup):
    return soup.find('section', class_='top-card-layout')

def extract_person_info(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')

    identification_card = get_identification_card(soup)

    name = parse_linkedin_name(identification_card)
    headline = parse_headline(identification_card)
    location = parse_location(identification_card)
    followers = parse_followers(identification_card)
    connections = parse_connections(identification_card)
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

