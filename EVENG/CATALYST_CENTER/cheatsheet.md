# Cisco Catalyst Center - Top Operational Maglev CLI Commands

## Accessing the Maglev Shell

```bash
maglev ssh
```

or

```bash
ssh maglev@<ip-address>
```

---

# Top Cisco Catalyst Center Commands

| # | Command | Description |
|---|---|---|
| 1 | `magctl appstack status` | Shows health of all application stacks |
| 2 | `magctl appstack status \| grep -i unhealthy` | Shows unhealthy services/pods |
| 3 | `magctl service status` | Shows platform service health |
| 4 | `magctl service logs -s <service>` | Shows logs for a service |
| 5 | `magctl appstack restart <service>` | Restarts an application stack |
| 6 | `magctl inventory display` | Displays cluster inventory |
| 7 | `magctl node display` | Shows node details and IP addresses |
| 8 | `magctl node status` | Displays node health |
| 9 | `magctl cluster display` | Shows cluster information |
| 10 | `magctl cluster network display` | Displays cluster network configuration |
| 11 | `magctl certs display` | Displays certificate information |
| 12 | `magctl certs expiry` | Shows certificate expiry dates |
| 13 | `magctl backup status` | Shows backup status |
| 14 | `magctl backup create` | Creates a backup |
| 15 | `magctl support bundle create` | Generates TAC support bundle |
| 16 | `kubectl get pods -A` | Lists all Kubernetes pods |
| 17 | `kubectl get nodes` | Lists Kubernetes nodes |
| 18 | `kubectl describe pod <pod> -n <namespace>` | Shows detailed pod information |
| 19 | `kubectl logs <pod> -n <namespace>` | Displays pod logs |
| 20 | `kubectl logs -f <pod> -n <namespace>` | Follows live pod logs |
| 21 | `kubectl top pods -A` | Shows pod CPU/memory usage |
| 22 | `kubectl top nodes` | Shows node CPU/memory usage |
| 23 | `kubectl get events -A` | Shows Kubernetes events |
| 24 | `ip addr` | Displays interface IP addresses |
| 25 | `ip route` | Displays routing table |
| 26 | `cat /etc/resolv.conf` | Displays DNS configuration |
| 27 | `df -h` | Displays filesystem usage |
| 28 | `free -m` | Displays memory usage |
| 29 | `top` | Real-time CPU/memory usage |
| 30 | `journalctl -xe` | Displays Linux system logs |

---

# Most Important Commands

| Command | Purpose |
|---|---|
| `magctl appstack status` | Overall application health |
| `magctl node display` | Node IP addresses |
| `magctl service status` | Platform service health |
| `kubectl get pods -A` | Kubernetes troubleshooting |
| `kubectl logs <pod> -n <namespace>` | Log troubleshooting |
| `kubectl top pods -A` | Resource troubleshooting |
| `ip addr` | Check IP addresses |
| `df -h` | Disk troubleshooting |
| `top` | CPU/memory troubleshooting |
| `magctl support bundle create` | TAC troubleshooting |

---

# How To Find The IP Address

## Show Node IP Addresses

```bash
magctl node display
```

---

## Show Interface IP Addresses

```bash
ip addr
```

---

## Show Routing Table

```bash
ip route
```

---

# Typical Troubleshooting Workflow

| Step | Command | Purpose |
|---|---|---|
| 1 | `magctl appstack status` | Check overall health |
| 2 | `magctl node display` | Check node IPs/status |
| 3 | `magctl service status` | Check services |
| 4 | `kubectl get pods -A` | Find failing pods |
| 5 | `kubectl logs <pod> -n <namespace>` | Review logs |
| 6 | `kubectl top pods -A` | Check resource usage |
| 7 | `df -h` | Verify disk space |
| 8 | `top` | Verify CPU/memory |

---

# Useful Service Troubleshooting Examples

## Find Authentication Services

```bash
magctl service status | grep -i auth
```

---

## Find Assurance Services

```bash
magctl service status | grep -i assurance
```

---

## Find Inventory Services

```bash
magctl service status | grep -i inventory
```

---

## Follow Service Logs

```bash
magctl service logs -s inventory-service -f
```

---

# Kubernetes Examples

## Restart a Pod

```bash
kubectl delete pod <pod-name> -n <namespace>
```

---

## Describe a Node

```bash
kubectl describe node <node-name>
```

---

## Find CrashLoopBackOff Pods

```bash
kubectl get pods -A | grep CrashLoopBackOff
```

---

# Official References

Cisco Catalyst Center Documentation  
https://www.cisco.com/c/en/us/support/cloud-systems-management/dna-center/products-installation-and-configuration-guides-list.html

Cisco DevNet Catalyst Center APIs  
https://developer.cisco.com/docs/dna-center/
