FROM minio/mc
COPY ./scripts/* /tmp/
RUN apk add --no-cache bash \
    && chmod +x /tmp/*
ENTRYPOINT ["/bin/bash"]