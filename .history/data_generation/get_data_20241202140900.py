import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import os
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from final_data import split_weather_data_by_title



# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

coordinates = [
    ("Gilgit, Gilgit-Baltistan", (35.920834, 74.308334)),
    ("Ahmedpur East, Bahawalpur", (29.143644, 71.257240)),
    ("Kāmoke, Gujranwala", (31.976515, 74.222015)),
    ("Jacobabad", (28.281891, 68.438171)),
    ("Sahiwal", (30.677717, 73.106812)),
    ("Zafarwal", (32.337006, 74.903336)),
    ("Khanewal", (30.286415, 71.932030)),
    ("Jaranwala, Faisalabad", (31.345394, 73.429810)),
    ("New Mirpur City, Azad Kashmir", (33.148392, 73.751770)),
    ("Multan", (30.181459, 71.492157)),
    ("Nawabshah", (26.244221, 68.410034)),
    ("Dera Ghāzi Khān", (30.032486, 70.640244)),
    ("Larkana", (27.563993, 68.215134)),
    ("Malakwāl", (32.555496, 73.194351)),
    ("Haveli Lakha", (30.448601, 73.697578)),
    ("Jalalpur Pirwala", (29.505283, 71.222084)),
    ("Nowshera", (34.015858, 71.975449)),
    ("Hafizabad", (32.071697, 73.685730)),
    ("Vehāri", (30.045246, 72.348869)),
    ("Okara", (30.808500, 73.459396)),
    ("Attock", (33.768051, 72.360703)),
    ("Abbottābad", (34.168751, 73.221497)),
    ("Qurtaba City", (33.351357, 72.774734)),
    ("Mandi Bahauddin", (32.588169, 73.497345)),
    ("Bahawalpur", (29.395721, 71.683334)),
    ("Karak", (33.115269, 71.095535)),
    ("Muzaffargarh", (30.074377, 71.184654)),
    ("Shikārpur", (27.955648, 68.637672)),
    ("Khairpur", (27.529951, 68.758141)),
    ("Kamoki", (31.975508, 74.223801)),
    ("Sargodha", (32.082466, 72.669128)),
    ("Pattoki", (31.025009, 73.847878)),
    ("Makli", (24.743303, 67.890938)),
    ("Garhi Habibullah", (34.405262, 73.380066)),
    ("Bhalwal", (32.265396, 72.905388)),
    ("Bannu", (32.986111, 70.604164)),
    ("Nankana Sahib", (31.452097, 73.708305)),
    ("Dijkot", (31.217646, 72.997368)),
    ("Sādiqābād", (28.310350, 70.127403)),
    ("Turbat", (26.004168, 63.060555)),
    ("Quetta", (30.183270, 66.996452)),
    ("Gujrat", (32.571144, 74.075005)),
    ("Bahawalpur", (29.418068, 71.670685)),
    ("Sukkur", (27.713926, 68.836899)),
    ("Khanqah Dogran", (31.831667, 73.623055)),
    ("Jhelum", (32.940548, 73.727631)),
    ("Qila Didar Singh", (32.136673, 74.012383)),
    ("Gujranwala", (32.166351, 74.195900)),
    ("Badin", (24.655720, 68.837242)),
    ("Sheikhupura", (31.716661, 73.985023)),
    ("Wah", (33.783184, 72.723076)),
    ("Taunsa", (30.705557, 70.657776)),
    ("Hub", (25.067562, 66.917038)),
    ("Narowal", (32.099476, 74.874733)),
    ("Chichawatni", (30.535133, 72.699539)),
    ("Muzaffarabad", (34.359688, 73.471054)),
    ("Shahdara", (31.621113, 74.282364)),
    ("Lahore", (31.582045, 74.329376)),
    ("Peshawar", (34.025917, 71.560135)),
    ("Thakot", (34.788040, 72.929115)),
    ("Saidu Sharif, Mingora", (34.749271, 72.357063)),
    ("Sanghar", (26.044418, 68.953880)),
    ("Mardan", (34.206123, 72.029800)),
    ("Saddar Town, Karachi", (24.858480, 67.001884)),
    ("Kalabagh", (32.966000, 71.553001)),
    ("Gwadar", (25.126389, 62.322498)),
    ("Pasrūr", (32.265652, 74.669525)),
    ("Mingora", (34.773647, 72.359901)),
    ("Kasur", (31.118793, 74.463272)),
    ("Kaku, Lahore", (31.721159, 74.273758)),
    ("Faisalabad", (31.418715, 73.079109)),
    ("Thatta", (24.749731, 67.911636)),
    ("Chowk Azam", (30.970655, 71.212303)),
    ("Layyah", (30.964750, 70.939934)),
    ("Mīrpur Khās", (25.529104, 69.013573)),
    ("Rawalpindi", (33.626057, 73.071442)),
    ("Daska", (32.338779, 74.353065)),
    ("Bhakkar", (31.633333, 71.066666)),
    ("Ārifwāla", (30.297859, 73.058235)),
    ("Karachi", (24.860966, 66.990501)),
    ("Dullewala", (31.839722, 71.430000)),
    ("Shahpur", (32.286613, 72.430252)),
    ("Kot Addu", (30.466667, 70.966667)),
    ("Jhang", (31.278046, 72.311760)),
    ("Jamshoro", (25.416868, 68.274307)),
    ("Islamabad", (33.738045, 73.084488)),
    ("Chunian", (30.963774, 73.977982)),
    ("Sialkot", (32.497223, 74.536110)),
    ("Dera Ismail Khan", (31.831482, 70.911598)),
    ("Dalbandin", (28.883612, 64.416061)),
    ("Chagai", (29.297670, 64.706734)),
    ("Khushāb", (32.294445, 72.349724))
]

# Function to fetch and process weather data for each coordinate
def fetch_weather_data():
    all_data = []

    for city, (lat, lon) in coordinates:
        # Define the request parameters for each location
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": "2024-08-16",
            "end_date": "2024-08-30",
            "hourly": [
                "temperature_2m", "relative_humidity_2m", "dew_point_2m",
                "precipitation", "surface_pressure", "cloud_cover",
                "wind_speed_10m", "wind_direction_10m"
            ]
        }

        # Fetch data from the Open Meteo API
        try:
            responses = openmeteo.weather_api(url, params=params)
            
            # Iterate over each response (typically only one in this case)
            for response in responses:
                
                # Process hourly data for the current location
                hourly = response.Hourly()
                hourly_data = {
                    "date": pd.date_range(
                        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                        freq=pd.Timedelta(seconds=hourly.Interval()),
                        inclusive="left"
                    ),
                    "title":city,
                    "latitude": lat,
                    "longitude": lon,
                    "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
                    "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
                    "dew_point_2m": hourly.Variables(2).ValuesAsNumpy(),
                    "precipitation": hourly.Variables(3).ValuesAsNumpy(),
                    "surface_pressure": hourly.Variables(4).ValuesAsNumpy(),
                    "cloud_cover": hourly.Variables(5).ValuesAsNumpy(),
                    "wind_speed_10m": hourly.Variables(6).ValuesAsNumpy(),
                    "wind_direction_10m": hourly.Variables(7).ValuesAsNumpy(),
                }

                # Create a DataFrame for the hourly data
                hourly_dataframe = pd.DataFrame(data=hourly_data)
                all_data.append(hourly_dataframe)

        except Exception as e:
            print(f"Error fetching data for ({lat}, {lon}): {e}")

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
    # Define the path to save in the 'assets' folder
        assets_dir = 'assets'
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)

        file_path = os.path.join(assets_dir, 'weather_data.csv')
        combined_df.to_csv(file_path, index=False)

        print(f"Data saved to {file_path}")
        # Example of how you might use the split function
        split_weather_data_by_title()
    else:
        print("No data fetched.")
        # Example of how you might use the split function
#split_weather_data_by_title()


