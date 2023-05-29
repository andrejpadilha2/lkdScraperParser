import pandas as pd
import random

# Read the CSV file into a DataFrame
df = pd.read_csv('people/name_variations.csv', sep=';')
print(df)

# Get unique 'name_id' values in the original order
unique_name_ids = df['name_id'].unique()

# Shuffle the 'name_id' values
random.shuffle(unique_name_ids)

# Create a mapping dictionary for the shuffled 'name_id' values
name_id_mapping = {old_id: new_id for old_id, new_id in zip(df['name_id'].unique(), unique_name_ids)}

# Apply the shuffled 'name_id' values to the DataFrame
df['name_id'] = df['name_id'].map(name_id_mapping)

# Sort the DataFrame by 'uid' to maintain the order
df = df.sort_values('uid').reset_index(drop=True)

# Print the shuffled DataFrame
print(df)
