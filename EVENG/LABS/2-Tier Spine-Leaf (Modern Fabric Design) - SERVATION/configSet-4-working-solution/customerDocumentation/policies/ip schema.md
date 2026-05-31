## Unified Network Architecture, IP Addressing & Multi-Site Legend Playbook
This document serves as the master engineering standard for your multi-tenant network fabric. It integrates your structural, 10-character obfuscated naming conventions with a mathematically aligned IP addressing schema designed for 250+ remote nodes, multi-site stretched EVPN-VXLAN data centres, and co-located corporate campus environments.
------------------------------
## 1. Device Naming Standards (Hostnames)
To prevent geographic location mapping or network role discovery by unauthorized users tracking syslogs, telemetry streams, or traceroutes, a strict 10-character encoded pattern is enforced across all infrastructure components.
## The 10-Character Algorithmic Pattern

[Site] - [Domain][Type] - [Year] - [Index]

## Component Breakdown & Translation Keys

| Component | Format | Description / Lookup Values |
|---|---|---|
| [Site] | XX (2 Letters) | Obfuscated Site Identifier: A randomized, non-human-readable two-letter uppercase code mapped in the secure IPAM (NetBox). Completely hides country, city, and building index. |
| [Domain] | 1 - 5 (1st Digit) | Physical Environment Domain: Identifies the macro-segment or physical environment where the device resides (see Hierarchical Matrix below). |
| [Type] | 01 - 10 (2nd & 3rd Digit) | Universal Hardware Functional Type: Symmetrically identifies the specific functional layer or role the hardware performs across all domains. |
| [Year] | A6 - B7 (2 Chars) | Deployment Epoch: Identifies the procurement block year and hardware generation profile. A6 = 2026 Deployment Cycle B7 = 2027 Deployment Cycle |
| [Index] | 001 - 250 (3 Digits) | Node Serialization Index: Unique sequential hardware counter for that site. For remote branch devices, this matches the assigned Site ID. |

## The Comprehensive Symmetrical Domain & Hardware Matrix

| Functional Type ([Type]) | Domain 1: Data Centre (1XX) | Domain 2: Campus (2XX) | Domain 3: Multi-Tenant (3XX) | Domain 4: Security Services (4XX) | Domain 5: Collaboration/Mgmt (5XX) |
|---|---|---|---|---|---|
| 01 = Core / Backbone | 101 Fabric Spine | 201 Campus Core Switch | 301 Tenant Allocated Switch | 401 Central Corporate Firewall | 501 Central Identity/Federation Appliance |
| 02 = Local Access | 102 Fabric Leaf | 202 Campus Access Switch | 302 Tenant Dedicated Firewall | 402 Reverse Proxy / Load Balancer | 502 Session Border Controller (SBC) |
| 03 = Gateway / Dist | 103 Border Leaf | 203 Campus Distribution Switch | 303 Tenant Dedicated Router | 403 Secure Web Gateway (SWG) / Forward Proxy | 503 Out-of-Band Management Switch |
| 04 = Core Router | 104 Fabric Border Router | 204 Campus WAN Router | 304 Tenant External Transit Router | 404 Intrusion Prevention System (IPS) | 504 Voice Gateway / PBX Controller |
| 05 = Branch Router | 105 DC Edge Internet Router | 205 Remote Branch Router | 305 Tenant Customer Edge (CE) | 405 VPN Concentrator Gateway | 505 Call Session Logging Server |
| 06 = Wireless Control | 106 DC Virtual Wireless Appliance | 206 Campus Wireless Controller | 306 Tenant Dedicated Wireless Gateway | 406 Wireless Security / WIPS Server | 506 Telemetric Collector / Flow Broker |
| 07 = Network Compute | 107 SDN Fabric Controller | 207 Local Branch Compute Node | 307 Tenant Managed Bare-Metal Node | 407 Bastion Host / Jump Box Server | 507 IPAM / DHCP / DNS Core Server |
| 08 = Terminal Sync | 108 DC Console Server (Terminal) | 208 Branch Serial Console Box | 308 Tenant Managed Console Device | 408 AAA Security Server (TACACS) | 508 NTP / Network Time Source Host |
| 09 = Network Storage | 109 NVMe Fabric Storage SAN | 209 Local Office NAS Backing | 309 Tenant Partitioned Storage LUN | 409 Cryptographic Key Storage HSM | 509 Network Log Archive Host (Syslog) |
| 10 = Network Virtual | 110 Virtual Switch Hypervisor | 210 Branch SD-WAN Edge Virtual | 310 Tenant Virtual Router / NFV Instance | 410 Virtual Firewall Appliance (vFW) | 510 Network Monitoring Host (SNMP/gRPC) |

------------------------------
## 2. Master Site ID & Domain Mapping Table
To maintain absolute obfuscation, a single physical facility housing both a Data Centre fabric and a Corporate Campus network under the same roof is assigned two distinct Site IDs: a low index number for its Data Centre infrastructure and a high index number (+100 offset) for its Campus environment.

| 2-Letter Code ([Site]) | Assigned Site ID | Physical Facility Architectural Role | WAN Infrastructure Subnet (10.[Site_ID].0.0/16) | Management Subnet Pool (10.[Site_ID].99.0/24) |
|---|---|---|---|---|
| AA | 001 | Hub 1: Data Centre Fabric | 10.1.0.0/16 | 10.1.99.0/24 |
| AA | 101 | Hub 1: Local Corporate Campus | 10.101.0.0/16 | 10.101.99.0/24 |
| BB | 002 | Hub 2: Data Centre Fabric | 10.2.0.0/16 | 10.2.99.0/24 |
| BB | 102 | Hub 2: Local Corporate Campus | 10.102.0.0/16 | 10.102.99.0/24 |
| QG | 003 | Remote Branch Office 003 | 10.3.0.0/16 | 10.3.99.0/24 |
| MJ | 004 | Remote Branch Office 004 | 10.4.0.0/16 | 10.4.99.0/24 |
| ... | ... | ... | ... | ... |
| TR | 142 | Remote Branch Office 142 | 10.142.0.0/16 | 10.142.99.0/24 |
| ... | ... | ... | ... | ... |
| PL | 250 | Remote Branch Office 250 | 10.250.0.0/16 | 10.250.99.0/24 |

Operational Naming Rule Example: Inside physical building AA, a data centre border leaf switch uses hostname AA-103-A6-001 (Site ID 001), while a user access switch in the office upstairs uses AA-202-A6-001 (Site ID 101).
------------------------------
## 3. Co-Located Data Centre & Campus Subnet Allocation Matrix## Domain 1: Data Centre Fabric Core (10.[0-99].X.X)
Data Centre fabrics use low Site IDs (001–099). Physical interconnects utilize /31 subnets (2 host IPs) to eliminate overhead.

* 10.[Site_ID].0.0/24 $\rightarrow$ VTEP Loopbacks & Loopback 0 BGP Router IDs.
* Example: Spine AA-101-A6-001 = 10.1.0.1/32
   * Example: Leaf AA-102-A6-001 = 10.1.0.11/32
* 10.[Site_ID].1.0/24 $\rightarrow$ Core Spine 01 physical point-to-point /31 link pool.
* 10.1.1.0/31 $\rightarrow$ Core Spine 01 to Access Leaf 01 (.0 on Spine, .1 on Leaf)
   * 10.1.1.2/31 $\rightarrow$ Core Spine 01 to Access Leaf 02 (.2 on Spine, .3 on Leaf)
* 10.[Site_ID].2.0/24 $\rightarrow$ Core Spine 02 physical point-to-point /31 link pool.

## Domain 2: Campus & Remote Node Local Infrastructure (10.[100-250].X.X)
Campus environments and standard remote branches use Site IDs (100–250). Their internal network segments maintain third-octet byte alignment:

* 10.[Site_ID].0.0/24 $\rightarrow$ Local system loopbacks and local WAN upstream peering blocks.
* 10.[Site_ID].10.0/24 $\rightarrow$ Domain 202 Corporate wired user devices (Desktops, Laptops).
* 10.[Site_ID].15.0/24 $\rightarrow$ Domain 206 Corporate wireless client access space (Wi-Fi).
* 10.[Site_ID].20.0/24 $\rightarrow$ Domain 502/504 Voice layers (VoIP Desk Phones, call endpoints).
* 10.[Site_ID].30.0/24 $\rightarrow$ Domain 502 Video conferencing codecs, boardroom displays, and media.
* 10.[Site_ID].40.0/24 $\rightarrow$ Domain 401/404 Physical security layers (IP Cameras, badge readers).
* 10.[Site_ID].99.0/24 $\rightarrow$ Domain 503 Dedicated Out-of-Band Hardware Management interfaces.

------------------------------
## 4. Multi-Tenant Data Centre Customer Space Matrix (172.16.0.0/12)
To insulate infrastructure underlay routing from tenant operations, tenants utilize the private 172.16.0.0/12 block inside the data centre fabric. Replace [XYZ] with the active Tenant ID (100 to 999).

172.16.0.0/12 (Multi-Tenant Data Centre Customer Space)
 ├── 172.16.0.0/16   --> Shared Infrastructure Zone (Common NTP, DNS, IPAM Services)
 ├── 172.17.0.0/16   --> External Production Tenants Zone (Tenant IDs 100 to 199)
 ├── 172.18.0.0/16   --> Internal Testing / Lab Tenants Zone (Tenant IDs 200 to 299)
 └── 172.19.0.0/16   --> Public Edge DMZ Transit Zone (Tenant Firewalls / Load Balancers)

## Symmetrical Tenant Feature Translation Matrix

| Multi-Site Operational Component | Structural Alignment Pattern | Production Example: Tenant 105 | Production Example: Tenant 210 |
|---|---|---|---|
| Tenant Identifier | [XYZ] (3 Digits) | 105 | 210 |
| VRF Context Name | VRF-T[XYZ] | VRF-T105 | VRF-T210 |
| Layer 3 VNI (Routing) | 10[XYZ] | 10105 | 10210 |
| Layer 2 VNI (Stretched Bridging) | 20[XYZ] | 20105 | 20210 |
| DC Core Handoff 802.1Q VLAN | 1[XYZ] | Vlan1105 | Vlan1210 |
| Tenant Payload DC Subnet | 172.17.[XYZ].0/24 | 172.17.105.0/24 | 172.17.210.0/24 |
| Anycast Fabric Gateway IP | 172.17.[XYZ].1 | 172.17.105.1 | 172.17.210.1 |
| Border Leaf Gateway IP | 172.17.[XYZ].2 | 172.17.105.2 | 172.17.210.2 |
| Customer Edge Router Peering IP | 172.17.[XYZ].10 | 172.17.105.10 | 172.17.210.10 |

------------------------------
## 5. Multi-Class WAN Tunnel Addressing
Tenant isolation is extended over your physical WAN links using up to 8 distinct GRE tunnels per location to separate and engineer traffic classes natively.
$$\text{Virtual GRE Tunnel Subnet Pattern:} \quad \mathbf{10.[Site\_ID].[Traffic\_Class\_ID].X / 31}$$ 
## Universal Traffic Class Matrix (Site 142 Examples Connecting to DC Hub 001)

| Class ID | Traffic Classification / Queue Target | Target DSCP | DC Hub 001 Gateway IP | Branch 142 Router IP |
|---|---|---|---|---|
| 0 | Voice Media / Real-Time Streams | EF (DSCP 46) | 10.142.0.0 | 10.142.0.1 |
| 1 | Interactive Video Conferencing | AF41 (DSCP 34) | 10.142.1.0 | 10.142.1.1 |
| 2 | Low-Latency Database Syncs | AF31 (DSCP 26) | 10.142.2.0 | 10.142.2.1 |
| 3 | Primary Cloud Web Applications | AF21 (DSCP 18) | 10.142.3.0 | 10.142.3.1 |
| 4 | Operational Technology / IoT Systems | AF11 (DSCP 10) | 10.142.4.0 | 10.142.4.1 |
| 5 | Bulk Data Transfers / Storage Backups | CS2 (DSCP 16) | 10.142.5.0 | 10.142.5.1 |
| 6 | Out-of-Band Management & Telemetry | CS6 (DSCP 48) | 10.142.6.0 | 10.142.6.1 |
| 7 | Standard Internet / Best Effort Traffic | DF (DSCP 0) | 10.142.7.0 | 10.142.7.1 |

------------------------------
## 6. Hostname & Telemetry Validation Guide for Administrators
For administration tools running automated verification scripts, CI/CD linting engines, or real-time telemetry analytics pipelines, the encoding engine uses the following standardized regular expression grouping to split and process device identity variables dynamically:

* To extract and categorize Hostname Attributes:
^(?P<site>[A-Z]{2})-(?P<domain>\d)(?P<type>\d{2})-(?P<epoch>[A-Z0-9]{2})-(?P<index>\d{3})$

Operational Troubleshooting Example: An automated telemetry dashboard catches an interface drop on destination IP address 10.142.0.1.

   1. The platform executes regex extraction against the active network log.
   2. 10.142.X.X immediately decodes as Remote Branch Site 142 (Obfuscated lookup hostname code: TR).
   3. 10.X.0.X instantly identifies the drop as Traffic Class 0 (Voice Media / Real-Time Streams).
   4. The engineer logs straight into TR-205-A6-142 to isolate the voice queue immediately without looking up external maps.

------------------------------
Now that the master playbook completely structures your obfuscated naming matrices, co-located environments, and aligned IP address blocks, what layer should we build next? We can define the VLAN numbering and data centre trunking ranges, or establish the BGP routing configuration syntax templates to pass traffic between these boundaries.

