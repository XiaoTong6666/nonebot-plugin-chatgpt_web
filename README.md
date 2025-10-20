# nonebot-plugin-chatgpt_web
这是一个基于NoneBot2的ChatGPT网页自动化插件是一款无需API Key的高效bot插件，通过DrissionPage自动化驱动Chromium内核的浏览器与ChatGPT的Web官网交互，实现与官方几乎同步的对话功能。它支持多会话隔离或群聊共享、消息唤醒、会话持久化与Cookie登录，所有行为可通过配置文件灵活控制；内置并发锁与智能分段回复机制，稳定性强且便于调试，非常适合希望免费使用ChatGPT5/5mini模型的机器人场景    

## 如何使用？
本地还是Docker都建议clone一下仓库，因为内包含配置文件（省事
```
git clone https://github.com/XiaoTong6666/nonebot-plugin-chatgpt_web $HOME/nonebot-plugin-chatgpt_web
```
其次是需要使用Cookie-Editor浏览器插件获取登录状态下的ChatGPT官网的cookie的json放到`data/zhanghao_cookies.json`,根据实际情况修改配置文件`.env.prod`（包括代理配置，连接onebot实现配置
### 本地
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
### Docker容器部署（推荐
确保存在并配置好`$HOME/nonebot-plugin-chatgpt_web`
#### Docker hub
```
docker pull xiaotong666/gpt-bot:latest
docker run -d --name gpt-bot -p 5789:5789 -p 5910:5901 --add-host=host.docker.internal:host-gateway -v "$HOME/nonebot-plugin-chatgpt_web/.env.prod:/app/.env.prod" -v "$HOME/nonebot-plugin-chatgpt_web/data:/app/data" gpt-bot
```
#### 阿里云仓库
```
docker pull crpi-6symead8lcrbtpwr.cn-guangzhou.personal.cr.aliyuncs.com/xiaotong666/gpt-bot
docker run -d --name gpt-bot -p 5789:5789 -p 5910:5901 --add-host=host.docker.internal:host-gateway -v "$HOME/nonebot-plugin-chatgpt_web/.env.prod:/app/.env.prod" -v "$HOME/nonebot-plugin-chatgpt_web/data:/app/data" crpi-6symead8lcrbtpwr.cn-guangzhou.personal.cr.aliyuncs.com/xiaotong666/gpt-bot
```
#### 手动构建Docker镜像
如果你在的服务器中国（使用国内镜像源）
```
docker build -t gpt-bot . -f Dockerfile_CN
```
如果非中国（使用官方源）
```
docker build -t gpt-bot . -f Dockerfile
```
Docker run
```
docker run -d --name gpt-bot -p 5789:5789 -p 5910:5901 --add-host=host.docker.internal:host-gateway -v "$HOME/nonebot-plugin-chatgpt_web/.env.prod:/app/.env.prod" -v "$HOME/nonebot-plugin-chatgpt_web/data:/app/data" gpt-bot
```
## Documentation

See [Docs](https://nonebot.dev/)
