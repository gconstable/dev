# create a lab
lab = {"name": "Jenkins_Auto_Lab", "description": "Lab created via Jenkins CI/CD", "path": "/"}
resp = client.api.create_lab(**lab)
if resp['status'] == "success":
  print("lab created successfully.")

# we need the lab path to create objects in the lab
lab_path = f"{lab['path']}{lab['name']}.unl"

# create management network
mgmt_cloud = {"name": "eve-mgmt", "network_type": "pnet1"}
client.api.add_lab_network(lab_path, **mgmt_cloud)

# create Nodes
nodes = [
    {"name": "R1", "template": "cat9kv", "image": "cat9kv-17.15.01", "left": 100, "top": 100},
    {"name": "R2", "template": "cat9kv", "image": "cat9kv-17.15.01", "left": 300, "top: "},
]
for node in nodes:
    client.api.add_node(lab_path, **node)

# connect nodes to management network
mgmt_connections = [
    {"src": "R1", "src_label": "Mgmt1", "dst": "eve-mgmt"},
    {"src": "R2", "src_label": "Mgmt1", "dst": "eve-mgmt"}
]
for link in mgmt_connections:
    client.api.connect_node_to_cloud(lab_path, **link)

# create p2p links
p2p_links = [
    {"src": "R1", "src_label": "Eth1", "dst": "R2", "dst_label": "Eth1"},
]
for link in p2p_links:
    client.api.connect_node_to_node(lab_path, **link)

client.logout()
