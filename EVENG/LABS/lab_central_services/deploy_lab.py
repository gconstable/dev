# REFERENCES
# reference: https://ttafsir.github.io/evengsdk/api_reference/#evengsdk.api.EvengApi.get_lab

# MODULES / CONFIGS
import os, json
from evengsdk.client import EvengClient
from config import *                                                                             # IMPORT LAB_CONFIGURATION
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
    resp = client.api.get_lab(LAB_PATH)                                                            # CHECK IF LAB EXISTS

    if resp['status'] == "success":                                                                # IF LAB FOUND CLOSE LAB
      print("lab found.")                                                                          # MSG CUSTOMER
      LAB_CREATED = True                                                                           # SET LAB CREATED BOOLEAN TO TRUE
      print("closing lab.")                                                                        # MSG CUSTOMER                                      
      resp = client.api.close_lab()                                                                # CLOSE LAB                                    
      print("stopping all nodes within lab.")                                                      # MSG CUSTOMER    
      resp = client.api.stop_all_nodes(LAB_PATH)                                                   # STOP ALL NODES WITHIN LAB

except Exception as e:
    print("no lab found.")
    print (e)
finally:
  if LAB_CREATED == True:                                                                          # IF LAB CREATED IS TRUE, MSG CUSTOMER             
    print("Lab was already created.")                                                              # MSG CUSTOMER

  if LAB_CREATED == False:                                                                         # IF LAB CREATED IS FALSE, CREATE LAB
    print("creating lab.")                                                                         # MSG CUSTOMER
    resp = client.api.create_lab(**lab)                                                            # CREATE LAB WITH CONFIGURED PROPERTIES
    LAB_CREATED = True                                                                             # SET LAB CREATED BOOLEAN TO TRUE

#################
# LOAD_LAB_DATA #
#################

# GET_CLOUD_DATA_FROM_DIRECTORY
try:
    LAB_CLOUDS = []                                                                                 # INITIALIZE LIST TO HOLD CLOUD CONFIGS
    LAB_NODES = []                                                                                  # INITIALIZE LIST TO HOLD NODE CONFIGS
    LAB_LINKS_N2C = []                                                                              # INITIALIZE LIST TO HOLD NODE TO CLOUD LINK CONFIGS
    LAB_LINKS_N2N = []                                                                              # INITIALIZE LIST TO HOLD NODE TO NODE LINK CONFIGS

    cfg_dir = (os.getcwd() + ('/EVENG/LABS/{name}/lab_configs').format(name=LAB_NAME))              # DEFINE DIRECTORY TO LOAD LAB CONFIGS FROM
    
    for filename in os.listdir(cfg_dir):                                                            # ITERATE THROUGH FILES IN CONFIG DIRECTORY
        if "cloud" in filename and filename.endswith('.json') and "template" not in filename:
            JSON_FILE_PATH = os.path.join(cfg_dir, filename)
            JSON_DATA = json.load(open(JSON_FILE_PATH))                           
            LAB_CLOUDS.append(JSON_DATA) 

        if "node" in filename and filename.endswith('.json') and "template" not in filename:
            JSON_FILE_PATH = os.path.join(cfg_dir, filename)
            JSON_DATA = json.load(open(JSON_FILE_PATH))                           
            LAB_NODES.append(JSON_DATA)
        
        if "n2c" in filename and filename.endswith('.json') and "template" not in filename:
            JSON_FILE_PATH = os.path.join(cfg_dir, filename)
            JSON_DATA = json.load(open(JSON_FILE_PATH))                           
            LAB_LINKS_N2C.append(JSON_DATA)
        
        if "n2n" in filename and filename.endswith('.json') and "template" not in filename:
            JSON_FILE_PATH = os.path.join(cfg_dir, filename)
            JSON_DATA = json.load(open(JSON_FILE_PATH))                           
            LAB_LINKS_N2N.append(JSON_DATA)

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
        
        resp = client.api.get_lab_network_by_name(LAB_PATH, cloud['name'])
        print(resp)
        if resp['name']:
            data = resp
            for i in resp:
                if i in cloud:
                    if i == "type":
                        data[i] = cloud["network_type"]
                    
                    data[i] = cloud[i]                   

            print(data)
            data.pop('id', None)
            print(resp['id'])
            print(data)
            client.api.edit_lab_network(LAB_PATH, resp['id'], **data)                                                               # IF LAB FOUND CLOSE LAB

        else:
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
