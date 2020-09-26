[main menu](../README.md)

## 03 - Installing Nginx ingress controller

Download the helm chart : 

```console
[root@workstation ~]# helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
"ingress-nginx" has been added to your repositories
[root@workstation ~]# helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "ingress-nginx" chart repository
...Successfully got an update from the "stable" chart repository
Update Complete. ⎈ Happy Helming!⎈ 
[root@workstation ~]# helm fetch --untar ingress-nginx/ingress-nginx
```

By default, the `values.yaml` of the helm chart is configured like this :

```yaml
   type: LoadBalancer

    # type: NodePort
    # nodePorts:
    #   http: 32080
    #   https: 32443
    #   tcp:
    #     8080: 32808
    nodePorts:
      http: ""
      https: ""
      tcp: {}
      udp: {}
```

You can modify it to request a `nodePort` instead of a `LoadBalancer` type. 