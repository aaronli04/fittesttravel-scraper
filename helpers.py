import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

def get_links(url):
    urls = []

    response = requests.get(url)
    if response.status_code == 200:
        xml_content = response.text

        ns = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}

        root = ET.fromstring(xml_content)
        for loc_element in root.findall(".//sitemap:loc", namespaces=ns):
            if loc_element is not None:
                link = loc_element.text
                if 'best-hotel' in link.lower():
                    urls.append(link)

    return urls


def extract_soup_with_selenium(link):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    driver.implicitly_wait(2)

    try:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup
    finally:
        driver.quit()


def get_hotel_data(list_link):
    hotels = []
    hotel_names = []
    hotel_descriptions = []
    hotel_ratings = []

    soup = extract_soup_with_selenium(list_link)
    
    rating_elems = soup.find_all('div', class_='sqs-block code-block sqs-block-code')
    if rating_elems and len(rating_elems) > 0:
        for rating_elem in rating_elems:
            stars_elems = rating_elem.find_all('span', class_='fa fa-star checked')
            stars = len(stars_elems)
            hotel_ratings.append(stars)

    block_elems = soup.find_all('div', 'sqs-html-content')
    if block_elems and len(block_elems) > 0:
        for block_elem in block_elems:
            name_elem = block_elem.find('h2')
            description_elems = block_elem.find_all('p')

            if description_elems and len(description_elems) > 0:
                description = ''
                for elem in description_elems:
                    description += elem.text.strip()
                hotel_descriptions.append(description.strip())

            if name_elem:
                name = name_elem.text.strip()
                hotel_names.append(name)

    if hotel_descriptions and (len(hotel_descriptions) > 10):
        hotel_descriptions.pop(0)

    counter = 0
    for hotel_description in hotel_descriptions:
        if 'These are the best hotel gyms'  in hotel_description:
            continue

        hotel = {
            'name': '',
            'description': '',
            'rating': 0
        }

        for hotel_name in hotel_names:
            if hotel_name in hotel_description:
                counter += 1
                hotel['name'] = hotel_name
                hotel['description'] = hotel_description

                if counter < len(hotel_ratings):
                    hotel['rating'] = hotel_ratings[counter]

                hotels.append(hotel)
                continue

    return hotels
