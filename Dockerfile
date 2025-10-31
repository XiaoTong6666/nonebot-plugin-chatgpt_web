FROM python:3.11-slim

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

RUN python3 -m pip install -r requirements.txt && \
    python3 -m pipx ensurepath && \
    pipx install nb-cli && \
    /root/.local/bin/nb adapter install nonebot-adapter-onebot && \
    /root/.local/bin/nb adapter install nonebot-adapter-telegram

COPY src/ ./src/
COPY start.sh ./

RUN chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]

