# 02 - OpenShift & Kubernetes common issues

## PV/PVC

After deleting a PVC with ```oc delete pvc <pvc-name>```, if PVC deletion is stuck, just check ```kubectl describe pvc <pvc-name> | grep Finalizers``` :

```console
[root@workstation ~ ]$ kubectl describe pvc vault-storage | grep Finalizers
Finalizers:    [kubernetes.io/pvc-protection]
```

Then force PVC deletion by executing ```kubectl patch pvc <pvc-name> -p '{"metadata":{"finalizers": []}}' --type=merge``` :

```console
[root@workstation ~ ]$ kubectl patch pvc vault-storage -p '{"metadata":{"finalizers": []}}' --type=merge
persistentvolumeclaim/vault-storage patched
```

**P.S: you can do the same for PV deletion**

When PV are in ```Released``` state :

```console
[root@workstation ~ ]$ oc get pv
NAME                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS     CLAIM                    STORAGECLASS             REASON   AGE
pvc-39450f72-00505681e1fd   10Gi       RWX            Retain           Released   hashicorp/vault-storage  trident-storage-retain            35d
```

Just set them to ```Available``` state with the command ```kubectl patch pv <pv-name> -p '{"spec":{"claimRef": null}}'```:

```bash
[root@workstation ~ ]$ kubectl patch pv pvc-39450f72-00505681e1fd -p '{"spec":{"claimRef": null}}'
persistentvolume/pvc-39450f72-00505681e1fd patched
```

```console
[root@workstation ~ ]$ oc get pv
NAME                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM   STORAGECLASS             REASON   AGE
pvc-39450f72-00505681e1fd   10Gi       RWX            Retain           Available           trident-storage-retain            35d
```
