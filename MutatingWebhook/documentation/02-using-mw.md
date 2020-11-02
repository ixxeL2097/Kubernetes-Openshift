[main menu](../README.md)

## 02 - Using MutatingWebhook

To use your Mutatingebhook injection, create new namespace `injection` and label it with `sidecar-injector=enabled`

```console
[root@workstation ~]# kubectl create ns injection
namespace/injection created
[root@workstation ~]# kubectl label namespace injection sidecar-injection=enabled
namespace/injection labeled

[root@workstation ~]#kubectl get namespace --show-labels
NAME               STATUS   AGE    LABELS
default            Active   101d   <none>
ingress-nginx      Active   99d    <none>
injection          Active   33s    sidecar-injection=enabled
kube-node-lease    Active   101d   <none>
kube-public        Active   101d   <none>
kube-system        Active   101d   <none>
nfs-provisioner    Active   100d   <none>
registry           Active   99d    <none>
sidecar-injector   Active   2d5h   <none>
```


