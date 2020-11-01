[main menu](../README.md)

## 09 - Deploy from registry

If you want to deploy container in your kubernetes cluster from your registry, you need to apply some modification. First ensure DNS are properly set up to resolve your registry FQDN. You can do the by editing CoreDNS `configMap` (coredns configMap in kube-system namespace) or, in case of failure, just edit the `/etc/resolv.conf`from each of your nodes.

Upload your registry certificate to you kubernetes worker in order to trust the certificate :

```console
[root@kube-worker01 ~]# cp registry-cert.pem /etc/ssl/certs/
[root@kube-worker01 ~]# systemctl daemon-reload
[root@kube-worker01 ~]# systemctl restart docker

[root@kube-worker02 ~]# cp registry-cert.pem /etc/ssl/certs/
[root@kube-worker02 ~]# systemctl daemon-reload
[root@kube-worker02 ~]# systemctl restart docker
```

Don't forget to create a registry secret and apply it to your SA responsible for deployment from your private registry :

```console
[root@workstation ~]# kubectl create secret docker-registry registry-fredcorp-auth --docker-server=registry.k8s.fredcorp.com --docker-username=fred --docker-password=password -n sidecar-injector
secret/registry-fredcorp-auth created
```

if you need to copy this secret to another namespace :

```console
[root@workstation ~]# kubectl get secret <secret-name> --namespace=<ns1> -o yaml | sed 's/namespace: <ns1>/namespace: <ns2>/g' | kubectl create -f -
```

```console
[root@workstation ~]# kubectl patch sa default -n sidecar-injector -p '{"imagePullSecrets": [{"name": "registry-fredcorp-auth"}]}'
serviceaccount/default patched
```

Now, when a new Pod is created in the current namespace and using the default ServiceAccount, the new Pod has its spec.imagePullSecrets field set automatically:

```console
[root@workstation ~]# kubectl get pod sidecar-injector-webhook-deployment-b6f676997-lnv65 -n sidecar-injector -o=jsonpath='{
.spec.imagePullSecrets[0].name}{"\n"}'
registry-fredcorp-auth
```