import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import os
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import time

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

coordinates = [
    (35.920834, 74.308334),  # Gilgit, Gilgit-Baltistan
    (29.143644, 71.257240),  # Ahmedpur East, Bahawalpur
    (31.976515, 74.222015),  # Kāmoke, Gujranwala
    (28.281891, 68.438171),  # Jacobabad
    (30.677717, 73.106812),  # Sahiwal
    (32.337006, 74.903336),  # Zafarwal
    (30.286415, 71.932030),  # Khanewal
    (31.345394, 73.429810),  # Jaranwala, Faisalabad
    (33.148392, 73.751770),  # New Mirpur City, Azad Kashmir
    (30.181459, 71.492157),  # Multan
    (26.244221, 68.410034),  # Nawabshah
    (30.032486, 70.640244),  # Dera Ghāzi Khān
    (27.563993, 68.215134),  # Larkana
    (32.555496, 73.194351),  # Malakwāl
    (30.448601, 73.697578),  # Haveli Lakha
    (29.505283, 71.222084),  # Jalalpur Pirwala
    (34.015858, 71.975449),  # Nowshera
    (32.071697, 73.685730),  # Hafizabad
    (30.045246, 72.348869),  # Vehāri
    (30.808500, 73.459396),  # Okara
    (33.768051, 72.360703),  # Attock
    (34.168751, 73.221497),  # Abbottābad
    (33.351357, 72.774734),  # Qurtaba City
    (32.588169, 73.497345),  # Mandi Bahauddin
    (29.395721, 71.683334),  # Bahawalpur
    (33.115269, 71.095535),  # Karak
    (30.074377, 71.184654),  # Muzaffargarh
    (27.955648, 68.637672),  # Shikārpur
    (27.529951, 68.758141),  # Khairpur
    (31.975508, 74.223801),  # Kamoki
    (32.082466, 72.669128),  # Sargodha
    (31.025009, 73.847878),  # Pattoki
    (24.743303, 67.890938),  # Makli
    (34.405262, 73.380066),  # Garhi Habibullah
    (32.265396, 72.905388),  # Bhalwal
    (32.986111, 70.604164),  # Bannu
    (31.452097, 73.708305),  # Nankana Sahib
    (31.217646, 72.997368),  # Dijkot
    (28.310350, 70.127403),  # Sādiqābād
    (26.004168, 63.060555),  # Turbat
    (30.183270, 66.996452),  # Quetta
    (32.571144, 74.075005),  # Gujrat
    (29.418068, 71.670685),  # Bahawalpur
    (27.713926, 68.836899),  # Sukkur
    (31.831667, 73.623055),  # Khanqah Dogran
    (32.940548, 73.727631),  # Jhelum
    (32.136673, 74.012383),  # Qila Didar Singh
    (32.166351, 74.195900),  # Gujranwala
    (24.655720, 68.837242),  # Badin
    (31.716661, 73.985023),  # Sheikhupura
    (33.783184, 72.723076),  # Wah
    (30.705557, 70.657776),  # Taunsa
    (25.067562, 66.917038),  # Hub
    (32.099476, 74.874733),  # Narowal
    (30.535133, 72.699539),  # Chichawatni
    (34.359688, 73.471054),  # Muzaffarabad
    (31.621113, 74.282364),  # Shahdara
    (31.582045, 74.329376),  # Lahore
    (34.025917, 71.560135),  # Peshawar
    (34.788040, 72.929115),  # Thakot
    (34.749271, 72.357063),  # Saidu Sharif, Mingora
    (26.044418, 68.953880),  # Sanghar
    (34.206123, 72.029800),  # Mardan
    (24.858480, 67.001884),  # Saddar Town, Karachi
    (32.966000, 71.553001),  # Kalabagh
    (25.126389, 62.322498),  # Gwadar
    (32.265652, 74.669525),  # Pasrūr
    (34.773647, 72.359901),  # Mingora
    (31.118793, 74.463272),  # Kasur
    (31.721159, 74.273758),  # Kaku, Lahore
    (31.418715, 73.079109),  # Faisalabad
    (24.749731, 67.911636),  # Thatta
    (30.970655, 71.212303),  # Chowk Azam
    (30.964750, 70.939934),  # Layyah
    (25.529104, 69.013573),  # Mīrpur Khās
    (33.626057, 73.071442),  # Rawalpindi
    (32.338779, 74.353065),  # Daska
    (31.633333, 71.066666),  # Bhakkar
    (30.297859, 73.058235),  # Ārifwāla
    (24.860966, 66.990501),  # Karachi
    (31.839722, 71.430000),  # Dullewala
    (32.286613, 72.430252),  # Shahpur
    (30.466667, 70.966667),  # Kot Addu
    (31.278046, 72.311760),  # Jhang
    (25.416868, 68.274307),  # Jamshoro
    (33.738045, 73.084488),  # Islamabad
    (30.963774, 73.977982),  # Chunian
    (32.497223, 74.536110),  # Sialkot
    (31.831482, 70.911598),  # Dera Ismail Khan
    (28.883612, 64.416061),  # Dalbandin
    (29.297670, 64.706734),  # Chagai
    (32.294445, 72.349724)   # Khushāb
]



# Function to fetch and process weather data for each coordinate
def fetch_weather_data():
    all_data = []

    for lat, lon in coordinates:
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
                #print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
                #print(f"Elevation {response.Elevation()} m asl")
                #print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
                #print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")
                
                # Process hourly data for the current location
                hourly = response.Hourly()
                hourly_data = {
                    "date": pd.date_range(
                        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                        freq=pd.Timedelta(seconds=hourly.Interval()),
                        inclusive="left"
                    ),
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
    else:
        print("No data fetched.")

#fetch_weather_data()


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
    else:
        print("No data fetched.")

#fetch_weather_data()
