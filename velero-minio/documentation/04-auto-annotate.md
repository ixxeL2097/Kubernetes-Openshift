[Main menu](../README.md)

# Volume data automatic annotations for Restic backup
## Python script : auto-annotate

In order to annotate Kubernetes resources with volume data to save faster, I created a python script to automatically detect and annotate pods which need annotations. The script annotations are made at `deployment` level to enable `velero-pvc-watcher` detection as well as sustainable annotations over pod restarts and recreation.

This script will come in several versions from standalone file script to embeded container. You can find the script here [auto-annotator script](./resources/velero/scripts/)

### What it does

Script will annotate all the `Deployment`, `DeploymentConfig` or `StatefulSet` with persist volume claims attached to related `pods` with the anotation: `backup.velero.io/backup-volumes: <volume-name-to-backup>`. You can backup full namespace with velero/restic and PVC/PV will be included. 

This script does the following :

- Take `namespace(s)` as entry
- Retrieve `pods` in namespace(s)
- Check for `PersistentVolumeClaim` attached to `pods`
- Retrieve `controller` and `deployment` of the `pod`
- Displays all information in a table
- Proceed to `deployment` tagging

### Usage

```
python3 auto-annotate-v1.0b.py <namespace>
```

### Output

```
╒═════════════╤═══════════════════════════╤════════════════════════╤═══════════════════╤═════════════════════╤═══════════════════════╤═══════════════════╤══════════════════╕
│ Namespace   │ Pod                       │ Volume-name            │ PVC               │ Controller          │ Controller-kind       │ Deployer          │ Deploy-kind      │
╞═════════════╪═══════════════════════════╪════════════════════════╪═══════════════════╪═════════════════════╪═══════════════════════╪═══════════════════╪══════════════════╡
│ cmp-core    │ bpm-app-56b7dfdcc4-f8pmv  │ bpm-files              │ bpm-files-pvc     │ bpm-app-56b7dfdcc4  │ ReplicaSet            │ bpm-app           │ Deployment       │
├─────────────┼───────────────────────────┼────────────────────────┼───────────────────┼─────────────────────┼───────────────────────┼───────────────────┼──────────────────┤
│ cmp-core    │ bpm-mysql-3-c6jng         │ bpm-mysql-data         │ bpm-mysql         │ bpm-mysql-3         │ ReplicationController │ bpm-mysql         │ DeploymentConfig │
├─────────────┼───────────────────────────┼────────────────────────┼───────────────────┼─────────────────────┼───────────────────────┼───────────────────┼──────────────────┤
│ cmp-core    │ cmdb-mongodb-1-gmfwj      │ cmdb-mongodb-data      │ cmdb-mongodb      │ cmdb-mongodb-1      │ ReplicationController │ cmdb-mongodb      │ DeploymentConfig │
├─────────────┼───────────────────────────┼────────────────────────┼───────────────────┼─────────────────────┼───────────────────────┼───────────────────┼──────────────────┤
│ cmp-core    │ ipam-mock-mongodb-1-msnwp │ ipam-mock-mongodb-data │ ipam-mock-mongodb │ ipam-mock-mongodb-1 │ ReplicationController │ ipam-mock-mongodb │ DeploymentConfig │
╘═════════════╧═══════════════════════════╧════════════════════════╧═══════════════════╧═════════════════════╧═══════════════════════╧═══════════════════╧══════════════════╛
```

### /!\ WARNING : before annotating
#### Access mode

You need to pay attention to the `PersistentVolume` **ACCESS MODE** and/or `deployment` strategy. 

If `PersistentVolume` access mode is `RWO`, and deployment strategy is `rollingUpdate`, you need to patch PV to `RWX` in order to make the `rollingUpdate` deployment strategy possible. If you proceed updating with `RWO` access mode, following error will occur and pod update will be stuck:

```console
[root@workstation ~ ]$ oc describe pod vault-675d877754-bpz5n -n vault-test
Events:
  Type     Reason              Age   From                     Message
  ----     ------              ----  ----                     -------
  Normal   Scheduled           60s   default-scheduler        Successfully assigned vault-test/vault-675d877754-bpz5n to worker-dev5-1
  Warning  FailedAttachVolume  60s   attachdetach-controller  Multi-Attach error for volume "pvc-1e129130-a986-11ea-8c68-00505681c5ae" Volume is already used by pod(s) vault-5646f44f9-gjdwh
```

The deployment strategy `rollingUpdate` is suited for production use since it provides zero downtime. Follow the next steps to patch your PV:

Get the list of pv and check for RWO access modes:
```bash
oc get pv
```

Optionally describe the pv :
```console
oc describe pv <pv-Name>
```

Change the PV access mode from `ReadWriteOnce` to `ReadWriteMany` :

```console
[root@workstation ~ ]$ kubectl patch pv pvc-458a85b0-4fc1-48a3-804d-7e1de15fd81c -p '{"spec":{"accessModes": ["ReadWriteMany"]}}'
persistentvolume/pvc-458a85b0-4fc1-48a3-804d-7e1de15fd81c patched
```

you should now be able to process rolling update properly.

If you prefer to keep `RWO` access mode, you can use `Recreate` deployment strategy instead of `rollingUpdate`, but you have to be aware that downtime will occure during recreation of the pod.

in `deployment.spec.strategy` change :

```yaml
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
```
to :

```yaml
  strategy:
    type: Recreate
```

#### Scaling down

Before processing auto-annotation on the `deployment`, `deploymentconfig` or `statefulset`, it's recommanded to scale down your pods to 0 and then annotate.

Scaling down :

```console
[root@workstation ~ ]$ kubectl scale deployment ipam-mock-db-mongodb --replicas=0
deployment.apps/ipam-mock-db-mongodb scaled
```


---------------------------------------------------------------------------------------------------------------------------------

[Main menu](../README.md)

[Next](05-add-ons.md)