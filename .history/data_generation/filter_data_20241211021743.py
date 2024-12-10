import pandas as pd
import os
# Load the weather_data.csv file
# Define the base directory
base_dir = os.getcwd()  # Get current working directory
assets_dir = os.path.join(base_dir, 'assets')

# Define file paths
weather_data_path = os.path.join(assets_dir, 'weather_data.csv')
station_list_path = os.path.join(assets_dir, 'station_list.csv')

# Load the files
weather_data = pd.read_csv(weather_data_path)
station_list = pd.read_csv(station_list_path, encoding='latin1')



# Clean up column names by stripping spaces
station_list.columns = station_list.columns.str.strip()

# Rename columns for consistency
station_list.rename(columns={"Index No.": "Station_ID"}, inplace=True)

# Clean up special characters in Station_ID and Title columns
station_list['Station_ID'] = station_list['Station_ID'].astype(str).str.strip()  # Remove leading/trailing spaces
station_list['Title'] = station_list['Title'].astype(str).str.replace(r'\u00a0', ' ', regex=True)  # Remove non-breaking spaces
station_list['Title'] = station_list['Title'].str.strip()  # Remove leading/trailing spaces

# Ensure Station_ID columns are the same data type
weather_data['Station_ID'] = weather_data['Station_ID'].astype(str).str.strip()
station_list['Station_ID'] = station_list['Station_ID'].astype(str)

# Drop duplicate Station_IDs from station_list and weather_data
station_list = station_list.drop_duplicates(subset='Station_ID')
weather_data = weather_data.drop_duplicates(subset='Station_ID')

# Merge the data on the Station_ID column
merged_data = pd.merge(
    weather_data,
    station_list,
    on="Station_ID",
    how="inner"  # Inner join to include only matching rows
)

# Calculate precipitation rate (amount / duration), handle NaN gracefully
merged_data['Precipitation_rate'] = merged_data['Precipitation_amount'] / (merged_data['Precipitation_duration'] * 100)
merged_data['Precipitation_rate'] = merged_data['Precipitation_rate'].fillna(0)  # Replace NaN with 0

# Combine Wind Speed and Direction into a new column
merged_data['Wind_combined'] = merged_data['Wind_speed'].astype(str) + "_" + merged_data['Wind_direction'].astype(str)

# Select the required columns
output_data = merged_data[
    [
        "Station_ID",
        "Title",
        "Latitude",
        "Longitude",
        "Temperature",
        "Station_pressure",
        "Sea_level_pressure",
        "Humidity",
        "High_clouds",
        "Low_clouds",
        "Mid_clouds",
        "Wind_combined",
        "Sky_cover",
        "Dew_point",
        "Wind_speed",
        "Wind_direction",
        "Precipitation_rate"
    ]
]

# Directory where the CSV will be saved
assets_dir = os.path.join(os.getcwd(), 'assets')

# Ensure the directory exists
os.makedirs(assets_dir, exist_ok=True)

# Full path for the output CSV file
csv_file_path = os.path.join(assets_dir, 'station.csv')

# Delete old station.csv if it exists
if os.path.exists(csv_file_path):
    os.remove(csv_file_path)

# Save the DataFrame to CSV
output_data.to_csv(csv_file_path, index=False, encoding='utf-8')

print(f"The station.csv file has been created successfully at {csv_file_path}.")