FROM python:3.11-slim

RUN sed -i 's|http://deb.debian.org/debian|http://ftp.cn.debian.org/debian|g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's|http://security.debian.org/debian-security|http://ftp.cn.debian.org/debian-security|g' /etc/apt/sources.list.d/debian.sources


RUN apt update && \
    apt install -y --no-install-recommends \
    xvfb \
    chromium \
    tigervnc-standalone-server \
    tigervnc-tools \
    openbox \
    fonts-wqy-zenhei \
    x11vnc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir -p /root/.vnc && \
    echo "123456" | vncpasswd -f > /root/.vnc/passwd && \
    chmod 600 /root/.vnc/passwd && \
    mkdir /root/.config && \
    cp -r /root/.vnc /root/.config/tigervnc

COPY requirements.txt ./
COPY pyproject.toml ./

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn && \
    python3 -m pip install -r requirements.txt && \
    python3 -m pipx ensurepath && \
    pipx install nb-cli && \
    /root/.local/bin/nb adapter install nonebot-adapter-onebot

COPY src/ ./src/
COPY start.sh ./

RUN chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]

