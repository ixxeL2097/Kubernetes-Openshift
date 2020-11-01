## Private docker registry
This project is dedicated to implement a private docker registry in Kubernetes cluster using cert-manager and HAproxy.

This tutorial assume that you have a kubernetes running cluster installed. In this example, we have 1 master and 2 workers.

### 1. [Install NFS server](documentation/01-nfs-server.md)

### 2. [Install NFS client provisioner](documentation/02-kube-nfs-client-provisionner.md)

### 3. [Install NGINX ingress controller](documentation/03-ingress-controller.md)

### 4. [Install private docker registry](documentation/04-install-docker-registry.md)

### 5. [Install load balancer with HAproxy](documentation/05-load-balancing.md)

### 6. [Securing docker registry](documentation/06-securing-registry-tls.md)

### 7. [Protect docker registry with login access](documentation/07-login-registry.md)

### 8. [Using registry](documentation/08-using-registry.md)

### 9. [Deploying from registry](documentation/09-deploy-from-registry.md)