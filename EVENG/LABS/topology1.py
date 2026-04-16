from evengsdk.client import EvengClient

# 1. Initialize and Login
client = EvengClient("10.0.0.10", ssl_verify=False, protocol="http")
client.login(username="admin", password="eve")

# 2. Create the Lab
lab_info = {"name": "Automated_Lab", "description": "API Test Lab", "path": "/"}
client.api.create_lab(**lab_info)
lab_path = "/Automated_Lab.unl"

# 3. Add Nodes (Routers)
r1_data = {"name": "R1", "template": "vios", "image": "vios-image-name", "left": 100, "top": 100}
r2_data = {"name": "R2", "template": "vios", "image": "vios-image-name", "left": 300, "top": 100}

client.api.add_node(lab_path, **r1_data)
client.api.add_node(lab_path, **r2_data)

# 4. Connect Devices
# Note: Connections typically require the node IDs assigned by EVE-NG (e.g., 1 and 2)
# and the interface index (e.g., 0 for GigabitEthernet0/0).
link_data = {
    "node_id": 1,           # Source Node ID
    "data": {"0": "2"}      # Maps Source Intf 0 to Destination Node ID 2
}
client.api.connect_node_interfaces(lab_path, 1, {"0": 2})

# 5. Start Nodes
client.api.start_node(lab_path, 1)
client.api.start_node(lab_path, 2)
