from bs4 import BeautifulSoup

def extract_person_info(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')

    identification_list = soup.find('section', class_='top-card-layout')

    name_item = identification_list.find('h1', class_='top-card-layout__title')
    name = name_item.text.strip() if name_item else None

    headline_item = identification_list.find('h2', class_='top-card-layout__headline')
    headline = headline_item.text.strip() if headline_item else None

    location_item = identification_list.find('div', class_='top-card__subline-item')
    location = location_item.text.strip() if location_item else None

    followers_item = identification_list.find('span', class_='top-card__subline-item')
    followers = followers_item.text.strip() if followers_item else None

    connections_item = identification_list.find('span', class_='top-card__subline-item--bullet')
    connections = connections_item.text.strip() if connections_item else None

    about_item = soup.find('section', class_='summary')
    about = about_item.find('div', class_='core-section-container__content').text.strip() if about_item else None

    person_info = {
        'linkedin_name': name,
        'headline': headline,
        'location': location,
        'followers': followers,
        'connections': connections,
        'about': about
    }

    return person_info

