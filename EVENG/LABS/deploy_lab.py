# deploy_lab.py
import os
from evengsdk.client import EvengClient

# Get credentials from environment variables (set in Jenkins)
EVE_IP = os.getenv('EVE_SERVER_IP')
EVE_USER = os.getenv('EVE_USERNAME')
EVE_PWD = os.getenv('EVE_PASSWORD')

client = EvengClient(EVE_IP, protocol="https", ssl_verify=False, log_file="eveng.log")
client.disable_insecure_warnings()
client.login(username=EVE_USER, password=EVE_PWD)
client.set_log_level('DEBUG')

# Create lab from the topology file
# Note: Ensure evengsdk is installed on the Jenkins runner
# os.system(f"eve-ng lab create-from-topology -t topology.yaml")

# LAB_DATA
lab = {"name": "Jenkins_Auto_Lab", "description": "Lab created via Jenkins CI/CD", "path": "/"}

# CHECK_FOR_LAB
resp = client.api.get_lab(lab.path)

# IF_LAB_DELETE_THEN_CREATE
if resp['status'] == "success":
  resp = client.api.delete_lab(lab.path)

  if resp['status'] == "success":
    resp = client.api.create_lab(**lab)
    if resp['status'] == "success":
      print("lab created successfully.")
    
# IF_NO_LAB_CREATE
if resp['status'] != "success":
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
    {"name": "R2", "template": "cat9kv", "image": "cat9kv-17.15.01", "left": 300, "top": 300},
]
for node in nodes:
    client.api.add_node(lab_path, **node)

# connect nodes to management network
mgmt_connections = [
    {"src": "R1", "src_label": "Gi0/0", "dst": "eve-mgmt"},
    {"src": "R2", "src_label": "Gi0/0", "dst": "eve-mgmt"}
]
for link in mgmt_connections:
    client.api.connect_node_to_cloud(lab_path, **link)

# create p2p links
p2p_links = [
    {"src": "R1", "src_label": "Gi1/0/1", "dst": "R2", "dst_label": "Gi1/0/1"},
]
for link in p2p_links:
    client.api.connect_node_to_node(lab_path, **link)

client.logout()

print("Lab deployment successful.")
