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


# Load weather data from CSV and filter by the specified date
current_dir = os.path.dirname(os.path.abspath(__file__))
weather_data_path = os.path.join(current_dir, '..', 'assets', 'weather_data.csv')

# Read the CSV file into a DataFrame
weather_data = pd.read_csv(weather_data_path)
# Rename columns if necessary


# Remove rows where 'Sea_level_pressure' is NaN or missing
filtered_data = weather_data.dropna(subset=['Sea_level_pressure'])

# Create a GeoDataFrame from the filtered weather data points
geometry = [Point(xy) for xy in zip(filtered_data['longitude'], filtered_data['latitude'])]
weather_gdf = gpd.GeoDataFrame(filtered_data, geometry=geometry, crs="EPSG:4326")

# Define bounds around Pakistan
minx, miny, maxx, maxy =  60.87, 23.63, 77.05, 37.23  # Bounds for Pakistan

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
pressure_values = filtered_data['Sea_level_pressure'].values  # Now this contains valid pressure values only


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

print("Interpolated pressure values range:", np.min(kriging_pressure), np.max(kriging_pressure))

# Plotting Kriging Heatmap
fig, ax = plt.subplots(figsize=(12, 12))

# Plot filled contours for heatmap
contour_filled = ax.contourf(x_grid, y_grid, kriging_pressure, levels=15, cmap='coolwarm', alpha=0.7)

# Remove title and axis labels
ax.set_xlabel('')
ax.set_ylabel('')
ax.set_title('')

# Hide axis
ax.set_xticks([])
ax.set_yticks([])

# Adjust layout to remove padding
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)


plt.savefig(os.path.join(current_dir, '..', 'assets', 'isobar_heatmap.png'), dpi=300, bbox_inches='tight', transparent=True, pad_inches=0)
crop_inches = 1
heatmap_path = os.path.join(current_dir, '..', 'assets', 'isobar_heatmap.png')
# Crop the heatmap image
crop_image(heatmap_path, crop_inches)

plt.close(fig)  # Close the figure to free memory

# Plotting Kriging Isolines
fig, ax = plt.subplots(figsize=(12, 12))

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


plt.savefig(os.path.join(current_dir, '..', 'assets', 'isobars.png'), dpi=300, bbox_inches='tight', transparent=True, pad_inches=0)
crop_inches = 1
isolines_path = os.path.join(current_dir, '..', 'assets', 'isobars.png')
# Crop the isolines image
crop_image(isolines_path, crop_inches)

plt.close(fig)  # Close the figure to free memory
