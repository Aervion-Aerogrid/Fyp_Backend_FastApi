import pandas as pd
import os

def split_weather_data_by_title():
    # Load the existing weather_data.csv
    
    file_path = os.path.join('assets', 'weather_data.csv')
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)

        # Ensure there's data to process
        if not df.empty:
            previous_title = None
            city_data = []

            # List to store all the city-specific rows for final CSV
            final_data = []

            # Iterate through the DataFrame and split the data by 'title' (city)
            for _, row in df.iterrows():
                title = row['title']

                # If the title changes, save the previous city's data to final_data
                if previous_title != title:
                    if city_data:
                        final_data.append(city_data)
                    
                    # Reset for the new city
                    city_data = [row]
                    previous_title = title
                else:
                    # Append the row to the current city's data
                    city_data.append(row)

            # Add the last city data after the loop
            if city_data:
                final_data.append(city_data)

            # Flatten the list of lists into a single list of rows
            final_data_flat = [row for city in final_data for row in city]

            # Create DataFrame and save to final_data.csv
            final_df = pd.DataFrame(final_data_flat)
            final_file_path = os.path.join('assets', 'final_data.csv')
            final_df.to_csv(final_file_path, index=False)
            print(f"Final data saved to {final_file_path}")

        else:
            print("The weather data CSV is empty.")
    else:
        print("No weather data file found.")


