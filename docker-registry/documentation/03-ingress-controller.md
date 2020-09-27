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

You can modify it to request a `nodePort` instead of a `LoadBalancer` type and set custom ports for your nodePort :

```
[root@workstation ~]# helm install nginx-ingress ingress-nginx/ --namespace ingress --set controller.service.type=NodePort --set controller.service.nodePorts.http=32080 --set controller.service.nodePorts.https=32443
NAME: nginx-ingress
LAST DEPLOYED: Sun Sep 27 01:25:30 2020
NAMESPACE: ingress
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
The ingress-nginx controller has been installed.
Get the application URL by running these commands:
  export HTTP_NODE_PORT=32080
  export HTTPS_NODE_PORT=32443
  export NODE_IP=$(kubectl --namespace ingress get nodes -o jsonpath="{.items[0].status.addresses[1].address}")

  echo "Visit http://$NODE_IP:$HTTP_NODE_PORT to access your application via HTTP."
  echo "Visit https://$NODE_IP:$HTTPS_NODE_PORT to access your application via HTTPS."

An example Ingress that makes use of the controller:

  apiVersion: networking.k8s.io/v1beta1
  kind: Ingress
  metadata:
    annotations:
      kubernetes.io/ingress.class: nginx
    name: example
    namespace: foo
  spec:
    rules:
      - host: www.example.com
        http:
          paths:
            - backend:
                serviceName: exampleService
                servicePort: 80
              path: /
    # This section is only required if TLS is to be enabled for the Ingress
    tls:
        - hosts:
            - www.example.com
          secretName: example-tls

If TLS is enabled for the Ingress, a Secret containing the certificate and key must also be provided:

  apiVersion: v1
  kind: Secret
  metadata:
    name: example-tls
    namespace: foo
  data:
    tls.crt: <base64 encoded cert>
    tls.key: <base64 encoded key>
  type: kubernetes.io/tls
```

Once deployed, you should have a service exposed on mentioned ports :

```
[root@workstation ~]# kubectl get svc -n ingress
NAME                                               TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
nginx-ingress-ingress-nginx-controller             NodePort    10.233.6.70    <none>        80:32080/TCP,443:32443/TCP   10s
nginx-ingress-ingress-nginx-controller-admission   ClusterIP   10.233.17.23   <none>        443/TCP                      11s
```