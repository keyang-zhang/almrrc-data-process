import pandas as pd


selected_date_str = "2018-08-08"
instance_dir = "./instances/complete"
save_dir = "./instances/2018-08-08"

# load data
depot_data = pd.read_csv(f"{instance_dir}/depots.csv")
veh_data = pd.read_csv(f"{instance_dir}/vehicles.csv")
cust_data = pd.read_csv(f"{instance_dir}/customers.csv")

cust_data = cust_data[cust_data["delivered_date"] == selected_date_str]

selected_veh_ids = cust_data["vehicle_id"].unique()
veh_data = veh_data[veh_data["vehicle_id"].isin(selected_veh_ids)]

selected_depot_ids = veh_data["depot_id"].unique()
depot_data = depot_data[depot_data["depot_id"].isin(selected_depot_ids)]

# save data
depot_data.to_csv(f"{save_dir}/depots.csv")
veh_data.to_csv(f"{save_dir}/vehicles.csv")
cust_data.to_csv(f"{save_dir}/customers.csv")
