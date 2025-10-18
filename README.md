# nonebot-plugin-chatgpt_web

## How to start
```
git clone https://github.com/XiaoTong6666/nonebot-plugin-chatgpt_web
```
需要使用Cookie-Editor获取浏览器cookies放到`data/zhanghao_cookies.json`
```
apt install xvfb chromium fonts-wqy-zenhei #可选 tigervnc-standalone-server tigervnc-tools x11vnc openbox
pip install -r requirements.txt
pip install 'nonebot2[fastapi,httpx,websockets]'
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
docker run -d --name gpt-bot -p 5789:5789 -p 5910:5901 --add-host=host.docker.internal:host-gateway -v "$(pwd)/.env.prod:/app/.env.prod" -v "$(pwd)/data:/app/data" gpt-bot
```

## Documentation

See [Docs](https://nonebot.dev/)
