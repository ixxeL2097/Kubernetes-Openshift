[main menu](../README.md)

## 04 - Installing Docker registry

Once NFS server and NFS client provisioner are installed, you can create a dedicated namespace for your registry :

```shell
kubectl create namespace registry
```

Then create a `PersistentVolume` and a `PersistentVolumeClaim` for your registry :

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: docker-registry-pv
  namespace: registry
spec:
  capacity:
    storage: 30Gi
  accessModes:
    - ReadWriteMany
  nfs:
    server: 192.168.0.26
    path: "/NFS/k8s-docker-registry"
```

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: docker-registry-pvc
  namespace: registry
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: ""
  resources:
    requests:
      storage: 30Gi
```

Then create it :

```shell
kubectl create -f pv-registry.yaml
kubectl create -f pvc-registry.yaml
```

Check creation and binding :

```console
[root@workstation ~]# kubectl get pv
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                                   STORAGECLASS   REASON   AGE
docker-registry-pv                         30Gi       RWX            Retain           Bound    registry/docker-registry-pvc                                    61s
```

In order to deploy a docker registry using our PersistentVolume we will create a Deployment, which will itself create a ReplicaSet and a Pod. [Deployment](../resources/deploy-registry.yaml)

Regarding the yaml file, you can see that we configured 2 replicas in order to keep the system alive in case of failure from one of the pods. In each one of the pods we will have only one container named docker-registry which is based on the registry image stored on the docker hub.

Create deployment in the cluster :

```shell
kubectl apply -f deploy-registry.yaml -n registry
```

After a while our pods should be up and running :

```console
[root@workstation ~]# kubectl get pods -n registry
NAME                               READY   STATUS    RESTARTS   AGE
docker-registry-6cf6d5b99b-ktlmp   1/1     Running   1          85s
docker-registry-6cf6d5b99b-wlgbz   1/1     Running   1          78s
```

Now our pods are running but we can not use our registry yet … Let’s create a Service for that! This service should be accessible from outside the cluster, and as we are not hosted on a cloud provider, we will use Ingress Nginx to access it from outside.

```yaml
kind: Service
apiVersion: v1
metadata:
  name: docker-registry
  namespace: registry
  labels:
    app: docker-registry
spec:
  selector:
    app: docker-registry
  ports:
  - name: http
    port: 5000
```

```shell
kubectl apply -f svc-registry.yaml 
```

```console
[root@workstation ~]# kubectl get svc -n registry
NAME              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
docker-registry   ClusterIP   10.233.21.230   <none>        5000/TCP   63s
```

First you need to have configured Ingress Nginx (https://github.com/kubernetes/ingress-nginx)

Once you’ve done it you should have an `ingress-nginx` namespace

Now you can create the ingress resource in your cluster :

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
kubectl apply -f ingress-registry.yaml 
```

then you need to make the domain `registry.k8s.fredcorp.com` to route to one of your worker nodes (everyone except the controller) IP address. You can do this by modifying your `/etc/hosts` file.

So now if you try to access the url : `http://registry.k8s.fredcorp.com` … It should not work ! This is both because we did not use a LoadBalancer and because the Ingress Nginx is listening on a specific port.


```console
[root@workstation ~]# kubectl get svc -n ingress-nginx
NAME                                                          TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
nginx-ingress-controller-ingress-nginx-controller             NodePort    10.233.46.92   <none>        80:31953/TCP,443:32755/TCP   63s
nginx-ingress-controller-ingress-nginx-controller-admission   ClusterIP   10.233.23.25   <none>        443/TCP                      63s

So you can see that Ingress Nginx is listening on ports :

- 31953 for http requests
- 32755 for https requests

```shell
curl http://registry.k8s.fredcorp.com:31953/v2/_catalog
```

This should output the list of repositories
