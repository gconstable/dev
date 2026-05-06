# Cisco CSR1000v VXLAN Static Ingress Replication Lab

This package provides everything required to build, configure, and verify a simplified L2 VXLAN tunnel using Static Ingress-Replication on Cisco IOS-XE.

## Contents
1. `Cisco_Simple_VXLAN.unl` - EVE-NG Cisco-based topology import layout.
2. `VTEP-1_config.txt` - Device configuration script for VTEP-1 (CSR1000v).
3. `VTEP-2_config.txt` - Device configuration script for VTEP-2 (CSR1000v).
4. `eve_generator.py` - Standalone python tool leveraging lxml to dynamically script the lab topology.
5. `RESEARCH_DEEP_DIVE.md` - Full root-level research analysis, packet format layouts, and engineering trade-offs.

## Topology mapping
* **VTEP-1 (CSR1000v)**: GigabitEthernet2 (10.0.0.1/30) <-> GigabitEthernet2 VTEP-2 (10.0.0.2/30)
* **Client-1 (VPCS)**: eth0 <-> GigabitEthernet1 VTEP-1
* **Client-2 (VPCS)**: eth0 <-> GigabitEthernet1 VTEP-2

## Run Instructions
1. Upload `Cisco_Simple_VXLAN.unl` to your EVE-NG instance.
2. Ensure you have the `csr1000v` or `c8000v` image mapped.
3. Paste the contents of `VTEP-1_config.txt` and `VTEP-2_config.txt` to the respective nodes.
4. On Client-1, execute: `ip 192.168.10.11 255.255.255.0`
5. On Client-2, execute: `ip 192.168.10.12 255.255.255.0`
6. Ping Client-2 from Client-1 to watch the data-plane learning mechanism update dynamically.
