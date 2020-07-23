[Main menu](../README.md)

# Migration
## General

When migrating, you need to ensure three things :

- 1. ReadOnly bucket mapping (https://velero.io/docs/master/migration-case/)
- 2. ServiceAccount gets proper permissions (https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/)
- 3. images are pushed to the new cluster

**1. ReadOnly bucket mapping** 

If you want to backup apps from **cluster 1** to **cluster 2**, you need to set storage location of cluster 1 as a **ReadOnly** storage location for cluster 2 (it's important to set as ReadOnly in order to not delete accidentally some files):

```console
[root@workstation ~ ]$ velero backup-location create awx-clusterdev5 --provider aws --bucket awx --prefix DEV5 --config region=minio,s3ForcePathStyle="true",s3Url=http://10.135.47.194:9001 --access-mode ReadOnly
Backup storage location "awx-clusterdev5" configured successfully.
```

```console
[root@workstation ~ ]$ velero get backup-location
NAME                    PROVIDER   BUCKET/PREFIX    ACCESS MODE
awx                     aws        awx/DEV6         ReadWrite
default                 aws        cmp-core/DEV6    ReadWrite
hashicorp               aws        hashicorp/DEV6   ReadWrite
awx-clusterdev5         aws        awx/DEV5         ReadOnly
```

Now you can see backups from cluster 1 in the Velero instance of cluster 2 as ReadOnly files :

```console
[root@workstation ~ ]$ velero get backup
NAME                                    STATUS      CREATED                          EXPIRES   STORAGE LOCATION        SELECTOR
awx-full-ns-dev5-20200713155238         Completed   2020-07-13 17:52:38 +0200 CEST   6d        awx-clusterdev5         <none>
```

**2. ServiceAccount permissions**

After restoring application, you will most probably end with uncorrect ServiceAccount permissions. Pods will be stuck in `ImagePullBackOff`/`ErrImagePull` state :

```console
[root@workstation ~ ]$ oc get pods
NAME                 READY   STATUS             RESTARTS   AGE
awx-0                3/4     ImagePullBackOff   0          38s
postgresql-2-pxzjx   0/1     Init:0/1           0          5m26s
```

if you describe the pod, you will notice a `unauthorized: authentication required` error message in logs :

```console
[root@workstation ~ ]$ oc describe pod awx-0
[...]
Warning  Failed     2m13s (x2 over 2m33s)  kubelet, compute-0  Error: ErrImagePull
  Warning  Failed     2m13s (x2 over 2m33s)  kubelet, compute-0  Failed to pull image "image-registry.openshift-image-registry.svc:5000/awx/awx_task_argo:9.2.0": rpc error: code = Unknown desc = Error reading manifest 9.2.0 in image-registry.openshift-image-registry.svc:5000/awx/awx_task_argo: unauthorized: authentication required
  Normal   BackOff    2m2s (x3 over 2m28s)   kubelet, compute-0  Back-off pulling image "image-registry.openshift-image-registry.svc:5000/awx/awx_task_argo:9.2.0"
  Warning  Failed     2m2s (x3 over 2m28s)   kubelet, compute-0  Error: ImagePullBackOff
  Normal   Pulling    108s (x3 over 2m33s)   kubelet, compute-0  Pulling image "image-registry.openshift-image-registry.svc:5000/awx/awx_task_argo:9.2.0"
```

To deal with this problem, you need to verify specific permission on the ServiceAccount assigned to the pod. When you create a pod, if you do not specify a service account, it is automatically assigned the `default` ServiceAccount in the same namespace. If you get the raw json or yaml for a pod you have created (for example, kubectl get pods/<podname> -o yaml), you can see the spec.serviceAccountName field has been automatically set.

Check which ServiceAccount the pod is assigned to : 

```console
[root@workstation ~ ]$ oc get pod awx-0 -o yaml | grep service
    service: django
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
  serviceAccount: awx
  serviceAccountName: awx
```

Here the ServiceAccount is `awx` and not `default`. You can list all ServiceAccount in the namespace : 

```console
[root@workstation ~ ]$ oc get sa
NAME       SECRETS   AGE
awx        2         33m
builder    3         33m
default    3         33m
deployer   3         33m
```

First describe the ServiceAccount to check the `Image pull secret` field :

```console
[root@workstation ~ ]$ oc describe sa awx
Name:                awx
Namespace:           awx
Labels:              velero.io/backup-name=awx-full-ns-dev5-20200714020004
                     velero.io/restore-name=awx-full-ns-dev5-20200714020004-20200715135244
Annotations:         kubectl.kubernetes.io/last-applied-configuration:
                       {"apiVersion":"v1","kind":"ServiceAccount","metadata":{"annotations":{},"name":"awx","namespace":"awx"}}
Image pull secrets:  awx-dockercfg-z8pvw (not found)
Mountable secrets:   awx-dockercfg-z8pvw (not found)
                     awx-token-zpzjw
Tokens:              awx-token-zpzjw
Events:              <none>
```

You can see here that the current `Image pull secret` is not found. You need to assigned a proper Image pull secret to your ServiceAccount, or change the ServiceAccount responsible for the pod. Let's change the secret for awx ServiceAccount :

```console
[root@workstation ~ ]$ oc get secret
NAME                       TYPE                                  DATA   AGE
awx-secrets                Opaque                                5      19m
awx-token-zpzjw            kubernetes.io/service-account-token   4      19m
builder-dockercfg-9b9ms    kubernetes.io/dockercfg               1      19m
builder-token-fd6hd        kubernetes.io/service-account-token   4      19m
builder-token-tsk45        kubernetes.io/service-account-token   4      19m
default-dockercfg-7wdcz    kubernetes.io/dockercfg               1      19m
default-token-hd566        kubernetes.io/service-account-token   4      19m
default-token-pvvmc        kubernetes.io/service-account-token   4      19m
deployer-dockercfg-6bhjp   kubernetes.io/dockercfg               1      19m
deployer-token-fwgfc       kubernetes.io/service-account-token   4      19m
deployer-token-wskjt       kubernetes.io/service-account-token   4      19m
postgresql                 Opaque                                4      19m
```

You can notice that the secret `awx-dockercfg-z8pvw` is not created here. So you might create a new one and assign it to awx ServiceAccount, or you can also point to an existing one like :

```console
[root@workstation ~ ]$ oc patch serviceaccount awx -p '{"imagePullSecrets": [{"name": "default-dockercfg-7wdcz"}]}'
serviceaccount/awx patched
```

Now your awx ServiceAccount is assigned the default-dockercfg-7wdcz secret to pull images and it should be working properly. If not working, you can add also image:pull policy to your service account :

```console
[root@workstation ~ ]$ oc policy add-role-to-user system:image-puller system:serviceaccount:awx:awx --namespace=awx
clusterrole.rbac.authorization.k8s.io/system:image-puller added: "system:serviceaccount:awx:awx"
```

Now, everything should be fine regarding Image pull policy.


**3. Re-push images**

When migrating from one cluster to another one, you will need to push manually images to the new cluster. ImageStream are not sufficient.

Once you resolved ServiceAccount permission policy, you might have another problem with pods still creating properly (still stucked on `ImagePullBackOff` state). If you describe your pod, you will notice a new error `manifest unknown: manifest unknown` :

```console
[root@workstation ~ ]$ oc describe pod awx-0
[...]
Normal   Pulling    19s                kubelet, compute-0  Pulling image "image-registry.openshift-image-registry.svc:5000/awx/awx_task_argo:9.2.0"
Warning  Failed     19s                kubelet, compute-0  Failed to pull image "image-registry.openshift-image-registry.svc:5000/awx/awx_task_argo:9.2.0": rpc error: code = Unknown desc = Error reading manifest 9.2.0 in image-registry.openshift-image-registry.svc:5000/awx/awx_task_argo: manifest unknown: manifest unknown
Warning  Failed     19s                kubelet, compute-0  Error: ErrImagePull
```

this problem occurs when you need to push image to your new cluster manually instead of relying of the Velero restore. Pull your image and push it to the cluster :

```console
[root@workstation ~ ]$ docker pull default-route-openshift-image-registry.apps.ocp4-dev5.devibm.local/awx/awx_task_argo:9.2.0
9.2.0: Pulling from awx/awx_task_argo
8a29a15cefae: Pull complete
[...]
Digest: sha256:a5f5c59f619060e39327cbb9fd5fce94e94a6a039116b4def84a72a1c7c65fc6
Status: Downloaded newer image for default-route-openshift-image-registry.apps.ocp4-dev5.devibm.local/awx/awx_task_argo:9.2.0
default-route-openshift-image-registry.apps.ocp4-dev5.devibm.local/awx/awx_task_argo:9.2.0

[root@workstation ~ ]$ docker tag default-route-openshift-image-registry.apps.ocp4-dev5.devibm.local/awx/awx_task_argo:9.2.0 default-route-openshift-image-registry.apps.devibm.local/awx/awx_task_argo:9.2.0

[root@workstation ~ ]$ docker push default-route-openshift-image-registry.apps.devibm.local/awx/awx_task_argo:9.2.0
The push refers to repository [default-route-openshift-image-registry.apps.devibm.local/awx/awx_task_argo]
00c17e2d5d75: Pushed 
[...]
9.2.0: digest: sha256:a5f5c59f619060e39327cbb9fd5fce94e94a6a039116b4def84a72a1c7c65fc6 size: 7837
```

Now you can delete the pod and wait for its creation, everything should work properly.

```console
[root@workstation ~ ]$ oc delete pod awx-0
pod "awx-0" deleted

[root@workstation ~ ]$ oc get pods
NAME                 READY   STATUS              RESTARTS   AGE
awx-0                0/4     ContainerCreating   0          0s
postgresql-2-wbbr8   1/1     Running             2          76m

[root@workstation ~ ]$ oc get pods
NAME                 READY   STATUS    RESTARTS   AGE
awx-0                4/4     Running   0          9s
postgresql-2-wbbr8   1/1     Running   2          76m
```

## Application migration
### Case A : New App, Cluster A namespace X --> Cluster B namespace X

In this case you only need to follow instructions from the general recommandation on this page :

1. Create a new backup-location with ReadOnly access mode 

```console
[root@workstation ~ ]$ velero backup-location create hashicorp-clusterdev5 --provider aws --bucket hashicorp --prefix DEV5 --config region=minio,s3ForcePathStyle="true",s3Url=http://10.135.47.194:9001 --access-mode ReadOnly
Backup storage location "hashicorp-clusterdev5" configured successfully.
```

2. Migrate your application from cluster A to cluster B (same namespace) :

```console
[root@workstation ~ ]$ velero restore create --from-backup hashicorp-full-ns-dev5-20200713155238
Restore request "hashicorp-full-ns-dev5-20200713155238-20200713181223" submitted successfully.
Run `velero restore describe hashicorp-full-ns-dev5-20200713155238-20200713181223` or `velero restore logs hashicorp-full-ns-dev5-20200713155238-20200713181223` for more details.
```

3. Deal with ServiceAccount policies as explained previously :

```console
[root@workstation ~ ]$ oc patch serviceaccount vault -p '{"imagePullSecrets": [{"name": "default-dockercfg-zf9vd"}]}'
serviceaccount/awx patched
```

```console
[root@workstation ~ ]$ oc policy add-role-to-user system:image-puller system:serviceaccount:hashicorp:vault --namespace=vault
clusterrole.rbac.authorization.k8s.io/system:image-puller added: "system:serviceaccount:hashicorp:vault"
```

4. Re-push images from cluster A to cluster B :

```console
[root@workstation ~ ]$ docker pull default-route-openshift-image-registry.apps.ocp4-dev5.devibm.local/hashicorp/vault:1.4.1

[root@workstation ~ ]$ docker tag default-route-openshift-image-registry.apps.ocp4-dev5.devibm.local/hashicorp/vault:1.4.1 default-route-openshift-image-registry.apps.devibm.local/hashicorp/vault:1.4.1

[root@workstation ~ ]$ docker push default-route-openshift-image-registry.apps.devibm.local/hashicorp/vault:1.4.1
```

5. Delete pod and wait for recreation

6. In case of specific application like Vault, you might need additional steps (recreate certificate secret, recreate route, unseal...)


### Case B : Additional App, Cluster A namespace X --> Cluster B namespace Y (app already existing in cluster X)

Generally speaking, you need to follow the classical steps previously explained in the the **Case A** and also execute the following instructions.
After restoring, you will most propably end with a `PartiallyFailed` restore :

```console
[root@workstation ~ ]$ velero get restore
NAME                                                   BACKUP                                  STATUS            WARNINGS   ERRORS   CREATED                          SELECTOR
awx-full-ns-dev5-20200714020004-20200715135244         awx-full-ns-dev5-20200714020004         Completed         1          0        2020-07-15 13:52:31 +0200 CEST   <none>
awx-full-ns-dev5-20200715020004-20200715153400         awx-full-ns-dev5-20200715020004         PartiallyFailed   8          1        2020-07-15 15:33:48 +0200 CEST   <none>
```

You can display errors from this restore :

```console
[root@workstation ~ ]$ velero describe restore awx-full-ns-dev5-20200715020004-20200715153400
Name:         awx-full-ns-dev5-20200715020004-20200715153400
Namespace:    velero
Labels:       <none>
Annotations:  <none>

Phase:  PartiallyFailed (run 'velero restore logs awx-full-ns-dev5-20200715020004-20200715153400' for more information)

Warnings:
  Velero:     <none>
  Cluster:  could not restore, customresourcedefinitions.apiextensions.k8s.io "monitoringdashboards.monitoringcontroller.cloud.ibm.com" already exists. Warning: the in-cluster version is different than the backed-up version.
  Namespaces:
    awx-test:  could not restore, rolebindings.authorization.openshift.io "system:deployers" already exists. Warning: the in-cluster version is different than the backed-up version.
               could not restore, rolebindings.authorization.openshift.io "system:image-builders" already exists. Warning: the in-cluster version is different than the backed-up version.
               could not restore, rolebindings.authorization.openshift.io "system:image-pullers" already exists. Warning: the in-cluster version is different than the backed-up version.
               could not restore, rolebindings.rbac.authorization.k8s.io "admin" already exists. Warning: the in-cluster version is different than the backed-up version.
               could not restore, rolebindings.rbac.authorization.k8s.io "system:deployers" already exists. Warning: the in-cluster version is different than the backed-up version.
               could not restore, rolebindings.rbac.authorization.k8s.io "system:image-builders" already exists. Warning: the in-cluster version is different than the backed-up version.
               could not restore, rolebindings.rbac.authorization.k8s.io "system:image-pullers" already exists. Warning: the in-cluster version is different than the backed-up version.

Errors:
  Velero:     <none>
  Cluster:    <none>
  Namespaces:
    awx-test:  error restoring rolebindings.authorization.openshift.io/awx-test/endpoint-reader: invalid origin role binding endpoint-reader: attempts to reference role in namespace "awx" instead of current namespace "awx-test"
[...]
```

You can see that `rolebindings` resources could not be restored. So check these resources inside your namespace :

```console
[root@workstation ~ ]$ oc get rolebindings.authorization.openshift.io -n awx-test
NAME                    ROLE                       USERS        GROUPS                            SERVICE ACCOUNTS   USERS
admin                   /admin                     kube:admin                                                        
endpoint-reader         awx-test/endpoint-reader                                                  awx                
system:deployers        /system:deployer                                                          deployer           
system:image-builders   /system:image-builder                                                     builder            
system:image-puller     /system:image-puller                                                      awx                
system:image-pullers    /system:image-puller                    system:serviceaccounts:awx-test
```

and compare it to the initial working namespace :

```console
[root@workstation ~ ]$ oc get rolebindings.authorization.openshift.io -n awx
NAME                    ROLE                    USERS        GROUPS                       SERVICE ACCOUNTS   USERS
admin                   /admin                  kube:admin                                                   
endpoint-reader         awx/endpoint-reader                                               awx                
system:deployers        /system:deployer                                                  deployer           
system:image-builders   /system:image-builder                                             builder            
system:image-puller     /system:image-puller                                              awx                
system:image-puller-0   /system:image-puller                                              default            
system:image-puller-1   /system:image-puller                                              builder            
system:image-puller-2   /system:image-puller                                              deployer           
system:image-pullers    /system:image-puller                 system:serviceaccounts:awx  
```

some are missing so you just need to add them :

```console
[root@workstation ~ ]$ oc policy add-role-to-user system:image-puller system:serviceaccount:awx-test:default --namespace=awx-test
clusterrole.rbac.authorization.k8s.io/system:image-puller added: "system:serviceaccount:awx-test:default"

[root@workstation ~ ]$  oc policy add-role-to-user system:image-puller system:serviceaccount:awx-test:builder --namespace=awx-test
clusterrole.rbac.authorization.k8s.io/system:image-puller added: "system:serviceaccount:awx-test:builder"

[root@workstation ~ ]$  oc policy add-role-to-user system:image-puller system:serviceaccount:awx-test:deployer --namespace=awx-test
clusterrole.rbac.authorization.k8s.io/system:image-puller added: "system:serviceaccount:awx-test:deployer"
```

Now you need to pay attention to the namespace refered in your `deployment` or `statefulset` resource. Even if you use `--namespace-mappings` from the Velero restore command, all the images refered in your `deployment` or `statefulset` resource is the same as the original (in this case refering to namespace `awx` instead of `awx-test`) so you need to change it manually **OR** you need to add the correct pull image policy to your ServiceAccount for them to be able to pull from the original namespace :

```console
[root@workstation ~ ]$  oc project
Using project "awx-test" on server "https://api.devibm.local:6443".

[root@workstation ~ ]$  oc describe pod awx-0
[...]
Normal   BackOff    27s (x2 over 28s)  kubelet, compute-0  Back-off pulling image "image-registry.openshift-image-registry.svc:5000/awx/awx_task_argo:9.2.0"
  Warning  Failed     27s (x2 over 28s)  kubelet, compute-0  Error: ImagePullBackOff
  Normal   Pulling    15s (x2 over 33s)  kubelet, compute-0  Pulling image "image-registry.openshift-image-registry.svc:5000/awx/awx_task_argo:9.2.0"
  Warning  Failed     15s (x2 over 33s)  kubelet, compute-0  Error: ErrImagePull
  Warning  Failed     15s (x2 over 33s)  kubelet, compute-0  Failed to pull image "image-registry.openshift-image-registry.svc:5000/awx/awx_task_argo:9.2.0": rpc error: code = Unknown desc = Error reading manifest 9.2.0 in image-registry.openshift-image-registry.svc:5000/awx/awx_task_argo: unauthorized: authentication required
```

Edit your `deployment` or `statefulset` and modify the namespace of the image accordingly to yours :

```console
[root@workstation ~ ]$  oc edit statefulset awx
statefulset.apps/awx edited
```

Now it should be working properly :

```console
[root@workstation ~ ]$  oc get pods
NAME                 READY   STATUS    RESTARTS   AGE
awx-0                4/4     Running   0          26s
postgresql-2-pxzjx   1/1     Running   0          27m
```


interesting links : 

- https://velero.io/docs/master/faq/
- https://velero.io/docs/master/migration-case/


---------------------------------------------------------------------------------------------------------------------------------

[Main menu](../README.md)

[Next](02-install-velero.md)