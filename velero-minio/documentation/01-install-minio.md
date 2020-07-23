[Main menu](../README.md)

# Minio Installation
## Description

This setup will install 4 Minio server instances and 1 Minio client on the same host. **Minio client** will be automatically configured and linked to **minio server instances**. Buckets will be created according to the ```buckets``` variables in ![configure_minio_server.sh script](../resources/minio/scripts/configure_minio_server.sh).

Some modifications:

- An ```.env``` file has been added to control docker-compose.yml variables.
- The ```minio/mc``` image is slightly modified through ```Dockerfile``` to incorporate script and bash cmd.
- ```configure_minio_server.sh``` script is added to link client to server cluster and create buckets.

## Installation

To install properly minio, follow the steps:

- Dowload the `resources/minio` directory.
- Modify ```IP``` variable from ```.env``` file to the external IP of your minio server.
- You can also modify **credentials** and **release version** of minio server image in the ```.env``` file.
- Execute ```docker-compose up -d``` command.

After few seconds of startup, you can check proper installation by executing :
```console
[root@minio-maquette scripts]# docker logs minio_minioclient_1
```
You should be prompted with something like the following picture:

<p align="center">
  <img src="./pictures/successful-minio-config.png" width="60%" height="60%">
</p>

Minio installation should be giving you 3 server instances and 1 client as following : 

```console
[root@minio-dev ~]# docker ps
CONTAINER ID        IMAGE                COMMAND                  CREATED             STATUS                 PORTS                    NAMES
16f5c52d5e41        minio_minioclient    "/bin/bash /tmp/conf…"   5 weeks ago         Up 5 weeks                                      minio_minioclient_1
804a82fb3677        minio/minio:latest   "/usr/bin/docker-ent…"   5 weeks ago         Up 5 weeks (healthy)   0.0.0.0:9001->9000/tcp   minio_minio1_1
cb837624edc2        minio/minio:latest   "/usr/bin/docker-ent…"   5 weeks ago         Up 5 weeks (healthy)   0.0.0.0:9003->9000/tcp   minio_minio3_1
26c0dd4eeb8f        minio/minio:latest   "/usr/bin/docker-ent…"   5 weeks ago         Up 5 weeks (healthy)   0.0.0.0:9004->9000/tcp   minio_minio4_1
c3ef77fc5b7a        minio/minio:latest   "/usr/bin/docker-ent…"   5 weeks ago         Up 5 weeks (healthy)   0.0.0.0:9002->9000/tcp   minio_minio2_1
```

## Using proxy

If you need to install your solution behind a proxy, you can configure docker engine that way:

1. Create a systemd drop-in directory for the docker service

```
mkdir -p /etc/systemd/system/docker.service.d
```

2. Create a file called /etc/systemd/system/docker.service.d/http-proxy.conf that adds the HTTP_PROXY environment variable

```
[Service]
Environment="HTTP_PROXY=http://proxy.example.com:80/" "NO_PROXY=localhost,127.0.0.0/8"
```

3. Flush changes

```
systemctl daemon-reload
```

5. Restart Docker

```
systemctl restart docker
```

6. Verify that the configuration has been loaded

```
systemctl show --property=Environment docker
```

7. Modify Dockerfile to use Proxy by adding following line

```
ENV http_proxy http://proxy.example.com:80/
```

## Adding buckets manually

if you need to add buckets manually after installation, you can do it via the minio client. First log in your minio client container :

```console
[root@minio-dev ~]# docker exec -it minio_minioclient_1 bash
bash-5.0#
```

You might need to re-add your server after a long time, especially if some connexion has been lost between client and server. Also, if you are behind a proxy, don't forget to export **HTTP_PROXY** variable :

```console
bash-5.0# export HTTP_PROXY=http://<user>:<password>@<IP>:<PORT>
bash-5.0# mc config host add minio http://10.135.47.194:9001 minio minio123
Added `minio` successfully.
bash-5.0# mc admin info minio
●  minio2:9000
   Uptime: 1 month 
   Version: 2020-05-28T23:29:21Z
   Network: 4/4 OK 
   Drives: 2/2 OK 

●  minio3:9000
   Uptime: 1 month 
   Version: 2020-05-28T23:29:21Z
   Network: 4/4 OK 
   Drives: 2/2 OK 

●  minio4:9000
   Uptime: 1 month 
   Version: 2020-05-28T23:29:21Z
   Network: 4/4 OK 
   Drives: 2/2 OK 

●  minio1:9000
   Uptime: 1 month 
   Version: 2020-05-28T23:29:21Z
   Network: 4/4 OK 
   Drives: 2/2 OK 

1.3 MiB Used, 2 Buckets, 131 Objects
8 drives online, 0 drives offline
```

check currently created buckets :

```console
bash-5.0# mc tree --depth 1 minio
minio
├─ awx
├─ cmp-core
│  ├─ backups
│  └─ restic
└─ hashicorp
   ├─ backups
   └─ restic
```

Now you can create your buckets manually :

```console
bash-5.0# mc mb minio/test
Bucket created successfully `minio/test`.
bash-5.0# mc tree --depth 1 minio
minio
├─ awx
├─ cmp-core
│  ├─ backups
│  └─ restic
├─ hashicorp
│  ├─ backups
│  └─ restic
└─ test
```

if you want to delete a bucket : 

```console
bash-5.0# mc rb minio/test
Removed `minio/test` successfully.
```

---------------------------------------------------------------------------------------------------------------------------------

[Main menu](../README.md)

[Next](02-install-velero.md)