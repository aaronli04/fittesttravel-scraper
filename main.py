import requests
from helpers import get_links, get_hotel_data
import pandas as pd
import concurrent.futures


def scrape_fittesttravel():
    sitemap_url = "https://www.fittesttravel.com/sitemap.xml"
    links = get_links(sitemap_url)

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        nested_results = list(executor.map(get_hotel_data, links))

    results = [item for sublist in nested_results for item in sublist]

    df = pd.DataFrame(results)
    df.to_csv('fittesttravel.csv', index=False)


if __name__ == "__main__":
    scrape_fittesttravel()
