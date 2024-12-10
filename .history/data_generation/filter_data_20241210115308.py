import pandas as pd
import os 
# Load the weather_data.csv file
weather_data = pd.read_csv('assets/weather_data.csv')

# Load the station_list.csv file with proper encoding
station_list = pd.read_csv('assets/station_list.csv', encoding='latin1')  # Adjust encoding to match your file

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
        "Wind_speed",
        "Wind_direction",
    ]
]

# Directory where the CSV will be saved
assets_dir = os.path.join(os.getcwd(), 'assets')

# Ensure the directory exists
os.makedirs(assets_dir, exist_ok=True)

# Full path for the output CSV file
csv_file_path = os.path.join(assets_dir, 'station.csv')

# Save the DataFrame to CSV
output_data.to_csv(csv_file_path, index=False, encoding='utf-8')

print("The station.csv file has been created successfully.")
