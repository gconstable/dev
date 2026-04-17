# Instructions

1. Copy eveng Yaml template to
```
/opt/unetlab/html/trmplates/amd/dnac.yml
```

2. Copy ova file to eveng directory.
```
/opt/unetlab/addons/qemu/dnac-x.x.x.x
```

3. Naavigate to directory if you are not already within it.

4. Extract the ova file.
```
tar xvf {ova filename}
```

5. Convert the vmdk files to qcow2 formats.
```
qemu-img convert -cf vmdk -0 qcow2 {vmdk file name} sata{a}.qcow2 -p
```
!Repeat steps for each vmdk making sure to update the disk id each time i.e. a,b,c

6. Start node
  
7. Commit the image
From within the eveng gui for the lab.  Navigate to the dir where the disks have been span up within i.e. lab node id location.
```
/opt/qemu/bin/qemu-img rebase -b "" sataa.qcow2 -p
```
!!! Repeat for each disk.

8. Copy these rebased disks back over the original disks.
   

