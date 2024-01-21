import numpy as np
import requests
from haversine import haversine

# Function to calculate distance
def calculate_distance(coord1, coord2):
    return haversine(coord1, coord2)

# Load addresses
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

# Assign addresses to agents
num_agents = 10
agent_routes = [[] for _ in range(num_agents)]

for i, (addr_id, _) in enumerate(distances):
    agent_routes[i % num_agents].append(addr_id)

# Print routes for each agent
for i, route in enumerate(agent_routes):
    print(f"Agent {i+1}: {route}")
