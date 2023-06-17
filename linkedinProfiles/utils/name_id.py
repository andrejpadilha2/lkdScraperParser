import csv

from utils.generate_name_variations import generate_name_variations

# Read the names from the file
with open('people/names_list.txt', 'r') as file:
    names = file.readlines()

# Process names, generate name variations add and add unique ID to each NAME
processed_names = []
uid = 0
for name_id, name in enumerate(names):
    name = name.strip()

    # Generate name variations for the current full_name
    name_variations = generate_name_variations(name)
    # Append each name variation to the output rows
    for name_variation in name_variations:
        processed_names.append(f'{uid},{name_id},{name},{name_variation}')
        uid += 1

# Save processed names as a CSV file
with open('people/name_variations.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(['uid', 'name_id', 'full_name', 'name_variation'])
    for name in processed_names:
        writer.writerow(name.split(','))  # Splitting uid and full_name