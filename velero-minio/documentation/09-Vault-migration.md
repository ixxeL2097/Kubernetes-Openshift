[Main menu](../README.md)

# Vault migration

pour vault : 

- restore
- delete route
- delete vault-cert
- delete pod
- create route

If you want to backup apps from **cluster 1** to **cluster 2**, you need to set storage location of cluster 1 as a **ReadOnly** storage location for cluster 2 (it's important to set as ReadOnly in order to not delete accidentally some files):

```console
[root@workstation ~ ]$ velero backup-location create hashicorp-clusterdev5 --provider aws --bucket hashicorp --prefix DEV5 --config region=minio,s3ForcePathStyle="true",s3Url=http://10.135.47.194:9001 --access-mode ReadOnly
Backup storage location "hashicorp-clusterdev5" configured successfully.
```

```console
[root@workstation ~ ]$ velero get backup-location
NAME                    PROVIDER   BUCKET/PREFIX    ACCESS MODE
awx                     aws        awx/DEV6         ReadWrite
default                 aws        cmp-core/DEV6    ReadWrite
hashicorp               aws        hashicorp/DEV6   ReadWrite
hashicorp-clusterdev5   aws        hashicorp/DEV5   ReadOnly
```

Now you can see backups from cluster 1 in the Velero instance of cluster 2 as ReadOnly files :

```console
[root@workstation ~ ]$ velero get backup
NAME                                    STATUS      CREATED                          EXPIRES   STORAGE LOCATION        SELECTOR
hashicorp-full-ns-dev5-20200713155238   Completed   2020-07-13 17:52:38 +0200 CEST   6d        hashicorp-clusterdev5   <none>
```

Now you can backup your application in cluster 2 by using classic restore command : 

```console
[root@workstation ~ ]$ velero restore create --from-backup hashicorp-full-ns-dev5-20200713155238
Restore request "hashicorp-full-ns-dev5-20200713155238-20200713181223" submitted successfully.
Run `velero restore describe hashicorp-full-ns-dev5-20200713155238-20200713181223` or `velero restore logs hashicorp-full-ns-dev5-20200713155238-20200713181223` for more details.
```

You should get your app installed on cluster 2 exactly as it is on cluster 1. In the case of Vault, some additional commands should be executed. You need of course to unseal Vault and also to replace the route since the route installed is from cluster 1. Juste delete the route and install a new one :

```console
[root@workstation ~ ]$ oc delete route vault
route.route.openshift.io "vault" deleted

[root@workstation ~ ]$ oc apply -f route-vault.yaml 
route.route.openshift.io/vault created
```

Pay attention to the certificate secret used for HTTPS that might need to be replaced. In case of auto generated OpenShift certificate, you just need to delete the secret (a new one will be atomatically created) and kill the pod in order to make things working :

```console
[root@workstation ~ ]$ oc get secret
NAME                       TYPE                                  DATA   AGE
builder-dockercfg-q7g4q    kubernetes.io/dockercfg               1      3m40s
builder-token-rl27m        kubernetes.io/service-account-token   4      3m31s
builder-token-smbgq        kubernetes.io/service-account-token   4      3m40s
default-dockercfg-7t2x4    kubernetes.io/dockercfg               1      3m40s
default-token-f2zk6        kubernetes.io/service-account-token   4      3m40s
default-token-ktfgv        kubernetes.io/service-account-token   4      3m31s
deployer-dockercfg-6qkvx   kubernetes.io/dockercfg               1      3m40s
deployer-token-8th6p       kubernetes.io/service-account-token   4      3m40s
deployer-token-rv9wh       kubernetes.io/service-account-token   4      3m31s
vault-cert                 kubernetes.io/tls                     2      3m40s
vault-token-757hc          kubernetes.io/service-account-token   4      3m30s

[root@workstation ~ ]$ oc delete secret vault-cert
secret "vault-cert" deleted

[root@workstation ~ ]$ oc delete pod vault-6cd89bbb74-pfr8x
pod "vault-6cd89bbb74-pfr8x" deleted
```

If you encounter some problem regarding pod's creation, it might be a problem due to ServiceAccount permissions. Check you vault SA :

```console
[root@workstation ~ ]$ oc describe sa vault
Name:                vault
Namespace:           hashicorp
Labels:              app.kubernetes.io/instance=vault
                     app.kubernetes.io/name=vault
                     velero.io/backup-name=hashicorp-full-ns-dev5-20200713155238
                     velero.io/restore-name=hashicorp-full-ns-dev5-20200713155238-20200713181223
Annotations:         kubectl.kubernetes.io/last-applied-configuration:
                       {"apiVersion":"v1","kind":"ServiceAccount","metadata":{"annotations":{},"labels":{"app.kubernetes.io/instance":"vault","app.kubernetes.io/...
Image pull secrets:  vault-dockercfg-zf9vd (not found)
Mountable secrets:   vault-dockercfg-zf9vd (not found)
                     vault-token-757hc
Tokens:              vault-token-757hc
Events:              <none>
```

ImagePull secret `vault-dockercfg-zf9vd` is not found so you should create a new one or point to another ImagePull secret in order to make things working.


---------------------------------------------------------------------------------------------------------------------------------

[Main menu](../README.md)

[Next](02-install-velero.md)