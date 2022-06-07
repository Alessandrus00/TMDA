# Unhealty containers problem
### If you got unhealty es01/kibana containers run from powershell: 

```shell
wsl -d docker-desktop
sysctl -w vm.max_map_count=262144
exit
```