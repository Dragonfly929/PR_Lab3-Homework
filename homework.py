import requests
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor

from in_class import parsed_product_urls


# Function to extract product details from a product URL
def extract_product_details(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            product_details = {}

            # Extract Name
            name_element = soup.find('h1', itemprop='name')
            product_details['Name'] = name_element.text.strip() if name_element else ''

            # Extract Owner
            owner_element = soup.find('a', class_='adPage__aside__stats__owner__login')
            product_details['Owner'] = owner_element.text.strip() if owner_element else ''

            # Extract Description
            description_element = soup.find('div', itemprop='description')
            product_details['Description'] = description_element.text.strip() if description_element else ''

            # Extract Characteristics
            characteristics_element = soup.find('div', class_='adPage__content__features')
            if characteristics_element:
                characteristics_list = characteristics_element.find_all('li', itemprop='additionalProperty')
                product_details['Characteristics'] = {}
                for char in characteristics_list:
                    key_element = char.find('span', class_='adPage__content__features__key')
                    value_element = char.find('span', class_='adPage__content__features__value')
                    if key_element and value_element:
                        key = key_element.text.strip()
                        value = value_element.text.strip()
                        product_details['Characteristics'][key] = value

            # Extract Price
            price_element = soup.find('li', class_='adPage__content__price-feature__prices__price is-main')
            if price_element:
                currency_element = price_element.find('span', class_='adPage__content__price-feature__prices__price__currency')
                value_element = price_element.find('span', class_='adPage__content__price-feature__prices__price__value')
                if currency_element and value_element:
                    currency = currency_element.text.strip()
                    value = value_element.text.strip()
                    product_details['Price'] = {currency: value}

            return product_details

    except Exception as e:
        print(f"Error while processing {url}: {e}")
        return None

# Function to save product details to a JSON file
def save_product_details_to_json(product_details, filename):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(product_details, json_file, ensure_ascii=False, indent=4)

# List to store product details
product_details_list = []

# Function to scrape product details for a batch of URLs
def scrape_batch_of_urls(urls):
    for url in urls:
        product_details = extract_product_details(url)
        if product_details:
            product_details_list.append(product_details)

# Number of threads for concurrent scraping (adjust as needed)
num_threads = 4

# Split the URLs into batches for concurrent processing
url_batches = [parsed_product_urls[i:i + num_threads] for i in range(0, len(parsed_product_urls), num_threads)]

# Create a ThreadPoolExecutor for concurrent scraping
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    executor.map(scrape_batch_of_urls, url_batches)

# Save the extracted product details to a JSON file
save_product_details_to_json(product_details_list, "product_details.json")

print("Scraping completed and data saved to product_details.json")
