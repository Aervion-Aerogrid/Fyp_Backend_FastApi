import pandas as pd
import os

def split_weather_data_by_title():
    # Load the existing weather_data.csv from the 'assets' folder
    file_path = os.path.join('assets', 'weather_data.csv')
    
    if os.path.exists(file_path):
        # Read the CSV into a DataFrame
        df = pd.read_csv(file_path)

        # Ensure there's data to process
        if not df.empty:
            previous_title = None
            last_row_of_city = None

            # List to store the last row of each city for final CSV
            final_data = []

            # Iterate through the DataFrame and split the data by 'title' (city)
            for _, row in df.iterrows():
                title = row['title']  # Get the city title

                # If the title changes and we have a previous row to store
                if previous_title != title:
                    if last_row_of_city is not None:
                        # Store the last row of the previous city
                        final_data.append(last_row_of_city)
                    
                    # Update the last row for the new city
                    last_row_of_city = row
                    previous_title = title
                else:
                    # Update the last row for the same city
                    last_row_of_city = row

            # Add the last row of the final city after the loop
            if last_row_of_city is not None:
                final_data.append(last_row_of_city)

            # Create a DataFrame from the final data (which contains only the last row of each city)
            final_df = pd.DataFrame(final_data)

            # Define the path where the final data will be saved
            final_file_path = os.path.join('assets', 'final_data.csv')

            # Save the final data to 'final_data.csv'
            final_df.to_csv(final_file_path, index=False)
            print(f"Final data saved to {final_file_path}")

        else:
            print("The weather data CSV is empty.")
    else:
        print("No weather data file found.")



