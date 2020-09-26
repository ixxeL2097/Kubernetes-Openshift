[main menu](../README.md)

## 02 - Installing NFS client provisionner on kube

- https://github.com/kubernetes-retired/external-storage/tree/master/nfs-client

You can download the helm chart associated :

```console
[root@workstation ~]# helm repo add stable https://kubernetes-charts.storage.googleapis.com
"stable" has been added to your repositories
[root@workstation ~]# helm repo update                                                                             [17:02:23]
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "stable" chart repository
Update Complete. ⎈ Happy Helming!⎈ 
[root@workstation ~]# helm fetch --untar stable/nfs-client-provisioner
```

And then install it using your needed configuration : 

```console
[root@workstation ~]# helm install nfs-provisioner nfs-client-provisioner/ -n nfs-provisioner --set nfs.server=192.168.0.26 --set nfs.path=/NFS
```

Or 

```console
[root@workstation ~]# helm upgrade -i nfs-provisioner nfs-client-provisioner/ -n nfs-provisioner --set nfs.server=192.168.0.26 --set nfs.path=/NFS --set storageClass.reclaimPolicy=Retain --set accessModes=ReadWriteMany
Release "nfs-provisioner" does not exist. Installing it now.
NAME: nfs-provisioner
LAST DEPLOYED: Sat Sep 26 17:25:22 2020
NAMESPACE: nfs-provisioner
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
[root@workstation ~]# helm ls -n nfs-provisioner
NAME           	NAMESPACE      	REVISION	UPDATED                               	STATUS  	CHART                       	APP VERSION
nfs-provisioner	nfs-provisioner	1       	2020-07-25 01:53:19.8497089 +0200 CEST	deployed	nfs-client-provisioner-1.2.8	3.1.0
```

You can retrieve provided values of a specific helm release :

```console
[root@workstation ~]# helm get values nfs-provisioner -n nfs-provisioner
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
NAME         PROVISIONER                                            RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
nfs-client   cluster.local/nfs-provisioner-nfs-client-provisioner   Retain          Immediate           true                   78s
```

And set it as default `storageClass` :

```console
[root@workstation ~]# kubectl patch storageclass nfs-client -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
storageclass.storage.k8s.io/nfs-client patched

[root@workstation ~]# kubectl get sc
NAME                   PROVISIONER                                            RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
nfs-client (default)   cluster.local/nfs-provisioner-nfs-client-provisioner   Retain          Immediate           true                   3m7s
```