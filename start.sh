#!/bin/sh
#Xvfb :1 -screen 0 1280x720x16 &
vncserver :1 -localhost no -geometry 1280x720 -depth 16
export DISPLAY=:1
sleep 2
#x11vnc -rfbport 5901 -display :1 -nopw -forever -listen 0.0.0.0 &
#sleep 2
#fluxbox &
openbox &
echo "正在启动NoneBot喵ing..."
$HOME/.local/bin/nb run
