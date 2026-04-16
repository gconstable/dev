# deploy_lab.py
# reference: https://ttafsir.github.io/evengsdk/api_reference/#evengsdk.api.EvengApi.get_lab
import os
from evengsdk.client import EvengClient

# GLOBAL_VARS
LAB_CREATED = False

# GET_JENKINS_CREDS
EVE_IP = os.getenv('EVE_SERVER_IP')
EVE_USER = os.getenv('EVE_USERNAME')
EVE_PWD = os.getenv('EVE_PASSWORD')

# SET_EVENG_CONNECTION
client = EvengClient(EVE_IP, protocol="https", ssl_verify=False, log_file="eveng.log")
client.disable_insecure_warnings()
client.login(username=EVE_USER, password=EVE_PWD)
client.set_log_level('DEBUG')

#################
# GENERATE_LABS #
#################

# LAB_DATA
lab = {
  "name": "Jenkins_Auto_Lab_catalyst_center", 
  "description": "Lab created via Jenkins CI/CD", 
  "path": "/"
}

# LAB_PATH
lab_path = f"{lab['path']}{lab['name']}.unl"

# CHECK_FOR_LAB_CREATE_IF_NO_LAB
try:
    # CHECK_FOR_LAB
    resp = client.api.get_lab(lab_path)

    # IF_LAB_CLOSE_STOP_DELETE
    if resp['status'] == "success":
      print("lab found.")
      print("closing lab.")
      resp = client.api.close_lab()
      
      print("stopping all nodes within lab.")
      resp = client.api.stop_all_nodes(lab_path)
     
      print("deleting lab.")
      resp = client.api.delete_lab(lab_path)
      LAB_CREATED = False
except Exception as e:
    print("no lab found.")
    print (e)
finally:
  # IF_LAB_CREATED_DISPLAY_MSG
  if LAB_CREATED == True:
    print("Lab was already created.  Something unexpected happened")

  # IF_NO_LAB_CREATE_LAB
  if LAB_CREATED == False:
    print("creating lab.")
    resp = client.api.create_lab(**lab)
    LAB_CREATED = True

#################
# LAB_NODE_DATA #
#################

# OOB_MANAGEMENT
mgmt_cloud = {"name": "oob-mgmt", "network_type": "bridge"}
client.api.add_lab_network(lab_path, **mgmt_cloud)

# ADD_NODES
nodes = [
    {"name": "R1", "template": "cat9kv", "image": "cat9kv-17.15.01", "left": 100, "top": 100},
    {"name": "R2", "template": "cat9kv", "image": "cat9kv-17.15.01", "left": 300, "top": 300},
]
for node in nodes:
    client.api.add_node(lab_path, **node)

# NODE_TO_OOB_MGMT
mgmt_connections = [
    {"src": "R1", "src_label": "Gi1/0/1", "dst": "oob-mgmt"},
    {"src": "R2", "src_label": "Gi1/0/1", "dst": "oob-mgmt"}
]
for link in mgmt_connections:
    client.api.connect_node_to_cloud(lab_path, **link)

# NODE_TO_NODE_LINKS
p2p_links = [
    {"src": "R1", "src_label": "Gi1/0/2", "dst": "R2", "dst_label": "Gi1/0/2"},
]
for link in p2p_links:
    client.api.connect_node_to_node(lab_path, **link)

# CLOSE_CONNECTION_TO_EVENG
client.logout()
print("Lab deployment successful.")
