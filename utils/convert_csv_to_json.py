import csv
import json

def convert_csv_to_json(csv_file, json_file):
    """Convert the US cities CSV to JSON with necessary fields."""
    filtered_data = []

    with open(csv_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            # Extract relevant fields: city, state, lat, lng
            filtered_data.append({
                "city": row['city'],
                "state": row['state_id'],
                "latitude": float(row['lat']),
                "longitude": float(row['lng'])
            })

    # Write to a JSON file
    with open(json_file, 'w') as jsonfile:
        json.dump(filtered_data, jsonfile, indent=4)

# Example usage
if __name__ == "__main__":
    convert_csv_to_json('utils/data/uscities.csv', 'us_cities.json')
