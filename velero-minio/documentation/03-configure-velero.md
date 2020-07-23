[Main menu](../README.md)

# Velero Configuration
## Backup location

After installation, Velero only has 1 `backup-location` set as default :

```console
[root@workstation ~ ]$ velero get backup-location
NAME      PROVIDER   BUCKET/PREFIX   ACCESS MODE
default   aws        cmp-core/DEV6   ReadWrite
```

you can find the associated CRDs as following :

```console
[root@workstation ~ ]$ oc get backupstoragelocation -n velero
NAME      AGE
default   47m
```

You need to add your remaining buckets to Velero configuration to be able to save data to these buckets. 

According to Velero documentation (https://velero.io/docs/master/faq/) :
```
We strongly recommend that each Velero instance use a distinct bucket/prefix combination to store backups. Having multiple Velero instances write backups to the same bucket/prefix combination can lead to numerous problems - failed backups, overwritten backups, inadvertently deleted backups, etc., all of which can be avoided by using a separate bucket + prefix per Velero instance.

It’s fine to have multiple Velero instances back up to the same bucket if each instance uses its own prefix within the bucket. This can be configured in your BackupStorageLocation, by setting the spec.objectStorage.prefix field. It’s also fine to use a distinct bucket for each Velero instance, and not to use prefixes at all.
```

So, to store data, it's recommanded to use **BUCKET** and **PREFIX** in order to separate backups from different clusters in the same bucket. To add a new storage location, execute following command :

```console
[root@workstation ~ ]$ velero backup-location create hashicorp --provider aws --bucket hashicorp --prefix DEV6 --config region=minio,s3ForcePathStyle="true",s3Url=http://10.135.47.194:9001
Backup storage location "hashicorp" configured successfully.
```

```console
[root@workstation ~ ]$ velero get backup-location
NAME        PROVIDER   BUCKET/PREFIX   ACCESS MODE
default     aws        cmp-core        ReadWrite
hashicorp   aws        hashicorp/DEV6  ReadWrite
```

If you need to delete a backup location, execute following command :

```console
[root@workstation ~ ]$ oc -n velero delete backupstoragelocation awx
backupstoragelocation.velero.io "awx" deleted
```

## Annotations
### Manual process

Velero will save Kubernetes resources (such as deployments, pods, services...) but Restic is intended to save data volumes. To enable these saves, you need to annotate **pods** to mention which volumes you want to save.

Select pods that need to save data and find volume name of the PVC : 

```console
[root@workstation ~ ]$ oc get pod postgresql-1-7gqh6 -n awx -o yaml
[...]
  volumes:
  - name: postgresql-data
    persistentVolumeClaim:
      claimName: postgresql
  - name: default-token-7nfv5
    secret:
      defaultMode: 420
      secretName: default-token-7nfv5
[...]
```

Then annotate it :

```console
[root@workstation ~ ]$ oc annotate pod postgresql-1-7gqh6 backup.velero.io/backup-volumes=postgresql-data -n awx

```

```console
[root@workstation ~ ]$ oc get pod postgresql-1-7gqh6 -n awx -o yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    backup.velero.io/backup-volumes: postgresql-data
[...]
```

if you want to remove annotation, just execute following command :

```console
[root@workstation ~ ]$ oc annotate pod postgresql-1-7gqh6 backup.velero.io/backup-volumes- -n awx
```

### Automatic process

In order to make things faster, more reliable and less error-prone, scripting this activity is useful. I made a script for this purpose, so refer to the chapter 4 about automated annotation with python script [Auto-annotation Python script](04-auto-annotate.md).

## Schedules

To enable automatic backup at a given time, you need to create `schedule`. Let's save our AWX namespace everyday at 2.00am :

```console
[root@workstation ~ ]$ velero schedule create awx-full-ns-dev5 --schedule "0 2 * * *" --ttl 168h0m0s --include-namespaces awx --storage-location awx
Schedule "awx-full-ns-dev5" created successfully.
```

`--ttl` flag create retention, here for 7 days. You can check your schedule and notice that Velero instantly backup resources from the scheduled task you just configured :

```console
[root@workstation ~ ]$ velero get schedule
NAME                    STATUS    CREATED                          SCHEDULE    BACKUP TTL   LAST BACKUP   SELECTOR
awx-full-ns-dev5        Enabled   2020-07-10 16:14:03 +0200 CEST   0 2 * * *   168h0m0s     1m            <none>
```





---------------------------------------------------------------------------------------------------------------------------------

[Main menu](../README.md)

[Next](04-auto-annotate.md)