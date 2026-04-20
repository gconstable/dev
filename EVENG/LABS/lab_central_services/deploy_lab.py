# REFERENCES
# reference: https://ttafsir.github.io/evengsdk/api_reference/#evengsdk.api.EvengApi.get_lab

# MODULES / CONFIGS
import os, json
from evengsdk.client import EvengClient
from config import lab                                                                            # IMPORT LAB_CONFIGURATION
from functions import get_api_command_node                                                        # IMPORT FUNCTION TO CHECK API COMMANDS FOR NODES
from functions import get_api_command_n2c                                                         # IMPORT FUNCTION TO CHECK API COMMANDS FOR N2C LINKS 
from functions import get_api_command_n2n                                                         # IMPORT FUNCTION TO CHECK API COMMANDS FOR N2N  LINKS 

# GLOBAL_VARS
LAB_CREATED = False                                                                               # LAB_CREATED_BOOLEAN
LAB_PATH = f"{lab['path']}{lab['name']}.unl"                                                      # LAB_PATH
EVE_IP = os.getenv('EVE_SERVER_IP')                                                               # JENKINS - EVE IP
EVE_USER = os.getenv('EVE_USERNAME')                                                              # JENKINS - EVE USERNAME
EVE_PWD = os.getenv('EVE_PASSWORD')                                                               # JENKINS - EVE PASSWORD

# CONFIGURE_EVENG_CONNECTION
client = EvengClient(EVE_IP, protocol="https", ssl_verify=False, log_file="eveng.log")            # SET EVENG CONNECTION DETAILS
client.disable_insecure_warnings()                                                                # DISABLE INSECURE WARNINGS ON CONNECTION
client.login(username=EVE_USER, password=EVE_PWD)                                                 # SET CONNECTION USERNAME / PASSWORD
client.set_log_level('DEBUG')                                                                     # SET LOG LEVEL TO DEBUG

#################
# GENERATE_LAB #
#################

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
# LOAD_LAB_DATA #
#################

# GET_CLOUD_DATA_FROM_DIRECTORY
try:
    LAB_CLOUDS = []
    LAB_NODES = []
    LAB_LINKS_N2C = []
    LAB_LINKS_N2N = []

    cfg_dir = (os.getcwd() + ('/EVENG/LABS/{name}/lab_configs').format(name=LAB_NAME))
    for filename in os.listdir(cfg_dir):
        if "cloud" in filename and filename.endswith('.json') and "template" not in filename:
            LAB_CLOUDS.append(os.path.join(cfg_dir, filename)) 

        if "node" in filename and filename.endswith('.json') and "template" not in filename:
            LAB_NODES.append(os.path.join(cfg_dir, filename))
        
        if "n2c" in filename and filename.endswith('.json') and "template" not in filename:
            LAB_LINKS_N2C.append(os.path.join(cfg_dir, filename))
        
        if "n2n" in filename and filename.endswith('.json') and "template" not in filename:
            LAB_LINKS_N2N.append(os.path.join(cfg_dir, filename))
except Exception as e:
    print("Error loading lab data from directory. Check that cloud, node, and link data files are properly formatted and located within the correct directory.")
    print(e)

# PROCESS_LOADED_LAB_CONFIGS
ci = ""
ci_check = ""

try:
    ## ADD_CLOUDS
    for cloud in LAB_CLOUDS:
        print("Adding cloud: " + cloud['name'])
        client.api.add_lab_network(LAB_PATH, **cloud)

    ## ADD_NODES
    for node in LAB_NODES:
        print("Adding node: " + node['name'])

        json_input = node
        ci = json.loads(json_input)
        ci_check = get_api_command_node(ci)
        
        if ci_check == "ADD":
            client.api.add_node(LAB_PATH, **node)
        
        ci = ""
        ci_check = ""

    ## ADD_NODE_TO_CLOUD_LINKS
    for link in LAB_LINKS_N2C:
        print("Adding link from node: " + link['src'] + " to cloud: " + link['dst'])

        json_input = node
        ci = json.loads(json_input)
        ci_check = get_api_command_n2c(ci)
        
        if ci_check == "ADD":
            client.api.connect_node_to_cloud(LAB_PATH, **link)
        
        ci = ""
        ci_check = ""

    # ADD_NODE_TO_NODE_LINKS
    for link in LAB_LINKS_N2N:
        print("Adding link from node: " + link['src'] + " to node: " + link['dst'])

        json_input = node
        ci = json.loads(json_input)
        ci_check = get_api_command_n2n(ci)
        
        if ci_check == "ADD":
            client.api.connect_node_to_node(LAB_PATH, **link)
        
        ci = ""
        ci_check = ""


except Exception as e:
    print("Error processing lab data. Check that cloud, node, and link data files are properly formatted and contain valid data.")
    print(e)

##############################
# LOAD DEVICE CONFIGURATIONS #
##############################

try:
    # GET_NODE_CONFIG_FILES_FROM_DIRECTORY
    LAB_CONFIGS = []
    cfg_directory = (os.getcwd() + ('/EVENG/LABS/{name}/device_configs').format(name=LAB_NAME))
    for filename in os.listdir(cfg_directory):
        if filename.endswith('.cfg'):
            LAB_CONFIGS.append(os.path.join(cfg_directory, filename)) 

    # LOAD_DEVICE_CONFIGS_TO_NODES
    for node_cfg in LAB_CONFIGS:
        node_name = (os.path.splitext(os.path.basename(node_cfg))[0]).upper()
        try:
            node_details = client.api.get_node_by_name(LAB_PATH, node_name)
            
            with open(node_cfg, 'r') as file:
                node_cfg_content = file.read()
            
            client.api.upload_node_config(LAB_PATH, node_details['id'], node_cfg_content, configset='default')
            client.api.enable_node_config(LAB_PATH, node_details['id'])
        except Exception as e:
            print("Supplied config file does not match a node with within the lab. ignoring & continuing...")
            print(e)
except Exception as e:
    print("Error loading device configurations to nodes. Check that config files are properly formatted and named to match lab nodes.")
    print(e)

##############################
# START_NODES                #
##############################

# START_ALL_NODES
print("starting all nodes within lab.")
resp = client.api.start_all_nodes(LAB_PATH)

##############################
# CLOSE_CONNECTION_TO_SERVER #
##############################

# CLOSE_CONNECTION_TO_EVENG
print("Closing connection to eveng.")
client.logout()
print("Lab deployment successful.")
