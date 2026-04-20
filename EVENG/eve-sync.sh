# SYNC MASTER TO SATELITE
#!/bin/bash
# place file in root directory as "/root/eve-sync.sh"

# EVE IMAGES
rsync -avz --delete /opt/unetlab/addons/qemu/ root@34.61.215.27:/opt/unetlab/addons/qemu/

# EVE TEMPLATES
rsync -avz --delete /opt/unetlab/html/templates/ root@34.61.215.27:/opt/unetlab/html/templates/

# FIX PERMISSIONS ON SATELITE
ssh root@34.61.215.27 "/opt/unetlab/wrappers/unl_wrapper -a fixpermissions"

#
# CRON JOB
#

# Once a day
# crontab -e
# 0 2 * * * /root/eve-sync.sh > /dev/null 2>&1
