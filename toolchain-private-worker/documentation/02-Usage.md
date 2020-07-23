# 02-Usage

## How to

First ensure that `ibmcom` and `tekton-releases` namespaces exist in your OpenShift cluster. IF you have some specific proxy settings, you need to modify python script (this feature will be modified to be an environment variable instead).

```console
[root@workstation ~]$ oc get is -n tekton-releases
No resources found.
[root@workstation ~]$ oc get is -n ibmcom
No resources found.
```

After executing script you should have all these images :

```console
[root@workstation ~]$ oc get is -n tekton-releases
NAME                  IMAGE REPOSITORY                                                                               TAGS      UPDATED
controller            default-route-openshift-image-registry.apps.devibm.local/tekton-releases/controller            v0.11.2   43 seconds ago
creds-init            default-route-openshift-image-registry.apps.devibm.local/tekton-releases/creds-init            v0.11.2   29 seconds ago
entrypoint            default-route-openshift-image-registry.apps.devibm.local/tekton-releases/entrypoint            v0.11.2   34 seconds ago
gcs-fetcher           default-route-openshift-image-registry.apps.devibm.local/tekton-releases/gcs-fetcher           v0.11.2   17 seconds ago
git-init              default-route-openshift-image-registry.apps.devibm.local/tekton-releases/git-init              v0.11.2   35 seconds ago
imagedigestexporter   default-route-openshift-image-registry.apps.devibm.local/tekton-releases/imagedigestexporter   v0.11.2   22 seconds ago
kubeconfigwriter      default-route-openshift-image-registry.apps.devibm.local/tekton-releases/kubeconfigwriter      v0.11.2   39 seconds ago
pullrequest-init      default-route-openshift-image-registry.apps.devibm.local/tekton-releases/pullrequest-init      v0.11.2   20 seconds ago
webhook               default-route-openshift-image-registry.apps.devibm.local/tekton-releases/webhook               v0.11.2   23 seconds ago

[root@workstation ~]$ oc get is -n ibmcom
NAME                      IMAGE REPOSITORY                                                                          TAGS    UPDATED
pipeline-private-worker   default-route-openshift-image-registry.apps.devibm.local/ibmcom/pipeline-private-worker   0.6.4   35 seconds ago
```

Private-worker will be installed in `tekton-pipelines` namespace :

```console
[root@workstation ~]$ oc get all -n tekton-pipelines
NAME                                               READY   STATUS    RESTARTS   AGE
pod/private-worker-agent-784d5cdfb4-cmnp5          1/1     Running   0          4m5s
pod/tekton-pipelines-controller-6bf859b7fb-99mj7   1/1     Running   0          4m8s
pod/tekton-pipelines-webhook-545b65b78b-knbkf      1/1     Running   0          4m7s

NAME                                   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                     AGE
service/private-worker-agent-metrics   ClusterIP   172.30.56.212   <none>        8383/TCP,8686/TCP           4m2s
service/tekton-pipelines-controller    ClusterIP   172.30.178.23   <none>        9090/TCP                    4m17s
service/tekton-pipelines-webhook       ClusterIP   172.30.78.253   <none>        9090/TCP,8008/TCP,443/TCP   4m17s

NAME                                          READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/private-worker-agent          1/1     1            1           4m17s
deployment.apps/tekton-pipelines-controller   1/1     1            1           4m17s
deployment.apps/tekton-pipelines-webhook      1/1     1            1           4m17s

NAME                                                     DESIRED   CURRENT   READY   AGE
replicaset.apps/private-worker-agent-784d5cdfb4          1         1         1       4m7s
replicaset.apps/tekton-pipelines-controller-6bf859b7fb   1         1         1       4m8s
replicaset.apps/tekton-pipelines-webhook-545b65b78b      1         1         1       4m7s
```

Proxy settings will be implemented in `deployment.apps/private-worker-agent`. 

After installation, you still need to register your private worker to IBM cloud and verify registration : 

```console
[root@workstation ~]$ kubectl apply --filename "https://private-worker-service.eu-de.devops.cloud.ibm.com/install/worker?serviceId=ServiceId-733eded5-ce92-465f-b543-7efba0228a1e&apikey=48p95udO7ZxqB_k5JdyuhagxavQjzjP5L7rg_K6V5swB&name=pw-ocp-dev6-test"
workeragent.devops.cloud.ibm.com/pw-ocp-dev6-test created
secret/pw-ocp-dev6-test-auth created

[root@workstation ~]$ kubectl get workeragent
NAME               SERVICEID                                        REGISTERED   VERSION   AUTH
pw-ocp-dev6-test   ServiceId-733eded5-ce92-465f-b543-7efba0228a1e   Succeeded    OK        OK
```

Following commands will be automatically done by the script but it's nice to mention that it's needed in order to work :

```
oc policy add-role-to-user system:image-puller system:serviceaccount:tekton-pipelines:tekton-pipelines-controller --namespace=tekton-releases
oc policy add-role-to-user system:image-puller system:serviceaccount:tekton-pipelines:private-worker-agent --namespace=tekton-releases
oc adm policy add-scc-to-user anyuid system:serviceaccount:tekton-pipelines:tekton-pipelines-controller
```

## Adding your own OCP environment

If you want to add your own OpenShift environment to be available in the script, you just need to add a global variable inside the python script. Name it as you want and populate variables like this:

```
my-new-environment =	{
    "OCP_API": "api.ocp4-example.dev.local:6443",
    "OCP_registry": "default-route-openshift-image-registry.apps.ocp4-example.dev.local",
    "OCP_user": "some_user",
    "OCP_pwd": "some_password"
}
```

You don't have to save your `OCP_user` and `OCP_password` inside the script, you can leave it blank and pass it as an environment variable inside the container with `docker run -e OC_USER=some_user -e OC_PWD=some_password`.

Once your environment is saved inside the script, just refer to it (`TARGET`) when running the scipt/container like this :

```
docker run --name pw -e TARGET=my_new_environment -e OC_USER=some_user -e OC_PWD=some_password -it <container> python3 install-pw-ocp-offline.py
```



