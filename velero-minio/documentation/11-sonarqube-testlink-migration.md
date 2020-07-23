[Main menu](../README.md)

# Sonarqube and Testlink migration from IKS

In this case, we will migrate Sonarqube and Testlink from IKS cluster A to IKS cluster B. Sonarqube and Testlink are in the **same namespace**, so we will bacup apps by selecting objects.

**From your cluster A**, to backup only your app, your need to look for its label. You can use this command to display all resources with label :

```bash
kubectl get all,secret,cm,pvc,ingress --show-labels
```

In our case we can restrict all of these to testlink for example :

```console
[root@workstation ~ ]$ kubectl get all,secret,cm,pvc,ingress --selector='release=testlink'
NAME                            READY   STATUS    RESTARTS   AGE
pod/testlink-6fd778bdb9-ws6sv   1/1     Running   3          41h
pod/testlink-mariadb-0          1/1     Running   0          41h

NAME                       TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)                      AGE
service/testlink           LoadBalancer   172.21.99.158   159.122.80.186   80:30992/TCP,443:31088/TCP   103d
service/testlink-mariadb   ClusterIP      172.21.16.165   <none>           3306/TCP                     103d

NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/testlink   1/1     1            1           103d

NAME                                  DESIRED   CURRENT   READY   AGE
replicaset.apps/testlink-5bc6ff6d77   0         0         0       103d
replicaset.apps/testlink-6fd778bdb9   1         1         1       41h

NAME                                READY   AGE
statefulset.apps/testlink-mariadb   1/1     103d

NAME                      TYPE     DATA   AGE
secret/testlink           Opaque   1      103d
secret/testlink-mariadb   Opaque   2      103d

NAME                         DATA   AGE
configmap/testlink-mariadb   1      103d

NAME                                            STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      AGE
persistentvolumeclaim/data-testlink-mariadb-0   Bound    pvc-bc8fe9f0-7a85-11ea-8acd-720f875802a6   20Gi       RWO            ibmc-block-gold   103d
persistentvolumeclaim/testlink-testlink         Bound    pvc-bc6f3c38-7a85-11ea-8acd-720f875802a6   20Gi       RWO            ibmc-block-gold   103d

NAME                          HOSTS                                                                                                     ADDRESS          PORTS     AGE
ingress.extensions/testlink   testlink.argo-s3p1-toolchains-hy-acd62f574b4aef68f9d01743b975866c-0001.eu-de.containers.appdomain.cloud   159.122.80.188   80, 443   103d
```

We can now use the label with Velero to backup only desired objects. You can possibly exclude `Ingress` resource type which is not needed in our case :

```console
[root@workstation ~ ]$ velero backup create release-testlink-only-ingressout --selector release=testlink --storage-location testlink --exclude-resources='Ingress.extensions,Ingress.networking.k8s.io'
Backup request "release-testlink-only-ingressout" submitted successfully.
Run `velero backup describe release-testlink-only-ingressout` or `velero backup logs release-testlink-only-ingressout` for more details.
```

**In your cluster B**, you need to add `ReadOnly` buckets from **cluster A** to be able to read the backups :

```console
[root@workstation ~ ]$ velero get backup-location
NAME                        PROVIDER   BUCKET/PREFIX               ACCESS MODE
default                     aws        sonar/SANDBOX               ReadWrite
sonar-toolchain-hybrid      aws        sonar/TOOLCHAIN-HYBRID      ReadOnly
testlink-toolchain-hybrid   aws        testlink/TOOLCHAIN-HYBRID   ReadOnly
```

```console
[root@workstation ~ ]$ velero get backup
NAME                               STATUS      CREATED                          EXPIRES   STORAGE LOCATION            SELECTOR
release-testlink-only-ingressout   Completed   2020-07-22 11:53:31 +0200 CEST   29d       testlink-toolchain-hybrid   release=testlink
```

Now you can restore this application **in you cluster B in the namespace of your choice** with the following command : 

```console
[root@workstation ~ ]$ velero restore create --from-backup release-testlink-only-ingressout --namespace-mappings default:testlink-test
Restore request "release-testlink-only-ingressout-20200722115957" submitted successfully.
Run `velero restore describe release-testlink-only-ingressout-20200722115957` or `velero restore logs release-testlink-only-ingressout-20200722115957` for more details.
```

If you end with and `ImagePullBackOff` on a container, verify that you `serviceAccount` gets the proper **pullImage permissions** :

```console
[root@workstation ~ ]$ kubectl get pod -n testlink-test
NAME                        READY   STATUS             RESTARTS   AGE
testlink-6fd778bdb9-ws6sv   0/1     ImagePullBackOff   0          3m7s
testlink-mariadb-0          1/1     Running            0          3m7s
```

```console
[root@workstation ~ ]$ kubectl describe pod testlink-6fd778bdb9-ws6sv -n testlink-test
[...]
  Normal   Pulling           3m41s (x4 over 5m9s)   kubelet, 10.134.215.59  Pulling image "de.icr.io/s3p1sandbox/testlink:1.0.1"
  Warning  Failed            3m41s (x4 over 5m9s)   kubelet, 10.134.215.59  Failed to pull image "de.icr.io/s3p1sandbox/testlink:1.0.1": rpc error: code = Unknown desc = failed to pull and unpack image "de.icr.io/s3p1sandbox/testlink:1.0.1": failed to resolve reference "de.icr.io/s3p1sandbox/testlink:1.0.1": failed to authorize: failed to fetch anonymous token: unexpected status: 401 Unauthorized
  Warning  Failed            3m41s (x4 over 5m9s)   kubelet, 10.134.215.59  Error: ErrImagePull
  Normal   BackOff           3m30s (x5 over 4m43s)  kubelet, 10.134.215.59  Back-off pulling image "de.icr.io/s3p1sandbox/testlink:1.0.1"
  Warning  Failed            2s (x20 over 4m43s)    kubelet, 10.134.215.59  Error: ImagePullBackOff
```

```console
[root@workstation ~ ]$ kubectl get pod testlink-6fd778bdb9-ws6sv -n testlink-test -o yaml | grep service
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
  serviceAccount: default
  serviceAccountName: default
```

```console
[root@workstation ~ ]$ kubectl describe sa default -n testlink-test
Name:                default
Namespace:           testlink-test
Labels:              <none>
Annotations:         <none>
Image pull secrets:  <none>
Mountable secrets:   default-token-bl9hw
Tokens:              default-token-bl9hw
Events:              <none>
```

The ServiceAccount doesn't have the secret to pull images from `de.icr.io`. We need to create it, and edit our ServiceAccount to point the field `Image pull secrets` to this secret. To do this, just copy the secret `all-icr-io` from the default namespace into your namespace and patch your serviceAccount accordingly :

```console
[root@workstation ~ ]$ kubectl get secret all-icr-io -n default -o yaml | sed 's/default/testlink-test/g' | kubectl create -n testlink-test -f -
secret/all-icr-io created
```

To add the image pull secret when no image pull secret is defined:

```console
[root@workstation ~ ]$ kubectl patch -n testlink-test serviceaccount/default -p '{"imagePullSecrets":[{"name": "all-icr-io"}]}'
serviceaccount/default patched
```

If you need to add multiple image pull secret, and one is already defined :

```
kubectl patch -n <namespace_name> serviceaccount/default --type='json' -p='[{"op":"add","path":"/imagePullSecrets/-","value":{"name":"<image_pull_secret_name>"}}]'
```

Delete the pod to refresh configuration :

```console
[root@workstation ~ ]$ kubectl delete pod testlink-6fd778bdb9-ws6sv -n testlink-test
pod "testlink-6fd778bdb9-ws6sv" deleted
```

```console
[root@workstation ~ ]$ kubectl get pods -n testlink-test
NAME                        READY   STATUS    RESTARTS   AGE
testlink-6fd778bdb9-8nbgn   1/1     Running   0          70s
testlink-mariadb-0          1/1     Running   0          3h12m
```

Now that everything is running smoothly, you can publish your application to make it accessible from outside of your cluster. You need to create Ingress to do this. Ingress will point to your service which is pointing to your pod.

If for any reason you need te create or re-create the service, you can do it with the following command :

```
kubectl expose deploy <deployment-name> --name <svc-name> --port <svc-port> --target-port <pod-port> -n <namespace>
```

You can use the IBM-provided domain, such as `mycluster-<hash>-0000.eu-de.containers.appdomain.cloud/myapp`, to access your app from the internet. To use a custom domain instead, you can set up a CNAME record to map your custom domain to the IBM-provided domain.

Get the IBM-provided domain. Replace `<cluster_name_or_ID>` with the name of the cluster where the app is deployed :

```
ibmcloud ks cluster get --cluster <cluster_name_or_ID> | grep Ingress
```

```console
[root@workstation ~ ]$ ibmcloud ks cluster get --cluster bs8qt9sf0aq0nlv6fjs0 | grep Ingress
Ingress Subdomain:              argo-s3p1-sandbox-acd62f574b4aef68f9d01743b975866c-0000.eu-de.containers.appdomain.cloud   
Ingress Secret:                 argo-s3p1-sandbox-acd62f574b4aef68f9d01743b975866c-0000
```

You need to create your `Ingress` resource now. You can follow examples from these models [HTTP INGRESS](../resources/migration/yaml/ibmcloud/ingress-http.yaml) and [HTTPS INGRESS](../resources/migration/yaml/ibmcloud/ingress-https.yaml) and replace fields according to your needs (https://cloud.ibm.com/docs/containers?topic=containers-ingress#ingress_expose_public). Here is an example :

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: testlink-test
spec:
  tls:
  - hosts:
    - testlink.argo-s3p1-sandbox-acd62f574b4aef68f9d01743b975866c-0000.eu-de.containers.appdomain.cloud
    secretName: argo-s3p1-sandbox-acd62f574b4aef68f9d01743b975866c-0000
  rules:
  - host: testlink.argo-s3p1-sandbox-acd62f574b4aef68f9d01743b975866c-0000.eu-de.containers.appdomain.cloud
    http:
      paths:
      - path: /
        backend:
          serviceName: testlink-svc
          servicePort: 443
```

Apply your `Ingress` resource :

```console
[root@workstation ~ ]$ kubectl apply -f ingress.yaml -n testlink-test
ingress.networking.k8s.io/testlink-test created
```

You can now access your resource through the Ingress URL you configured.

If you need to change your PV configuration regarding reclaim policy and access mode, you can execute following commands.

Change PV reclaim policy to `Retain` :

```console
[root@workstation ~ ]$ kubectl patch pv pvc-458a85b0-4fc1-48a3-804d-7e1de15fd81c -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
persistentvolume/pvc-458a85b0-4fc1-48a3-804d-7e1de15fd81c patched
```

Change the PV access mode to `ReadWriteMany` :

```console
[root@workstation ~ ]$ kubectl patch pv pvc-458a85b0-4fc1-48a3-804d-7e1de15fd81c -p '{"spec":{"accessModes": ["ReadWriteMany"]}}'
persistentvolume/pvc-458a85b0-4fc1-48a3-804d-7e1de15fd81c patched
```


interested link :

- https://cloud.ibm.com/docs/containers?topic=containers-registry#use_imagePullSecret
- https://cloud.ibm.com/docs/containers?topic=containers-registry#other

---------------------------------------------------------------------------------------------------------------------------------

[Main menu](../README.md)

[Next](02-install-velero.md)