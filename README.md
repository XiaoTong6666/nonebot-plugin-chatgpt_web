# nonebot-plugin-chatgpt_web

## How to start
```
git clone https://github.com/XiaoTong6666/nonebot-plugin-chatgpt_web
```
需要使用Cookie-Editor获取浏览器cookie的json放到`data/zhanghao_cookies.json`,根据实际情况修改配置文件`.env.prod`（包括代理配置，连接onebot配置）
```
apt install chromium fonts-wqy-zenhei 
# 如果是无头环境还需要
apt install xvfb x11vnc openbox # 无头组合1
apt install tigervnc-standalone-server tigervnc-tools # 无头组合2
pip install -r requirements.txt
pipx install nb-cli
nb adapter install nonebot-adapter-onebot
./start.sh
```
1. generate project using `nb create` .
2. create your plugin using `nb plugin create` .
3. writing your plugins under `gpt-bot/plugins` folder.
4. run your bot using `nb run --reload` .
## Docker
```
docker pull xiaotong666/gpt-bot:latest
docker run -d --name gpt-bot -p 5789:5789 -p 5910:5901 --add-host=host.docker.internal:host-gateway -v "$(pwd)/.env.prod:/app/.env.prod" -v "$(pwd)/data:/app/data" gpt-bot
```

## Documentation

See [Docs](https://nonebot.dev/)
