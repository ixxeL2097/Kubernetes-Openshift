[Main menu](../README.md)

# 01-Python script
## Auto installer

This script is intended to automatically install IBM private worker in offline OpenShift environment.

## What it does

The script does the following :

- Download IBM yaml descriptor file for private-worker
- Download all docker images related to private worker installation
- Modify yaml descriptor file with OpenShift private registry URL instead
- Modify yaml descriptor file to add HTTPS_PROXY and NO_PROXY variables to deployment
- Upload docker images to OpenShift internal registry
- Install private-worker on OpenShift
- Set adequate policies

### Usage

Mandatory parameters :
- TARGET (name of the OCP environment your are targeting)

Optional parameters :
- OC_USER (oc login user)
- OC_PWD (oc login password)
- OC_HTTPS_PROXY (https proxy settings for OCP cluster)

```
docker run --name pw -e TARGET=<ENVIRONMENT> -e OC_USER=<OCP USER> -e OC_PWD=<OCP PASSWORD> -e OC_HTTPS_PROXY=http://<user>:<password>@<IP>:<PORT> -it <container> python3 install-pw-ocp-offline.py
```

### Output

```console
[root@workstation ~]$ docker run --name pw -e TARGET=dev6 -e OC_USER=admin -e OC_PWD=password -e OC_HTTPS_PROXY=http://admin:password@10.194.216.124:3128 -it pw-builder:v2 python3 install-pw-ocp-offline.py

[ SKOPEO PULL ] > COPYING IMAGE FROM [[ docker://gcr.io/tekton-releases/github.com/tektoncd/pipeline/cmd/controller:v0.11.2 ]] to [[ dir:/tmp/controller:v0.11.2 ]]
Getting image source signatures
Copying blob 9ff2acc3204b done  
Copying blob 0840a7aebc20 done  
Copying blob 80071018d72b done  
Copying config 0e1e79945d done  
Writing manifest to image destination
Storing signatures
[ SKOPEO PULL ] > COPYING IMAGE FROM [[ docker://gcr.io/tekton-releases/github.com/tektoncd/pipeline/cmd/kubeconfigwriter:v0.11.2 ]] to [[ dir:/tmp/kubeconfigwriter:v0.11.2 ]]
Getting image source signatures
Copying blob 9ff2acc3204b done  
Copying blob 0840a7aebc20 done  
Copying blob e8849851826b done  
Copying config 391b941d52 done  
Writing manifest to image destination
Storing signatures

[...]

OC login : https://api.devibm.local:6443
Login successful.

You have access to 57 projects, the list has been suppressed. You can list all projects with 'oc projects'

Using project "default".
Welcome! See 'oc help' to get started.
[ SKOPEO PUSH ] > COPYING IMAGE FROM [[ dir:/tmp/controller:v0.11.2 ]] to [[ docker://default-route-openshift-image-registry.apps.devibm.local/tekton-releases/controller:v0.11.2
Getting image source signatures
Copying blob 9ff2acc3204b skipped: already exists  
Copying blob 0840a7aebc20 skipped: already exists  
Copying blob 80071018d72b [--------------------------------------] 0.0b / 0.0b
Copying config 0e1e79945d [--------------------------------------] 0.0b / 1003.0b
Writing manifest to image destination
Storing signatures
[ SKOPEO PUSH ] > COPYING IMAGE FROM [[ dir:/tmp/kubeconfigwriter:v0.11.2 ]] to [[ docker://default-route-openshift-image-registry.apps.devibm.local/tekton-releases/kubeconfigwriter:v0.11.2
Getting image source signatures
Copying blob 9ff2acc3204b skipped: already exists  
Copying blob 0840a7aebc20 skipped: already exists  
Copying blob e8849851826b [--------------------------------------] 0.0b / 0.0b
Copying config 391b941d52 [--------------------------------------] 0.0b / 1.0KiB
Writing manifest to image destination
Storing signatures

[...]

[ OCP ] > INSTALLING PRIVATE WORKER
namespace/tekton-pipelines created
podsecuritypolicy.policy/tekton-pipelines created
clusterrole.rbac.authorization.k8s.io/tekton-pipelines-admin created
serviceaccount/tekton-pipelines-controller created
clusterrolebinding.rbac.authorization.k8s.io/tekton-pipelines-controller-admin created
customresourcedefinition.apiextensions.k8s.io/clustertasks.tekton.dev created
customresourcedefinition.apiextensions.k8s.io/conditions.tekton.dev created
customresourcedefinition.apiextensions.k8s.io/images.caching.internal.knative.dev created
customresourcedefinition.apiextensions.k8s.io/pipelines.tekton.dev created
customresourcedefinition.apiextensions.k8s.io/pipelineruns.tekton.dev created
customresourcedefinition.apiextensions.k8s.io/pipelineresources.tekton.dev created
customresourcedefinition.apiextensions.k8s.io/tasks.tekton.dev created
customresourcedefinition.apiextensions.k8s.io/taskruns.tekton.dev created
secret/webhook-certs created
validatingwebhookconfiguration.admissionregistration.k8s.io/validation.webhook.pipeline.tekton.dev created
mutatingwebhookconfiguration.admissionregistration.k8s.io/webhook.pipeline.tekton.dev created
validatingwebhookconfiguration.admissionregistration.k8s.io/config.webhook.pipeline.tekton.dev created
clusterrole.rbac.authorization.k8s.io/tekton-aggregate-edit created
clusterrole.rbac.authorization.k8s.io/tekton-aggregate-view created
configmap/config-artifact-bucket created
configmap/config-artifact-pvc created
configmap/config-defaults created
configmap/feature-flags created
configmap/config-logging created
configmap/config-observability created
deployment.apps/tekton-pipelines-controller created
service/tekton-pipelines-controller created
deployment.apps/tekton-pipelines-webhook created
service/tekton-pipelines-webhook created
customresourcedefinition.apiextensions.k8s.io/workeragents.devops.cloud.ibm.com created
deployment.apps/private-worker-agent created
role.rbac.authorization.k8s.io/private-worker-agent created
rolebinding.rbac.authorization.k8s.io/private-worker-agent created
serviceaccount/private-worker-agent created
clusterrolebinding.rbac.authorization.k8s.io/private-worker-agent created
storageclass.storage.k8s.io/tekton-local-storage created
[ OCP ] > APPLYING PULL IMAGE POLICY
clusterrole.rbac.authorization.k8s.io/system:image-puller added: "system:serviceaccount:tekton-pipelines:tekton-pipelines-controller"
clusterrole.rbac.authorization.k8s.io/system:image-puller added: "system:serviceaccount:tekton-pipelines:private-worker-agent"
[ OCP ] > APPLYING SERVICE ACCOUNT POLICY
securitycontextconstraints.security.openshift.io/anyuid added to: ["system:serviceaccount:tekton-pipelines:tekton-pipelines-controller"]
[[ Elapsed time : 0:01:32.819096 ]]
```

Registering private worker :

```console
[root@workstation ~]$ kubectl apply --filename "https://private-worker-service.eu-de.devops.cloud.ibm.com/install/worker?serviceId=ServiceId-733eded5-ce92-465f-b543-7efba0228a1e&apikey=##############################&name=pw-ocp-dev6-test"
workeragent.devops.cloud.ibm.com/pw-ocp-dev6-test created
secret/pw-ocp-dev6-test-auth created

[root@workstation ~]$ kubectl get workeragent
NAME               SERVICEID                                        REGISTERED   VERSION   AUTH
pw-ocp-dev6-test   ServiceId-733eded5-ce92-465f-b543-7efba0228a1e   Succeeded    OK        OK
```

---------------------------------------------------------------------------------------------------------------------------------

[Main menu](../README.md)