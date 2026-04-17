## LAB_CONFIG
LAB_NAME = "cisco_validated_design_dnac"

############
# LAB_DATA #
############
lab = {
    "name": ("Jenkins_Auto_Lab_" + LAB_NAME), 
    "description": "Lab created via Jenkins CI/CD", 
    "path": "/"
  }

##############
# CLOUDS     #
##############
clouds = [
  { 
    "name": "oob_mgmt", 
    "network_type": 
    "pnet0", 
    "left": 300, 
    "top": 400
  },
  {
    "name": "core_services", 
    "network_type": "pnet9", 
    "left": 700, 
    "top": 130
  }
]

############
# NODES    #
############

nodes = [
    {
      "name": "CORE_A", 
      "template": "viosl2", 
      "image": "viosl2-adventerprisek9-m.ssa.high_iron_20200929", 
      "left": 700, 
      "top": 300
    },
     {
      "name": "CORE_B", 
      "template": "viosl2", 
      "image": "viosl2-adventerprisek9-m.ssa.high_iron_20200929", 
      "left": 1400, 
      "top": 300
    },
    {
      "name": "DIST_A", 
      "template": "viosl2", 
      "image": "viosl2-adventerprisek9-m.ssa.high_iron_20200929", 
      "left": 1400, 
      "top": 600
    },
    {
      "name": "DIST_B", 
      "template": "viosl2", 
      "image": "viosl2-adventerprisek9-m.ssa.high_iron_20200929", 
      "left": 1400, 
      "top": 600
    },
    {
      "name": "ACCESS_A", 
      "template": "viosl2", 
      "image": "viosl2-adventerprisek9-m.ssa.high_iron_20200929", 
      "left": 350, 
      "top": 900
    },
    {
      "name": "ACCESS_B", 
      "template": "viosl2", 
      "image": "viosl2-adventerprisek9-m.ssa.high_iron_20200929", 
      "left": 700, 
      "top": 900
    },
    {
      "name": "ACCESS_C", 
      "template": "viosl2", 
      "image": "viosl2-adventerprisek9-m.ssa.high_iron_20200929", 
      "left": 1050, 
      "top": 900
    },
    {
      "name": "ACCESS_D", 
      "template": "viosl2", 
      "image": "viosl2-adventerprisek9-m.ssa.high_iron_20200929", 
      "left": 1400, 
      "top": 900
    },
]

#################
# NODE_TO_CLOUD #
#################

node_to_clouds = [
    {
      "src": "CORE_A", 
      "src_label": "e0", 
      "dst": "oob_mgmt"
    },
    {
      "src": "CORE_B", 
      "src_label": "e0", 
      "dst": "oob_mgmt"
    },
    {
      "src": "DIST_A", 
      "src_label": "e0", 
      "dst": "oob_mgmt"
    },
    {
      "src": "DIST_B", 
      "src_label": "e0", 
      "dst": "oob_mgmt"
    },
    {
      "src": "ACCESS_A", 
      "src_label": "e0", 
      "dst": "oob_mgmt"
    },
    {
      "src": "ACCESS_B", 
      "src_label": "e0", 
      "dst": "oob_mgmt"
    },
    {
      "src": "ACCESS_C", 
      "src_label": "e0", 
      "dst": "oob_mgmt"
    },
    {
      "src": "ACCESS_D", 
      "src_label": "e0", 
      "dst": "oob_mgmt"
    }
  ]

#################
# NODE_TO_NODE  #
#################

node_to_node = [
    {
      "src": "CORE_A", 
      "src_label": "e1", 
      "dst": "CORE_B", 
      "dst_label": "e1"
    },
    {
      "src": "CORE_A", 
      "src_label": "e1", 
      "dst": "DIST_A", 
      "dst_label": "e1"
    },
    {
      "src": "CORE_A", 
      "src_label": "e1", 
      "dst": "DIST_B", 
      "dst_label": "e1"
    },
    {
      "src": "CORE_B", 
      "src_label": "e2", 
      "dst": "DIST_A", 
      "dst_label": "e2"
    },
    {
      "src": "CORE_B", 
      "src_label": "e3", 
      "dst": "DIST_B", 
      "dst_label": "e2"
    },
    {
      "src": "DIST_A", 
      "src_label": "e3", 
      "dst": "DIST_B", 
      "dst_label": "e3"
    },
    {
      "src": "ACCESS_A", 
      "src_label": "e1", 
      "dst": "DIST_A", 
      "dst_label": "e4"
    },
    {
      "src": "ACCESS_A", 
      "src_label": "e2", 
      "dst": "DIST_B", 
      "dst_label": "e4"
    },
    {
      "src": "ACCESS_B", 
      "src_label": "e1", 
      "dst": "DIST_A", 
      "dst_label": "e4"
    },
    {
      "src": "ACCESS_B", 
      "src_label": "e2", 
      "dst": "DIST_B", 
      "dst_label": "e4"
    },
    {
      "src": "ACCESS_C", 
      "src_label": "e1", 
      "dst": "DIST_A", 
      "dst_label": "e5"
    },
    {
      "src": "ACCESS_C", 
      "src_label": "e2", 
      "dst": "DIST_B", 
      "dst_label": "e5"
    },
        {
      "src": "ACCESS_D", 
      "src_label": "e1", 
      "dst": "DIST_A", 
      "dst_label": "e5"
    },
    {
      "src": "ACCESS_D", 
      "src_label": "e2", 
      "dst": "DIST_B", 
      "dst_label": "e5"
    },
  ]

