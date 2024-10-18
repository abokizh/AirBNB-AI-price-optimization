from web_parser import Parser
import json
import csv

def create_csv(data):
    # Flatten the data and prepare for CSV
    flattened_data = []
    for item in data:
        features = item['features']
        flattened_data.append({
            'id': item["id"],
            'guests': features.get('guests') or "N/A",  # Handle different keys
            'rooms': features.get('bedrooms') or features.get('bedroom') or 0,  # Handle different keys
            'beds': features.get('beds') or features.get('bed') or 0,
            'baths': features.get('baths') or features.get('bath') or 0,
            'price': item.get('price') or "N/A",
            'booked': item.get('booked') or "N/A",
            'available': item.get('available') or "N/A"
        })

    # Define CSV file name
    csv_file = 'state_florida_data.csv'

    # Writing to CSV file
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=flattened_data[0].keys())
        writer.writeheader()
        writer.writerows(flattened_data)

def main():

    parser = Parser()
    URLs = parser.parse_links()

    print(len(URLs))
    for i, URL in enumerate(URLs):
        URL = URL.split('?')
        URLs[i] = URL[0]+"?check_in=2025-01-21&check_out=2025-01-23"
    URLs = set(URLs)
    print(len(URLs))
    parser = Parser(URLs)
    data = parser.run()
    print(data)
    create_csv(data)

main()