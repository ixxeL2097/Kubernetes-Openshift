[main menu](../README.md)

## 07 - Protect registry with login access

Ok, so now we have a public registry that can receive data from anyone. This is cool but I would prefer to allow push (or pull) only to trusted users.

Looking at the Docker [Registry Documentation](https://docs.docker.com/registry/spec/auth/token/) we see that we can easily protect our registry with a login / password, using htpassword.

In order to do this first we need to create an htpasswd file. You can do it with the command htpasswd from your system :

```console
[root@workstation ~]# htpasswd -B -C 10 -c encrypted-password fred
New password: 
Re-type new password: 
Adding password for user fred

[root@workstation ~]# cat encrypted-password
fred:$2y$10$8yBbNmvNRrfoHdQPWWPe7eiHMqVGQ29udk5mRqjhl6cGSfvucoIDS
```

So we can create a Kubernetes secret with this file as input :


```console
[root@workstation ~]# kubectl create secret generic registry-auth-secret --from-file=credentials=encrypted-password
secret/registry-auth-secret created
```

```console
[root@workstation ~]# kubectl get secret registry-auth-secret created -o yaml
apiVersion: v1
data:
  credentials: ZnJlZDokMnkkMTAkOHlCYk5tdk5ScmZvSGRRUFdXUGU3ZWlITXFWR1EyOXVkazVtUnFqaGw2Y0dTZnZ1Y29JRFMK
kind: Secret
metadata:
  creationTimestamp: "2020-09-27T00:38:25Z"
  name: registry-auth-secret
  namespace: registry
  resourceVersion: "6060338"
  selfLink: /api/v1/namespaces/registry/secrets/registry-auth-secret
  uid: 8408d3bc-ae27-4c39-83dd-c9dc23795458
type: Opaque
```

Finally we can edit the registry-deployment file to add the configuration for the auth parameters :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docker-registry
  namespace: registry
spec:
  replicas: 2
  selector:
    matchLabels:
      app: docker-registry
  template:
    metadata:
      labels:
        app: docker-registry
    spec:
      containers:
        - name: docker-registry
          image: registry:2.7.1
          env:
            - name: REGISTRY_HTTP_SECRET
              value: azerty
            - name: REGISTRY_HTTP_ADDR
              value: ":5000"
            - name: REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY
              value: "/var/lib/registry"
            - name: REGISTRY_AUTH_HTPASSWD_REALM
              value: basic_realm
            - name: REGISTRY_AUTH_HTPASSWD_PATH
              value: /auth/credentials
          ports:
          - name: http
            containerPort: 5000
          volumeMounts:
          - name: image-store
            mountPath: "/var/lib/registry"
          - name: auth-dir
            mountPath: /auth
      volumes:
      - name: image-store
        persistentVolumeClaim:
          claimName: docker-registry-pvc
      - name: auth-dir
        secret:
          secretName: registry-auth-secret
```

```shell
kubectl apply -f deploy-registry-auth.yaml
```

Your docker-registry pods should be restarted with the new configuration. You can now login to your registry :

```console
[root@workstation ~]# sudo docker login registry.k8s.fredcorp.com -u fred
Password: 
WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded
```

If you need to decrypt an Opaque kubernete secret, just do like this :

```console
[root@workstation ~]# kubectl get secrets registry-auth-secret --template={{.data.credentials}} | base64 -d
fred:$2y$05$lDWRblhzk45RjCKB0q87JeluuikbbibK7CEb1Yfo.ad6WcFE6UZs.
```




