#!/bin/sh
if [ -f "/.dockerenv" ]; then
    in_docker=1
else
    in_docker=0
fi

if [ -n "$DISPLAY" ]; then
    echo "有DISPLAY=$DISPLAY了喵，直接启动NoneBot喵ing..."
    $HOME/.local/bin/nb run
    exit 0
fi
if [ "$in_docker" = "1" ]; then
    n="2"
    echo "检测到Docker环境了喵~"
else
    while true; do
        echo "没有DISPLAY喵，将使用无头模式喵！"
        echo "请选择启动模式："
        echo "1) Xvfb + x11vnc + NoneBot"
        echo "2) Tigervnc + NoneBot"
        read -p "1 或 2 喵: " n

        if [ "$n" = "1" ] || [ "$n" = "2" ]; then
            break
        else
            echo "你在干嘛喵？请重新选择喵~"
        fi
    done
fi
if [ "$n" = "1" ]; then
    Xvfb :1 -screen 0 1280x720x24 &
    export DISPLAY=:1
    sleep 2
    x11vnc -rfbport 5901 -display :1 -rfbauth /root/.vnc/passwd -forever -listen 0.0.0.0 &
    sleep 1
    openbox &
    echo "正在启动NoneBot喵ing..."
    $HOME/.local/bin/nb run
elif [ "$n" = "2" ]; then
    vncserver :1 -localhost no -geometry 1280x720 -depth 24
    export DISPLAY=:1
    sleep 1
    openbox &
    echo "正在启动NoneBot喵ing..."
    $HOME/.local/bin/nb run
fi
