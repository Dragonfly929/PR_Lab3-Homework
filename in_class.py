import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json


def extract_product_type(start_url):
    parsed_url = urlparse(start_url)
    path_parts = parsed_url.path.split('/')
    product_type = None
    for part in reversed(path_parts):
        if part.lower() != "or":
            product_type = part
            break
    return product_type


def is_booster(link):
    return 'booster' not in link.lower()


def crawl_product_urls(start_url, max_pages, parsed_product_urls=None):
    if parsed_product_urls is None:
        parsed_product_urls = []

    product_type = extract_product_type(start_url)

    if not product_type:
        print("Product type not found in the URL.")
        return parsed_product_urls

    parsed_pages = set()

    page_number = 1

    while page_number <= max_pages:
        current_url = f"{start_url}?page={page_number}"

        try:
            response = requests.get(current_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                product_links = soup.find_all('a', class_='js-item-ad', href=True)
                for link in product_links:
                    absolute_path = urljoin(current_url, link['href'])
                    if is_booster(absolute_path):
                        parsed_product_urls.append(absolute_path)

                parsed_pages.add(current_url)

                page_number += 1

            else:
                print(f"Error while processing {current_url}: {response.status_code}")
                break

        except Exception as e:
            print(f"Error while processing {current_url}: {e}")
            break

    return parsed_product_urls, parsed_pages


def save_to_json(parsed_product_urls, filename):
    with open(filename, 'w') as json_file:
        json.dump(parsed_product_urls, json_file, ensure_ascii=False, indent=4)


start_url = "https://999.md/ro/list/musical-instruments/guitars"
max_pages = 1  # adjust the maximum number of pages to crawl as needed

parsed_product_urls, parsed_pages = crawl_product_urls(start_url, max_pages)

save_to_json(parsed_product_urls, "parsed_product_urls.json")


print("Extracted Product URLs:")
for url in parsed_product_urls:
    print(url)

print("\nParsed Page URLs:")
for page_url in parsed_pages:
    print(page_url)
