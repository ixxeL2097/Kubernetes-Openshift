[main menu](../README.md)

## 06 - Securing registry with TLS

Great ! Now our registry is available on HTTP. This a good start, but we would prefer it to be available over HTTPS.

After a quick search online you should find a solution called **cert-manager**.

Let's download the helm chart:

```console
[root@workstation ~]# helm repo add jetstack https://charts.jetstack.io
"jetstack" has been added to your repositories
[root@workstation ~]# helm repo update
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "ingress-nginx" chart repository
...Successfully got an update from the "jetstack" chart repository
...Successfully got an update from the "stable" chart repository
Update Complete. ⎈ Happy Helming!⎈
```

**/!\ some versions of cert-manager do not work properly. Please test different versions**

Download the desired version and install it :

```console
[root@workstation ~]# helm fetch --untar jetstack/cert-manager --version 0.12.0
[root@workstation ~]# helm install cert-manager --namespace kube-system cert-manager/
```

Once cert-manager is installed, you can use different kind of certificate. Let's go for a self signed certificate in our case. You need to create an `issuer` resource :

```yaml
apiVersion: cert-manager.io/v1alpha2
kind: Issuer
metadata:
  name: selfsigned
  namespace: registry
spec:
  selfSigned: {}
```

And even better, create a `ClusterIssuer` resource :

```yaml
apiVersion: cert-manager.io/v1alpha2
kind: ClusterIssuer
metadata:
  name: selfsigned-cluster-issuer
  namespace: default
spec:
  selfSigned: {}
```

then create it :

```shell
kubectl apply -f clusterissuer-selfsigned.yaml
```

So now we can create a certificate, and store it in a kubernetes Secrets.

```yaml
apiVersion: cert-manager.io/v1alpha2
kind: Certificate
metadata:
  name: cert-registry
  namespace: registry
spec:
  secretName: cert-registry
  organization:
  - fredcorporation
  keySize: 4096
  keyAlgorithm: rsa
  commonName: 'registry.k8s.fredcorp.com'
  dnsNames:
  - registry.k8s.fredcorp.com
  issuerRef:
    name: selfsigned-cluster-issuer
    kind: ClusterIssuer
```

```shell
kubectl apply -f certificate-registry.yaml
```

It should create a secret containing the certificate : 

```console
[root@workstation ~]# kubectl get secret,certificate -n registry
NAME                          TYPE                                  DATA   AGE
secret/cert-registry          kubernetes.io/tls                     3      85s
secret/default-token-2wdkq    kubernetes.io/service-account-token   3      2d

NAME                                        READY   SECRET          AGE
certificate.cert-manager.io/cert-registry   True    cert-registry   86s
```

Now that we have a certificate we need to edit the ingress configuration to add the SSL information.

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: registry-ingress
  namespace: registry
  labels:
    version: "1.0"
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "0"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
    kubernetes.io/ingress.class: "nginx"
spec:
  tls:
    - secretName: cert-registry
      hosts:
        - registry.k8s.fredcorp.com
  rules:
  - host: registry.k8s.fredcorp.com
    http:
      paths:
      - path: /
        backend:
          serviceName: docker-registry
          servicePort: 5000
```

```shell
kubectl apply -f ingress-registry-tls.yaml
```

You can try to push an image to your registry now :

```console
[root@workstation ~]# sudo docker pull busybox:1.28.3
1.28.3: Pulling from library/busybox
f70adabe43c0: Pull complete 
Digest: sha256:58ac43b2cc92c687a32c8be6278e50a063579655fe3090125dcb2af0ff9e1a64
Status: Downloaded newer image for busybox:1.28.3
docker.io/library/busybox:1.28.3

[root@workstation ~]# sudo docker tag busybox:1.28.3 registry.k8s.fredcorp.com/busybox:1.28.3

[root@workstation ~]# sudo docker push registry.k8s.fredcorp.com/busybox:1.28.3
The push refers to repository [registry.k8s.fredcorp.com/busybox]
0314be9edf00: Pushed 
1.28.3: digest: sha256:186694df7e479d2b8bf075d9e1b1d7a884c6de60470006d572350573bfa6dcd2 size: 527
```