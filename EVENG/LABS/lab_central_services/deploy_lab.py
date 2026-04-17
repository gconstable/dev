# deploy_lab.py
# reference: https://ttafsir.github.io/evengsdk/api_reference/#evengsdk.api.EvengApi.get_lab
import os
from evengsdk.client import EvengClient

# GLOBAL_VARS
LAB_CREATED = False
LAB_NAME = "lab_central_services"

# GET_JENKINS_CREDS
EVE_IP = os.getenv('EVE_SERVER_IP')
EVE_USER = os.getenv('EVE_USERNAME')
EVE_PWD = os.getenv('EVE_PASSWORD')

# GET_NODE_CONFIG_FILES
LAB_CONFIGS = []
directory = (os.getcwd() + ('/EVENG/LABS/{name}/configs').format(name=LAB_NAME))
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

# IMPORT LAB_CONFIGURATION
from config import lab

# IMPORT_OOB_MANAGEMENT
from config import mgmt_cloud

# IMPORT_LAB_CLOUD
from config import lab_cloud

# IMPORT_NODES
from config import nodes

# IMPORT_NODE_TO_CLOUD_CONNECTIONS
from config import node_to_clouds

# IMPORT_NODE_TO_NODE_CONNECTIONS
from config import node_to_node


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
client.api.add_lab_network(LAB_PATH, **mgmt_cloud)

# LAB_PRIVATE_ACCESS
print("Adding lab network access")
client.api.add_lab_network(LAB_PATH, **lab_cloud)

# ADD_NODES
print("Adding lab nodes")
for node in nodes:
    client.api.add_node(LAB_PATH, **node)

# NODE_TO_CLOUD_LINKS
for link in node_to_clouds:
    client.api.connect_node_to_cloud(LAB_PATH, **link)

# NODE_TO_NODE_LINKS
print("Adding node to node connections.")
for link in node_to_node:
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
        
        client.api.upload_node_config(LAB_PATH, node_details['id'], node_cfg_content, configset='default')
        client.api.enable_node_config(LAB_PATH, node_details['id'])
    except Exception as e:
        print("Supplied config file does not match a node with within the lab. ignoring & continuing...")
        print(e)

# START_ALL_NODES
print("starting all nodes within lab.")
resp = client.api.start_all_nodes(LAB_PATH)

# CLOSE_CONNECTION_TO_EVENG
print("Closing connection to eveng.")
client.logout()
print("Lab deployment successful.")
