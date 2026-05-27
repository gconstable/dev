# LICENSES
1. Configure device license and reboot: license boot level network-advantage addon dna-advantage

# MTU
2. System mtu is 8978 (CI is different)

# BGP
3. BGP needs a listen range configured before BGP configured even though we are not dynamic? 
   CI-1. "bgp listen range 10.1.0.0/24 peer-group LEAF-EVPN-PEERS" (Spine item)
   CI-2. "bgp listen range 10.1.0.0/24 peer-group INT-EVPN-SPINES" (Leaf item)

# INTERFACES
4. Physical interfaces need to be configured before rest of configuration.

# VERIFICATION COMMANDS
## EVPN - VXLAN
show nve peers
show nve vni
show l2vpn evpn
show bgp l2vpn evpn summary
