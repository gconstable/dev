# Readme
## Notes

## File Naming
### lab configs
Lab config files need to be of type .json
The file is named with the following format: <name>.<configType>.json

#### CONFIG_TYPES
1. cloud = cloud (Contains cloud network data)
2. node = node (Contains node device data)
3. n2c = node to cloud link (Contains link data towards a cloud)
4. n2n = node to node link (Contains link data towards another node)

#### EXAMPLES
cloud.<oob>.json (Cloud Network)

## IPAM
### OOB MGMT
#### STATIC
1. 10.57.1.0/24 
2. 10.57.1.1 - 10.57.1.20 (Reserved)
3. 10.57.1.1 - Gateway (Router - Linksys)
4. 10.57.1.18 - Cisco DNAC Service (Central Services)

#### DHCP
1. 10.57.1.21 - 10.57.1.254

#### Services
1. 8.8.8.8 (Google DNS)
2. 216.29.35.12 (NTP - time4.google.com)

## Services
### Cisco Caalyst Center (DNAC)
#### IP Addresses
1. 10.57.1.18

### Creds
1. GUI Username: admin
1. GUI Password: Adm1ni5trat0r
1. CLI Username: maglev
1. CLI Password: maglev1@3
1. CLI Port: 2222
1. CIMC Default: admin / password

### Key CLI Commands
1. magctl service status (service status)
2. magctl service restart -d <service name> (restart service)
3. sudo maglev-config update (rerun config wizard)
4. magctl appstack status (View all services and status)
5. ip a (List ip addresses on device)
6. ip a | grep management (Check management interface) {management | enterprise | cluster}
7. sudo maglev-config update (Launches text based wizard that walks through every network adapter setting)

### Key CLI Managemement commands
Connect to management interface via ssh on port 2222

1. magctl appstack status | grep kong
2. magctl service restart -d kong
3. _shell -c 'sudo magctl ssh shell bash' (escape restricted shell)
4. magctl node diagnostics (run node diagnostics)
5. sudo kubectl describe pod dragonfly-kong-7d5b57d8bd-2qp87 -n maglev-ingress (Hidden logs for process)


