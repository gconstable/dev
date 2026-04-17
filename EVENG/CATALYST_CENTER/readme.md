# Instructions

1. Copy eveng Yaml template to
```
/opt/unetlab/html/trmplates/amd/dnac.yml
```
1. Copy ova file to eveng directory.
```
/opt/unetlab/addons/qemu/dnac-x.x.x.x
```
1. Naavigate to directory if you are not already within it.
1. Extract the ova file.
```
tar xvf {ova filename}
```
1. Convert the vmdk files to qcow2 formats.
```
qemu-img convert -cf vmdk -0 qcow2 {vmdk file name} sata{a}.qcow2 -p
```
!Repeat steps for each vmdk making sure to update the disk id each time i.e. a,b,c
