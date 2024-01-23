import json
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


def fill_by_constant_coefficient():
    instance_dir = "./instances/2018-08-08"

    depot_data = pd.read_csv(f"{instance_dir}/depots.csv")
    cust_data = pd.read_csv(f"{instance_dir}/customers.csv")
    with open(f"{instance_dir}/tt_matrix.json", "r") as f:
        tt_data = json.load(f)

    if "node_id" not in depot_data.columns:
        depot_data["node_id"] = depot_data["depot_id"]
        # depot_data.to_csv(f"{instance_dir}/depots.csv", index=False)

    nodes_data = depot_data[["node_id", "long", "lat"]]
    name_map = {"dropoff_node_id": "node_id", "dropoff_long": "long", "dropoff_lat": "lat"}
    nodes_data = pd.concat(
        [nodes_data, cust_data[["dropoff_node_id", "dropoff_long", "dropoff_lat"]].rename(columns=name_map)])
    nodes_data.drop_duplicates(keep="first", inplace=True)
    all_node_ids = nodes_data["node_id"]
    all_nodes_longs = {i: l for i, l in zip(nodes_data["node_id"], nodes_data["long"])}
    all_nodes_lats = {i: l for i, l in zip(nodes_data["node_id"], nodes_data["lat"])}

    coefficients = []
    for orig in tt_data:
        for dest in tt_data[orig]:
            if orig == dest:
                continue
            if all_nodes_lats[orig] != all_nodes_lats[dest] and all_nodes_longs[orig] != all_nodes_longs[dest]:
                euclidean_dist = geo_distance(all_nodes_lats[orig], all_nodes_longs[orig], all_nodes_lats[dest],
                                              all_nodes_longs[dest])
                if euclidean_dist != 0:
                    coefficients.append(tt_data[orig][dest] / euclidean_dist)
    avg_coefficient = sum(coefficients) / len(coefficients)

    for orig in all_node_ids:
        for dest in all_node_ids:
            if tt_data.get(orig, None) is None:
                tt_data[orig] = {}
                tt_data[orig][dest] = geo_distance(all_nodes_lats[orig], all_nodes_longs[orig], all_nodes_lats[dest],
                                                   all_nodes_longs[dest]) * avg_coefficient
            else:
                if tt_data[orig].get(dest, None) is None:
                    tt_data[orig][dest] = geo_distance(all_nodes_lats[orig], all_nodes_longs[orig],
                                                       all_nodes_lats[dest], all_nodes_longs[dest]) * avg_coefficient
    with open(f"{instance_dir}/tt_matrix-complete.json", "w") as f:
        json.dump(tt_data, f, indent=4)


fill_by_constant_coefficient()
