import folium
import requests

# Function to get travel time from Google Maps Directions API
# def get_travel_time(origin, destination, mode, api_key):
#     params = {
#         'origin': f'{origin[0]},{origin[1]}',
#         'destination': f'{destination[0]},{destination[1]}',
#         'mode': mode,
#         'key': api_key
#     }
#     response = requests.get("https://maps.googleapis.com/maps/api/directions/json", params=params)
#     directions = response.json()

#     if directions['status'] == 'OK' and directions['routes']:
#         duration = directions['routes'][0]['legs'][0]['duration']['text']  # Duration as text
#         return duration
#     else:
#         return 'Unavailable'
# Have to Pay some price -> https://console.cloud.google.com/project/_/billing/enable



# Google Maps API key
google_api_key = 'AIzaSyDMTd5i1jyilkU5uN8gpHz_743FSjbCf1Y'

# Loading addresses
response = requests.get('https://zorang-recrutment.s3.ap-south-1.amazonaws.com/addresses.json')
addresses = response.json()

# Store coordinates
store_coordinates = (28.9428, 77.2276)

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


# Function to find address by _id
def find_address_by_id(addr_id, addresses):
    return next(addr for addr in addresses if addr['_id'] == addr_id)

# Distribute addresses to agents using Round-Robin algorithm
num_agents = 10
agent_routes = [[] for _ in range(num_agents)]
for i, address in enumerate(addresses):
    agent_routes[i % num_agents].append(address['_id'])


# Plotting routes for each agent and fetching travel times
for i, route in enumerate(agent_routes):
    route_group = folium.FeatureGroup(name=f'Agent {i+1}')
    last_coords = store_coordinates
    for addr_id in route:
        addr = find_address_by_id(addr_id, addresses)
        addr_coords = (addr['latitude'], addr['longitude'])
        popup_text = f'Address ID: {addr_id}\nLatitude: {addr_coords[0]}\nLongitude: {addr_coords[1]}'

        # Fetch travel times for driving
        # driving_time = get_travel_time(store_coordinates, addr_coords, 'driving', google_api_key)
        # popup_text = f'Address ID: {addr_id}\nDriving: {driving_time}'
        
        folium.Marker(addr_coords, popup=popup_text, icon=folium.Icon(color='blue')).add_to(route_group)
        folium.PolyLine([last_coords, addr_coords], color='blue').add_to(route_group)
        last_coords = addr_coords

    # Connecting back to store
    folium.PolyLine([last_coords, store_coordinates], color='blue').add_to(route_group)
    route_group.add_to(m)

# Add LayerControl to toggle each agent's route
folium.LayerControl().add_to(m)

# Save the map to an HTML file
print("Map created")
m.save('delivery_routes_map_google.html')

