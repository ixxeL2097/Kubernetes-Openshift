[Main menu](../README.md)

# CMP-CORE migration

```
velero restore create --from-backup cmp-core-full-ns-dev5-20200716020005
Restore request "cmp-core-full-ns-dev5-20200716020005-20200716142254" submitted successfully.
Run `velero restore describe cmp-core-full-ns-dev5-20200716020005-20200716142254` or `velero restore logs cmp-core-full-ns-dev5-20200716020005-20200716142254` for more details.
```

```
velero get restore
NAME                                                   BACKUP                                  STATUS            WARNINGS   ERRORS   CREATED                          SELECTOR
cmp-core-full-ns-dev5-20200716020005-20200716142254    cmp-core-full-ns-dev5-20200716020005    InProgress        0          0        2020-07-16 14:22:55 +0200 CEST   <none>
```

```
velero get restore
NAME                                                   BACKUP                                  STATUS            WARNINGS   ERRORS   CREATED                          SELECTOR
cmp-core-full-ns-dev5-20200716020005-20200716142254    cmp-core-full-ns-dev5-20200716020005    Completed         5          0        2020-07-16 14:22:55 +0200 CEST   <none>
```

```
oc get pods
NAME                                                       READY   STATUS                  RESTARTS   AGE
bpm-app-5b7988dc9d-64m8b                                   0/1     Init:ImagePullBackOff   0          101m
bpm-mysql-1-deploy                                         0/1     Error                   0          101m
bpm-mysql-6-r94h7                                          0/1     ImagePullBackOff        0          101m
bpm-standalone-8588674f4c-skrxv                            0/1     Init:ImagePullBackOff   0          101m
cmdb-app-548cc4cc88-wchnn                                  0/1     Init:0/1                0          101m
cmdb-mongodb-4-xwd7p                                       0/1     ImagePullBackOff        0          101m
connector-app-snow-connector-app-helm-798554cf8d-k967s     0/1     ImagePullBackOff        0          101m
dispatcher-app-snow-dispatcher-app-helm-5cd469947f-6zzbh   0/1     ImagePullBackOff        0          101m
ipam-mock-app-67cc657d87-sjm9x                             0/1     Init:0/1                0          101m
ipam-mock-mongodb-4-7b2d9                                  0/1     ImagePullBackOff        0          101m
```



---------------------------------------------------------------------------------------------------------------------------------

[Main menu](../README.md)

[Next](02-install-velero.md)