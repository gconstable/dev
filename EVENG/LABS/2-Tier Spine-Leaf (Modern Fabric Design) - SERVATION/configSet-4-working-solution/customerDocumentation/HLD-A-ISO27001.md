# High-Level Design Document
## BGP EVPN/VXLAN Multi-Tenant Data Centre Fabric
### ISO/IEC 27001:2022 Compliance Focus

**Document Classification:** Confidential — Internal Engineering  
**Revision:** 1.0  
**Date:** 2026-05-31  
**Scope:** Production Fabric — AA-EDGE-GW-01, AA-EDGE-GW-02, AA-SPINE-01, AA-SPINE-02  
**CVD Baseline:** Cisco BGP EVPN/VXLAN Multi-Tenancy Validated Design  
**Platform:** Cisco IOS-XE — Catalyst 8000 (Border/WAN Edge), Catalyst 9000 (Spine)

---

## Table of Contents

1. Executive Summary
2. Topology & Structural Design
3. Protocol & Technology Deep Dive
4. ISO 27001 Alignment & Best Practices
5. Observations, Gaps & Hardening Recommendations

---

## 1. Executive Summary

This document constitutes the High-Level Design (HLD) record for a Cisco Catalyst IOS-XE data centre fabric implementing BGP-signalled Layer 2 VPN (L2VPN) Ethernet VPN (EVPN) with VXLAN data-plane encapsulation across a two-tier spine-and-gateway topology. The fabric delivers multi-tenant network virtualisation, providing cryptographically isolated forwarding domains per tenant through Virtual Routing and Forwarding (VRF) instances, and extends tenant Layer 3 reachability from the VXLAN overlay to external customer-edge devices via eBGP.

The architecture comprises four network devices in scope: two Catalyst 8000 series border gateway nodes (AA-EDGE-GW-01, AA-EDGE-GW-02) operating within Autonomous System (AS) 65100, and two Catalyst 9000 series spine nodes (AA-SPINE-01, AA-SPINE-02) operating within AS 65000. The topology implements a full eBGP mesh across both the IPv4 unicast underlay and the L2VPN EVPN overlay address families, using /30 point-to-point transit links and loopback-anchored VTEP (VXLAN Tunnel End Point) addresses. BFD (Bidirectional Forwarding Detection) is enabled for sub-second peer failure detection on all underlay sessions.

Multi-tenancy is implemented via VRF-101, representing a single tenant (Customer A / AS 65200) instantiated across all four fabric nodes. Tenant traffic is encapsulated in VXLAN VNI 50101, bridged via bridge-domain 101 (gateway nodes) or VLAN 101 (spine nodes), and forwarded within the VRF-101 routing context. Route distribution between the fabric overlay and the tenant's external network is achieved through eBGP peering on dedicated per-spine trunk SVIs (VLANs 200–203), with explicit VLAN 666 defined as a parked/unused native VLAN on trunk interfaces.

From an ISO/IEC 27001:2022 Information Security Management System (ISMS) perspective, the design addresses network segregation (Annex A.8.22), network security controls (A.8.20), and access control (A.8.3 / A.5.15) through: (i) hard VRF separation between tenant and fabric infrastructure planes; (ii) eBGP AS boundary enforcement at the fabric edge; (iii) per-VTEP loopback-anchored next-hop rewriting, preventing direct transit IP disclosure; and (iv) explicit trunk VLAN allowlists restricting tenant VLAN propagation to named ports only.

This document is produced against the Cisco Validated Design (CVD) for BGP EVPN/VXLAN multi-tenancy as the reference architecture baseline. Deviations from the CVD and residual security gaps are documented in Section 5.

---

## 2. Topology & Structural Design

### 2.1 Physical & Logical Topology

The fabric implements a non-blocking two-tier topology. Gateway nodes (CAT8K) function as the WAN/border termination layer and VTEP nodes for the EVPN overlay. Spine nodes (CAT9K) function as the forwarding plane for intra-fabric traffic and as the tenant service demarcation point toward downstream leaf devices (not yet in scope for this build phase).

All inter-node links are routed point-to-point /30 GigabitEthernet segments with jumbo MTU configured (9216 on gateway interfaces; 8978 on spine interfaces), accommodating the 50-byte VXLAN/UDP/IP encapsulation overhead without IP fragmentation.

```
+==============================================================+
|                    FABRIC UNDERLAY PLANE                     |
|                                                              |
|   AS 65100                          AS 65000                 |
|  +----------------+                +----------------+        |
|  | AA-EDGE-GW-01  |                |  AA-SPINE-01   |        |
|  |  Lo0:10.200.0.1|                |  Lo0: 10.0.0.1 |        |
|  |  Lo1: 1.1.1.1  |                |  RID: 10.0.0.1 |        |
|  |  RID:10.200.0.1|                +----------------+        |
|  +----------------+                                          |
|         |  Gi1 10.255.1.1/30 <---> 10.255.1.2/30 Gi1/0/1   |
|         |  Gi2 10.255.1.5/30 <---> 10.255.1.6/30 Gi1/0/1   |
|                                                              |
|  +----------------+                +----------------+        |
|  | AA-EDGE-GW-02  |                |  AA-SPINE-02   |        |
|  |  Lo0:10.200.0.2|                |  Lo0: 10.0.0.2 |        |
|  |  Lo1: 2.2.2.2  |                |  RID: 10.0.0.2 |        |
|  |  RID:10.200.0.2|                +----------------+        |
|  +----------------+                                          |
|         |  Gi1 10.255.1.9/30 <---> 10.255.1.10/30 Gi1/0/2  |
|         |  Gi2 10.255.1.13/30<---> 10.255.1.14/30 Gi1/0/2  |
|                                                              |
|  GW-01 Lo1 (1.1.1.1) <--iBGP AS65100--> GW-02 Lo1(2.2.2.2)|
|  SP-01 Gi1/0/3 10.255.1.17/30 <--> 10.255.1.18/30 SP-02    |
+==============================================================+

+==============================================================+
|                   VXLAN EVPN OVERLAY PLANE                   |
|                                                              |
|   VTEP: GW-01 (10.200.0.1)    VTEP: GW-02 (10.200.0.2)     |
|   VTEP: SP-01 (10.0.0.1)      VTEP: SP-02 (10.0.0.2)       |
|                                                              |
|   All VTEPs: NVE1, host-reachability protocol bgp            |
|   Encapsulation: VXLAN (VNI 50101 -> VRF-101)               |
|                                                              |
|   EVPN RT Export/Import Matrix (VNI 50101):                  |
|     10.0.0.1:101, 10.0.0.2:101                              |
|     10.200.0.1:101, 10.200.0.2:101                          |
+==============================================================+

+==============================================================+
|                   TENANT PLANE (VRF-101 / VNI 50101)        |
|                                                              |
|  GW-01 BDI101: 101.101.103.1/24  (Tenant L3 Gateway)        |
|  GW-02 BDI101: 101.101.102.1/24  (Tenant L3 Gateway)        |
|  SP-01 Vlan101: ip unnumbered Lo0 (10.0.0.1)                 |
|  SP-02 Vlan101: ip unnumbered Lo0 (10.0.0.2)                 |
|                                                              |
|  SP-01 --> LEAF-01: Gi1/0/13 trunk VLANs 101,200            |
|  SP-01 --> LEAF-02: Gi1/0/14 trunk VLANs 101,201            |
|  SP-02 --> LEAF-01: Gi1/0/13 trunk VLANs 101,202            |
|  SP-02 --> LEAF-02: Gi1/0/14 trunk VLANs 101,203            |
|                                                              |
|  SP-01 SVI-200: 10.255.2.1/30 <--> LEAF-01 AS65200          |
|  SP-01 SVI-201: 10.255.2.5/30 <--> LEAF-02 AS65200          |
|  SP-02 SVI-202: 10.255.2.9/30 <--> LEAF-01 AS65200          |
|  SP-02 SVI-203: 10.255.2.13/30 <-> LEAF-02 AS65200          |
+==============================================================+
```

### 2.2 Security Segregation Zones (ISO/IEC 27001:2022 Annex A.8.22)

The design enforces three logical security domains:

**Zone 1 — Fabric Infrastructure Plane (AS 65000 / AS 65100):** All inter-node transit /30 links, loopback addresses, and BGP control-plane sessions. Isolated from tenant traffic by VRF default (global routing table). No tenant routes are leaked into this zone absent explicit BGP VRF advertisement policy.

**Zone 2 — VXLAN EVPN Overlay (VRF-101 / VNI 50101):** Tenant-specific forwarding domain. All traffic within this zone is encapsulated in VXLAN at the VTEP and forwarded as UDP/IP across the underlay. The VRF boundary enforces Layer 3 isolation between tenants and between tenants and the fabric infrastructure plane.

**Zone 3 — Tenant External Boundary (AS 65200):** Customer-facing eBGP peering zone. Demarcated by spine SVI interfaces (VLANs 200–203) carrying VRF-101 context. Route exchange with AS 65200 is governed by explicit BGP peer-policy templates with `send-community both` and `advertise l2vpn evpn`.

### 2.3 Trust Boundary Diagram

```
+-------------------+      +-------------------+
|  EXTERNAL / WAN   |      | TENANT (AS 65200) |
|  (Out of Scope)   |      |  LEAF-01 / LEAF-02|
+-------------------+      +-------------------+
          |                          |
  [ CAT8K BORDER ]          [ CAT9K SPINE TRUNK ]
  [ AS 65100 EDGE ]         [ VLANs 200-203 ]
          |                          |
+=========================================+
|         FABRIC TRUST BOUNDARY           |
|  +-------------+    +-------------+    |
|  | AA-EDGE-GW-01|   | AA-SPINE-01  |   |
|  | AS 65100     |   | AS 65000     |   |
|  | VTEP Lo0     |   | VTEP Lo0     |   |
|  +-------------+    +-------------+    |
|  +-------------+    +-------------+    |
|  | AA-EDGE-GW-02|   | AA-SPINE-02  |   |
|  | AS 65100     |   | AS 65000     |   |
|  | VTEP Lo0     |   | VTEP Lo0     |   |
|  +-------------+    +-------------+    |
|      [Zone 1: Infrastructure Plane]    |
|      [Zone 2: VXLAN Overlay VRF-101]   |
+=========================================+
                    |
            [ ZONE 3: Tenant Boundary ]
            [ eBGP VRF-101 / AS 65200 ]
```

---

## 3. Protocol & Technology Deep Dive

### 3.1 Border Gateway Protocol (BGP) — Underlay IPv4 Unicast

BGP (RFC 4271) is the sole dynamic routing protocol deployed for both underlay reachability and EVPN control-plane signalling. No IGP (OSPF/IS-IS) is present; BGP carries all IPv4 prefix distribution, consistent with the Cisco BGP-only fabric CVD approach.

**AS Architecture:**

- AS 65000: Spine nodes (AA-SPINE-01, AA-SPINE-02). Inter-spine peering via Gi1/0/3 /30 link (10.255.1.17/18).
- AS 65100: Gateway/border nodes (AA-EDGE-GW-01, AA-EDGE-GW-02). iBGP peering between gateways via Loopback1 (1.1.1.1 / 2.2.2.2), using `update-source Loopback1` and `ebgp-multihop 5`.
- AS 65200: External tenant network (Customer A). eBGP peering with spine VRF-101 SVIs.

**Session Templates:** All underlay peers are configured via `template peer-session` constructs, ensuring consistent transport-layer parameters (remote-as, multihop TTL, BFD fall-over, update-source). This pattern aligns with the CVD peer-template model and enforces uniform session behaviour across all fabric nodes.

**`no bgp fast-external-fallover`:** Explicitly disabled on all nodes, preventing premature session tear-down on connected interface flaps — a deliberate stability measure consistent with the Cisco CVD recommendation for EVPN fabrics.

**`redistribute connected`:** Applied within the IPv4 unicast address family on all nodes, distributing loopback and transit interface prefixes into BGP for VTEP reachability. Loopback0 (VTEP source) reachability is a prerequisite for VXLAN tunnel establishment.

**`allowas-in 2`:** Configured on gateway nodes for AS 65000 peers. This permits routes carrying the local AS (65100) in their AS-PATH — a necessary accommodation for the eBGP design where EVPN routes traversing the spine may contain the originating gateway's AS. This represents a deliberate design allowance and is documented in the CVD.

**Relevant RFCs:** RFC 4271 (BGP-4), RFC 4456 (BGP Route Reflection), RFC 7938 (BGP in Large-Scale Data Centres).

### 3.2 Bidirectional Forwarding Detection (BFD)

BFD (RFC 5880, RFC 5881) is enabled via `fall-over bfd` within BGP peer-session templates on all underlay sessions between gateway and spine nodes. BFD provides link-level failure detection at sub-second intervals, significantly reducing BGP hold-timer-dependent convergence time. This directly supports availability objectives under ISO 27001 Annex A.8.6 (Capacity Management) and A.8.14 (Redundancy of Information Processing Facilities).

Note: BFD `fall-over` is present on AS 65000 peer-session templates at the spine layer but absent from the AS 65100 iBGP peer-session template (`PS_UNDERLAY_INFRA_65100`) on GW-01 — see Section 5 for gap analysis.

**Relevant RFCs:** RFC 5880 (BFD), RFC 5881 (BFD for IPv4/IPv6 Single Hop), RFC 5883 (BFD for Multihop Paths).

### 3.3 BGP L2VPN EVPN Address Family

EVPN (RFC 7432, RFC 8365) is implemented as a BGP address family (`address-family l2vpn evpn`) providing the control-plane for VXLAN MAC/IP advertisement, VTEP discovery, and inter-subnet routing across the overlay. Key operational aspects extracted from configuration:

**VTEP Loopback Anchoring:** Each device configures a dedicated Loopback0 as the `source-interface` for the NVE1 interface. Route-map `EVPN-OUT-VTEP-REWRITE` is applied outbound on all L2VPN EVPN peers, setting `ip next-hop` to the local Loopback0 address. This next-hop rewriting ensures that EVPN routes advertised to peers carry the correct VTEP source IP, enabling accurate tunnel endpoint resolution. This is a mandatory step in IOS-XE EVPN deployments where the BGP router-ID and VTEP source address differ.

**`host-reachability protocol bgp`:** Configured on all NVE1 interfaces, specifying that host MAC/IP binding distribution is handled by the BGP EVPN control-plane rather than data-plane flooding (multicast or ingress replication with static peers). Combined with `replication-type ingress` (configured per EVPN instance on gateway nodes), this eliminates the requirement for multicast underlay infrastructure.

**`replication-type ingress`:** Configured on gateway EVPN instance 101. Ingress replication distributes BUM (Broadcast, Unknown Unicast, Multicast) traffic via unicast copies to each known VTEP. This is the preferred BUM handling method for environments where multicast is unavailable or undesired, and aligns with the Cisco CVD recommendation.

**`send-community both`:** Applied universally across all peer-policy templates for both IPv4 and L2VPN EVPN address families. This passes both standard and extended BGP communities, which are required for EVPN Route Target (RT) matching and VRF import/export policy enforcement.

**Relevant RFCs:** RFC 7432 (BGP EVPN), RFC 8365 (Network Virtualisation Overlays Using EVPN), RFC 4364 (BGP/MPLS IP VPNs — RT community model), RFC 8277 (NLRI for BGP EVPN).

### 3.4 VXLAN Data Plane (VNI 50101)

VXLAN (RFC 7348) encapsulates tenant Ethernet frames within UDP/IP packets for transport across the IP underlay. Key parameters:

- **VNI 50101** is the sole active VNI in this build, mapped to VRF-101 on all four fabric nodes.
- **Bridge-Domain 101 (Gateway nodes):** IOS-XE CAT8K uses the bridge-domain model (`bridge-domain 101`, `member evpn-instance 101 vni 50101`) with BDI101 as the Layer 3 tenant gateway interface.
- **VLAN 101 (Spine nodes):** IOS-XE CAT9K uses the traditional VLAN-to-VNI mapping model (`vlan configuration 101`, `member vni 50101`) with SVI Vlan101 as the Layer 3 gateway, configured as `ip unnumbered Loopback0`.
- **MTU:** Transit interfaces are configured with jumbo MTU (9216/8978) to accommodate the VXLAN encapsulation overhead (50 bytes: 14 Ethernet + 8 VXLAN + 8 UDP + 20 IP) without fragmentation.

**Relevant RFCs:** RFC 7348 (VXLAN), RFC 7637 (NVGRE — referenced for context), RFC 8926 (Geneve — referenced for context).

### 3.5 BGP Multi-Tenancy: VRF-101 Route Target Architecture

VRF-101 is instantiated on all four fabric devices with device-specific Route Distinguishers (RDs) and a shared symmetric Route Target (RT) import/export matrix. The RT design is critical to the multi-tenant isolation model:

**Route Distinguishers (per-device):**

- GW-01: `10.200.0.1:101`
- GW-02: `10.200.0.2:101`
- SP-01: `10.0.0.1:101`
- SP-02: `10.0.0.2:101`

**Route Target Matrix (VRF IPv4 AF, stitching):** Each device exports and imports all four RTs (`10.0.0.1:101`, `10.0.0.2:101`, `10.200.0.1:101`, `10.200.0.2:101`), enabling full-mesh tenant route exchange across the overlay.

**EVPN Instance 101 RT Matrix (Gateway nodes):** The EVPN instance carries an identical symmetric RT matrix across all four VTEP loopback addresses, ensuring consistent EVPN type-2/type-5 route import across the fabric.

**`stitching` keyword:** Present on VRF route-targets. In IOS-XE, the `stitching` keyword on VRF RTs instructs the EVPN control-plane to use these RTs for EVPN-to-IP-VPN route stitching (type-5 prefix routes). This is the correct configuration for EVPN IRB (Integrated Routing and Bridging) deployments requiring L3 prefix advertisement.

### 3.6 802.1Q Trunking & Native VLAN Hardening

Spine nodes trunk tenant VLANs to downstream leaf nodes via IEEE 802.1Q trunk interfaces. Security-relevant parameters:

- **`switchport trunk allowed vlan`:** Explicit VLAN allowlists restrict trunk propagation to VLANs 101 and the relevant per-leaf SVI VLAN (200/201 on SP-01; 202/203 on SP-02). No implicit "permit all" (`vlan all`) is present.
- **`switchport trunk native vlan 666`:** VLAN 666 (named `PARKED`) is configured as the native VLAN on all trunk interfaces, preventing untagged traffic from being associated with any active service VLAN. This mitigates VLAN hopping attacks by displacing the default native VLAN 1.

**Relevant Standards:** IEEE 802.1Q, CVE-1999-0807 (VLAN hopping via native VLAN 1).

---

## 4. ISO 27001 Alignment & Best Practices

### 4.1 Annex A.8.22 — Segregation of Networks

**Control Objective:** Networks should be segregated to manage security risks associated with different asset groups, organisational units, or information classifications.

**Implementation Evidence:**

The design enforces multi-layer network segregation:

- **VRF Isolation:** VRF-101 creates a hardware-enforced forwarding boundary between tenant and infrastructure routing tables. Absent explicit route leaking (none configured), no cross-VRF reachability exists. Additional tenants would instantiate separate VRF instances with discrete RD/RT sets, maintaining isolation.
- **AS Boundary Enforcement:** The eBGP AS structure (65000/65100/65200) enforces routing domain boundaries. AS-PATH filtering and RT-based import/export policies govern cross-boundary route propagation.
- **VXLAN Encapsulation:** Tenant frames are encapsulated at the VTEP boundary, preventing Layer 2 adjacency between tenant endpoints and fabric infrastructure nodes.
- **VLAN Trunk Allowlisting:** Explicit `switchport trunk allowed vlan` configurations on spine trunk ports prevent unauthorised VLAN propagation beyond designated boundaries.

**CVD Alignment:** Fully aligned with the Cisco BGP EVPN/VXLAN multi-tenancy CVD network segmentation model.

**Gaps:** No route-map inbound filtering is present on eBGP peers in VRF-101 (AS 65200 sessions). A malicious or misconfigured AS 65200 device could advertise arbitrary prefixes into VRF-101. Inbound prefix-list or route-map filtering is recommended (Section 5.1).

### 4.2 Annex A.8.20 — Networks Security (formerly A.13.1.1 — Network Controls)

**Control Objective:** Networks should be secured and managed to protect information systems and applications.

**Implementation Evidence:**

- **BFD Fast Failure Detection:** Sub-second convergence reduces the window during which a failed path may be used, limiting potential black-hole or misdirection scenarios.
- **`no bgp fast-external-fallover`:** Prevents premature BGP session teardown on transient interface events, reducing instability-induced routing anomalies.
- **BGP Peer-Session Templates:** Consistent, auditable session parameters applied via named templates. Reduces misconfiguration risk from ad-hoc per-neighbour configuration.
- **Jumbo MTU:** Consistent MTU policy across fabric links prevents fragmentation-induced packet loss, supporting integrity of in-flight data.
- **`bgp log-neighbor-changes`:** Enabled on all nodes, producing syslog records for all BGP adjacency state transitions. This provides audit trail data supporting Annex A.8.15 (Logging) and A.8.16 (Monitoring Activities).

**Gaps:** No BGP TTL Security (GTSM, RFC 5082) is configured. `ebgp-multihop 5` is necessary for loopback-sourced sessions but removes the single-hop TTL protection available for directly-connected peers. BGP MD5 authentication (RFC 2385) is absent on all sessions. See Section 5.2.

### 4.3 Annex A.8.3 / A.5.15 — Access Control & Identity Management

**Control Objective:** Access to information and other associated assets should be restricted in accordance with the established topic-specific policy on access control.

**Implementation Evidence:**

- **VRF-Based Tenant Isolation:** Each tenant's routing domain is strictly bounded by VRF assignment. Tenant endpoints cannot reach infrastructure or other tenant addresses without explicit policy.
- **BGP Route Target Policy:** Import/export RT matching enforces which prefixes are accepted into each VRF — functionally equivalent to an access control list at the routing layer.
- **VLAN Allowlisting on Trunks:** `switchport trunk allowed vlan` acts as a Layer 2 access control boundary, constraining which VLANs (and therefore which tenant services) are reachable via each physical port.
- **Native VLAN Displacement (VLAN 666):** Mitigates untagged frame injection attacks that could otherwise bypass trunk VLAN controls.

**Gaps:** No BGP maximum-prefix limits (`maximum-prefix` command) are configured on VRF-101 eBGP peers (AS 65200). An unconstrained route advertisement from AS 65200 could exhaust BGP table memory. See Section 5.3.

### 4.4 Annex A.8.6 / A.8.14 — Capacity Management & Redundancy

**Control Objective:** Resources should be monitored and adjusted to ensure adequate capacity and availability.

**Implementation Evidence:**

- **Dual-Path Underlay:** Each gateway peers with both spines, providing physical path redundancy. BGP ECMP (`maximum-paths 4` configured in VRF-101 address family on gateway nodes) enables load distribution and eliminates single-path availability dependency.
- **Dual VTEP Design:** GW-01 and GW-02 maintain independent VTEP addresses with symmetric RT configuration, providing VTEP-level redundancy. Tenant traffic can traverse either gateway node.
- **BFD-Accelerated Failover:** `fall-over bfd` on underlay sessions ensures that link failures are propagated to the BGP routing layer at BFD detection speed rather than BGP hold-timer expiry (default 90 seconds).
- **Inter-Spine Link:** Direct Gi1/0/3 peering between SP-01 and SP-02 provides an additional convergence path for intra-spine EVPN synchronisation.

**Gaps:** BFD `fall-over` is absent on the GW-01 iBGP session toward GW-02 (Loopback1-sourced peer), and on the Spine-02 peer-session template for AS 65100. See Section 5.4.

### 4.5 Annex A.8.15 / A.8.16 — Logging & Monitoring

**Control Objective:** Event logs recording activities, exceptions, faults, and information security events should be produced, stored, protected, and analysed.

**Implementation Evidence:**

- **`bgp log-neighbor-changes`:** All four nodes log BGP adjacency state changes (established, reset, notification) to syslog. This provides a minimum audit baseline for control-plane events.

**Gaps:** No centralised syslog server configuration is present in the configurations under review (noting that management plane is out of scope). No SNMP trap or streaming telemetry (gRPC/gNMI) configuration is visible. No `ip flow` / NetFlow configuration is present for data-plane traffic visibility. These are management-plane capabilities and are noted as out-of-scope for this review but recommended for ISMS completeness.

---

## 5. Observations, Gaps & Hardening Recommendations

### 5.1 Absence of Inbound BGP Prefix Filtering on VRF-101 External Peers

**Risk:** AS 65200 (Customer A) eBGP sessions in VRF-101 accept all advertised prefixes without inbound route-map or prefix-list filtering. A misconfigured or compromised CE device could inject arbitrary routes into VRF-101, potentially causing traffic misdirection within the tenant domain or exhausting the routing table.

**Recommendation:** Apply inbound `route-map` or `prefix-list` on all AS 65200 neighbour statements within `address-family ipv4 vrf VRF-101`, permitting only the expected customer prefix space. Example:

```
ip prefix-list CUST-A-IN seq 5 permit 10.0.0.0/8 le 24
route-map CUST-A-IN permit 10
  match ip address prefix-list CUST-A-IN
neighbor 10.255.2.2 route-map CUST-A-IN in
```

**ISO Mapping:** A.8.22 (Network Segregation), A.8.20 (Network Security).

### 5.2 Absence of BGP Session Authentication (MD5 / GTSM)

**Risk:** All BGP sessions are unauthenticated. An attacker with network adjacency could inject crafted BGP OPEN/UPDATE packets to disrupt or manipulate routing state. `ebgp-multihop 5` is necessary for loopback-sourced sessions but increases the attack surface relative to single-hop sessions with GTSM.

**Recommendation:** Enable BGP MD5 authentication (`neighbor X.X.X.X password`) on all inter-AS eBGP sessions. For directly-connected eBGP peers, consider enabling GTSM (`ttl-security hops 1`) as a complementary defence. For the loopback-sourced iBGP session (GW-01 <-> GW-02), MD5 authentication is the primary available control.

**ISO Mapping:** A.8.20 (Network Security), A.5.15 (Access Control).

### 5.3 Absence of BGP Maximum-Prefix Limits

**Risk:** No `maximum-prefix` limit is configured on any BGP neighbour. An unconstrained route advertisement storm (deliberate or accidental) from any peer could exhaust device memory and destabilise the fabric.

**Recommendation:** Configure `maximum-prefix` with a threshold warning and optionally a hard limit on all eBGP sessions, particularly AS 65200 external peers where prefix count is predictable.

```
neighbor 10.255.2.2 maximum-prefix 100 80 warning-only
```

**ISO Mapping:** A.8.6 (Capacity Management), A.8.20 (Network Security).

### 5.4 Inconsistent BFD Configuration Across Peer-Session Templates

**Risk:** BFD `fall-over` is present on the AS 65000 peer-session templates on the spine nodes and on GW-01/GW-02 templates for AS 65000 peers. However, the AS 65100 iBGP peer-session template (`PS_UNDERLAY_INFRA_65100`) on GW-01 does not include `fall-over bfd`. Similarly, AA-SPINE-02's AS 65100 template lacks `fall-over bfd`. This inconsistency creates asymmetric convergence behaviour — a failure on the GW-01 to GW-02 iBGP path would not benefit from BFD-accelerated detection.

**Recommendation:** Add `fall-over bfd` to `PS_UNDERLAY_INFRA_65100` on both gateway nodes and verify BFD session establishment on all fabric links.

**ISO Mapping:** A.8.14 (Redundancy), A.8.6 (Capacity Management).

### 5.5 EVE-NG Lab Origin — License Commentary Present

**Observation:** All four device configurations contain the commented line `! license boot level network-advantage addon dna-advantage`, indicating this build was developed in an EVE-NG simulation environment. This is not a security gap but is a documentation observation: production deployment must validate that the appropriate IOS-XE license tier (Network Advantage + DNA Advantage) is active on all physical hardware prior to service activation, as EVPN/VXLAN feature availability is license-gated on Catalyst platforms.

**ISO Mapping:** A.5.9 (Inventory of Information and Other Associated Assets), A.8.8 (Management of Technical Vulnerabilities).

### 5.6 VLAN 666 Native VLAN — Consistency Verification Required

**Observation:** VLAN 666 (`PARKED`) is defined on spine nodes and assigned as native VLAN on all trunk interfaces, which is a positive security configuration. However, VLAN 666 must also be defined and similarly quarantined on all downstream leaf devices that terminate these trunk connections. If leaf devices retain the default native VLAN 1, a VLAN hopping vector may exist at the leaf-to-spine boundary.

**Recommendation:** Verify `switchport trunk native vlan 666` is consistently applied at both ends of all trunk links. Confirm VLAN 666 carries no active services and is not routed on any device.

**ISO Mapping:** A.8.22 (Network Segregation).

---

*End of Document A — ISO/IEC 27001:2022 HLD*
