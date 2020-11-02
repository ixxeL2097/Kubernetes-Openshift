[main menu](../README.md)

## 01 - Installing Webhook Server

Main link : 

- https://github.com/morvencao/kube-mutating-webhook-tutorial

You should install go before going further -> https://golang.org/doc/install

Download go archive and untar it :

```shell
wget https://golang.org/dl/go1.15.3.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.15.3.linux-amd64.tar.gz
```

Then you need to export the GOPATH to your PATH environment variable. If you use fish shell you can do it this way :

```shell
set -U fish_user_paths /usr/local/go/bin/ $fish_user_paths
```

**P.S: don't forget to do it for `root` user as well.**

Then check the go version :

```console
[root@kube-worker01 ~]# go version
go version go1.15.3 linux/amd64
```

You can now clone the repo or use the files provided in this repo.

```shell
git clone https://github.com/morvencao/kube-mutating-webhook-tutorial.git
```

Once done, you need to build the binary.

```shell
make build
make build-image
make push-image
```

In our case, we will not use the `make push-image` command, but rather push the image to our personal private registry instead. Check docker images and push it :

```console
[root@workstation ~]# docker images
REPOSITORY                          TAG                 IMAGE ID            CREATED             SIZE
morvencao/sidecar-injector          latest              1e21d3f5708a        2 days ago          26.3MB
morvencao/sidecar-injector          v20201031-740876e   1e21d3f5708a        2 days ago          26.3MB
```

```console
[root@workstation ~]# skopeo copy docker-daemon:morvencao/sidecar-injector:v20201031-740876e docker://registry.k8s.fredcorp.com/morvencao/sidecar-injector:v20201031-740876e --dest-tls-verify=false
Getting image source signatures
Copying blob 12602ff71fe8 skipped: already exists  
Copying blob ace0eda3e3be skipped: already exists  
Copying blob d195c1adb68c skipped: already exists  
Copying blob 777f5af13851 [--------------------------------------] 0.0b / 0.0b
Copying config 1e21d3f570 [======================================] 3.6KiB / 3.6KiB
Writing manifest to image destination
Storing signatures
```

Now that your image is available on your private registry, edit the `deployment.yaml` file to change the image reference :

```yaml
    spec:
      containers:
        - name: sidecar-injector
          image: registry.k8s.fredcorp.com/morvencao/sidecar-injector:v20201031-740876e
          imagePullPolicy: IfNotPresent
          args:
```

You can create a signed cert/key pair and store it in a Kubernetes secret that will be consumed by sidecar injector deployment with the provided script :

```shell
./deployment/webhook-create-signed-cert.sh \
    --service sidecar-injector-webhook-svc \
    --secret sidecar-injector-webhook-certs \
    --namespace sidecar-injector
```

**/!\ If the script doesn't execute well, you might need to perform some commands manualy.**

Patch the MutatingWebhookConfiguration by set caBundle with correct value from Kubernetes cluster:

```shell
cat deployment/mutatingwebhook.yaml | \
    deployment/webhook-patch-ca-bundle.sh > \
    deployment/mutatingwebhook-ca-bundle.yaml
```

You can now deploy all resources : 

```shell
kubectl create -f deployment/nginxconfigmap.yaml
kubectl create -f deployment/configmap.yaml
kubectl create -f deployment/deployment.yaml
kubectl create -f deployment/service.yaml
kubectl create -f deployment/mutatingwebhook-ca-bundle.yaml
```

The `MutatingWebhookConfiguration` should be deployed, as well as your webhook server.

```console
[root@workstation ~]# kubectl get mutatingwebhookconfiguration,pods -n sidecar-injector
NAME                                                                                     CREATED AT
mutatingwebhookconfiguration.admissionregistration.k8s.io/sidecar-injector-webhook-cfg   2020-10-31T13:46:44Z

NAME                                                      READY   STATUS    RESTARTS   AGE
pod/sidecar-injector-webhook-deployment-b6f676997-rfzbb   1/1     Running   0          32h
```





Note that with the default configuration, resources will be mutated only if n






