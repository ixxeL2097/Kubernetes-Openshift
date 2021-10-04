[main menu](../README.md)

## 02 - Installing NFS client provisionner on kube


NEW version :
- https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner

OLD :
- https://github.com/kubernetes-retired/external-storage/tree/master/nfs-client

You can download the helm chart associated :

```console
[root@workstation ~]# helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
"nfs-subdir-external-provisioner" has been added to your repositories
[root@workstation ~]# helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "nfs-subdir-external-provisioner" chart repository
Update Complete. ⎈ Happy Helming!⎈ 
[root@workstation ~]# helm fetch --untar nfs-subdir-external-provisioner/nfs-subdir-external-provisioner
```

And then install it using your needed configuration : 

```console
[root@workstation ~]# helm upgrade -i nfs-ext-provider nfs-subdir-external-provisioner/ -n nfs --set nfs.server=192.168.0.26 --set nfs.path=/NFS
```

Or 

```console
[root@workstation ~]# helm upgrade -i nfs-ext-provider nfs-subdir-external-provisioner/ -n nfs --set nfs.server=192.168.0.26 --set nfs.path=/NFS --set storageClass.reclaimPolicy=Retain --set accessModes=ReadWriteMany
Release "nfs-ext-provider" does not exist. Installing it now.
NAME: nfs-ext-provider
LAST DEPLOYED: Wed Jul 21 11:27:32 2021
NAMESPACE: nfs
STATUS: deployed
REVISION: 1
TEST SUITE: None
```

You can specify additional flags :

```
--set storageClass.reclaimPolicy=Retain
--set accessModes=ReadWriteMany
```

Check that your release is properly installed : 

```console
[root@workstation ~]# helm ls -n nfs
NAME            	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART                                 	APP VERSION
nfs-ext-provider	nfs      	1       	2021-07-21 11:27:32.199062693 +0000 UTC	deployed	nfs-subdir-external-provisioner-4.0.12	4.0.2
```

You can retrieve provided values of a specific helm release :

```console
[root@workstation ~]# helm get values nfs-ext-provider -n nfs
USER-SUPPLIED VALUES:
accessModes: ReadWriteMany
nfs:
  path: /NFS
  server: 192.168.0.26
storageClass:
  reclaimPolicy: Retain
```

Alternate commands :

```shell
helm get manifest nfs-provisioner -n nfs-provisioner
helm get all nfs-provisioner -n nfs-provisioner
```

Check your new `storageClass` :

```console
[root@workstation ~]# kubectl get sc
NAME                   PROVISIONER                                                      RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
nfs-client             cluster.local/nfs-ext-provider-nfs-subdir-external-provisioner   Retain          Immediate              true                   4m27s
```

And set it as default `storageClass` :

```console
[root@workstation ~]# kubectl patch storageclass nfs-client -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
storageclass.storage.k8s.io/nfs-client patched

[root@workstation ~]# kubectl get sc
NAME                   PROVISIONER                                                      RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
nfs-client (default)   cluster.local/nfs-ext-provider-nfs-subdir-external-provisioner   Retain          Immediate              true                   8m39s
```
