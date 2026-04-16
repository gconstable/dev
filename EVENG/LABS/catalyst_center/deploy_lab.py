# deploy_lab.py
# reference: https://ttafsir.github.io/evengsdk/api_reference/#evengsdk.api.EvengApi.get_lab
import os
from evengsdk.client import EvengClient

# GLOBAL_VARS
LAB_CREATED = False
LAB_NAME = "catalyst_center"

# GET_JENKINS_CREDS
EVE_IP = os.getenv('EVE_SERVER_IP')
EVE_USER = os.getenv('EVE_USERNAME')
EVE_PWD = os.getenv('EVE_PASSWORD')

# GET_NODE_CONFIG_FILES
LAB_CONFIGS = []
directory = (os.getcwd() + '/EVENG/LABS/catalyst_center/configs')
for filename in os.listdir(directory):
    if filename.endswith('.cfg'):
        LAB_CONFIGS.append(os.path.join(directory, filename)) 

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
  "name": ("Jenkins_Auto_Lab_" + LAB_NAME), 
  "description": "Lab created via Jenkins CI/CD", 
  "path": "/"
}

# LAB_PATH
LAB_PATH = f"{lab['path']}{lab['name']}.unl"

# CHECK_FOR_LAB_CREATE_IF_NO_LAB
try:
    # CHECK_FOR_LAB
    resp = client.api.get_lab(LAB_PATH)

    # IF_LAB_CLOSE_STOP_DELETE
    if resp['status'] == "success":
      print("lab found.")
      print("closing lab.")
      resp = client.api.close_lab()
      
      print("stopping all nodes within lab.")
      resp = client.api.stop_all_nodes(LAB_PATH)
     
      print("deleting lab.")
      resp = client.api.delete_lab(LAB_PATH)
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
print("Adding management network")
mgmt_cloud = {"name": "oob_mgmt", "network_type": "pnet0", "left": 700, "top": 130}
client.api.add_lab_network(LAB_PATH, **mgmt_cloud)

# ADD_NODES
print("Adding lab nodes")
nodes = [
    {"name": "R1", "template": "cat9kv", "image": "cat9kv-17.15.01", "left": 300, "top": 300},
    {"name": "R2", "template": "cat9kv", "image": "cat9kv-17.15.01", "left": 600, "top": 300},
]
for node in nodes:
    client.api.add_node(LAB_PATH, **node)

# NODE_TO_OOB_MGMT
print("Adding node management connections.")
mgmt_connections = [
    {"src": "R1", "src_label": "Gi1/0/1", "dst": "oob_mgmt"},
    {"src": "R2", "src_label": "Gi1/0/1", "dst": "oob_mgmt"}
]
for link in mgmt_connections:
    client.api.connect_node_to_cloud(LAB_PATH, **link)

# NODE_TO_NODE_LINKS
print("Adding node to node connections.")
p2p_links = [
    {"src": "R1", "src_label": "Gi1/0/2", "dst": "R2", "dst_label": "Gi1/0/2"},
]
for link in p2p_links:
    client.api.connect_node_to_node(LAB_PATH, **link)

# LOAD_CONFIGS_TO_NODES
for node_cfg in LAB_CONFIGS:
    node_name = (os.path.splitext(os.path.basename(node_cfg))[0]).upper()
    print(node_name)
    try:
        node_details = client.api.get_node_by_name(LAB_PATH, node_name)
        print(node_details)
        with open(node_cfg, 'r') as file:
            node_cfg_content = file.read()
        
        client.api.upload_node_config(LAB_PATH, node_details['id'], node_cfg_content, configset='default', enable=True)
    except Exception as e:
        print("Supplied config file does not match a node with name: {name} within the lab. continuing..."),format(name=node_name)
        print(e)

# START_ALL_NODES
print("stopping all nodes within lab.")
resp = client.api.start_all_nodes(LAB_PATH)

# CLOSE_CONNECTION_TO_EVENG
print("Closing connection to eveng.")
client.logout()
print("Lab deployment successful.")
