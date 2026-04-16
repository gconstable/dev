# deploy_lab.py
import os
from evengsdk.client import EvengClient

# Get credentials from environment variables (set in Jenkins)
EVE_IP = os.getenv('EVE_SERVER_IP')
EVE_USER = os.getenv('EVE_USERNAME')
EVE_PWD = os.getenv('EVE_PASSWORD')

client = EvengClient(EVE_IP, protocol="http")
client.disable_insecure_warnings()
client.login(username=EVE_USER, password=EVE_PWD)

# Create lab from the topology file
# Note: Ensure evengsdk is installed on the Jenkins runner
os.system(f"eve-ng lab create-from-topology -t topology.yaml")

print("Lab deployment successful.")
