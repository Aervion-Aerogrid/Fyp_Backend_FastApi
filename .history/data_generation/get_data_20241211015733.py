import requests
from datetime import datetime, timedelta
import urllib3
import time
import re
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_and_process_synop12_file():
    current_time = datetime.utcnow()
    hour = (current_time.hour // 3) * 3
    adjusted_time = current_time.replace(hour=hour, minute=0, second=0, microsecond=0)
    base_urls = [
        "https://www.pmdnmcc.net/websites/RealTime/Data/",
        "http://www.pmdnmcc.net/websites/RealTime/Data/"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }
    file_found = False
    downloaded_file_path = None

    while not file_found:
        formatted_time = adjusted_time.strftime("%Y%m%d%H")
        file_name = f"{formatted_time}syn.txt"
        
        for base_url in base_urls:
            url = f"{base_url}{file_name}"
            try:
                print(f"Attempting to download: {file_name} from {url}")
                response = requests.get(url, headers=headers, timeout=10, verify=False)
                response.raise_for_status()
                
                downloaded_file_path = file_name
                with open(file_name, "wb") as file:
                    file.write(response.content)
                print(f"File downloaded and saved as {file_name}")
                file_found = True
                break
            
            except requests.exceptions.RequestException as e:
                print(f"Failed to download from {url}: {e}")
        
        if not file_found:
            print(f"File not found for {file_name} on all servers, trying the previous 3-hour interval...")
            adjusted_time -= timedelta(hours=3)
            time.sleep(3)  # Delay to avoid triggering rate limits
            if adjusted_time < current_time - timedelta(days=2):
                print("No file found within the last 2 days. Exiting...")
                return

    # If a file was downloaded, filter and process it
    if downloaded_file_path:
        filter_and_process_weather_data(downloaded_file_path)


def filter_and_process_weather_data(file_path):
    # Filter relevant lines starting with a 5-digit number
    filtered_file_path = f"filtered_{file_path}"
    with open(file_path, 'r') as infile, open(filtered_file_path, 'w') as outfile:
        for line in infile:
            # Keep lines starting with a 5-digit number and exclude lines containing characters other than digits and '/'
            if line.strip()[:5].isdigit() and not re.search(r'[^0-9/ =%RH]', line.strip()):
                outfile.write(line)
    print(f"Filtered data saved to {filtered_file_path}")

    # Now process the filtered file
    with open(filtered_file_path, 'r') as infile:
        synop_batch = infile.readlines()
    
    # Process the synop data with the provided logic
    processed_synop_batch = process_synop_batch(synop_batch)
    
    # Ensure the directory exists before saving the processed file
    final_dir = os.path.abspath("../assets")
    os.makedirs(final_dir, exist_ok=True)
    final_file_path = os.path.join(final_dir, "synop_data.txt")
    
    # Save the processed data to `synop_data.txt`, overwriting existing content
    with open(final_file_path, 'w') as outfile:
        for line in processed_synop_batch:
            outfile.write(line + "\n")
    
    print(f"Processed data saved to {final_file_path}")
    
    # Optionally delete the original and filtered files
    os.remove(file_path)
    os.remove(filtered_file_path)
    print(f"Unfiltered and filtered files removed.")


def find_missing_groups(strings):
    # Extract the first digit from each string to determine the groups present
    present_groups = {int(s[0]) for s in strings if s.isdigit() and len(s) >= 5}
    
    # Find the missing groups (1 to 9)
    all_groups = set(range(1, 10))
    missing_groups = all_groups - present_groups

    # Generate the missing strings by multiplying the group number by 10000
    missing_strings = [f"{group}////" for group in sorted(missing_groups)]
    
    # Combine the original strings with the missing strings and sort them
    complete_list = sorted(strings + missing_strings)

    return complete_list

def process_synop_batch(synop_batch):
    complete_batches = []
    seen_rows = set()  # Set to track unique rows
    
    for synop in synop_batch:
        # Split the row into parts
        parts = synop.split()
        
        # Skip rows with more than 13 items
        if len(parts) > 13:
            continue
        
        if len(parts) >= 4:
            # Remove any strings containing '/'
            filtered_parts = [part for part in parts if '/' not in part]
            
            # Find and remove everything from '333' onwards including '333'
            if '333' in filtered_parts:
                end_index = filtered_parts.index('333')
                relevant_data = filtered_parts[3:end_index]  # Get data from the fourth position to before '333'
            else:
                relevant_data = filtered_parts[3:]
            
            # Remove any numbers with 3 or 4 digits
            relevant_data = [num for num in relevant_data if not (len(num) == 3 or len(num) == 4)]
            
            # Remove any numbers greater than 5 digits
            relevant_data = [num for num in relevant_data if len(num) <= 5]
            
            # Find and add missing numbers
            complete_list = find_missing_groups(relevant_data)
            
            # Extract and clean the last value (humidity)
            humidity = parts[-1]
            cleaned_humidity = re.sub(r'\D', '', humidity)
            
            if int(cleaned_humidity) > 99:
                cleaned_humidity = '//'
            
            # Join the completed list and add the other data back, including cleaned humidity
            completed_synop = " ".join(filtered_parts[:3] + complete_list) + " " + cleaned_humidity
            
            # Add to the result only if it's not a duplicate
            if completed_synop not in seen_rows:
                complete_batches.append(completed_synop)
                seen_rows.add(completed_synop)  # Mark this row as seen
        else:
            # Add the unprocessed row if it's not a duplicate
            if synop not in seen_rows:
                complete_batches.append(synop)
                seen_rows.add(synop)  # Mark this row as seen
    
    return complete_batches


# Call the function
download_and_process_synop12_file()
