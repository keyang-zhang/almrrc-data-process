# focus on three depots in Chicago metropolitan area: DCH1 (Chicago), DCH2 (Morton Grove), DCH3 (Lise)

import json
import matplotlib.pyplot as plt
import pandas as pd
import math

EARTH_RADIUS = 6371.0008
def geo_distance(lat1, lon1, lat2, lon2):
    # Convert all angles to radians
    lat1_r = math.radians(lat1)
    lon1_r = math.radians(lon1)
    lat2_r = math.radians(lat2)
    lon2_r = math.radians(lon2)
    # Calculate the distance
    dp = math.cos(lat1_r) * math.cos(lat2_r) * math.cos(lon1_r - lon2_r) + math.sin(lat1_r) * math.sin(lat2_r)
    angle = math.acos(dp)
    return EARTH_RADIUS * angle


package_data_file = "./almrrc2021/almrrc2021-data-training/model_build_inputs/package_data.json"
route_data_file = "./almrrc2021/almrrc2021-data-training/model_build_inputs/route_data.json"
save_folder = "./instances"
selected_depot_ids = ['DCH1', 'DCH2', 'DCH3']
depot_coordinates = {'DCH1':(41.84032828797428, -87.68433006138673), # (lat, long)
                     'DCH2':(42.031472230740874, -87.77709166137727),
                     'DCH3':(41.803348036444014, -88.09727436138859)}

with open(package_data_file, "r") as f:
    package_data_all = json.load(f)
with open(route_data_file, "r") as f:
    route_data_all = json.load(f)


vehicle_info = {"vehicle_id": [], "depot_id": [], "capacity": []}
route_id_to_vehicle_id = {}
vehicle_count = 0
for route_id, route in route_data_all.items():
    depot_id = route["station_code"]
    if depot_id in selected_depot_ids:
        vehicle_id = f"v{vehicle_count}"
        vehicle_info["vehicle_id"].append(vehicle_id)
        vehicle_info["capacity"].append(route["executor_capacity_cm3"])
        vehicle_info["depot_id"].append(depot_id)
        route_id_to_vehicle_id[route_id] = vehicle_id
        vehicle_count += 1

customer_info = {"customer_id": [], "dropoff_long":[], "dropoff_lat":[], "volume":[],
                 "dropoff_tw_start":[], "dropoff_tw_end":[], "service_duration":[],
                 "depth":[],"height":[],"width":[],
                 "dropoff_zone_id":[], "delivered_date":[], "depot_id":[], "vehicle_id":[]}
customer_count = 0
for route_id in package_data_all:
    depot_id = route_data_all[route_id]["station_code"]
    dispatched_date = route_data_all[route_id]["date_YYYY_MM_DD"]
    if depot_id in selected_depot_ids:
        for stop_id in package_data_all[route_id]:
            stop_info = route_data_all[route_id]["stops"][stop_id]
            for parcel_id in package_data_all[route_id][stop_id]:
                parcel_info = package_data_all[route_id][stop_id][parcel_id]
                customer_info["customer_id"].append(f"c{customer_count}")
                customer_info["dropoff_long"].append(stop_info["lng"])
                customer_info["dropoff_lat"].append(stop_info["lat"])
                customer_info["dropoff_zone_id"].append(stop_info["zone_id"])
                customer_info["delivered_date"].append(dispatched_date)
                customer_info["dropoff_tw_start"].append(parcel_info["time_window"]["start_time_utc"])
                customer_info["dropoff_tw_end"].append(parcel_info["time_window"]["end_time_utc"])
                customer_info["service_duration"].append(parcel_info["planned_service_time_seconds"])
                customer_info["depth"].append(parcel_info["dimensions"]["depth_cm"])
                customer_info["height"].append(parcel_info["dimensions"]["height_cm"])
                customer_info["width"].append(parcel_info["dimensions"]["width_cm"])
                d, h, w = parcel_info["dimensions"]["depth_cm"], parcel_info["dimensions"]["height_cm"], parcel_info["dimensions"]["width_cm"]
                customer_info["volume"].append(d * h * w)
                customer_info["depot_id"].append(depot_id)
                customer_info["vehicle_id"].append(route_id_to_vehicle_id[route_id])
                customer_count += 1

# convert the data to tabular format
pd.DataFrame(customer_info).to_csv(f"{save_folder}/customers.csv")
pd.DataFrame(vehicle_info).to_csv(f"{save_folder}/vehicles.csv")

# get statistics
# - depot distance to the gravity of customers
# - average size/volume of parcels
# - average capacity of vehicles
# - size of rectangular area just cover all customers

# average distance to customers per depot
depot_avg_dist_to_cust = {}
for depot_id in selected_depot_ids:
    depot_lat, depot_long = depot_coordinates[depot_id]
    total_dist = 0
    for cust_lat, cust_long in zip(customer_info["dropoff_lat"], customer_info["dropoff_long"]):
        total_dist += geo_distance(depot_lat, depot_long, cust_lat, cust_long)
    average_dist = total_dist / customer_count
    depot_avg_dist_to_cust[depot_id] = average_dist

# average size of parcels
cust_average_volume = sum(customer_info["volume"]) / customer_count

# size of study area
cust_lat_max, cust_lat_min = max(customer_info["dropoff_lat"]), min(customer_info["dropoff_lat"])
cust_long_max, cust_long_min = max(customer_info["dropoff_long"]), min(customer_info["dropoff_long"])
area_width = geo_distance(cust_lat_max, cust_long_max, cust_lat_max, cust_long_min)
area_depth = geo_distance(cust_lat_max, cust_long_max, cust_lat_min, cust_long_max)
area_size = area_depth * area_depth

vehicle_capacity_avg = sum(vehicle_info['capacity']) / vehicle_count


with open(f"{save_folder}/statistics.txt", "w") as f:
    res_str = ""
    for depot_id in depot_avg_dist_to_cust:
        avg_dist = depot_avg_dist_to_cust[depot_id]
        res_str += f"Average distance from depot {depot_id} to all customers (km): {avg_dist} \n"
    res_str += f"Average size of parcels (cm3): {cust_average_volume} \n"
    res_str += f"Average capacity of vehicles (cm3): {vehicle_capacity_avg} \n"
    res_str += f"Size of study area (km^3): {area_size} \n"
    f.write(res_str)