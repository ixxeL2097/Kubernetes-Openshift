[Main menu](../README.md)

# Velero Installation
## Description

This setup will install Velero server in an OpenShift cluster coupled with Minio S3 storage. Consult velero documentation at this link :

- https://velero.io/docs

## Installation : Online environment

To setup Velero server, you can user either Helm chart or Velero CLI. In order to stay agnostic from environment, I recommand using Velero CLI, especially if you are in Online environment.
To install CLI follow this link :

- https://velero.io/docs/master/basic-install/#install-the-cli

To install Velero on your cluster, you need first to login (`oc login`). Then you can use this command to install Velero and bound it to your Minio server :

```bash
velero install \
    --provider aws \
    --image velero/velero:v1.4.0 \
    --plugins velero/velero-plugin-for-aws:v1.1.0 \
    --bucket cmp-core \
    --prefix DEV6 \
    --secret-file ./credentials-velero \
    --use-volume-snapshots=false \
    --use-restic \
    --backup-location-config region=minio,insecureSkipTLSVerify="true",s3ForcePathStyle="true",s3Url=http://10.135.47.194:9001/
```

`--bucket cmp-core` will set the cmp-core bucket as default bucket location. It's recommended to use a default bucket location to install Velero but you can still skip this by using `--no-default-backup-location` flag (consult documentation for more information). `--use-restic` will be  usefull to 
The `credential-velero` is intended to give Minio credentials to Velero. You can format it that way :

```
[default]
aws_access_key_id = minio
aws_secret_access_key = minio123
```

if you install Velero with Restic on an **OpenShift cluster**, you will eventually end with `CrashLoopBackOff` Restic pods :

```console
[root@workstation ~ ]$ oc get all -n velero
NAME                          READY   STATUS             RESTARTS   AGE
pod/restic-76gkt              0/1     CrashLoopBackOff   3          83s
pod/restic-7bk4s              0/1     CrashLoopBackOff   3          83s
pod/restic-r8fxv              0/1     CrashLoopBackOff   3          83s
pod/velero-6c9c44f87d-zppgv   1/1     Running            0          83s

NAME                    DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR   AGE
daemonset.apps/restic   3         3         0       3            0           <none>          74s

NAME                     READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/velero   1/1     1            1           74s

NAME                                DESIRED   CURRENT   READY   AGE
replicaset.apps/velero-6c9c44f87d   1         1         1       83s
```

You need to setup specific configuration (https://velero.io/docs/v1.4/restic/).
If restic is not running in a privileged mode, it will not be able to access pods volumes within the mounted hostpath directory because of the default enforced SELinux mode configured in the host system level. You can create a custom SCC in order to relax the security in your cluster so that restic pods are allowed to use the hostPath volume plug-in without granting them access to the privileged SCC.

The restic containers should be running in a privileged mode to be able to mount the correct hostpath to pods volumes.

1. Add the velero ServiceAccount to the privileged SCC:

```console
[root@workstation ~ ]$ oc adm policy add-scc-to-user privileged -z velero -n velero
securitycontextconstraints.security.openshift.io/privileged added to: ["system:serviceaccount:velero:velero"]
```

2. For OpenShift version >= 4.1, Modify the DaemonSet yaml to request a privileged mode:

```console
[root@workstation ~ ]$ oc patch ds/restic --namespace velero --type json -p '[{"op":"add","path":"/spec/template/spec/containers/0/securityContext","value": { "privileged": true}}]'
daemonset.extensions/restic patched
```

After a short time, your pods will be up and running:

```console
[root@workstation ~ ]$ oc get pods -n velero
NAME                      READY   STATUS    RESTARTS   AGE
restic-8k7kw              1/1     Running   0          23m
restic-n6rqh              1/1     Running   0          23m
restic-vf2zq              1/1     Running   0          23m
velero-6c9c44f87d-zppgv   1/1     Running   0          25m
```

## Installation : Offline environment

In offline environment, you can use Helm chart to refer to images locally. Here is the link to official Velero Helm Chart :

- https://vmware-tanzu.github.io/helm-charts/

But you can also tweak your velero install script. For more information, see this link : 

- https://velero.io/docs/master/on-premises/

You need to pull 3 different images :
- Velero
- Plugin for Velero (AWS in this case)
- Restic helper

Consult this link for more information on Restic helper :

- https://velero.io/docs/master/restic/

## Uninstall Velero

If you need to uninstall Velero, just execute following commands ; 

```console
oc delete namespace/velero clusterrolebinding/velero
oc delete crds -l component=velero
```

```bash
kubectl delete namespace/velero clusterrolebinding/velero
kubectl delete crds -l app.kubernetes.io/name=velero
```


## Useful links 

- https://medium.com/@ludovicbonivert/backup-restore-of-vsphere-persistent-volumes-in-openshift-with-velero-restic-minio-2cb786eeaa4c



---------------------------------------------------------------------------------------------------------------------------------

[Main menu](../README.md)

[Next](03-configure-velero.md)