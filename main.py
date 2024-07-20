import os
import requests
from bs4 import BeautifulSoup
import csv
import time  # Import time module for delay between requests

# Function to scrape the main page
def scrape_main_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    else:
        print(f"Failed to retrieve page: {url}")
        return None

# Function to scrape the child page
def scrape_child_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    else:
        print(f"Failed to retrieve page: {url}")
        return None

# Function to parse the main page
def parse_main_page(soup):
    houses = soup.select('div.listing-card')
    for house in houses:
        house_href = house.select_one('div.block h3 > a')['href']
        house_href = f"https://www.buyrentkenya.com{house_href}"
        house_price = house.select_one('div.hidden p a').get_text(strip=True)
        house_location = house.select_one('div.flex p').get_text(strip=True)
        furnished = house.select_one('div.block h3 > a')['href']  # Not sure what this represents, adjust accordingly

        yield {
            'house_href': house_href,
            'house_price': house_price,
            'house_location': house_location,
            'furnished': furnished
        }

# Function to parse the child page
def parse_child_page(soup):
    service_type = soup.select_one('a.text-grey-550:nth-child(1)').get_text(strip=True)
    property_type = soup.select_one('li.items-center:nth-child(3) > a:nth-child(2)').get_text(strip=True)
    num_beds_element = soup.select_one('span[aria-label="bedrooms"]')
    num_beds = num_beds_element.get_text(strip=True) if num_beds_element else None

    return {
        'service_type': service_type,
        'property_type': property_type,
        'num_beds': num_beds
    }

# Main function
def main():
    # URL of the main page
    base_url = "https://www.buyrentkenya.com/houses-for-sale"
    max_pages = 2  # Number of pages to scrape
    results = []  # List to store all results

    for page_number in range(1, max_pages + 1):
        url = f"{base_url}?page={page_number}" if page_number > 1 else base_url
        print(f"Scraping page {page_number}: {url}")

        # Scrape the main page
        main_soup = scrape_main_page(url)   
        if main_soup:
            # Parse the main page
            for house_data in parse_main_page(main_soup):
                house_href = house_data['house_href']

                # Scrape and parse the child page
                child_soup = scrape_child_page(house_href)
                if child_soup:
                    child_data = parse_child_page(child_soup)

                    # Merge data from main and child pages
                    merged_item = {**house_data, **child_data}
                    results.append(merged_item)

        # Delay before next request to avoid overloading the server
        time.sleep(1)

    # Write results to CSV
    home_path = os.path.expanduser("~")
    output_file_path = os.path.join(home_path, "Documents", "house_price_prediction", "buyrent2.csv")
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(output_file_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['house_href','house_price', 'house_location', 'furnished', 'service_type', 'property_type', 'num_beds']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"Data saved to {output_file_path}")


if __name__ == "__main__":
    main()