# EVPN VXLAN Overlay Deployment: Tenant_C

This configuration deploys a Layer 2 and Layer 3 BGP EVPN VXLAN overlay network on a Cisco IOS-XE platform (such as a Catalyst 9000 switch). It establishes network encapsulation, edge connectivity, and a distributed default gateway for **Tenant_C**.

---

## Architectural Breakdown

This configuration snippet achieves three primary architectural objectives:

### 1. Hardware-to-Overlay Mapping (VXLAN Bridging)
The configuration binds a traditional, local broadcast domain (`VLAN 12`) to a global fabric identifier (`VNI 10012`). This allows the switch to accept standard Layer 2 Ethernet frames from end-hosts, encapsulate them into IP/UDP packets via the Network Virtualization Edge (`interface nve 1`), and tunnel them across a standard Layer 3 underlay infrastructure.

### 2. Control Plane Signaling (BGP EVPN)
By creating the `l2vpn evpn instance 12 vlan-based` block, the switch uses the BGP EVPN control plane to advertise MAC addresses. Instead of relying on traditional data-plane flooding to find hosts, the fabric uses BGP. 
* **Ingress Replication:** The configuration specifies `replication-type ingress`. This enables Head-end/Ingress replication, instructing the switch to use BGP EVPN Route Type 3 (Inclusive Multicast Ethernet Tag routes) to automatically discover remote fabric endpoints (VTEPs) and replicate Broadcast, Unknown Unicast, and Multicast (BUM) traffic using unicast delivery.

### 3. Distributed Anycast Gateway
`interface Vlan12` is configured as a Distributed Anycast Gateway. Every leaf switch in the fabric hosting Tenant_C will share the exact same IP address (`10.10.12.1`) and virtual MAC address (`0000.1212.1212`). 
* This provides localized, high-performance routing for end-hosts.
* It eliminates traffic "hairpinning" to a centralized core or firewall.
* It enables seamless host mobility (like VM live migrations) because the gateway identity never changes across physical switch boundaries.

---

## Clean, Visually Decoupled Configuration

```text
! ------------------------------------------------------------------------------
! SECTION 1: CREATE LAYER 2 CONFIG
! ------------------------------------------------------------------------------
!
! [TECHNICAL FEATURE]: Define the Layer 2 broadcast domain (VLAN) for the tenant.
! [BEST PRACTICE]:     Use a descriptive, uppercase name for organizational clarity and rapid troubleshooting.
!
vlan 12
 name Tenant_C
!
! [TECHNICAL FEATURE]: Bind the traditional Layer 2 VLAN to the EVPN VXLAN Overlay.
! [BEST PRACTICE]:     Ensure the Virtual Network Identifier (VNI) mapping is consistent across all VTEPs in the fabric.
!
vlan configuration 12
 member evpn-instance 12 vni 10012
!
! [TECHNICAL FEATURE]: Global EVPN configuration block defining BGP EVPN control plane behavior.
! [RISK / AUDIT]:      "replication-type static" is explicitly configured here but overridden as "ingress" inside the instance. 
! [BEST PRACTICE]:     Align global and instance replication types to "ingress" to maintain consistency and avoid operational confusion.
! [BEST PRACTICE]:     Always advertise the default gateway to allow local VTEPs to answer ARP requests, reducing fabric-wide flooding.
!
l2vpn evpn
 replication-type static
 router-id loopback10
 default-gateway advertise
!
! [TECHNICAL FEATURE]: Configure a vlan-based EVPN instance mapping a single VLAN to a single VNI.
! [BEST PRACTICE]:     Use "replication-type ingress" (Ingress Replication) to replicate BUM traffic via unicast 
!                      to all remote VTEPs when IP Multicast is not deployed or supported in the Underlay network.
!
l2vpn evpn instance 12 vlan-based
 encapsulation vxlan
 replication-type ingress
!
! EDITE VTEP (NVE) - ADD ADDITIONAL VNI FOR TENANT_B
!
! [TECHNICAL FEATURE]: Map the new Tenant VNI to the logical Network Virtualization Edge (NVE) tunnel interface.
! [RISK / AUDIT]:      The description text references "TENANT_B", but the code configures VNI 10012 (Tenant_C). Correct the comment to avoid operational confusion.
! [BEST PRACTICE]:     Ensure "ingress-replication" matches the replication type configured in the EVPN instance block.
!
interface nve 1
 member vni 10012 ingress-replication
!
! ------------------------------------------------------------------------------
! SECTION 2: CREATE INTERFACES & ADD ETHERNET SEGMENT TO INTERFACES
! ------------------------------------------------------------------------------
!
! [TECHNICAL FEATURE]: Configure the physical access edge port facing the end-host or server.
! [BEST PRACTICE]:     "spanning-tree portfast" must be enabled on edge access ports to bypass listening/learning states and prevent DHCP timeouts. 
! [RISK / AUDIT]:      To prevent loops caused by downstream switches or unauthorized cabling on a PortFast-enabled interface, 
!                      always configure "spanning-tree bpduguard enable" globally or directly on the interface.
!
interface GigabitEthernet1/0/12
 switchport access vlan 12
 switchport mode access
 spanning-tree portfast
 description ACCESS_TO_TENANT_C
!
!
! ------------------------------------------------------------------------------
! SECTION 3: CREATE ANYCAST GATEWAY CONFIG
! ------------------------------------------------------------------------------
!
! [TECHNICAL FEATURE]: Define the Switched Virtual Interface (SVI) acting as the centralized default gateway for the overlay network.
! [BEST PRACTICE]:     "no autostate" keeps the SVI in an "up/up" operational status regardless of physical port line states. This is 
!                      critical in VXLAN environments to ensure the gateway remains reachable via the fabric even if all local access ports are down.
! [BEST PRACTICE]:     Use a static, synchronized virtual MAC address ("mac-address 0000.1212.1212") across all VTEPs performing 
!                      Anycast Gateway functions. This enables seamless virtual machine mobility (vMotion/live migration) without causing ARP timeouts or host re-learning.
!
interface Vlan12
 description ANYCAST_GATEWAY_FOR_TENANT_C
 ip address 10.10.12.1 255.255.255.0
 no autostate
 mac-address 0000.1212.1212
!
```
