[main menu](../README.md)

## 08 - Using the registry

I recommend using skopeo to use registry. You can connect to the registry :

```console
[root@workstation ~]# skopeo login --tls-verify=false registry.k8s.fredcorp.com -u fred
Password: 
Login Succeeded!
```

Push images :

```console
[root@workstation ~]# skopeo copy docker://alpine:latest docker://registry.k8s.fredcorp.com/alpine:latest --dest-tls-verify=false
Getting image source signatures
Copying blob 188c0c94c7c5 done  
Copying config d6e46aa247 done  
Writing manifest to image destination
Storing signatures
```

List tags from your registry this way :

```console
[root@workstation ~]# skopeo list-tags --tls-verify=false docker://registry.k8s.fredcorp.com/alpine
{
    "Repository": "registry.k8s.fredcorp.com/alpine",
    "Tags": [
        "latest"
    ]
}
```

If you want to be able to be able to delete images from your registry, you need to add some environment variable to your registry pod :

```console
[root@workstation ~]# kubectl set env deployment.apps/docker-registry -n registry REGISTRY_STORAGE_DELETE_ENABLED=true
deployment.apps/docker-registry env updated
```

And then you can delete :

```console
[root@workstation ~]# skopeo delete --tls-verify=false docker://registry.k8s.fredcorp.com/alpine
[root@workstation ~]# skopeo list-tags --tls-verify=false docker://registry.k8s.fredcorp.com/alpine
{
    "Repository": "registry.k8s.fredcorp.com/alpine",
    "Tags": []
}
```

If you want to synchronize :

```console
[root@workstation ~]# skopeo sync --tls-verify=false --src docker --dest dir registry.k8s.fredcorp.com/busybox /tmp/
WARN[0000] '--tls-verify' is deprecated, please set this on the specific subcommand 
INFO[0000] Tag presence check                            imagename=registry.k8s.fredcorp.com/busybox tagged=false
INFO[0000] Getting tags                                  image=registry.k8s.fredcorp.com/busybox
INFO[0000] Copying image tag 1/1                         from="docker://registry.k8s.fredcorp.com/busybox:1.28.3" to="dir:/tmp/busybox:1.28.3"
Getting image source signatures
Copying blob f70adabe43c0 done  
Copying config 8ac4858969 done  
Writing manifest to image destination
Storing signatures
INFO[0000] Synced 1 images from 1 sources
```