## High-Level Design (HLD): Multi-Tenant Data Center & WAN Infrastructure## 1. Executive Summary & Design Principles
This document outlines the architectural blueprint for a highly scalable, multi-tenant network infrastructure spanning three Data Centers (DCs) and 500 remote sites. The design natively accommodates a growth path from 1 tenant (Day 1) to 100 tenants (Day 3), supporting both modern EVPN-VXLAN encapsulation and legacy VRF-Lite deployments.

## Key Design Pillars
* Strict Multi-Tenancy: Complete control-plane and data-plane isolation using VRFs, MP-BGP, and VXLAN VNIs.
* Separation of Layers: Underlay routing (physical reachability) is entirely decoupled from Overlay routing (tenant traffic).
* Deterministic Traffic Flow: DC1 acts as the Primary hub, while DC2 and DC3 operate as Active/Standby Disaster Recovery (DR) hubs.
* Vendor Agnostic Compute Edge: Open-standards EVPN-VXLAN and eBGP allow seamless integration of Cisco and Dell leaf/compute switches.

------------------------------
## 1. VLAN, VNI & Tenant Schemas
To deliver a highly predictable, automated, and scalable infrastructure across your four data centers, the VLAN, VNI, and VRF mapping schemas must follow a strict mathematical formula.

### 1.1 The Mapping Formula
The schema uses a structured 5-digit number block to prevent overlapping and to simplify configuration generation:

* Tenant ID (T): A value from 1 to 100.
* Layer 2 VLANs: 1000 + T (Internal DC access ports).
* Layer 3 VRF VLAN: 2000 + T (The infrastructure transit VLAN between Leafs and the Cat 8K Edge).
* Layer 2 VNI (Bridging): 10000 + T (Used if extending a specific broadcast domain across DCs).
* Layer 3 VNI (Routing): 30000 + T (The Symmetric L3 VNI transit network that binds the VRF across the fabric).

### 1.2 VRF & VNI Schema Matrix (Tenants 1–100)
This matrix defines the exact control-plane configurations for your 100 tenants across all four data centers.

| Tenant ID | VRF Name | L3 VNI (Symmetric) | L2 VNI (Stretched LAN) | L3 Transit VLAN | L2 LAN VLAN | Route Distinguisher (RD)* | Route Target (RT) [RFC4364] |
|---|---|---|---|---|---|---|---|
| Tenant 1 | Tenant_1 | 30001 | 10001 | 2001 | 1001 | ASN:30001 | 4200000000:30001 |
| Tenant 2 | Tenant_2 | 30002 | 10002 | 2002 | 1002 | ASN:30002 | 4200000000:30002 |
| Tenant 3 | Tenant_3 | 30003 | 10003 | 2003 | 1003 | ASN:30003 | 4200000000:30003 |
| Tenant 4 | Tenant_4 | 30004 | 10004 | 2004 | 1004 | ASN:30004 | 4200000000:30004 |
| ... | ... | ... | ... | ... | ... | ... | ... |
| Tenant 50 | Tenant_50 | 30050 | 10050 | 2050 | 1050 | ASN:30050 | 4200000000:30050 |
| Tenant 51 | Tenant_51 | 30051 | 10051 | 2051 | 1051 | ASN:30051 | 4200000000:30051 |
| ... | ... | ... | ... | ... | ... | ... | ... |
| Tenant 100 | Tenant_100 | 30100 | 10100 | 2100 | 1100 | ASN:30100 | 4200000000:30100 |

*Note on Route Distinguishers (RD): To ensure uniqueness across the 4 data centers, the ASN prefix of the RD dynamically matches the local physical switch/router BGP ASN (e.g., On DC1 Edge, Tenant 1's RD is 4200000001:30001, while on a DC1 Leaf it is 4200000101:30001). The Route Target (RT) remains globally identical across all nodes to facilitate seamless EVPN route importing.

## Example: Tenant 1 (172.16.0.0/23 Allocation)
* Data Center 1 (VLAN 1001): 172.16.0.0/25
* Anycast Gateway IP: 172.16.0.1 (Configured on all DC1 Leaf switches)
* Data Center 2 (VLAN 1001): 172.16.0.128/25
* Anycast Gateway IP: 172.16.0.129 (Configured on all DC2 Leaf switches)
* Data Center 3 (VLAN 1001): 172.16.1.0/25
* Anycast Gateway IP: 172.16.1.1 (Configured on all DC3 Leaf switches)
* Data Center 4 (VLAN 1001): 172.16.1.128/25
* Anycast Gateway IP: 172.16.1.129 (Configured on all DC4 Leaf switches)

## 2. Global IP Addressing & Summarisation Strategy
To ensure clean BGP summarisation and prevent routing table bloat across the 500 remote nodes, the 10.0.0.0/8 and 172.16.0.0/12 private spaces are strictly blocked out.

## 2.1 Infrastructure & Underlay Allocations (10.0.0.0/8)
The underlay network strictly handles physical connectivity, loopbacks, and point-to-point tunnel interfaces. Tenant traffic never runs natively on these subnets.

| Network Block | Use Case / Assignment | Strategy / Detail |
|---|---|---|
| 10.1.0.0/16 | Data Center 1a Underlay | Loopbacks, Spine-Leaf links, Edge-Spine links |
| 10.2.0.0/16 | Data Center 1b Underlay | Loopbacks, Spine-Leaf links, Edge-Spine links |
| 10.3.0.0/16 | Data Center 2 Underlay | Loopbacks, Spine-Edge links |
| 10.4.0.0/16 | Data Center 3 Underlay | Loopbacks, Spine-Edge links |
| 10.10.0.0/16 | DCI Dark Fibre Transit | 10.10.12.0/30 (DC1-DC2), 10.10.13.0/30 (DC1-DC3), etc. |
| 10.100.0.0/14 | WAN Provider Transport | Physical allocations for Catalyst 8K outer WAN interfaces |
| 10.200.0.0/14 | WAN GRE Tunnel Overlay | 10.200.0.0/24 to 10.201.243.0/24 (Point-to-Point GREs to 500 sites) |

## 2.2 Tenant Overlay Range Matrix (172.16.0.0/12)
The entire 172.16.0.0/16 range (65,536 addresses) is dedicated strictly to multi-tenant compute environments (virtual machines, bare-metal app servers, and databases) residing within the four data center fabrics.
To hit your Day 3 target of 100 tenants, the space is carved into /23 blocks (512 IP addresses per tenant). A /16 network contains exactly 128 unique /23 subnets, fitting your 100 tenants perfectly with a buffer of 28 blocks left over.

### 2.2.1 The 4-Way Data Center Compute Split per Tenant
To maintain strict path isolation and clean summary mechanics, every tenant's /23 block is divided into four /25 subnets (128 addresses per data center fabric):

                        [ Tenant 1 Compute Block: 172.16.0.0/23 ]
                        /          |              |             \
                 [ DC1 Pod ]  [ DC2 Pod ]    [ DC3 Pod ]    [ DC4 Pod ]
                172.16.0.0/25 172.16.0.128/25 172.16.1.0/25 172.16.1.128/25

### 2.2.2 The 100-Tenant Data Center Compute Matrix

| Tenant ID | Total Compute Allocation | DC 1 Subnet (/25) | DC 2 Subnet (/25) | DC 3 Subnet (/25) | DC 4 Subnet (/25) |
|---|---|---|---|---|---|
| Tenant 1 | 172.16.0.0/23 | 172.16.0.0/25 | 172.16.0.128/25 | 172.16.1.0/25 | 172.16.1.128/25 |
| Tenant 2 | 172.16.2.0/23 | 172.16.2.0/25 | 172.16.2.128/25 | 172.16.3.0/25 | 172.16.3.128/25 |
| Tenant 3 | 172.16.4.0/23 | 172.16.4.0/25 | 172.16.4.128/25 | 172.16.5.0/25 | 172.16.5.128/25 |
| Tenant 4 | 172.16.6.0/23 | 172.16.6.0/25 | 172.16.6.128/25 | 172.16.7.0/25 | 172.16.7.128/25 |
| ... | Sequential Gap | ... | ... | ... | ... |
| Tenant 50 | 172.16.98.0/23 | 172.16.98.0/25 | 172.16.98.128/25 | 172.16.99.0/25 | 172.16.99.128/25 |
| Tenant 51 | 172.16.100.0/23 | 172.16.100.0/25 | 172.16.100.128/25 | 172.16.101.0/25 | 172.16.101.128/25 |
| ... | Sequential Gap | ... | ... | ... | ... |
| Tenant 100 | 172.16.198.0/23 | 172.16.198.0/25 | 172.16.198.128/25 | 172.16.199.0/25 | 172.16.199.128/25 |

(Note: The 172.16.0.0/16 global block ends at 172.16.255.255, meaning you have a hard ceiling of 128 tenants total if using this specific /16 constraint. If you ever scale to Day N and need more than 128 tenants, we will simply widen this compute pool to a /12 or /14 space).

## 2.3 Remote nodes (Non compute nodes)
To give 500 separate branch locations ample space for user subnets, local management, and voice VLANs without relying on data center infrastructure, we assign a massive /12.

1. Global Nodes Pool: 10.100.0.0/12 (Contains exactly 16 /16 blocks, spanning 10.100.0.0 to 10.115.255.255)
2. Sizing per Node: Each of the 500 sites receives a large /22 subnet (1,024 IP addresses). A /12 block can host up to 4,096 unique /22 networks, meaning your 500 sites use only about 12% of the space, leaving massive room for expansion.

| Remote Node ID | CIDR Allocation | Usable IP Range | Intended Use / Description |
|---|---|---|---|
| Remote Node 1 | 10.100.0.0/22 | 10.100.0.1 – 10.100.3.254 | Local LANs, branch edge routers, and local users |
| Remote Node 2 | 10.100.4.0/22 | 10.100.4.1 – 10.100.7.254 | Local LANs, branch edge routers, and local users |
| Remote Node 3 | 10.100.8.0/22 | 10.100.8.1 – 10.100.11.254 | Local LANs, branch edge routers, and local users |
| Remote Node 4 | 10.100.12.0/22 | 10.100.12.1 – 10.100.15.254 | Local LANs, branch edge routers, and local users |
| ... | Sequential Gap | ... | ... |
| Remote Node 499 | 10.107.204.0/22 | 10.107.204.1 – 10.107.207.254 | Local LANs, branch edge routers, and local users |
| Remote Node 500 | 10.107.208.0/22 | 10.107.208.1 – 10.107.211.254 | Local LANs, branch edge routers, and local users |
| Spare Pools | 10.107.212.0/22 – 10.115.252.0/22 | N/A | Reserved for Day N future remote node expansion (3,596 spare sites remaining) |

## 2.3 Legacy IP Integration & Migration Strategy
Legacy networks using overlapping or unstructured IP space will be integrated via a Three-Phase Migration Strategy:

   1. VRF Isolation: Legacy environments inside the DC are placed into dedicated "Legacy-VRFs" on the Catalyst 8K edge routers.
   2. Interim Non-Encapsulated Peering: Remote sites that cannot support modern encapsulation peer with the WAN edge using standard VRF-Lite over sub-interfaces or point-to-point circuits.
   3. Bi-Directional NAT / Leak-Route Maps: If a legacy site uses an IP address that conflicts with the new structured range, Twice-NAT is implemented on the Catalyst 8K edge routers during the transition window.

## 2.4 WAN GRE Tunnel Overlay (DMVPN)
Because DMVPN uses a shared multipoint subnet per cloud, we no longer use /31 subnets for every link. Instead, each of the 8 DMVPN clouds gets its own large /22 subnet (1,024 IP addresses).
Within each /22 DMVPN cloud:

* IPs .1 to .4 are statically assigned to the 4 Data Center Hub Edges.
* IPs .5 to .504 are dynamically or statically assigned to the 500 remote spokes.

This approach organizes your 8 QoS DMVPN tunnels into an exceptionally neat, predictable slice of your 10.200.0.0/14 block:

| Tunnel ID | QoS / Traffic Class | DSCP / PHB | DMVPN Network Block | Hub Edge IPs (DC1 – DC4) | Spoke Nodes IP Range |
|---|---|---|---|---|---|
| Tunnel 101 | Voice / Real-Time | EF | 10.200.0.0/22 | 10.200.0.1 – 10.200.0.4 | 10.200.0.5 – 10.200.1.248 |
| Tunnel 102 | Video Conferencing | AF41 | 10.200.4.0/22 | 10.200.4.1 – 10.200.4.4 | 10.200.4.5 – 10.200.5.248 |
| Tunnel 103 | Critical Apps (Data 1) | AF31 | 10.200.8.0/22 | 10.200.8.1 – 10.200.8.4 | 10.200.8.5 – 10.200.9.248 |
| Tunnel 104 | Business Apps (Data 2) | AF21 | 10.200.12.0/22 | 10.200.12.1 – 10.200.12.4 | 10.200.12.5 – 10.200.13.248 |
| Tunnel 105 | Network Operations | CS6 | 10.200.16.0/22 | 10.200.16.1 – 10.200.16.4 | 10.200.16.5 – 10.200.17.248 |
| Tunnel 106 | Scavenger Traffic | CS1 | 10.200.20.0/22 | 10.200.20.1 – 10.200.20.4 | 10.200.20.5 – 10.200.21.248 |
| Tunnel 107 | Out-of-Band Mgmt | CS2 | 10.200.24.0/22 | 10.200.24.1 – 10.200.24.4 | 10.200.24.5 – 10.200.25.248 |
| Tunnel 108 | Best Effort Default | BE | 10.200.28.0/22 | 10.200.28.1 – 10.200.28.4 | 10.200.28.5 – 10.200.29.248 |

(Note: These 8 core QoS clouds take up a tiny portion of your allocation—specifically 10.200.0.0 through 10.200.31.255—leaving massive blocks free in the rest of the /14 space for future expansion).

## 2.4.1 BGP Routing Dynamics for the Multi-Tunnel DMVPN Design
WAN Traffic Orchestration Engine: To prevent traffic from choosing paths at random across the 8 parallel DMVPN tunnels, the control plane will utilize BGP eBGP-Multihop to maintain equal-cost path distribution across all 8 tunnel underlays. Actual traffic mapping will be handled at the data plane using Cisco Performance Routing (PfR) or egress QoS DSCP-to-Tunnel mapping policies, ensuring applications (e.g., 172.16.Voice) are deterministically bound to their corresponding QoS Tunnel Interface (Tunnel 101) without altering BGP path vector selections.

1. BGP Cost Community / Local Pref: To prevent traffic from choosing paths at random, apply BGP route-maps on the Hubs and Spokes to match the traffic profiles. For example, the subnet 172.16.Voice is advertised with a high Local Preference exclusively over the Tunnel 101 (10.200.0.0/22) peering session.

## 2.4.2 Cisco Application-Aware Routing (Enhanced Policy-Based Routing (PBR) combined with Object Tracking and IP SLA Probes)
1. To make the router aware of tunnel conditions, the Catalyst 8K edge routers run continuous, sub-second IP SLA tests down the 8 separate DMVPN tunnel interfaces.
1. Next, the router maps application classes based on the inner packet DSCP markings
2. Using a standard policy-map type routing configuration block, the router checks the track states. If the preferred tunnel is healthy, traffic is locked to that specific tunnel interface. If the track object fails, the router skips to the next sequence or drops back to the standard BGP routing table.
3. To activate this behavior across your multi-tenant environment, the routing policy must be applied directly to the ingress interface where the tenant computing blocks or branch LAN connections meet the local router.

Unlike SD-WAN BFD probes which are handled directly in the data plane (ASIC), standard IOS-XE CLI ip sla probes utilize CPU processing. Running multiple active ICMP echo tests across 8 tunnels on 500 remote sites will cause a small, steady CPU utilization load on your core routers. It is vital to set the probe frequency conservatively (e.g., every 1 to 2 seconds instead of every 100 milliseconds) to prevent performance degradation on lower-tier branch hardware.

### 2.4.3 Application to Your 8-Tunnel QoS Design
In this architecture, PfR is what makes the 8-tunnel layout work cleanly without breaking BGP path logic.

                                  [ Catalyst 8K Edge Router ]
                                 /             |             \
  LAN Traffic Ingress          [PfR Engine]  [PfR Engine]  [PfR Engine]
  - Voice Packet (EF)   ====>  Map to Tu101       |             |
  - Video Packet (AF41) ====>       |        Map to Tu102       |
  - Data Packet (BE)    ====>       |             |        Map to Tu108
                                    v             v             v
                                (Tunnel 101)  (Tunnel 102)  (Tunnel 108)


   1. BGP Stays Intact: eBGP sees 8 completely equal-cost paths to a destination and installs them all using ECMP. BGP's path vector table remains untouched and stable.
   2. Data-Plane Interception: When a packet enters the LAN interface of the Catalyst 8K, PfR looks at the packet before the routing engine does.
   3. Deterministic Steering: It matches the DSCP marking (e.g., EF) to your policy and forces that specific flow into Tunnel 101's next-hop identifier.
   4. Dynamic Recovery (SLA Violation): If the MPLS provider drops a queue or experiences a brownout on the physical path carrying Tunnel 101, PfR detects the SLA breach. It instantly shifts the Voice flow to Tunnel 102 or 103 (whichever is the next best compliant path). Once the primary tunnel heals, PfR cleanly restores the traffic to its home queue after a protective dampening window to prevent link flapping. [12, 13] 

------------------------------
## 3. Data Center Fabric Architecture & ASN Strategy
The fabric implements an eBGP-on-Large-Clos design for the underlay, while the overlay utilizes MP-BGP EVPN running on the Catalyst 8K edge routers acting as Route Reflectors (RRs).

               +---------------------------------------+

               |  DC1 Core/Edge: Cat 8K (AS 4200000001)| <-- EVPN Route Reflectors
               +-------------------+---------------+---+

                                   |               |
               +-------------------+---------------+---+

               |       DC1 Spines: Cat 9500 (AS 4200000100)    |
               +--------+---------------------+--------+

                        |                     |
        +---------------+---------------+     +---------------+---------------+

        |  Leaf 1: Cisco/Dell (AS 4200000101) |     |  Leaf 2: Cisco/Dell (AS 4200000102) |
        +-------------------------------------+     +-------------------------------------+

## 3.1 32-Bit Autonomous System Number (ASN) Allocation
| Infrastructure Layer | DC 1 (Primary Hub) | DC 2 (DR Hub) | DC 3 (DR Hub) |
|---|---|---|---|
| Edge Routers (Cat 8K) | 4200000001 (4 Edges) | 4200000002 (2 Edges) | 4200000003 (2 Edges) |
| Spine Layer (Cat 9500) | 4200000100 (4 Spines) | 4200000200 (2 Spines) | 4200000300 (2 Spines) |
| Leaf Layer (Compute Edge) | 4200000101 – 4200000199 | 4200000201 – 4200000299 | 4200000301 – 4200000399 |
| Remote Nodes / Spokes | 4220000000 (Single reused ASN across all 500 sites) | | |

## 3.2 Underlay vs. Overlay Protocol Matrix
* Physical Fabric Underlay: eBGP IPv4 Unicast is configured between Leafs, Spines, and Edges. This maximizes hardware ECMP load balancing across all paths.
* EVPN Control Plane: MP-BGP EVPN (address-family l2vpn evpn) sessions are established directly between the Leaf switches and the Catalyst 8K Edge Routers. The Spines remain pure transport nodes and do not process EVPN routes.
* Route Reflector Design: The Catalyst 8K Edge routers act as the centralized EVPN Route Reflectors (4x RRs in DC1, 2x RRs in DC2 and DC3) for the internal leaf switches.

### 3.2.1 BGP-Only Fabric
In a traditional two-tier Clos (Spine-Leaf) architecture, networks often use an IGP (OSPF/IS-IS) to build the infrastructure's physical reachability (the underlay) and then run iBGP on top for tenant virtual routing.In a BGP-Only Fabric, you strip away the IGP completely:The Underlay: You run standard External BGP (eBGP) between the Leaf switches and Spine switches [RFC7938]. Every Leaf switch pair has its own unique AS, and the Spine switches share an AS. Physical point-to-point links between Leafs and Spines are configured with eBGP peering using simple /30 or /31 subnets [RFC3021].The Overlay: You run Multiprotocol BGP (MP-BGP) over the top of the fabric to handle tenant virtual routing instances (VRFs) via EVPN-VXLAN or traditional VRF-Lite.

### 3.2.2 Why a BGP-Only Fabric is Highly Recommended (Architectural Advantages)
Traditional IGPs use Link-State Advertisements (LSAs) and run the Dijkstra Shortest Path First (SPF) algorithm. When a network scales to hundreds of switches, a single link flapping can cause an entire data centre fabric to constantly recalculate its topology, driving up CPU usage.

BGP uses path-vector metrics and operates as a step-by-step state machine. It handles massive scalability effortlessly (as proven by the global internet table). By utilizing eBGP, the fabric naturally establishes Equal-Cost Multi-Pathing (ECMP) across all four of your spines without running a separate underlay calculation.

### 3.2.3 Strict Error and Failure Isolation (Blast Radius Reduction)
If an IGP experiences an issue (such as a database corruption or severe link flapping), it can impact the entire routing domain. eBGP handles failures locally using explicit peer-to-peer relationships. If a link fails between a Leaf and a Spine, BGP quickly withdraws the path via standard BGP updates. This confines the "blast radius" of a network issue to that single point-to-point connection.

### 3.2.4 Single Control Plane Protocol Space
Operating a BGP-only fabric means your operations and network automation teams only need to monitor, configure, and troubleshoot one protocol. It simplifies policy engine designs (route maps, prefix lists) because the exact same protocol constructs manage both physical link transport and tenant VRF routes.

### 3.2.5 How this applies to your Multi-Vendor Environment
Because a BGP-only architecture relies entirely on open standards, it prevents vendor lock-in. Cisco Catalyst 9500 Spines simply act as fast, predictable eBGP packet forwarders. They do not care if they are talking to a Cisco Leaf or a Dell Leaf.  Because eBGP behavior is identical across vendor operating systems (Cisco NX-OS/IOS-XE and Dell OS10), route propagation, community tagging, and convergence mechanisms behave identically across your entire multi-vendor compute edge.

### 3.2.6 References
This design is fully compliant with the following Internet Engineering Task Force (IETF) Request for Comments (RFCs) and foundational industry white papers:
1. RFC 7938: "Use of BGP for Routing in Large-Scale Data Centers
2. RFC 4271: "A Border Gateway Protocol 4 (BGP-4)"
3. RFC 4364: "BGP/MPLS IP Virtual Private Networks (VPNs)"

## 3.3 Handoff Mechanics (EVPN-VXLAN & VRF-Lite Multi-Vendor)
To design a multi-vendor, multi-tenant hand-off framework that integrates both EVPN-VXLAN and Traditional VRF-Lite without vendor lock-in, the architecture must rely entirely on open-standards protocols. 

Because your compute edge contains a mix of Cisco and Dell hardware, we must eliminate any proprietary fabrics (such as Cisco ACI or fabric extenders) at the hand-off layer. Instead, the Catalyst 8K Edge routers act as the universal translation boundaries between the encapsulated EVPN world and the non-encapsulated VRF-Lite world.

                                  +-----------------------------+
                                  |   DC Edge: Catalyst 8K     |
                                  |   (Symmetric L3 VNI / VRFs) |
                                  +--------------+--------------+

                                                 |
                       +-------------------------+-------------------------+
                       | 802.1Q Sub-interfaces                             | VXLAN Tunnel (Symmetric L3VNI)
                       | (Traditional VRF-Lite)                            | (Modern EVPN-VXLAN Overlay)
                       v                                                   v
        +-----------------------------+                     +-----------------------------+

        |  Legacy / Basic Leaf Switch |                     | Modern EVPN Leaf Switch     |
        |  (Cisco / Dell - L2 Only)   |                     | (Cisco / Dell OS10 Open)    |
        +-----------------------------+                     +-----------------------------+

### 3.3.1 Method A: Modern EVPN-VXLAN Hand-off (Symmetric L3 VNI)
Modern, EVPN-capable leaf switches (Cisco Nexus/Catalyst or Dell PowerSwitch running OS10 Enterprise), traffic remains completely encapsulated inside VXLAN headers as it moves through the Spines up to the Catalyst 8K Edge.

1. Control Plane Standard (RFC 8365): The multi-vendor leafs and the Catalyst 8K edges peer using MP-BGP EVPN (AFI 25, SAFI 70) over the underlay. Tenant MAC addresses and IP prefixes are exchanged using EVPN Type-2 and Type-5 routes.
2. Data Plane Standard (RFC 7348): Traffic is encapsulated in standard VXLAN packets using a globally agreed-upon Layer 3 VNI (Virtual Network Identifier) per tenant.
3. Multi-Vendor Interoperability Rule: The fabric mandates Symmetric L3 VNI Routing [RFC 9136]. Both Cisco and Dell switches support this mode, where routing occurs at both the ingress VTEP (Leaf) and egress VTEP (Edge) over a transit VNI. This avoids the interoperability glitches often found in older asymmetric implementations.

### 3.3.2 Method B: Traditional VRF-Lite Hand-off (802.1Q Multi-VRF)
For legacy compute pods, bare-metal nodes, or legacy leaf switches that lack the hardware or licensing to run VXLAN encapsulation, the Catalyst 8K Edge handles them via physical or logical segmentation.
1. Control Plane Standard (RFC 4364): The Edge router provisions a dedicated standard eBGP IPv4 Unicast session inside that specific tenant’s local VRF to peer with the leaf switch.
2. Data Plane Isolation: Traffic is segmented using standard IEEE 802.1Q (Dot1Q) VLAN tagging across an Ethernet bundle or sub-interfaces. Each tenant VRF is mapped to a unique VLAN ID across the wire.
3. Multi-Vendor Interoperability Rule: Because Dot1Q and standard eBGP are universal across all networking hardware, a legacy Dell switch or Cisco Catalyst switch can peer with the Edge router flawlessly without needing to understand any underlying VXLAN topology.

### 3.3.3 Multi-Vendor Control Plane Mapping Matrix
To ensure that a tenant route learned via VRF-Lite can cross the network and talk to a tenant host inside the EVPN-VXLAN fabric, the Catalyst 8K Edge routers perform a Mutual Route Redistribution and Translation function.

| Architectural Component | Cisco IOS-XE (Cat 8K / Edge) | Dell OS10 (Modern Leaf) | Purpose / Standardization |
|---|---|---|---|
| Tenant Isolation Engine | vrf definition Tenant_X | vrf Tenant_X | Creates the isolated routing table instance per tenant. |
| Route Distinguisher (RD) | rd 4200000001:VNI_ID | rd 4200000101:VNI_ID | Ensures overlapping IPs remain unique in MP-BGP. |
| Route Target (RT) Import/Export | route-target both 100:VNI_ID | route-target both 100:VNI_ID | Inter-switch community string that controls route leaking. |
| EVPN EVPN Instance (EVI) | Automatically bound via RT | evpn; instance VNI_ID type l3 | Creates the EVPN instance mapping for Layer 3. |
| VRF-Lite Peer Engine | router bgp X; address-family ipv4 vrf T | router bgp X; vrf T; address-family ipv4 | Standard eBGP engine used to peer with legacy switches. |

* EVPN-VXLAN Leafs: Standard symmetric L3 VNI routing is configured. VTEP peers use standard BGP EVPN type-2 (MAC/IP) and type-5 (IP Prefix) routes.
* Traditional VRF-Lite Leafs: Multi-vendor switches lacking EVPN capabilities connect via 802.1Q tagged sub-interfaces directly to the Catalyst 8K Edge routers. Standard eBGP runs inside each tenant VRF between the Leaf and Edge.

### 3.3.4 Route Leak and Translation Flow (Step-by-Step Example)
To illustrate the seamless operation of this setup, consider a scenario where a bare-metal server connected to a Legacy Dell Leaf (VRF-Lite) needs to communicate with an application server hosted on a Modern Cisco Leaf (EVPN-VXLAN) within Tenant 1:

1. Route Ingress (VRF-Lite): The Legacy Dell Leaf advertises the bare-metal subnet 172.16.2.0/24 to the Catalyst 8K Edge over a Dot1Q VLAN sub-interface via standard eBGP inside VRF Tenant_1.
2. Route Normalization on Catalyst 8K: The Edge router receives the prefix, injects it into its local VRF Tenant_1 routing table, and notes the next-hop interface.
3. EVPN Export (The Translation Step): Inside the Catalyst 8K BGP process, the router is configured to automatically redistribute ipv4 vrf Tenant_1 routes into the l2vpn evpn address family. The Edge router appends the tenant's standard Route Target (e.g., 64512:10001) and encapsulates the route into an EVPN Type-5 Route Advertisement.
4. Fabric Propagation: The Edge router sends this EVPN Type-5 route to the Spines, which reflect it down to the Modern Cisco Leaf switch.
5. Route Ingress (EVPN): The Modern Cisco Leaf receives the EVPN Type-5 route, matches the Route Target to its local VRF Tenant_1, and installs 172.16.2.0/24 into its VRF routing table. The next hop is set to the VXLAN VTEP IP of the Catalyst 8K Edge router.
6. Data Path Execution: When the application server sends a packet to the bare-metal server, the Modern Cisco Leaf encapsulates the data packet into a VXLAN packet (destined for the Edge router's VTEP) using the tenant's Layer 3 VNI. The Edge router receives the VXLAN packet, strips the header, looks up VRF Tenant_1, and strips the packet down to a standard untagged Ethernet frame to send down the 802.1Q trunk to the Legacy Leaf.

### 3.3.5 Multi-Vendor Best Practices
To prevent performance drops or routing loops at the hand-off layer, The following guard rails are to be implemented.
1. Maximum Prefix Limits: Always configure neighbor x.x.x.x maximum-prefix on the VRF-Lite eBGP sessions facing legacy switches. This ensures a misconfigured legacy or multi-vendor leaf switch cannot accidentally dump thousands of unauthorized routes into the primary data center core.
2. Consistent MTU Settings: Set a global Jumbo MTU of 9216 bytes across the entire physical underlay (Spines, Leafs, and Edge physical links). This ensures that the 50-byte VXLAN encapsulation overhead does not cause packet fragmentation when communicating with non-encapsulated VRF-Lite nodes.
3. AS-Path Cleanliness: When redistributing routes between the VRF-Lite domains and the EVPN overlay, ensure that the Catalyst 8K Edge routers remove or normalize private ASNs if necessary using the as-override or remove-private-as commands to prevent downstream loop-prevention drops.

------------------------------
## 4. WAN Transport & Remote Site Integration
The 500 remote sites connect over a private MPLS L3VPN backbone using dual GRE tunnels terminated on the Catalyst 8K Edge clusters.

       +------------------------------------+      +------------------------------------+

       |   DC1 Edge 1/2 (WAN Conn 1 & 2)    |      |   DC1 Edge 3/4 (WAN Conn 3 & 4)    |
       +-----------------+------------------+      +-----------------+------------------+

                         |                                           |
                         +---------------------+---------------------+

                                               |
                                     [ Private MPLS Network ]
                                               |
                                        (Dual GRE Tunnels)

                                               |
                                     +-------------------+
                                     |  Remote Site K8K  | (ASN 4220000000)
                                     +-------------------+

## 4.1 Encapsulation Architecture
* Each remote site establishes two distinct GRE tunnels back to the Data Centers over the private MPLS provider network.
* For DC1, to balance load across its 4x WAN links, GRE Tunnels from Remote Nodes 1–250 terminate on Edge Routers 1 and 2 (WAN Connection Group A). Tunnels from Remote Nodes 251–500 terminate on Edge Routers 3 and 4 (WAN Connection Group B).
* 
## 4.2 BGP over WAN Overlay Configuration & Loop Prevention
* Protocol: Multi-Protocol eBGP running the address-family vpnv4 or individual VRF IPv4 instances over the GRE tunnel endpoints.
* Spoke Loop Prevention: Because all 500 sites share ASN 4220000000, the Data Center Edge routers must be configured with as-override on their WAN-facing tenant neighbor configurations. This replaces the originating spoke's ASN with the DC Edge ASN before propagating routes to other branches.
* Route Aggregation Rules:
* DC1 Edge Routers: Advertise exactly one aggregate summary per active tenant to the WAN GRE Tunnels: Summary: 172.X.X.0/21 (This covers the local DC1, DC2, and DC3 chunks via the dark fibre interconnect).
   * Remote Spoke Nodes: Advertise only their small locally assigned subnet up the GRE tunnels. The DC Edge routers see these and roll them up into a single tidy 172.X.X.0/20 routing object inside the data center core.

------------------------------
## 5. Multi-DC Interconnectivity (DCI) & Traffic Engineering
The 3 Data Centers are directly interconnected via 100Gbps dark fibre circuits running eBGP between the Catalyst 8K Edge routers.

## 5.1 Active/Standby Routing Orchestration
To enforce the requirement that DC1 is the Primary hub and DC2/DC3 are Standby DR hubs, BGP attributes are modified at the DC Edge:

## Inbound Traffic Engineering (External Sites/Internet to DC)
* DC1 Edge: Advertises tenant prefixes to the WAN with a high Multi-Exit Discriminator (MED) or neutral AS-Path length.
* DC2 / DC3 Edges: Advertises identical tenant prefixes to the WAN but applies AS-Path Prepending (appending its own ASN 3 times). This forces incoming WAN traffic to prefer DC1 paths under normal conditions.

## Outbound Traffic Engineering (DC to Remote Sites/External)
* DC1 Edge: Learns branch routes over the WAN GRE tunnels and redistributes them into the DCI with a high Local Preference (Local-Pref = 200).
* DC2 / DC3 Edges: Learns the same branch routes but sets a lower Local Preference (Local-Pref = 100). Traffic originating inside DC2 or DC3 destined for a remote site will actively cross the 100Gbps DCI dark fibre to exit out of DC1.

------------------------------
## 6. Failure Scenarios & High Availability (HA) Analysis## Scenario A: Loss of Primary WAN Link at a Remote Site
* Mechanism: BGP Keepalive/Hold-timer expiry or BFD (Bidirectional Forwarding Detection) down-event over the primary GRE tunnel interface.
* Convergence Behavior: Traffic instantly shifts to the secondary GRE tunnel interface running over the alternative WAN link. Convergence occurs in under 1 second when BFD is enabled.

## Scenario B: Complete Isolation / Failure of DC1 (Primary Hub)
* Mechanism: Complete loss of DCI peering and WAN GRE tunnel terminations at DC1.
* Convergence Behavior: The WAN provider network and remote branch nodes realize DC1 is unreachable. Because the AS-Path prepended routes advertised by DC2 and DC3 are now the only paths available, the enterprise network automatically converges on DC2 and DC3 as active hubs.

## Scenario C: Leaf Switch Link Failure inside EVPN Fabric
* Mechanism: Physical interface failure between an EVPN Leaf and a Spine switch.
* Convergence Behavior: Equal-Cost Multi-Pathing (ECMP) triggers sub-millisecond rerouting of the VXLAN encapsulated traffic across the remaining operational Spine switches within the underlay fabric.
