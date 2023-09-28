import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json

# Function to extract the product type
def extract_product_type(start_url):
    parsed_url = urlparse(start_url)
    path_parts = parsed_url.path.split('/')
    product_type = None
    for part in reversed(path_parts):
        if part.lower() != "or":
            product_type = part
            break
    return product_type

# Function to determine if a URL is a booster
def is_booster(link):
    return 'booster' not in link.lower()

# Function to crawl product URLs and extract individual product URLs
def crawl_product_urls(start_url, max_pages, parsed_product_urls=None):
    if parsed_product_urls is None:
        parsed_product_urls = []

    product_type = extract_product_type(start_url)

    if not product_type:
        print("Product type not found in the URL.")
        return parsed_product_urls

    parsed_pages = set()  # Set to store visited page URLs

    page_number = 1

    while page_number <= max_pages:
        current_url = f"{start_url}?page={page_number}"

        try:
            response = requests.get(current_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract product links and filter out boosters
                product_links = soup.find_all('a', class_='js-item-ad', href=True)
                for link in product_links:
                    absolute_path = urljoin(current_url, link['href'])
                    if is_booster(absolute_path):
                        parsed_product_urls.append(absolute_path)

                parsed_pages.add(current_url)  # Add the parsed page URL to the set

                page_number += 1

            else:
                print(f"Error while processing {current_url}: {response.status_code}")
                break  # Exit the loop if there's an error

        except Exception as e:
            print(f"Error while processing {current_url}: {e}")
            break  # Exit the loop if there's an error

    return parsed_product_urls, parsed_pages  # Return both the product URLs and parsed page URLs

# Function to save parsed product URLs to a JSON file
def save_to_json(parsed_product_urls, filename):
    with open(filename, 'w') as json_file:
        json.dump(parsed_product_urls, json_file, ensure_ascii=False, indent=4)

# Example usage with a single start URL:
start_url = "https://999.md/ro/list/musical-instruments/guitars"
max_pages = 1  # Adjust the maximum number of pages to crawl as needed

# List to store the URLs of individual products
parsed_product_urls, parsed_pages = crawl_product_urls(start_url, max_pages)

# Save the extracted product URLs to a JSON file
save_to_json(parsed_product_urls, "parsed_product_urls.json")

# Print the extracted product URLs
print("Extracted Product URLs:")
for url in parsed_product_urls:
    print(url)

# Print the URLs of the pages that were parsed
print("\nParsed Page URLs:")
for page_url in parsed_pages:
    print(page_url)
