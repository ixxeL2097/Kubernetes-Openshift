FROM alpine:edge as builder

COPY ./resources/oc43.sh /bin/oc43.sh

RUN apk update --no-cache \
    && apk add wget curl --no-cache \
    && wget $(curl -s https://api.github.com/repos/mikefarah/yq/releases/latest | grep browser_download_url | grep linux_amd64 | cut -d '"' -f 4) -O /usr/bin/yq \
    && curl https://mirror.openshift.com/pub/openshift-v4/clients/oc/4.3/linux/oc.tar.gz -o /tmp/oc.tar.gz \
    && tar -xzvf /tmp/oc.tar.gz -C /bin \
    && rm /tmp/oc.tar.gz \
    && chmod +x /usr/bin/yq \
    && chmod a+x /bin/oc43.sh

FROM alpine:edge

COPY --from=builder /usr/bin/yq /usr/bin/yq
COPY --from=builder /bin/oc43.sh /bin/oc /bin/
COPY ./resources/requirements.txt ./install-pw-ocp-offline.py app/

WORKDIR /app

RUN apk update --no-cache \
    && apk add python3 skopeo py3-pip --no-cache \
    && pip3 install -r requirements.txt

