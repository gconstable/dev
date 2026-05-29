## Technical Guide: Why EVPN Underlays Belong in the Global Routing Table (GRT)## Executive Summary
In Multi-Protocol BGP (MP-BGP) EVPN VXLAN architectures, a fundamental design rule is the strict separation of the Underlay (Transport Layer) and the Overlay (Tenant Layer).
Industry best practices mandate that all physical core-facing interfaces, VTEP loopbacks, underlay Interior Gateway Protocols (IGPs), and BGP peering addresses reside within the Global Routing Table (GRT) / Default VRF. Virtual Routing and Forwarding (VRF) instances are strictly reserved to isolate overlay tenant traffic.
This guide outlines the architectural, technical, and operational reasons for this standard to ensure fabric stability, scalability, and simplified troubleshooting.
------------------------------
## 1. Architectural Alignment: Underlay vs. Overlay
Modern network virtualization relies on a tiered architecture. Forcing infrastructure components into customer VRFs breaks this structural framework:

* The Underlay Layer (The GRT): The primary purpose of the physical network (Spines and Leaves) is to provide rapid, high-speed IP reachability between VTEP loopbacks. The GRT is natively designed for this baseline transport.
* The Overlay Layer (User VRFs): VRFs exist exclusively to segment and virtualize tenant traffic. Placing infrastructure loopbacks or physical links inside a tenant VRF mixes network management traffic with untrusted customer data traffic, violating the core computer networking tenant of Separation of Concerns.

------------------------------
## 2. Technical Dependencies & Platform Constraints## BGP Recursive Routing Failures
When a BGP neighbor is reached via a route inside a VRF, but the BGP session itself is configured globally (such as the l2vpn evpn address family), the routing engine can encounter recursive lookup failures.

* The global BGP process attempts to resolve the next-hop IP in the GRT.
* If it must rely on leaked routes or indirect VRF paths, it can trigger a routing loop within the control plane.
* This results in BGP session flapping, where the neighbor connection continuously disconnects and reconnects as the routing engine struggles to resolve the next hop.

## Network Virtualization Edge (NVE) Interface Rules
On Cisco IOS-XE, the virtual tunnel endpoint—configured via the interface NVE1 command—sources its VXLAN-encapsulated tunnels from a loopback interface using the source-interface LoopbackX statement.

* By default, the IOS-XE NVE process expects this source loopback to reside in the Global Routing Table.
* Keeping your BGP peering loopback in the GRT allows it to double seamlessly as your VTEP source IP, conforming to standard software expectations.

## Cisco IOS-XE Multi-Protocol BGP Constraints
Unlike Cisco NX-OS (Nexus switches), which features a transport vrf command to map global BGP peers to a specific VRF routing table, Cisco IOS-XE does not natively support crossing VRF boundaries for global BGP address families.

* Forcing a loopback into a VRF means the global router bgp daemon cannot compute a path to the peer.
* Overcoming this requires complex, bidirectional static route leaking between tables, creating an fragile configuration.

------------------------------
## 3. Industry-Wide Consensus & Vendor Standards
The model of keeping the underlay in the default/global routing instance is recognized and deployed by all major networking vendors:

* Cisco Validated Designs (CVD): In the Cisco Campus EVPN VXLAN Deployment Guide, the "Underlay Network Design" configuration blueprints omit the vrf forwarding command from core physical interfaces and VTEP loopbacks, defaulting them to the global instance.
* NVIDIA Networking (Cumulus Linux): The EVPN Deployment Scenarios Guide explicitly states: "The underlay routing table is assumed to be in the default or global routing table, while the overlay routing table is assumed to be in a VRF-specific routing table."
* HPE Aruba Networking: The Aruba AOS-CX VXLAN Multi-Fabric Best Practices mandate: "It is recommended to include all VTEP loopbacks in the underlay default VRF routing."
* Arista Networks: Arista's EOS VXLAN Framework isolates the underlay into the default routing table to limit the security blast radius, preventing tenant environments from reaching or attacking core infrastructure.

------------------------------
## 4. Operational & Engineering Benefits## Reduced Configuration Complexity
Using route leaking to fix a misplaced loopback creates an operational burden. It is:

* Hard to scale: Manual static route-leaking entry tweaks must be added for every single leaf switch introduced to the fabric.
* Prone to human error: Maintaining cross-table static routes increases the likelihood of typos, leading to fabric-wide outages during maintenance windows.

## Simplified Troubleshooting
When an issue occurs, network engineers must be able to diagnose it rapidly using simple tools.

* If the underlay is in the GRT, engineers can verify fabric connectivity using standard, non-VRF commands like ping 10.1.1.1 or traceroute 10.1.1.1.
* If the underlay is buried inside a VRF, engineers must constantly parse multiple routing tables and leak policies (show ip route vrf UNDERLAY_VRF), significantly increasing the Mean Time to Resolution (MTTR).

------------------------------
## Summary Matrix

| Layer | Network Component | Routing Table Context | Primary Responsibility |
|---|---|---|---|
| Underlay | Core Physical Links, VTEP Loopbacks, IGP (OSPF/IS-IS), BGP Peering IPs | Global Routing Table (Default VRF) | Core IP transit. Moves encapsulated VXLAN packets as fast as possible. |
| Overlay | Tenant Subnets, Customer MACs, Virtual Interfaces (SVIs), Anycast Gateways | User-Defined VRFs | Customer isolation. Keeps tenant routing decisions completely separate from the physical backbone. |

------------------------------
To help your team visualize how this looks in practice, would you like me to generate a clean Cisco IOS-XE configuration template showing the exact separation of the global underlay links and overlay VRFs?

