# Cisco Symmetric IRB BGP-EVPN VXLAN Lab

This lab bundles the configuration templates and EVE-NG topologies required to deploy a modern, production-grade VXLAN system featuring a dynamic MP-BGP EVPN control plane, symmetric IRB routing, and hardware-efficient ARP suppression.

## Contents
1. `Cisco_EVPN_VXLAN_BestPractice.unl` - EVE-NG XML topology import.
2. `Spine-1_config.txt` - BGP Route Reflector & OSPF core configuration.
3. `Leaf-1_config.txt` - VTEP Leaf-1 configuration (Symmetric IRB + EVPN + VRF Tenant-A).
4. `RESEARCH_DEEP_DIVE.md` - Technical deep-dive on EVPN Route Types, ARP suppression, and design trade-offs.

## Setup Sequence
1. Load the `.unl` topology file into your EVE-NG platform.
2. Ensure you are utilizing a Cisco CSR1000v or C8000v virtual machine.
3. Paste configurations onto `Spine-1` and `Leaf-1` accordingly.
4. Verify OSPF neighbor states (`show ip ospf neighbor`) and MP-BGP peers (`show bgp l2vpn evpn summary`).
