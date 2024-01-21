import requests
import folium
from haversine import haversine

# Function to calculate distance
def calculate_distance(coord1, coord2):
    return haversine(coord1, coord2)

# Function to find address by _id
def find_address_by_id(addr_id, addresses):
    return next(addr for addr in addresses if addr['_id'] == addr_id)

# Loading the addresses
response = requests.get('https://zorang-recrutment.s3.ap-south-1.amazonaws.com/addresses.json')
addresses = response.json()

# Store coordinates
store_coordinates = (28.9428, 77.2276)

# Calculate distances from the store to each address
distances = []
for address in addresses:
    addr_coordinates = (address['latitude'], address['longitude'])
    distance = calculate_distance(store_coordinates, addr_coordinates)
    distances.append((address['_id'], distance))

# Sort addresses by distance
distances.sort(key=lambda x: x[1])

# Distribute addresses to agents using Round-Robin algorithm
num_agents = 10
agent_routes = [[] for _ in range(num_agents)]
for i, (addr_id, _) in enumerate(distances):
    agent_routes[i % num_agents].append(addr_id)

# Google Map API key
google_api_key = 'AIzaSyDMTd5i1jyilkU5uN8gpHz_743FSjbCf1Y'

# Creating a map centered around the store location
m = folium.Map(location=store_coordinates, zoom_start=12, tiles=None)

# Marking the store location
folium.Marker(store_coordinates, popup='Store', icon=folium.Icon(color='red', icon='info-sign')).add_to(m)

# Adding Google Map
google_maps_tile = f'https://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}&hl=en&key={google_api_key}'
folium.TileLayer(tiles=google_maps_tile, attr='Google', name='Google Street Map', overlay=False).add_to(m)


# Adding Equator line (0 degrees latitude)
folium.PolyLine(locations=[(-180, 0), (180, 0)], color='orange', weight=2, opacity=1).add_to(m)

# Adding Prime Meridian line (0 degrees longitude)
folium.PolyLine(locations=[(0, -180), (0, 180)], color='orange', weight=2, opacity=1).add_to(m)


# Plotting routes for each agent
for i, route in enumerate(agent_routes):
    route_group = folium.FeatureGroup(name=f'Agent {i+1}')
    last_coords = store_coordinates
    for addr_id in route:
        addr = find_address_by_id(addr_id, addresses)
        addr_coords = (addr['latitude'], addr['longitude'])
        popup_text = f'Address ID: {addr_id}\nLatitude: {addr_coords[0]}\nLongitude: {addr_coords[1]}'
        folium.Marker(addr_coords, popup=popup_text, icon=folium.Icon(color='blue')).add_to(route_group)
        folium.PolyLine([last_coords, addr_coords], color='blue').add_to(route_group)
        last_coords = addr_coords
    # Connecting back to store
    folium.PolyLine([last_coords, store_coordinates], color='blue').add_to(route_group)
    route_group.add_to(m)

# Add LayerControl to toggle each agent's route
folium.LayerControl().add_to(m)

# Save the map to an HTML file
m.save('delivery_routes_map_google.html')
print("Map created")
