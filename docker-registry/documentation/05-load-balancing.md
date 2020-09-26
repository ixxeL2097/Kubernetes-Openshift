[main menu](../README.md)

## 05 - Load balancing

Ok, now our registry can be connected from outside the cluster with a pretty domain name, but we don’t want to type the port each time we want to connect to the registry.

In order to remove that port we will need to install a Proxy in front of our cluster, in a cloud environment like GKE or AWS, you can use the `Service Type LoadBalancer`. Since we are on “Bare Metal” server we will instead install `HaProxy` on the master (or any other host that can have access to our nodes).

```console
[root@workstation ~]# yum install haproxy
```

Then you need to configure it by editing/creating the file : `/etc/haproxy/haproxy.cfg`

```
#---------------------------------------------------------------------
# Example configuration for a possible web application.  See the
# full configuration options online.
#
#   http://haproxy.1wt.eu/download/1.4/doc/configuration.txt
#
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# Global settings
#---------------------------------------------------------------------
global
    log /dev/log local2
    log /dev/log local1 notice

    chroot      /var/lib/haproxy
    pidfile     /var/run/haproxy.pid
    maxconn     4000
    user        haproxy
    group       haproxy
    daemon

    # turn on stats unix socket
    stats socket /var/lib/haproxy/stats

#---------------------------------------------------------------------
# common defaults that all the 'listen' and 'backend' sections will
# use if not designated in their block
#---------------------------------------------------------------------
defaults
    mode                    tcp
    log                     global
    option                  tcplog
    timeout connect         10s
    timeout client          1m
    timeout server          1m

#---------------------------
# KUBERNETES CONFIG
#---------------------------

frontend http-frontend
    bind *:80
    default_backend http-backend

backend http-backend
   balance roundrobin
   #  31953 is the "NodePort" of Ingress HTTP Service
   server worker1 192.168.0.151:31953 check
   server worker2 192.168.0.152:31953 check

frontend https-frontend
    bind *:443
    default_backend https-backend

backend https-backend
   balance roundrobin
   # 32755 is the "NodePort" of Ingress HTTPS Service
   server worker1 192.168.0.151:32755 check
   server worker2 192.168.0.152:32755 check
```

I chose to use HAProxy in TCP mode, in order to delegate everything regarding http or https negociation to the Ingress Controller.

As you can see, `http-backend` points to the nodes ingress’s `http` port, and `https-backend` is pointing to the ingress’s `https` port.


```console
[root@workstation ~]# systemctl restart haproxy
```
