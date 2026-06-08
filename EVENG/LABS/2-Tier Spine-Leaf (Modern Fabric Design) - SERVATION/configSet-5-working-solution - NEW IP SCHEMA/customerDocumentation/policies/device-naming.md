## Network Infrastructure Architecture & Administration Playbook
This document serves as the unified standard for naming conventions, hardware tagging, and device roles. It is designed to be easily readable for human engineers during on-call troubleshooting while remaining structured enough for automated asset inventory and network orchestration pipelines.
------------------------------
## 1. Device Naming Standards (Hostnames)
To prevent geographic location mapping or network role discovery by unauthorized users tracking syslogs or traceroutes, a strict 10-character encoded pattern is enforced for all hostnames.
## The 10-Character Algorithmic Pattern

[Site] - [Role] - [Year] - [Index]

## Component Breakdown & Translation Keys

| Component | Format | Description / Lookup Values |
|---|---|---|
| [Site] | XX (2 Letters) | Obfuscated Site Identifier: A randomized two-letter uppercase code mapped in the secure IPAM (NetBox). Completely hides country, city, and building index. |
| [Role] | 301 - 850 (3 Digits) | Operational Layer Class: Tells engineers exactly what functional layer or specialized service tier the device operates in (see Master Device Role Codes below). |
| [Year] | A6 - B7 (2 Chars) | Deployment Epoch: Identifies the procurement block year and hardware generation profile. A6 = 2026 Deployment Cycle B7 = 2027 Deployment Cycle |
| [Index] | 001 - 250 (3 Digits) | Node Serialization Index: Unique sequential hardware counter for that site. For remote branches, this matches the assigned Site ID. |

## Master Device Role Codes ([Role])
## 1. Data Centre Fabric & Core Layer

* 301 = Fabric Spine Switch (Data centre backbone core)
* 412 = Fabric Leaf Switch (Data centre server/access layer)
* 523 = Border Leaf Switch (Data centre fabric edge gateway handling internal handoffs)
* 810 = Fabric Border Router (Dedicated high-throughput core routers connecting the fabric to external transit or WAN core)

## 2. Campus & Local Site Infrastructure

* 310 = Campus Core Switch (The backbone switch for a corporate office/campus)
* 320 = Campus Distribution Switch (Aggregation layer for office buildings or floors)
* 420 = Campus Access Switch (The switch where end-user laptops and desks plug in)
* 830 = Campus WAN Router (Local office routers connecting to the corporate WAN)
* 844 = Remote Node Edge Router (Your 250+ small remote site routers)

## 3. Multi-Tenant & Customer Edge Layer

* 450 = Tenant Provisioning Switch (Dedicated physical switch or hardware slice reserved for a single customer's hardware)
* 650 = Customer Dedicated Firewall (Dedicated security appliance assigned to an isolated tenant domain)
* 850 = Customer Edge (CE) Router (Dedicated routing appliance assigned to a specific tenant/customer)

## 4. Edge Security & Reverse Proxy Services

* 610 = Central Firewall (Security perimeter appliances)
* 620 = Reverse Proxy / Load Balancer (DMZ devices terminating web traffic, e.g., F5, NGINX)
* 630 = Secure Web Gateway / Proxy Server (Inbound/Outbound user web filter proxies)

## 5. Collaboration, Voice, Identity & Management

* 710 = Out-of-Band Management Switch (Isolated hardware control network)
* 720 = Session Border Controller (SBC) (Voice security gateways for SIP/VoIP trunking)
* 730 = Identity & Federation Device (Servers/Appliances handling Single Sign-On and trust federations, e.g., ADFS, Ping)

## Baseline Hostname Examples

* Primary Data Centre Border Gateway Switch (Site Code: AA, Node #1, Deployed 2026):
AA-523-A6-001
* A central Data Centre Border Router connecting to your ISP (Site Code: AA, Router #1, Deployed 2026):
AA-810-A6-001
* A dedicated Customer Edge router for a tenant (Site Code: AA, Device #1, Deployed 2026):
AA-850-A6-001
* A Campus Access Switch at an office location (Site Code: BB, Switch #3, Deployed 2026):
BB-420-A6-003
* An Identity Federation server appliance (Site Code: AA, Device #1, Deployed 2026):
AA-730-A6-001
* Remote Branch Site #142 Edge Router (Site Code: TR, Deployed 2026):
TR-844-A6-142

------------------------------
## 2. Hostname Validation Guide for Administrators (Regex Extraction)
For administration tools running automated verification scripts, the metrics pipeline uses the following standardized regular expression groupings to pull tags directly out of device variables:

* To extract Hostname Attributes:
^(?P<site>[A-Z]{2})-(?P<role>\d{3})-(?P<epoch>[A-Z0-9]{2})-(?P<index>\d{3})$

Using this structure, if an automated inventory script scans the network, it can instantly decode that device TR-844-A6-142 is a WAN Edge Router belonging to Remote Site 142 without needing to query an external database.
------------------------------
Now that the master naming standard and expanded role codes are fully locked in, how would you like to handle the VLAN numbers and customer IP address allocation plans across your data centres and multi-site environments?

