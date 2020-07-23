[Main menu](../README.md)

# 01 - Openshift Cheat Sheet

## Login and config

Get cluster info
```
oc cluster-info
```

Login with a user

```
oc login --insecure-skip-tls-verify=true https://api.devibm.local:6443 -u user -p password
```
 
Login internal docker registry

```
docker login -u user -p $(oc whoami -t) default-route-openshift-image-registry.apps.devibm.local
```
 
User Information

```
oc whoami
```
 
View your configuration
```
oc config view
```

## Basic commands
 
Create objects from a file
```
oc create -f myobject.yaml -n myproject
```

Delete objects contained in a file
```
oc delete -f myobject.yaml -n myproject
```

Create or merge objects from file
```
oc apply -f myobject.yaml -n myproject 
```
 
Update existing object 
```
oc patch svc mysvc --type merge --patch '{"spec":{"ports":[{"port": 8080, "targetPort": 5000 }]}}'
```
 
Display all resources 
```
oc get all,secret,configmap 
```
 
Get the Openshift Console Address 
```
oc get -n openshift-console route console 
```

## Pods

Monitor Pod status
```
watch oc get pods
```
 
Show labels
```
oc get pods --show-labels
``` 
 
Gather information on a project's pod deployment with node information 
```
oc get pods -o wide 
```
 
Hide inactive Pods 
```
oc get pods --show-all=false
```

Get the Pod name from the Selector and rsh in it 
```
POD=$(oc get pods -l app=myapp -o name) oc rsh -n $POD 
```
 
Exec single command in pod 
```
oc exec $POD $COMMAND 
```
 
Copy file from myrunning-pod-2 path in the current location 
```
oc rsync myrunning-pod-2:/tmp/LogginData_20180717220510.json . 
```

Get resources usage by pod
```
oc adm top pod <pod-name> -n <namespace>
```

Get resources usage by container
```
oc adm top pod <pod-name> -n <namespace> --containers
```

## Scaling

Scale number of pods to x
```
oc scale deployment <deploy-name> --replicas=x
```

Auto scale of pods regarding cpu usage
```
oc autoscale dc/app-cli --min 2 --max 5 --cpu-percent=75
```

## Image streams

List available IS for openshift project
```
oc get is -n openshift
```
 
Import an image from an external registry
```
oc import-image --from=registry.access.redhat.com/jboss-amq-6/amq62-openshift -n openshift jboss-amq-62:1.3 --confirm
```
 
List available IS and templates
```
oc new-app --list
```

## Templates

Deploy resources contained in a template
```
oc process -f template.yaml | oc create -f -
```
 
List parameters available in a template
```
oc process --parameters -f .template.yaml
```

## Nodes

Get Nodes lits
```
oc get nodes
```

View resources usage on nodes
```
oc adm top nodes
kubectl top nodes
```
 
Check on which Node your Pods are running
```
oc get pods -o wide
```
 
Schedule an application to run on another Node
```
oc patch dc myapp -p '{"spec":{"template":{"spec":{"nodeSelector":{"kubernetes.io/hostname": "ip-10-0-0-74.acme.compute.internal"}}}}}'
```
 
List all pods which are running on a Node
```
oc adm manage-node node1.local --list-pods
```
 
Add a label to a Node
```
oc label node node1.local mylabel=myvalue
```
 
Remove a label from a Node
```
oc label node node1.local mylabel-
```

## Advanced

Create a secret from the CLI and mount it as a volume to a deployment config

```
oc create secret generic <secret-name> --from-literal=username=myuser --from-literal=password=mypassword

oc set volumes dc/<myapp> --add --name=<secret-volume> --mount-path=/opt/app-root/ --secret-name=<secret-name>
```

Create a config map file and mount it as a volume to a deployment config

```
oc create configmap <cm-name> --from-file=<file>

oc set volumes dc/myapp --add --overwrite=true --name=<configmap-volume> --mount-path=/data -t configmap --configmap-name=<cm-name>
```

---------------------------------------------------------------------------------------------------------------------------------

[Main menu](../README.md)

[Suivant](02-ocp-k8s-common-issues.md)