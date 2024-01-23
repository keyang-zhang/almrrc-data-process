import json

import pandas as pd

selected_date_str = "2018-08-08"
instance_dir = "./instances/Chicago-all"
save_dir = "./instances/2018-08-08"

# load data
depot_data = pd.read_csv(f"{instance_dir}/depots.csv")
veh_data = pd.read_csv(f"{instance_dir}/vehicles.csv")
cust_data = pd.read_csv(f"{instance_dir}/customers.csv")
with open(f"{instance_dir}/tt_matrix.json", "r") as f:
    tt_data = json.load(f)

cust_data = cust_data[cust_data["delivered_date"] == selected_date_str]

selected_veh_ids = cust_data["vehicle_id"].unique()
veh_data = veh_data[veh_data["vehicle_id"].isin(selected_veh_ids)]

selected_depot_ids = veh_data["depot_id"].unique()
depot_data = depot_data[depot_data["depot_id"].isin(selected_depot_ids)]

selected_node_ids = cust_data["dropoff_node_id"].unique()

selected_tt_matrix = {}
for orig_id in selected_node_ids:
    if selected_tt_matrix.get(orig_id, None) is None:
        selected_tt_matrix[orig_id] = {}
    for dest_id in selected_node_ids:
        if tt_data[orig_id].get(dest_id, None) is not None:
            selected_tt_matrix[orig_id][dest_id] = tt_data[orig_id][dest_id]

for df in [depot_data, veh_data, cust_data]:
    df.drop(df.columns[df.columns.str.contains('unnamed', case=False)], axis=1, inplace=True)

# save data
depot_data.to_csv(f"{save_dir}/depots.csv", index=False)
veh_data.to_csv(f"{save_dir}/vehicles.csv", index=False)
cust_data.to_csv(f"{save_dir}/customers.csv", index=False)
with open(f"{save_dir}/tt_matrix.json", "w") as f:
    json.dump(selected_tt_matrix, f, indent=4)
