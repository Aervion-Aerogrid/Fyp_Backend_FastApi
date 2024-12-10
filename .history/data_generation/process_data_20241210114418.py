import csv

# Helper function to safely convert strings to integers, handling non-numeric values
def safe_int(value):
    """Try to convert a value to an integer, returning None if it fails."""
    try:
        return int(value)
    except ValueError:
        return None  # Return None for invalid values

def process_synop_row(token):
    """Process a single row of SYNOP data."""
    # Initialize variables
    station_id = None
    status = None
    value = None
    cloud_range = None
    visibility_range = None

    # Station ID
    station_id = token[0] if token[0] else None

    # Precipitation and Station Type
    precipitation = safe_int(token[1][0])  # Precipitation range (0-4)
    if precipitation is not None:
        if precipitation == 0:
            status = (True, True)
        elif precipitation == 1:
            status = (True, False)
        elif precipitation == 2:
            status = (False, True)
        elif precipitation == 3:
            status = (False, False)
        else:
            status = None

    station_type = safe_int(token[1][1])  # Station type (1-7)
    if 1 <= station_type <= 3:
        value = "Manned"
    else:
        value = "Unmanned"

    # Cloud height range
    cloud_height = safe_int(token[1][2])  # Cloud height range (0-9)
    if cloud_height == 0:
        cloud_range = (0, 150)
    elif cloud_height == 1:
        cloud_range = (150, 300)
    elif cloud_height == 2:
        cloud_range = (300, 600)
    elif cloud_height == 3:
        cloud_range = (600, 1000)
    elif cloud_height == 4:
        cloud_range = (1000, 2000)
    elif cloud_height == 5:
        cloud_range = (2000, 3000)
    elif cloud_height == 6:
        cloud_range = (3000, 5000)
    elif cloud_height == 7:
        cloud_range = (5000, 6000)
    elif cloud_height == 8:
        cloud_range = (6000, 8000)
    elif cloud_height == 9:
        cloud_range = "Above 8000"
    else:
        cloud_range = None

    # Visibility
    visibility = safe_int(token[0][-2:])  # Extract last two digits for visibility
    visibility_range = None
    if visibility == 90:
        visibility_range = (0, 50)
    elif visibility == 91:
        visibility_range = (50, 200)
    elif visibility == 92:
        visibility_range = (200, 500)
    elif visibility == 93:
        visibility_range = (500, 1000)
    elif visibility == 94:
        visibility_range = (1000, 2000)
    elif visibility == 95:
        visibility_range = (2000, 4000)
    elif visibility == 96:
        visibility_range = (4000, 10000)
    elif visibility == 97:
        visibility_range = (10000, 20000)
    elif visibility == 98:
        visibility_range = (20000, 50000)
    elif visibility == 99:
        visibility_range = (50000, float('inf'))  # Use 'inf' for "above"
    
    # Cloud cover, wind speed, and direction
    cloud_cover = safe_int(token[2][0])  # Cloud cover (0-9)
    sky_status = None
    if cloud_cover == 9:
        sky_status = 9
    else:
        sky_status = cloud_cover

    wind_direction = safe_int(token[2][1:3])  # Wind direction (0-36)
    wind_direction *= 10  # Convert to degrees
    wind_speed = safe_int(token[2][3:])  # Wind speed (knots)

    # Temperature (Air and Dew Point)
    air_temperature = None
    dew_point_temperature = None

    if len(token) > 3 and token[3]:
        temperature_sign = safe_int(token[3][1])  # Extract the sign (0 or 1)
        if temperature_sign is not None:
            sign = 1 if temperature_sign == 0 else -1
            air_temperature = safe_int(token[3][2:]) / 10  # Temperature in Celsius
            if air_temperature is not None:
                air_temperature *= sign

    if len(token) > 4 and token[4]:
        dew_point_sign = safe_int(token[4][1])  # Extract the sign (0 or 1)
        if dew_point_sign is not None:
            sign = 1 if dew_point_sign == 0 else -1
            dew_point_temperature = safe_int(token[4][2:]) / 10  # Dew point temperature
            if dew_point_temperature is not None:
                dew_point_temperature *= sign

    # Pressure values (Station and Sea Level)
    pressure_value = safe_int(token[5][1:])  # Station pressure (hPa)
    if pressure_value is not None:
        pressure_value /= 10  # Divide by 10 only if the value is valid
        if pressure_value < 100:
            pressure_value += 1000

    sea_pressure_value = safe_int(token[6][1:])  # Sea level pressure (hPa)
    if sea_pressure_value is not None:
        sea_pressure_value /= 10  # Divide by 10 only if the value is valid
        if sea_pressure_value < 100:
            sea_pressure_value += 1000

    # Rainfall data (Rain amount and Duration)
    rain_amount = None
    rain_duration = None
    if len(token) > 7 and token[7]:
        rain_amount = safe_int(token[7][1:4])  # Rain amount (mm)
        rain_duration = safe_int(token[7][-1])  # Rain duration (in hours)

    # Cloud cover types (Total, Low, Mid, High)
    Total_cloud_cover = None
    low_clouds = None
    mid_clouds = None
    high_clouds = None
    if len(token) > 10 and token[10]:
        if token[10][1] != '/':
            Total_cloud_cover = safe_int(token[10][1])
        if token[10][2] != '/':
            low_clouds = safe_int(token[10][2])
        if token[10][3] != '/':
            mid_clouds = safe_int(token[10][3])
        if token[10][4] != '/':
            high_clouds = safe_int(token[10][-1])
    # Humidity
    humidity = None
    if len(token) > 0:
        last_token = token[-1]
        if last_token.isdigit():
            humidity = safe_int(last_token)
        elif last_token == "//":
            humidity = None  # Disregard //

    # Storing the processed data
    station_data = {
        "Station_ID": station_id,
        "Station_type": value,
        "Temperature": air_temperature,
        "Station_pressure": pressure_value,
        "Sea_level_pressure": sea_pressure_value,
        "Humidity": humidity,
        "High_clouds": high_clouds,
        "Low_clouds": low_clouds,
        "Mid_clouds": mid_clouds,
        "Sky_cover": sky_status,
        "Cloud_height_range": cloud_range,
        "Visibility": visibility_range,
        "Precipitation_status": status,
        "Precipitation_amount": rain_amount,
        "precipitation_duration": rain_duration,
        "Dew_point": dew_point_temperature,
        "Wind_direction": wind_direction,
        "Wind_speed": wind_speed,
        "Total_cloud_cover": Total_cloud_cover, 
    }

    return station_data


def decode_and_save_to_csv(input_file, output_file):
    """Decode SYNOP data from a text file and save the result to a CSV file."""
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Prepare the CSV output file
    with open(output_file, mode='w', newline='') as csv_file:
        fieldnames = ["Station_ID", "Station_type", "Temperature", "Station_pressure", "Sea_level_pressure", "Humidity", 
                      "High_clouds", "Low_clouds", "Mid_clouds", "Wind_direction", "Wind_speed", "Sky_cover", "Cloud_height_range", "Visibility", 
                      "Precipitation_status", "Precipitation_amount", "precipitation_duration", "Dew_point", "Total_cloud_cover"] 
        
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # Process each line in the SYNOP data file
        for line in lines:
            tokens = line.split()  # Tokenize each line
            station_data = process_synop_row(tokens)  # Process the row and get decoded data
            writer.writerow(station_data)  # Write the decoded data to the CSV file


# Run the function to decode the SYNOP data and save it to a CSV file
decode_and_save_to_csv('assets/synop_data.txt', 'assets/weather_data.csv')
