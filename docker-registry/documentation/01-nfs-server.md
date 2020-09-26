[main menu](../README.md)

## 01 - Installing NFS server

First install packages : `nfs-kernel-server` for the server and `nfs-common` for nfs client.

```
sudo apt install nfs-kernel-server nfs-common
```

installation might be different regarding Linux distro.

Create a directory for NFS data 

```
mkdir -p  /NFS
```

Then export the above file systems in the NFS server `/etc/exports` configuration file to determine local physical file systems that are accessible to NFS clients :

```console
[root@nfs-server ~]# cat /etc/exports
/NFS 192.168.0.150(rw,sync,no_root_squash) 192.168.0.151(rw,sync,no_root_squash) 192.168.0.152(rw,sync,no_root_squash)
```

- rw – allows both read and write access on the file system.
- sync – tells the NFS server to write operations (writing information to the disk) when requested (applies by default).
- all_squash – maps all UIDs and GIDs from client requests to the anonymous user.
- no_all_squash – used to map all UIDs and GIDs from client requests to identical UIDs and GIDs on the NFS server.
- root_squash – maps requests from root user or UID/GID 0 from the client to the anonymous UID/GID.

To export the above file system, run the exportfs command with the -a flag means export or unexport all directories, -r means reexport all directories, synchronizing /var/lib/nfs/etab with /etc/exports and files under /etc/exports.d, and -v enables verbose output.

```console
[root@nfs-server ~]# exportfs -arv
exporting 192.168.0.150:/NFS
exporting 192.168.0.151:/NFS
exporting 192.168.0.152:/NFS
```

To display the current export list, run the following command :

```console
[root@nfs-server ~]# exportfs -s
/NFS  192.168.0.150(sync,wdelay,hide,no_subtree_check,sec=sys,rw,secure,no_root_squash,no_all_squash)
/NFS  192.168.0.151(sync,wdelay,hide,no_subtree_check,sec=sys,rw,secure,no_root_squash,no_all_squash)
/NFS  192.168.0.152(sync,wdelay,hide,no_subtree_check,sec=sys,rw,secure,no_root_squash,no_all_squash)
```

If you have firewalld running, you need to allow traffic to the necessary NFS services then reload the service :

```
firewall-cmd --permanent --add-service=nfs
firewall-cmd --permanent --add-service=rpc-bind
firewall-cmd --permanent --add-service=mountd
firewall-cmd --reload
```

You can display your firewalld config : 

```console
[root@nfs-server ~]# firewall-cmd --list-all
public (active)
  target: default
  icmp-block-inversion: no
  interfaces: eth0
  sources: 
  services: dhcpv6-client mountd nfs rpc-bind ssh
  ports: 
  protocols: 
  masquerade: no
  forward-ports: 
  source-ports: 
  icmp-blocks: 
  rich rules:
```

Or services allowed in the current zone:

```console
[root@nfs-server ~]# firewall-cmd --list-services
dhcpv6-client mountd nfs rpc-bind ssh
```

On the NFS client you can display NFS shares : 

```console
[root@kube-master01 ~]# showmount -e 192.168.0.26
Export list for 192.168.0.26:
/NFS 192.168.0.152,192.168.0.151,192.168.0.150
```


## Interesting links

- https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/security_guide/sec-viewing_current_status_and_settings_of_firewalld
- https://www.tecmint.com/install-nfs-server-on-centos-8/

---------------------------------------------------------------------------------------------------------------------------------

[main menu](../README.md)

[next]()

