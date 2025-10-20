# nonebot-plugin-chatgpt_web

## How to start
本地还是Docker都建议clone一下仓库，因为内包含配置文件（省事
```
git clone https://github.com/XiaoTong6666/nonebot-plugin-chatgpt_web $HOME/nonebot-plugin-chatgpt_web
```
其次是需要使用Cookie-Editor浏览器插件获取浏览器cookie的json放到`data/zhanghao_cookies.json`,根据实际情况修改配置文件`.env.prod`（包括代理配置，连接onebot配置）
### Local
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
### Docker
```
cd $HOME/nonebot-plugin-chatgpt_web
```
```
docker pull xiaotong666/gpt-bot:latest
docker run -d --name gpt-bot -p 5789:5789 -p 5910:5901 --add-host=host.docker.internal:host-gateway -v "$(pwd)/.env.prod:/app/.env.prod" -v "$(pwd)/data:/app/data" gpt-bot
```
#### 阿里云仓库
```
docker pull crpi-6symead8lcrbtpwr.cn-guangzhou.personal.cr.aliyuncs.com/xiaotong666/gpt-bot
docker run -d --name gpt-bot -p 5789:5789 -p 5910:5901 --add-host=host.docker.internal:host-gateway -v "$(pwd)/.env.prod:/app/.env.prod" -v "$(pwd)/data:/app/data" crpi-6symead8lcrbtpwr.cn-guangzhou.personal.cr.aliyuncs.com/xiaotong666/gpt-bot
```

## Documentation

See [Docs](https://nonebot.dev/)
