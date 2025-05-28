FROM alpine:3.20

# 拷贝配置
COPY dist/config.json /opt/honeypots/config.json

# 安装依赖
RUN apk --no-cache -U upgrade && \
    apk --no-cache -U add \
        build-base \
        freetds \
        freetds-dev \
        gcc \
        git \
        hiredis \
        jpeg-dev \
        libcap \
        libcap-utils \
        libffi-dev \
        libpq \
        linux-headers \
        musl-dev \
        openssl \
        openssl-dev \
        postgresql-dev \
        py3-chardet \
        py3-click \
        py3-cryptography \
        py3-dnspython \
        py3-flask \
        py3-future \
        py3-hiredis \
        py3-itsdangerous \
        py3-jinja2 \
        py3-ldap3 \
        py3-markupsafe \
        py3-openssl \
        py3-packaging \
        py3-pip \
        py3-psycopg2 \
        py3-pycryptodomex \
        py3-setuptools \
        py3-werkzeug \
        py3-wheel \
        python3 \
        python3-dev \
        zlib-dev && \
    pip3 install --break-system-packages --no-cache-dir \
        pyftpdlib \
        netifaces \
        psutil \
        twisted \
        service_identity \
        pyasn1 \
        pyopenssl \
        requests \
        scapy \
        colorama \
        tqdm \
        psycopg[binary] \
        paramiko \
        pycryptodome \
        git+https://github.com/fortra/impacket.git && \
    setcap cap_net_bind_service=+ep $(readlink -f $(which python3)) && \
    rm -rf /root/.cache /tmp/*

# 拷贝源码
COPY honeypots/ /opt/honeypots/

# 创建用户和日志目录
RUN addgroup -g 2000 honeypots && \
    adduser -S -H -u 2000 -D -G honeypots honeypots && \
    mkdir -p /var/log/honeypots && \
    chown -R honeypots:honeypots /opt/honeypots /var/log/honeypots

USER honeypots:honeypots
WORKDIR /opt/honeypots

# 模块导入路径
ENV PYTHONPATH=/opt

STOPSIGNAL SIGINT

CMD ["python3", "-m", "honeypots", "--setup", "ftp", "--config", "config.json"]
