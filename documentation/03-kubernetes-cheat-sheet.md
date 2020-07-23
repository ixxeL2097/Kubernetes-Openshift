# 03 - Kubernetes Cheat Sheet

## PODS

```
$ kubectl get pods
$ kubectl get pods --all-namespaces
$ kubectl get pod monkey -o wide
$ kubectl get pod monkey -o yaml
$ kubectl describe pod monkey
```

Get resources usage by pod
```
kubectl top pod <pod-name> -n <namespace>
```

Get resources usage by container
```
kubectl top pod <pod-name> -n <namespace> --containers
```

## Create Deployments

Create single deployment

```
$ kubectl run monkey --image=monkey --record
```

## Scaling PODs

```bash
$ kubectl scale deployment/POD_NAME --replicas=N
```

## POD Upgrade and history

#### List history of deployments

```
$ kubectl rollout history deployment/DEPLOYMENT_NAME
```

#### Jump to last revision

```
$ kubectl rollout undo deployment/DEPLOYMENT_NAME
$ kubectl rollout undo deployment/DEPLOYMENT_NAME --to-revision=0
```

#### Jump to specific revision

```
$ kubectl rollout undo deployment/DEPLOYMENT_NAME --to-revision=N
```

## Services

List services

```
$ kubectl get services
```

Expose PODs as services (creates endpoints)

```
$ kubectl expose deployment/monkey --port=2001 --type=NodePort
```

Expose an app through ClusterIP service 

```
kubectl expose deploy <app_deployment_name> --name my-app-svc --port <app_port> -n <namespace>
```

Expose an app through LoadBalancer service

```
kubectl expose rc example --port=<svc-port> --target-port=<app_port> --name=example-service --type=LoadBalancer
```

## Volumes

Lits Persistent Volumes and Persistent Volumes Claims:

```
$ kubectl get pv
$ kubectl get pvc
```

## Secrets

```
$ kubectl get secrets
$ kubectl create secret generic --help
$ kubectl create secret generic mysql --from-literal=password=root
$ kubectl get secrets mysql -o yaml
```
## ConfigMaps

```
$ kubectl create configmap foobar --from-file=config.js
$ kubectl get configmap foobar -o yaml
```

## DNS

List DNS-PODs:

```
$ kubectl get pods --all-namespaces | grep dns
```

Check DNS for pod nginx (assuming a busybox POD/container is running)

```
$ kubectl exec -ti busybox -- nslookup nginx
```

> Note: kube-proxy running in the worker nodes manage services and set iptables rules to direct traffic.

## Ingress

Commands to manage Ingress for ClusterIP service type:

```
$ kubectl get ingress
$ kubectl expose deployment ghost --port=2368
```

Spec for ingress:

- [backend](https://github.com/kubernetes/ingress/tree/master/examples/deployment/nginx)
 
## Horizontal Pod Autoscaler

When heapster runs:

```
$ kubectl get hpa
$ kubectl autoscale --help
```

## DaemonSets

```
$ kubectl get daemonsets
$ kubectl get ds
```

## Scheduler

NodeSelector based policy:

```
$ kubectl label node minikube foo=bar
```

Node Binding through API Server:

```
$ kubectl proxy 
$ curl -H "Content-Type: application/json" -X POST --data @binding.json http://localhost:8001/api/v1/namespaces/default/pods/foobar-sched/binding
```

## Tains and Tolerations

```
$ kubectl taint node master foo=bar:NoSchedule
```

## Troubleshooting

```
$ kubectl describe
$ kubectl logs
$ kubectl exec
$ kubectl get nodes --show-labels
$ kubectl get events
```

Docs Cluster: 
- https://kubernetes.io/docs/tasks/debug-application-cluster/debug-cluster/
- https://github.com/kubernetes/kubernetes/wiki/Debugging-FAQ

## Role Based Access Control

- Role
- ClusterRule
- Binding
- ClusterRoleBinding

```
$ kubectl create role fluent-reader --verb=get --verb=list --verb=watch --resource=pods
$ kubectl create rolebinding foo --role=fluent-reader --user=minikube
$ kubectl get rolebinding foo -o yaml
```

## Security Contexts

Docs: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/

- spec
 - securityContext
   - runAsNonRoot: true
   
## Pod Security Policies

Docs: https://github.com/kubernetes/kubernetes/blob/master/examples/podsecuritypolicy/rbac/README.md

## Network Policies

Network isolation at Pod level by using annotations

```
$ kubectl annotate ns <namespace> "net.beta.kubernetes.io/network-policy={\"ingress\": {\"isolation\": \"DefaultDeny\"}}"
```

More about Network Policies as a resource: 

https://kubernetes.io/docs/tasks/administer-cluster/declare-network-policy/


## Bonus

Delete 'completed' pods

```
$ kubectl get pods -n cmp-core | awk '{if ($3 == "Completed") system("kubectl delete pod " $1 " -n <namespace>")}'
```

Display node on which pods are running

```
$ kubectl get pod -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName -n <namespace>
```

Get plain text secret from secret resource

```
$ kubectl get secret <secretName> -n <namespace> -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

Change PV status from 'released' to 'available'

```
$ kubectl patch pv pv-for-rabbitmq -p '{"spec":{"claimRef": null}}'
```

Delete a protected PVC stuck on 'terminating'

```
$ kubectl patch pvc PVC_NAME -p '{"metadata":{"finalizers": []}}' --type=merge
```

Patch a deployment annotatiion

```
$ kubectl -n kube-system patch deployment <Deploymentname> -p '{"spec":{"template":{"metadata":{"annotations":{"runtime.frakti.alpha.kubernetes.io/OSContainer": "true"}}}}}'
```
