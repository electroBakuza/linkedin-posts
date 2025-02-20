import requests
import folium
from folium.plugins import MarkerCluster

# Define API endpoint with bounding box, date range, and a limit of 50 results
url = "https://www.ncdc.noaa.gov/swdiws/geojson/nx3hail/20240601:20240608/?bbox=-102,37,-94,40"

# Fetch the GeoJSON data from the SWDI API
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
else:
    print("Error fetching data:", response.status_code)
    data = None

# Create a Folium map centered on the average of the bounding box coordinates
m = folium.Map(location=[38.5, -98.0], zoom_start=6)

# Add a marker cluster to group nearby markers
marker_cluster = MarkerCluster().add_to(m)

# Check if data exists and iterate through GeoJSON features to add markers
if data and "features" in data:
    for feature in data["features"]:
        geometry = feature.get("geometry")
        properties = feature.get("properties", {})
        if geometry and geometry["type"] == "Point":
            # GeoJSON points are in [longitude, latitude] format
            lon, lat = geometry["coordinates"]
            # Create a popup displaying key properties of the event
            popup_info = "<br>".join([f"{key}: {value}" for key, value in properties.items()])
            # Use a custom small icon (a cloud icon from Font Awesome) to represent hail events
            icon = folium.Icon(icon='cloud', color='blue', prefix='fa')
            folium.Marker([lat, lon], popup=popup_info, icon=icon).add_to(marker_cluster)

# Save the map to an HTML file so you can view it in a web browser
m.save("hail_events_map_custom.html")
print("Map saved as hail_events_map_custom.html")
