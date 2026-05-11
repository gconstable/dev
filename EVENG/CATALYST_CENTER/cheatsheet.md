````markdown
# Cisco Catalyst Center (DNA Center) - Top Maglev CLI Commands

## Overview

This document contains commonly used Cisco Catalyst Center (formerly Cisco DNA Center) Maglev CLI commands used for:

- Cluster health
- Node management
- IP addressing
- Kubernetes troubleshooting
- Service troubleshooting
- Resource monitoring
- Log collection

---

# Accessing the Maglev CLI

```bash
maglev ssh
```

or directly:

```bash
ssh maglev@<dnac-ip>
```

---

# Top Maglev CLI Commands

| # | Command | Description |
|---|---|---|
| 1 | `maglev status` | Shows overall cluster health and status |
| 2 | `maglev node list` | Lists all cluster nodes and status |
| 3 | `maglev service list` | Displays platform services and health |
| 4 | `maglev package status` | Shows package deployment status |
| 5 | `magctl appstack status` | Displays Kubernetes/AppStack health |
| 6 | `magctl appstack status \| grep -i unhealthy` | Filters unhealthy pods/services |
| 7 | `maglev cluster network display` | Displays cluster networking configuration |
| 8 | `maglev node display` | Shows node IP addresses and hostnames |
| 9 | `ip addr` | Displays all interface IP addresses |
| 10 | `ifconfig` | Legacy interface information |
| 11 | `ip route` | Displays routing table |
| 12 | `cat /etc/resolv.conf` | Displays DNS configuration |
| 13 | `nslookup cisco.com` | Tests DNS resolution |
| 14 | `ping 8.8.8.8` | Tests ICMP connectivity |
| 15 | `nc -zv <ip> <port>` | Tests TCP port connectivity |
| 16 | `kubectl get nodes` | Lists Kubernetes nodes |
| 17 | `kubectl get pods -A` | Lists all Kubernetes pods |
| 18 | `kubectl describe pod <pod-name> -n <namespace>` | Displays detailed pod information |
| 19 | `kubectl logs <pod-name> -n <namespace>` | Displays pod logs |
| 20 | `kubectl logs -f <pod-name> -n <namespace>` | Follows live pod logs |
| 21 | `kubectl rollout restart deployment <deployment-name> -n <namespace>` | Restarts deployment |
| 22 | `top` | Real-time CPU and memory usage |
| 23 | `htop` | Enhanced process viewer |
| 24 | `df -h` | Displays disk usage |
| 25 | `free -m` | Displays memory usage |
| 26 | `kubectl top pods -A` | Displays pod CPU/memory usage |
| 27 | `kubectl top nodes` | Displays node CPU/memory usage |
| 28 | `journalctl -xe` | Displays Linux system logs |
| 29 | `magctl service logs -s <service-name>` | Displays service logs |
| 30 | `maglev support bundle` | Generates TAC support bundle |

---

# Additional Useful Commands

| Command | Description |
|---|---|
| `timedatectl` | Displays system time and NTP sync status |
| `chronyc sources` | Displays NTP sources |
| `docker ps` | Shows running Docker containers |
| `sudo su -` | Enters root shell |

---

# Most Important Commands to Memorize

| Command | Purpose |
|---|---|
| `maglev status` | Cluster health |
| `maglev node display` | Node IP addresses |
| `maglev service list` | Service health |
| `magctl appstack status` | Pod/container health |
| `kubectl get pods -A` | Kubernetes pod visibility |
| `kubectl logs <pod> -n <namespace>` | Troubleshooting logs |
| `ip addr` | Interface IP addresses |
| `df -h` | Disk space |
| `top` | CPU/memory troubleshooting |
| `maglev support bundle` | TAC troubleshooting |

---

# Typical Troubleshooting Workflow

| Step | Command | Purpose |
|---|---|---|
| 1 | `maglev status` | Verify overall cluster health |
| 2 | `maglev node display` | Check node IPs and status |
| 3 | `maglev service list` | Validate services |
| 4 | `magctl appstack status` | Identify failing pods |
| 5 | `kubectl logs <pod-name> -n <namespace>` | Review logs |
| 6 | `df -h` | Check disk space |
| 7 | `top` | Check CPU and memory |
| 8 | `kubectl top pods -A` | Identify resource-heavy pods |

---

# Official References

Cisco Catalyst Center Documentation  
https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/products-installation-and-configuration-guides-list.html

Cisco Catalyst Center Administration Guides  
https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/products-maintenance-guides-list.html

Cisco DevNet Catalyst Center APIs  
https://developer.cisco.com/docs/dna-center/

````
