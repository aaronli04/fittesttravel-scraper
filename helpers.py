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

    soup = extract_soup_with_selenium(list_link)
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

    for hotel_description in hotel_descriptions:
        hotel = {
            'name': '',
            'description': ''
        }

        for hotel_name in hotel_names:
            if hotel_name in hotel_description:
                hotel['name'] = hotel_name
                hotel['description'] = hotel_description
                hotels.append(hotel)
                continue

    return hotels
