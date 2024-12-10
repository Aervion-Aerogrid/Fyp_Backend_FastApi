import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
from pykrige.ok import OrdinaryKriging
from PIL import Image
import os

def crop_image(image_path, crop_inches):
    # Open the image
    img = Image.open(image_path)
    
    # Convert inches to pixels (assuming 300 DPI)
    dpi = 300
    crop_pixels = int(crop_inches * dpi)
    
    # Get the dimensions of the image
    width, height = img.size
    
    # Define the cropping box
    left = crop_pixels
    top = crop_pixels
    right = width - crop_pixels
    bottom = height - crop_pixels
    
    # Crop the image
    img_cropped = img.crop((left, top, right, bottom))
    
    # Save the cropped image back to the original file
    img_cropped.save(image_path, format='PNG')


# Construct the file path for the CSV
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, '..', 'assets', 'weather_data.csv')

# Load weather data from CSV
weather_data = pd.read_csv(csv_path)
filtered_data = weather_data[weather_data['date'] == "2024-08-26 20:00:00+00:00"]

# Create a GeoDataFrame from the filtered weather data points
geometry = [Point(xy) for xy in zip(filtered_data['longitude'], filtered_data['latitude'])]
weather_gdf = gpd.GeoDataFrame(filtered_data, geometry=geometry, crs="EPSG:4326")

# Define bounds around the northeastern hemisphere
minx, miny, maxx, maxy = 60.87, 23.63, 77.05, 37.23  # Bounds for the northeastern hemisphere

# Create grid points for interpolation
grid_resolution = 0.25  # Change this value to adjust the grid density
x_points = np.arange(minx, maxx, grid_resolution)
y_points = np.arange(miny, maxy, grid_resolution)
x_grid, y_grid = np.meshgrid(x_points, y_points)  # Meshgrid for interpolation
grid_points = [Point(x, y) for x in x_points for y in y_points]

# Create a GeoDataFrame for the grid points
grid_gdf = gpd.GeoDataFrame(geometry=grid_points, crs="EPSG:4326")

# Extract coordinates and pressure values
weather_coords = np.array([(point.x, point.y) for point in weather_gdf.geometry])
pressure_values = filtered_data['precipitation'].values

# Kriging Interpolation
# Create Kriging model using Ordinary Kriging
ok = OrdinaryKriging(
    weather_coords[:, 0], 
    weather_coords[:, 1], 
    pressure_values, 
    variogram_model='spherical', 
    verbose=False, 
    enable_plotting=False
)

# Interpolate grid points using Kriging
kriging_pressure, ss = ok.execute('grid', x_points, y_points)

# Plotting Kriging Isobars with Contour Lines, Labels
fig, ax = plt.subplots(figsize=(12, 12))

# Plot filled contours
contour_filled = ax.contourf(x_grid, y_grid, kriging_pressure, levels=15, cmap='coolwarm', alpha=0.7)

# Plot contour lines
contour_lines = ax.contour(x_grid, y_grid, kriging_pressure, levels=15, colors='black', linewidths=1.5)

# Add contour labels
ax.clabel(contour_lines, inline=True, fontsize=10, fmt='%1.1f', colors='black')

# Remove title and axis labels
ax.set_xlabel('')
ax.set_ylabel('')
ax.set_title('')

# Hide axis
ax.set_xticks([])
ax.set_yticks([])

# Adjust layout to remove padding
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)


# Save the plot to a high-quality PNG file with a transparent background
plt.savefig(os.path.join(current_dir, '..', 'assets', 'isohyets.png'), dpi=300, bbox_inches='tight', transparent=True, pad_inches=0)

# Usage
image_path = os.path.join(current_dir, '..', 'assets', 'isohyets.png')  # Replace with the path to your image
crop_inches = 0.05  # Crop 0.05 inches from each side
crop_image(image_path, crop_inches)
