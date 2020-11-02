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

In our case, we will not use the `make push-image` command, but rather push the image to our personal private registry instead.



