## LAB_CONFIG
LAB_NAME = "lab_central_services"

# LAB_DATA
lab = {
    "name": ("Jenkins_Auto_Lab_" + LAB_NAME), 
    "description": "Lab created via Jenkins CI/CD", 
    "path": "/"
  }

# OOB_MGMT
mgmt_cloud = {
    "name": "oob_mgmt", 
    "network_type": 
    "pnet0", 
    "left": 300, 
    "top": 400
  }

# LAB_CLOUD
lab_cloud = {
    "name": "core_services", 
    "network_type": "pnet9", 
    "left": 700, 
    "top": 130
  }

nodes = [
    {
      "name": "PE01", 
      "template": "vios", 
      "image": "vios-adventerprisek9-m.spa.159-3.m9", 
      "left": 700, 
      "top": 300
    },
    {
      "name": "CORE_SW01", 
      "template": "viosl2", 
      "image": "viosl2-adventerprisek9-m.ssa.high_iron_20200929", 
      "left": 700, 
      "top": 500
    },
]

# NODE_TO_CLOUD_LINKS
node_to_clouds = [
    {
      "src": "PE01", 
      "src_label": "Gi0/1", 
      "dst": "oob_mgmt"
    },
    {
      "src": "CORE_SW01", 
      "src_label": "E0", 
      "dst": "oob_mgmt"
    },
    {
      "src": "PE01", 
      "src_label": "Gi0/2", 
      "dst": "core_services"
    }
  ]

# NODE_TO_NODE_LINKS
node_to_node = [
    {"src": "PE01", 
     "src_label": "Gi0/3", 
     "dst": "CORE_SW01", 
     "dst_label": "E3"
    }
  ]

