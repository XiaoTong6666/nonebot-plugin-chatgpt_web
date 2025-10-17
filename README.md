# nonebot-plugin-chatgpt_web

## How to start

```
apt install xvfb chromium fonts-wqy-zenhei #可选 tigervnc-standalone-server tigervnc-tools openbox
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

## Documentation

See [Docs](https://nonebot.dev/)
