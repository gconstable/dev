# High-Level Design Document
## BGP EVPN/VXLAN Multi-Tenant Data Centre Fabric
### NIST SP 800-53 Rev. 5 / Cybersecurity Framework (CSF) 2.0 Focus

**Document Classification:** Confidential — Internal Engineering  
**Revision:** 1.0  
**Date:** 2026-05-31  
**Scope:** Production Fabric — AA-EDGE-GW-01, AA-EDGE-GW-02, AA-SPINE-01, AA-SPINE-02  
**CVD Baseline:** Cisco BGP EVPN/VXLAN Multi-Tenancy Validated Design  
**Platform:** Cisco IOS-XE — Catalyst 8000 (Border/WAN Edge), Catalyst 9000 (Spine)  
**NIST SP 800-53 Revision:** Rev. 5 (September 2020)  
**NIST CSF Version:** 2.0 (February 2024)

---

## Table of Contents

1. Executive Summary
2. Topology & Boundary Protection
3. Protocol & Technology Deep Dive
4. NIST Control Mapping & Best Practices
5. Observations, Gaps & Hardening Recommendations

---

## 1. Executive Summary

This document constitutes the High-Level Design (HLD) record for a Cisco Catalyst IOS-XE data centre network fabric implementing BGP-signalled L2VPN EVPN with VXLAN data-plane encapsulation, analysed against the NIST Cybersecurity Framework (CSF) 2.0 core functions and NIST Special Publication 800-53 Revision 5 security and privacy controls. The primary control families assessed are: **AC** (Access Control), **CA** (Assessment, Authorization, and Monitoring), **IA** (Identification and Authentication), **SC** (System and Communications Protection), and **SI** (System and Information Integrity).

The fabric comprises four Cisco IOS-XE nodes: two Catalyst 8000 series border gateway devices (AA-EDGE-GW-01, AA-EDGE-GW-02, AS 65100) and two Catalyst 9000 series spine switching nodes (AA-SPINE-01, AA-SPINE-02, AS 65000). The architecture implements eBGP across two Autonomous Systems for both IPv4 unicast underlay reachability and L2VPN EVPN overlay control-plane signalling. Multi-tenancy is delivered through VRF instantiation (VRF-101), VXLAN encapsulation (VNI 50101), and BGP Route Target (RT) import/export policy — providing tenant isolation commensurate with a logically separated security domain.

From a NIST risk management perspective, the design implements boundary protection at three layers: (i) the AS-level eBGP boundary between fabric domains (SC-7); (ii) VRF-enforced information flow control between tenant and infrastructure routing planes (AC-4); and (iii) explicit VLAN trunk allowlisting as a Layer 2 boundary enforcement mechanism (SC-7(5)). The VXLAN overlay provides cryptographic-equivalent traffic separation through network-layer encapsulation, consistent with the zero-trust network segmentation principles described in NIST SP 800-207.

Convergence resilience is addressed through BFD-assisted BGP fast failover, dual-path physical topology, and symmetric dual-VTEP configuration — directly supporting availability controls under SC-5 (Denial of Service Protection) and CP-7 (Alternate Processing Sites) in the context of network path diversity.

This document identifies control alignment, gaps, and hardening recommendations for each relevant NIST SP 800-53 control family.

---

## 2. Topology & Boundary Protection

### 2.1 Authorization Boundary Definition

The NIST Risk Management Framework (RMF, SP 800-37 Rev. 2) requires explicit definition of the system authorisation boundary. For this fabric, the authorisation boundary encompasses the four network nodes in scope and the logical interfaces between them. The external boundary terminations are:

- **WAN/Upstream:** Interfaces on AA-EDGE-GW-01/02 facing external networks (not present in the supplied configurations — referenced as out-of-scope WAN edge).
- **Tenant Boundary:** Spine trunk interfaces (Gi1/0/13, Gi1/0/14 on SP-01 and SP-02) connecting to downstream leaf devices in AS 65200.
- **Management Plane:** Out of scope per discovery parameters.

```
+=====================================================+
|         AUTHORISATION BOUNDARY                      |
|                                                     |
|  +---------------+        +---------------+         |
|  | AA-EDGE-GW-01 |        |  AA-SPINE-01  |         |
|  | CAT8K IOS-XE  |        |  CAT9K IOS-XE |         |
|  | AS 65100      |<------>|  AS 65000     |         |
|  | VTEP:10.200.0.1        |  VTEP:10.0.0.1|         |
|  +---------------+        +---------------+         |
|          |                        |                 |
|  +---------------+        +---------------+         |
|  | AA-EDGE-GW-02 |        |  AA-SPINE-02  |         |
|  | CAT8K IOS-XE  |        |  CAT9K IOS-XE |         |
|  | AS 65100      |<------>|  AS 65000     |         |
|  | VTEP:10.200.0.2        |  VTEP:10.0.0.2|         |
|  +---------------+        +---------------+         |
|                                                     |
+===[BOUNDARY]===========+===========+===============+
                         |           |
             [WAN/EXTERNAL]    [TENANT AS 65200]
             [Out of Scope]    [LEAF-01 / LEAF-02]
```

### 2.2 Perimeter Defence Architecture & Zero-Trust Principles

NIST SP 800-207 (Zero Trust Architecture) defines zero-trust as a shift from perimeter-based implicit trust to per-session explicit verification. The fabric implements several zero-trust-aligned controls:

**Micro-Segmentation via VRF:** VRF-101 enforces per-tenant forwarding isolation at the hardware level. No lateral movement between VRFs is possible without explicit route leaking policy — none is present in this configuration.

**Explicit Trust via BGP RT Policy:** Tenant route acceptance into VRF-101 is governed by BGP RT import matching. Only routes carrying the defined RT values (`10.0.0.1:101`, `10.0.0.2:101`, `10.200.0.1:101`, `10.200.0.2:101`) are imported. Routes not carrying these RTs are implicitly rejected.

**VXLAN Encapsulation as Overlay Boundary:** Tenant frames are encapsulated at each VTEP boundary. From the underlay perspective, all tenant traffic appears as UDP datagrams between known VTEP IP addresses, enforcing a clean separation between overlay and underlay trust domains.

**eBGP AS Boundary as Enforcement Point:** The AS boundary between 65100 (gateways) and 65000 (spines) and between 65000 and 65200 (tenant) functions as an explicit trust demarcation. Route acceptance across these boundaries is governed by BGP policy templates — not implicit trust.

### 2.3 Boundary Protection Diagram (SC-7)

```
+----------------------------------------------------------+
|  EXTERNAL NETWORKS (WAN / INTERNET)                      |
|  [Implicit Deny — No config in scope]                    |
+----------------------------------------------------------+
                          |
             +------------+------------+
             |   BORDER LAYER (SC-7)   |
             |   AA-EDGE-GW-01/02      |
             |   AS 65100 / CAT8K      |
             |   VTEP: 10.200.0.x      |
             +------------+------------+
                          |
             [eBGP AS 65100 <-> AS 65000]
             [EVPN RT-filtered route acceptance]
                          |
             +------------+------------+
             |   SPINE LAYER (SC-7(5)) |
             |   AA-SPINE-01/02        |
             |   AS 65000 / CAT9K      |
             |   VTEP: 10.0.0.x        |
             |   VRF-101 enforcement   |
             +------------+------------+
                          |
          +---------------+---------------+
          |  TENANT BOUNDARY (AC-4/SC-7)  |
          |  Trunk: VLANs 101,200-203     |
          |  Native VLAN: 666 (PARKED)    |
          |  eBGP: VRF-101 / AS 65200     |
          +-------------------------------+
                          |
             [TENANT NETWORK: AS 65200]
             [LEAF-01 / LEAF-02]
```

### 2.4 Secure Enclave Design (VXLAN Overlay)

The VXLAN overlay constitutes a logical secure enclave for tenant VRF-101 traffic. Enclave characteristics:

- **Boundary enforcement:** NVE1 interface on each VTEP. Only traffic with VNI 50101 membership is accepted into VRF-101 forwarding.
- **Reachability control:** `host-reachability protocol bgp` — host MAC/IP bindings are distributed exclusively via BGP EVPN control-plane, not via data-plane flooding. Unknown sources cannot inject host routes.
- **Ingress replication:** BUM traffic (broadcast/unknown unicast/multicast) is replicated to known VTEPs only, using a known-peers model rather than multicast, restricting BUM exposure to VTEP-to-VTEP paths.

```
+========================================================+
|          VXLAN SECURE ENCLAVE (VNI 50101 / VRF-101)    |
|                                                        |
|  VTEP-GW01          VTEP-SP01                          |
|  10.200.0.1 <-----> 10.0.0.1  (EVPN BGP control)      |
|       |                  |                             |
|  VTEP-GW02          VTEP-SP02                          |
|  10.200.0.2 <-----> 10.0.0.2  (EVPN BGP control)      |
|                                                        |
|  Encapsulation: VXLAN UDP/IP                           |
|  Host reachability: BGP EVPN (no flood/learn)          |
|  BUM: Ingress replication to known VTEPs only          |
|  RT Import guard: 4-RT symmetric matrix                |
+========================================================+
```

---

## 3. Protocol & Technology Deep Dive

### 3.1 BGP-4 Underlay (IPv4 Unicast)

BGP (RFC 4271) is the sole dynamic routing protocol. The dual-AS eBGP topology implements a strict routing domain separation between the gateway layer (AS 65100) and the spine layer (AS 65000). No IGP is deployed; BGP carries all reachability information via `redistribute connected`, ensuring only explicitly configured interfaces are advertised.

**Session Template Architecture:** All BGP sessions are instantiated via `template peer-session` constructs. This programmatic consistency reduces configuration drift — a direct mitigating control for CA-7 (Continuous Monitoring) and CM-6 (Configuration Settings). The use of named templates also facilitates auditability: a single template change propagates uniformly to all inheriting peers.

**`no bgp fast-external-fallover`:** Globally disabled on all nodes, preventing premature BGP session teardown on interface-level transient events. This is a deliberate stability control aligned with the Cisco CVD and reduces the risk of unnecessary routing instability that could be exploited for traffic manipulation.

**`bgp log-neighbor-changes`:** Present on all four nodes. State transition logging supports AU-2 (Event Logging) and AU-12 (Audit Record Generation) requirements.

**`soft-reconfiguration inbound`:** Present on AA-SPINE-01's AS 65100 peer-session template. This enables inbound soft reset capability without requiring a full BGP session tear-down, supporting operational maintenance without service disruption. Note: `soft-reconfiguration inbound` is absent on AA-SPINE-02's equivalent template — an asymmetric configuration.

**Relevant RFCs:** RFC 4271 (BGP-4), RFC 7938 (BGP in Large-Scale Data Centres), RFC 8212 (Default EBGP Route Propagation Behaviour Without Policies).

### 3.2 Bidirectional Forwarding Detection (BFD)

BFD (RFC 5880) provides sub-second link failure detection, configured via `fall-over bfd` in BGP peer-session templates. BFD operates independently of the BGP hold timer, detecting forwarding plane failures that may not immediately manifest as BGP notification messages.

From a NIST control perspective, BFD addresses SC-5 (Denial of Service Protection) by ensuring that black-hole forwarding conditions resulting from link failures are rapidly resolved. It also supports CP-7 (Alternate Processing Sites) by enabling fast failover to redundant fabric paths.

**Configuration Gap:** `fall-over bfd` is present on all AS 65000 peer-session templates (spine-to-spine and spine-to-gateway). It is absent from the AS 65100 iBGP peer-session template (`PS_UNDERLAY_INFRA_65100`) on GW-01, and from AA-SPINE-02's AS 65100 peer-session template. This creates asymmetric convergence: a failure on the GW-01 ↔ GW-02 iBGP path would recover at BGP hold-timer speed (default 90 seconds) rather than BFD-detection speed.

**Relevant RFCs:** RFC 5880 (BFD), RFC 5881 (BFD IPv4/IPv6 Single-Hop), RFC 5883 (BFD Multihop).

### 3.3 BGP L2VPN EVPN Overlay

EVPN (RFC 7432, RFC 8365) implements the BGP-based control-plane for the VXLAN data plane. EVPN replaces data-plane MAC learning with a control-plane distribution model, directly supporting SC-7 (Boundary Protection) by ensuring that MAC/IP bindings are distributed only through authenticated BGP sessions — not learned from arbitrary data-plane frames.

**Next-Hop Rewriting (EVPN-OUT-VTEP-REWRITE):** Each VTEP applies a route-map on outbound L2VPN EVPN advertisements, setting `ip next-hop` to the local Loopback0 address. This prevents transit infrastructure IP addresses from being exposed as BGP next-hops to external EVPN peers — a control aligned with SC-7(10) (Prevent Exfiltration) in the sense that internal infrastructure addressing is not disclosed in reachability advertisements.

**`replication-type ingress`:** BUM traffic is replicated by the ingress VTEP to all known remote VTEPs via unicast. This eliminates multicast state from the underlay and constrains BUM traffic propagation to explicitly known VTEP addresses — aligned with AC-4 (Information Flow Enforcement).

**Relevant RFCs:** RFC 7432 (BGP EVPN), RFC 8365 (NVO Using EVPN), RFC 4364 (BGP/MPLS IP VPNs), RFC 8277 (NLRI for BGP EVPN).

### 3.4 VXLAN Encapsulation (RFC 7348)

VXLAN encapsulates tenant Ethernet frames within UDP/IP (destination port 4789) for transport across the IP underlay fabric. Security and integrity properties relevant to NIST controls:

- **Tenant Isolation:** Each VNI (Virtual Network Identifier) represents a distinct Layer 2 broadcast domain. VNI 50101 is exclusively associated with VRF-101. Cross-VNI communication requires explicit routing policy — none is configured beyond the defined RT matrix.
- **Encapsulation Integrity:** VXLAN does not natively provide encryption or cryptographic authentication of encapsulated frames (RFC 7348, Section 7). Traffic confidentiality between VTEPs relies on the physical security and access control of the underlay network. For environments requiring in-flight encryption, MACsec (IEEE 802.1AE) or IPsec tunnel mode would be required as a complementary control.
- **MTU Engineering:** Jumbo MTU (9216/8978) on all fabric links prevents IP fragmentation of VXLAN-encapsulated frames, eliminating fragmentation-based evasion vectors and supporting SC-8 (Transmission Confidentiality and Integrity) indirectly by ensuring frame integrity through the encapsulation boundary.

**Relevant RFCs:** RFC 7348 (VXLAN), RFC 7637 (NVGRE — referenced for comparison).

### 3.5 VRF-101 Multi-Tenancy Architecture

VRF-101 implements the NIST concept of a logically separated security domain (SP 800-53 SC-2, System and Communications Partitioning). Key architectural parameters:

**Route Distinguishers:** Per-device RDs prevent route ambiguity in the BGP EVPN control-plane. Each VTEP advertises its VRF-101 routes with a unique RD, allowing the receiving BGP speaker to differentiate routes from different VTEPs even when the prefixes are identical.

**Route Target Stitching:** The `stitching` keyword on VRF route-targets instructs IOS-XE to use these RTs specifically for EVPN type-5 (IP prefix) route stitching — the mechanism by which L3 prefixes are distributed across the fabric overlay. This is the correct and complete implementation for EVPN IRB deployments.

**`advertise l2vpn evpn`:** Configured in VRF-101 address-family on all devices. This command redistributes VRF-101 IPv4 routes into the L2VPN EVPN address family as type-5 prefix routes, enabling L3 reachability advertisement across the overlay. Without this, VRF-101 routes would not be visible to remote VTEPs via EVPN.

**`maximum-paths 4`:** Configured in the VRF-101 IPv4 address-family on gateway nodes. ECMP across up to four equal-cost BGP paths supports load distribution and path redundancy within the tenant forwarding plane.

### 3.6 802.1Q Trunking — Boundary Control

Spine trunk interfaces to downstream leaf devices implement the following NIST SC-7(5) (Deny by Default / Allow by Exception) boundary controls:

- **Explicit VLAN Allowlist:** `switchport trunk allowed vlan 101,200` (SP-01→LEAF-01) and equivalents on all trunk ports. Only named VLANs traverse each trunk. No implicit "permit all" is present.
- **Parked Native VLAN (666):** `switchport trunk native vlan 666` displaces the default native VLAN 1, neutralising the double-encapsulation VLAN hopping attack vector (CVE-1999-0807). VLAN 666 carries no routed services.
- **No Negotiation:** Physical interfaces are explicitly configured (`switchport mode trunk`) rather than relying on DTP (Dynamic Trunking Protocol) auto-negotiation, which is an implicit trust mechanism inconsistent with SC-7 deny-by-default principles.

---

## 4. NIST Control Mapping & Best Practices

### 4.1 AC-4 — Information Flow Enforcement

**Control Text (SP 800-53 Rev. 5):** The system enforces approved authorizations for controlling the flow of information within the system and between connected systems based on [organization-defined information flow control policies].

**Implementation Assessment:**

The fabric enforces information flow control at three hierarchical layers:

Layer 1 (BGP AS Policy): eBGP policies govern which prefixes cross AS boundaries. The `send-community both` directive on all peer-policy templates ensures that BGP communities (including EVPN Route Targets) are propagated, enabling RT-based import/export filtering as the flow enforcement mechanism.

Layer 2 (VRF RT Import/Export): VRF-101 accepts only routes carrying the defined RT set. Routes not matching the RT import policy are silently discarded at the VRF boundary, implementing a default-deny information flow posture.

Layer 3 (VLAN Trunk Allowlist): Layer 2 information flow between spine nodes and leaf devices is constrained to explicitly listed VLANs per trunk port, preventing VLAN-based information leakage between tenants or from tenant to infrastructure VLANs.

**Gap:** Inbound route-map filtering is absent on AS 65200 eBGP sessions within VRF-101. Customer-originated route advertisements are accepted without explicit permit/deny filtering — a deviation from the AC-4 default-deny principle. See Section 5.1.

**Alignment Rating:** Partial. Core overlay flow enforcement is implemented; external boundary inbound filtering is absent.

### 4.2 AC-17 — Remote Access (Applicable to eBGP Peering Context)

**Control Text (SP 800-53 Rev. 5):** The organization establishes and documents usage restrictions, configuration/connection requirements, and implementation guidance for each type of remote access allowed.

**Implementation Assessment:**

eBGP sessions to AS 65200 (Customer A) constitute a form of controlled remote network access — a third-party network establishing a routing adjacency within VRF-101. Session parameters are governed by named peer-session templates (`PS_CUSTOMER_A_65200`) with `ebgp-multihop 5` and `send-community both` policies. This provides a documented, auditable session parameter baseline.

**Gap:** No BGP MD5 session authentication is configured on AS 65200 peer sessions. Any device reachable at the defined peer IP addresses (10.255.2.2, 10.255.2.6, 10.255.2.10, 10.255.2.14) could attempt a BGP session establishment without credential verification. See Section 5.2.

### 4.3 IA-3 — Device Identification and Authentication

**Control Text (SP 800-53 Rev. 5):** The system uniquely identifies and authenticates [organization-defined devices and/or types of devices] before establishing connections.

**Implementation Assessment:**

BGP session establishment relies on IP-address-based peer identification (`neighbor X.X.X.X`) without cryptographic device authentication. BGP MD5 (RFC 2385) provides a shared-secret authentication mechanism for BGP sessions, mitigating BGP session hijacking and spoofed UPDATE injection. No MD5 or TCP-AO (RFC 5925) authentication is configured on any session in the fabric.

**Gap:** Complete absence of BGP session authentication constitutes a gap against IA-3. While the physical/network access controls of the underlay provide implicit device identification through IP address binding, this is not equivalent to cryptographic authentication.

**Alignment Rating:** Not Met. BGP session authentication is absent on all fabric and external sessions.

### 4.4 SC-2 — System and Communications Partitioning (Separation of System Components)

**Control Text (SP 800-53 Rev. 5):** The system separates user functionality from system management functionality.

**Implementation Assessment:**

The VRF architecture provides hardware-enforced partitioning between the tenant forwarding plane (VRF-101) and the fabric infrastructure routing plane (global VRF/default routing table). Infrastructure control-plane traffic (BGP sessions, BFD packets, VTEP tunnel traffic) operates in the global routing table. Tenant data-plane traffic is encapsulated in VXLAN and forwarded within the overlay domain, with Layer 3 routing confined to VRF-101 contexts.

No cross-VRF route leaking is configured. The `vrf forwarding VRF-101` directive on all tenant-facing interfaces (BDI101, Vlan101, SVIs 200–203) ensures strict VRF binding — traffic arriving on these interfaces is processed exclusively within the VRF-101 forwarding context.

**Alignment Rating:** Met. The VRF model directly implements SC-2 separation of system components.

### 4.5 SC-5 — Denial of Service Protection

**Control Text (SP 800-53 Rev. 5):** The system protects against or limits the effects of denial-of-service events, including attacks originating from external sources.

**Implementation Assessment:**

- **BFD Fast Convergence:** Reduces black-hole duration following link failure, limiting the denial-of-service impact of physical link failures on tenant traffic.
- **`no bgp fast-external-fallover`:** Prevents BGP session instability from link micro-flaps, reducing susceptibility to oscillation-based DoS against the BGP control-plane.
- **Dual-path physical topology:** Each gateway peers with both spines; each spine peers with both gateways and with each other. No single link failure results in a total loss of fabric connectivity.

**Gap:** No BGP maximum-prefix limits (`maximum-prefix`) are configured. A prefix-flooding attack from AS 65200 (or a misconfigured CE) could exhaust BGP table memory. See Section 5.3.

**Gap:** No rate-limiting or CoPP (Control Plane Policing) configuration is visible in the supplied files. CoPP is recommended on all IOS-XE devices to protect the control-plane from data-plane-sourced floods targeting BGP, BFD, or other protocol processes.

**Alignment Rating:** Partial. Physical redundancy and BFD are implemented; prefix-limit and CoPP controls are absent.

### 4.6 SC-7 — Boundary Protection

**Control Text (SP 800-53 Rev. 5):** The system monitors and controls communications at the external boundary of the system and at key internal boundaries within the system.

**Implementation Assessment:**

- **External Boundary (SC-7(3) — Access Points):** The fabric does not expose any transit services beyond the defined eBGP peering points. No default route redistribution into external AS is present in the configurations under review.
- **Internal Boundary (SC-7(5) — Deny by Default):** VRF RT policy and VLAN trunk allowlisting implement an implicit deny-by-default posture at internal boundaries. Routes not matching RT import policy are rejected; VLANs not explicitly listed on trunk ports are blocked.
- **VTEP Boundary (SC-7(10) — Prevent Exfiltration):** The `EVPN-OUT-VTEP-REWRITE` route-map rewrites EVPN next-hops to Loopback0 addresses, preventing internal transit IP addresses from being disclosed to external BGP peers in EVPN route advertisements.

**Gap:** Inbound prefix filtering on AS 65200 sessions is absent — see Section 5.1. This represents an incomplete SC-7 implementation at the tenant external boundary.

**Alignment Rating:** Substantially Met with noted gaps.

### 4.7 SC-8 — Transmission Confidentiality and Integrity

**Control Text (SP 800-53 Rev. 5):** The system implements cryptographic mechanisms to prevent unauthorized disclosure of information and detect changes to information during transmission unless otherwise protected by alternative physical safeguards.

**Implementation Assessment:**

VXLAN (RFC 7348) does not provide native encryption or cryptographic integrity verification of encapsulated frames. Transmission confidentiality within the fabric relies entirely on the physical and logical access controls of the underlay network. Where the underlay traverses shared or untrusted physical infrastructure, this constitutes a gap against SC-8.

For this fabric topology (a data centre environment where the underlay is presumed to be operator-controlled), physical safeguards may constitute the alternative protection referenced in SC-8. However, this assumption should be explicitly documented in the system's System Security Plan (SSP).

**Gap:** No MACsec (IEEE 802.1AE) or IPsec tunnel-mode encryption is configured for inter-VTEP VXLAN traffic. If the underlay traverses any shared or provider-managed infrastructure, SC-8 is not met without encryption.

**Alignment Rating:** Conditionally Met (physical safeguard assumption); Not Met if underlay traverses shared infrastructure.

### 4.8 CA-7 — Continuous Monitoring

**Control Text (SP 800-53 Rev. 5):** The organization develops a continuous monitoring strategy and implements a continuous monitoring program.

**Implementation Assessment:**

- **`bgp log-neighbor-changes`:** Provides a baseline audit stream for BGP control-plane state changes, supporting ongoing awareness of fabric routing stability.

**Gap:** No streaming telemetry (gRPC/gNMI), SNMP trap configuration, or NetFlow/IPFIX data-plane visibility is present in the in-scope configurations. While management-plane tooling is out of scope for this review, the absence of data-plane flow telemetry constitutes a gap against CA-7's requirement for ongoing security-relevant event collection. This should be addressed in the management-plane design.

**Alignment Rating:** Minimally Met. BGP state logging exists; data-plane and structured telemetry are absent in the reviewed configurations.

---

## 5. Observations, Gaps & Hardening Recommendations

### 5.1 Absent Inbound BGP Prefix Filtering — AS 65200 VRF-101 Sessions

**NIST Controls:** AC-4 (Information Flow Enforcement), SC-7 (Boundary Protection), SC-7(5) (Deny by Default)

**Risk:** All four AS 65200 eBGP neighbour relationships within `address-family ipv4 vrf VRF-101` accept routes without inbound filtering. An unconstrained or hostile CE device can advertise arbitrary prefixes — including infrastructure addresses, other tenant subnets, or supernets — into VRF-101. This violates the AC-4 default-deny information flow principle and could enable traffic hijacking within the tenant domain.

**Recommendation:** Apply explicit inbound prefix-list or route-map on all AS 65200 neighbour sessions:

```
ip prefix-list CUST-A-PERMITTED-IN seq 5 permit 10.0.0.0/8 le 24
ip prefix-list CUST-A-PERMITTED-IN seq 10 deny 0.0.0.0/0 le 32

route-map CUST-A-IN permit 10
  match ip address prefix-list CUST-A-PERMITTED-IN

router bgp 65000
  address-family ipv4 vrf VRF-101
    neighbor 10.255.2.2 route-map CUST-A-IN in
    neighbor 10.255.2.6 route-map CUST-A-IN in
```

Apply equivalent policy on all four AS 65200 session points (SP-01 and SP-02).

### 5.2 Absent BGP Session Authentication (MD5 / TCP-AO)

**NIST Controls:** IA-3 (Device Identification and Authentication), SC-8 (Transmission Integrity)

**Risk:** All BGP sessions — both intra-fabric eBGP and the AS 65200 external sessions — are unauthenticated. TCP-level BGP session hijacking or spoofed UPDATE injection is possible from any host capable of reaching the BGP peer IP addresses. While `ebgp-multihop 5` increases the TTL attack surface, it does not substitute for cryptographic session authentication.

**Recommendation:** Enable BGP MD5 authentication (RFC 2385) on all sessions. For inter-fabric sessions, use a strong, unique shared secret per session pair. For AS 65200 sessions, coordinate pre-shared key exchange with the tenant as part of the service onboarding process. Where IOS-XE supports it, TCP-AO (RFC 5925) via `ip tcp ao` provides stronger authentication than MD5.

```
neighbor 10.255.1.2 password <REDACTED>
neighbor 10.255.1.6 password <REDACTED>
```

### 5.3 Absent BGP Maximum-Prefix Limits

**NIST Controls:** SC-5 (Denial of Service Protection), SC-6 (Resource Availability)

**Risk:** No `maximum-prefix` limits are configured on any BGP neighbour. An unconstrained route advertisement from any peer — particularly the external AS 65200 sessions — could exhaust BGP RIB memory, causing process instability or system-level resource exhaustion. This is a known BGP-based DoS vector.

**Recommendation:** Configure `maximum-prefix` with a threshold alert and hard limit on all eBGP sessions. For external AS 65200 sessions, use a conservative limit reflecting expected customer prefix counts:

```
neighbor 10.255.2.2 maximum-prefix 200 80
```

The `80` argument triggers a syslog warning at 80% of the limit before the hard limit is enforced. For intra-fabric sessions, apply limits commensurate with the expected prefix count (loopbacks + transit links).

### 5.4 Absent Control Plane Policing (CoPP)

**NIST Controls:** SC-5 (Denial of Service Protection), SC-6 (Resource Availability)

**Risk:** No CoPP (Control Plane Policing) configuration is present in the supplied configurations. IOS-XE on Catalyst 8000/9000 platforms supports granular CoPP policy to rate-limit protocol traffic (BGP, BFD, OSPF, ARP, ICMP) destined for the Route Processor. Without CoPP, a data-plane flood of protocol-destined traffic (e.g., SYN flood targeting TCP port 179) could exhaust Route Processor CPU, disrupting all BGP and BFD sessions simultaneously.

**Recommendation:** Deploy a CoPP policy classifying and policing control-plane traffic by protocol class. Cisco provides a default CoPP template for IOS-XE that should be customised for the specific protocol mix of this fabric. Example class structure:

```
class-map match-any CoPP-BGP
  match access-group name ACL-BGP
policy-map CoPP-POLICY
  class CoPP-BGP
    police rate 1000 pps
control-plane
  service-policy input CoPP-POLICY
```

### 5.5 Absent VXLAN Encryption (SC-8 Gap)

**NIST Controls:** SC-8 (Transmission Confidentiality and Integrity), SC-8(1) (Cryptographic Protection)

**Risk:** VXLAN does not encrypt encapsulated frames. If the underlay network traverses any shared physical infrastructure (e.g., provider dark fibre, co-location cross-connects), tenant data is transmitted in cleartext within the VXLAN UDP payload. An attacker with physical access to the underlay layer could capture and inspect tenant traffic.

**Recommendation:** Evaluate the physical security posture of the underlay. If the underlay traverses any non-exclusively-controlled physical media, implement MACsec (IEEE 802.1AE) on inter-node links or IPsec in tunnel mode between VTEP loopback addresses. IOS-XE on Catalyst 9000 supports MACsec on physical interfaces. Document the physical safeguard assumption in the System Security Plan if encryption is deferred.

### 5.6 Asymmetric `soft-reconfiguration inbound` Configuration

**NIST Controls:** CM-6 (Configuration Settings), CA-7 (Continuous Monitoring)

**Risk:** `soft-reconfiguration inbound` is present in AA-SPINE-01's peer-session template for AS 65100 peers but absent from AA-SPINE-02's equivalent template. This asymmetry means that inbound soft reset operations on SPINE-02 will require a hard BGP session reset, causing a brief routing disruption during policy maintenance operations. More significantly, configuration asymmetry between redundant nodes is a configuration management discipline gap — it increases the likelihood of undetected divergence between nodes over time.

**Recommendation:** Standardise peer-session templates across both spine nodes. Add `soft-reconfiguration inbound` to AA-SPINE-02's `PS_UNDERLAY_INFRA_65100` template. Implement a configuration compliance check (e.g., via Cisco NSO, Ansible, or NAPALM) to continuously validate template parity between redundant node pairs.

### 5.7 EVE-NG Lab Origin — Production Readiness Gate

**NIST Controls:** CM-2 (Baseline Configuration), SA-10 (Developer Configuration Management)

**Observation:** The presence of `! license boot level network-advantage addon dna-advantage` (commented out) in all four device configurations indicates this build was developed and validated in an EVE-NG simulation environment. Prior to production deployment, the following gates must be cleared:

- Validate IOS-XE license tier (Network Advantage + DNA Advantage) is active on all physical Catalyst 8000/9000 hardware.
- Execute full feature validation (EVPN/VXLAN, BFD, VRF, NVE) on physical hardware against tested EVE-NG configuration.
- Remove or document all simulation-context comments from production configurations.
- Establish a baseline configuration backup in a version-controlled repository prior to service activation.

---

*End of Document B — NIST SP 800-53 Rev. 5 / CSF 2.0 HLD*
