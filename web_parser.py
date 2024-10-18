from lxml import html
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import random
import re
from selenium.common.exceptions import NoSuchElementException
import base64

class Parser:

    links = list()

    def __init__(self, links = []):
        self.links = links

    def parse_links(self):
        URLs = list()

        base_urls = [
            "https://www.airbnb.com/s/Tampa--Florida--United-States/homes?date_picker_type=calendar&checkin=2025-01-21&checkout=2025-01-23",
            "https://www.airbnb.com/s/Miami--Florida--United-States/homes?date_picker_type=calendar&checkin=2025-01-21&checkout=2025-01-23",
            "https://www.airbnb.com/s/Panama-City-Beach--Florida--United-States/homes?date_picker_type=calendar&checkin=2025-01-21&checkout=2025-01-23",
            "https://www.airbnb.com/s/Orlando--Florida--United-States/homes?date_picker_type=calendar&checkin=2025-01-21&checkout=2025-01-23",
            "https://www.airbnb.com/s/Fort-Myers--Florida--United-States/homes?date_picker_type=calendar&checkin=2025-01-21&checkout=2025-01-23",
        ]
        num_pages = 15

        for base_url in base_urls:
            # Loop through pages
            for page in range(num_pages):
                items_offset = page * 18
                cursor_dict = {
                    "section_offset": 0,
                    "items_offset": items_offset,
                    "version": 1
                }
                cursor_json = json.dumps(cursor_dict)
                cursor_base64 = base64.b64encode(cursor_json.encode('utf-8')).decode('utf-8')

                url = base_url+f"&cursor={cursor_base64}"
                # Set up the webdriver (you need a driver like ChromeDriver or GeckoDriver)
                driver = webdriver.Chrome()  # or webdriver.Firefox(), etc.
                # Open the Airbnb page
                driver.get(url)
                # Wait for the dynamic content to load (can use WebDriverWait for better control)
                driver.implicitly_wait(3)
                # Check if an error page is displayed or data is missing
                links = driver.find_elements(By.XPATH, '//div[contains(@data-testid, "card-container")]/a')
                for link in links:
                    URLs.append(link.get_attribute('href'))
                driver.quit()

        return URLs
    
    def get_js_data(self, link):
        # Set up the webdriver (you need a driver like ChromeDriver or GeckoDriver)
        driver = webdriver.Chrome()  # or webdriver.Firefox(), etc.

        id = link.split("/")[-1]

        # Open the Airbnb page
        driver.get(link)

        # Wait for the dynamic content to load (can use WebDriverWait for better control)
        driver.implicitly_wait(2)

        # Check if an error page is displayed or data is missing
        error_elements = driver.find_elements(By.XPATH, '//div[contains(text(), "Oops")]')
        if error_elements:
            raise IndexError("505 Error: Page not available")
        

        # Now you can use XPath to get dynamic elements
        booked = len(driver.find_elements(By.XPATH, '//div[@data-is-day-blocked="true"]'))
        available = len(driver.find_elements(By.XPATH, '//div[@data-is-day-blocked="false"]'))

        features_raw = driver.find_elements(By.XPATH, '//section/div/ol[contains(@class, "dir-ltr")]/li[contains(@class, "dir-ltr")]')
        features = dict()
        for f in features_raw:
            string = f.text.split(" ")
            string = [s for s in string if s not in ['·', '']]

            if len(string) == 1:
                if string[0] == "Studio":
                    features["bedrooms"] == 0
            else:
                (value, feature) = string
                features[feature] = value

        price_raw = driver.find_elements(By.XPATH, '//div[contains(@style, "--pricing-guest-display-price-alignment")]/div/span/div/span[@class and normalize-space(@class) != ""]')
        price = float((price_raw[2].text).replace("$", ""))

        data = {
            "id": id,
            "booked": booked,
            "available": available,
            "features": features,
            "price": price
        }
        # for element in elements:
        #     print(element.text)

        # Close the browser
        driver.quit()

        return data

    def parse(self, link):
        js_data = self.get_js_data(link)

        return js_data

    def run(self):
        data = list()
        
        count = 1
        for l in self.links:
            print(count)
            count += 1
            try:
                data.append(self.parse(l))
            except Exception as e:
                print(f"Error parsing {l}: {e}")  # Print the error message and continue
        return data

# # Save JSON to a file
# with open("data3.json", 'w') as json_file:
#     json.dump(json_data, json_file, indent=4)

# # Loop over the list and write each JSON string to a separate file
# for i, json_str in enumerate(availability):
#     # Check if the string is not empty
#     if json_str.strip():  # Only process non-empty strings
#         try:
#             # Convert JSON string to Python dictionary
#             json_obj = json.loads(json_str)
#             # Create a filename dynamically based on the index
#             filename = f'output_file_{i}.json'
#             # Open the file in write mode
#             with open(filename, 'w') as file:
#                 # Write the dictionary to the file as a JSON string
#                 json.dump(json_obj, file, indent=4)
#             print(f"Successfully wrote {filename}")
#         except json.JSONDecodeError as e:
#             print(f"Skipping invalid JSON string: {json_str} - Error: {e}")