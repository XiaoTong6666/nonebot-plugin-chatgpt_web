import os
import time
import asyncio
import concurrent.futures
from typing import Optional, Dict
from nonebot import on_command, get_plugin_config, get_driver, on_message
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message, Event, Bot
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.log import logger
from DrissionPage import Chromium, ChromiumOptions, ChromiumPage
from .config import Config
from .message_formatter import MessageFormatter
from nonebot.adapters.onebot.v11 import MessageEvent as V11MessageEvent

__plugin_meta__ = PluginMetadata(
    name="gpt-bot",
    description="ChatGPT自动化问答插件",
    usage="群聊: /gpt <问题> | 私聊: 直接发送问题",
    type="application",
    config=Config,
)

peizhi = get_plugin_config(Config)
qudong = get_driver()

# 全局浏览器变量
liulanqi: Optional[Chromium] = None
# biaoqian = None
duihua_biaoqian_map: Dict[str, ChromiumPage] = {}
yichushihua = False

def is_private_message(event: V11MessageEvent) -> bool:
    #真私聊
    is_true_private = event.message_type == "private"
    #双id同
    is_temp_session = (
        event.message_type == "group" and
        event.user_id == event.group_id
    )

    return is_true_private or is_temp_session

def is_group_message(event: V11MessageEvent) -> bool:
    # 规则：判断消息是否来自群聊
    return event.message_type == "group"

def chushihua_liulanqi_jincheng() -> bool:
    """仅同步初始化浏览器进程，不创建标签页"""
    global liulanqi, yichushihua
    try:
        if yichushihua:
          return True
        logger.info("在初始化 Chromium 进程喵ing...")
        co = ChromiumOptions().set_browser_path(peizhi.chromium_path)
        co.set_user_data_path(os.path.expanduser("~/.config/chromium"))
        liulanqi = Chromium(co)
        yichushihua = True
        logger.info("Chromium 进程初始化完成了喵~")
        return True

    except Exception as e:
        logger.error(f"浏览器进程初始化失败喵qwq：{e}")
        guanbi_liulanqi()
        return True

def huoqu_huo_chuangjian_biaoqian(duihua_id: str) -> Optional[ChromiumPage]:
    """根据对话ID获取或创建新的标签页"""
    global liulanqi
    if not yichushihua or not liulanqi:
        logger.error("浏览器进程还没初始化，没法创建标签页喵qwq")
        return None
    if duihua_id in duihua_biaoqian_map:
        return duihua_biaoqian_map[duihua_id]

    try:
        logger.info(f"在给 {duihua_id} 创建 ChatGPT 标签页喵ing...")
        biaoqian = liulanqi.new_tab(url="https://chatgpt.com")
        biaoqian.ele("#prompt-textarea", timeout=20)

        # JS注入拦截脚本（核心）
        zhuru_js = r"""
          (async () => {
            window.zuihouHuifu = "";
            const yuanshiFetch = window.fetch;
            window.fetch = async (...canshu) => {
              const [lianjie, xuanxiang] = canshu;
              if (lianjie.includes('/backend-api/f/conversation') && xuanxiang?.method === 'POST') {
                const fanhui = await yuanshiFetch(...canshu);
                const fuben = fanhui.clone();
                const duzhe = fuben.body.getReader();
                const bianmaqi = new TextDecoder("utf-8");
                let quanwen = "";
                let buffer = "";
                try {
                  while (true) {
                    const { value: zhi, done: wancheng } = await duzhe.read();
                    if (wancheng) break;
                    buffer += bianmaqi.decode(zhi, { stream: true });
                    const hangshu = buffer.split('\n');
                    if (!buffer.endsWith('\n')) buffer = hangshu.pop();
                    else buffer = "";
                    for (const hangRaw of hangshu) {
                      if (!hangRaw) continue;
                      const hang = hangRaw.replace(/\r$/, '');
                      console.log('[raw_line]', hang);
                      if (!hang.startsWith('data: ') || hang.includes('[DONE]')) continue;
                      try {
                        const shuju = JSON.parse(hang.replace(/^data:\s*/, ''));
                        if (shuju?.o === 'patch' && Array.isArray(shuju.v)) {
                          for (const i of shuju.v) {
                            if (i?.o === 'append' && typeof i.v === 'string') {
                              quanwen += i.v;
                              console.log('[patch append追加]', i.v);
                            }
                          }
                        } else if (Array.isArray(shuju?.v)) {
                          for (const i of shuju.v) {
                            if (i?.o === 'append' && typeof i.v === 'string') {
                              quanwen += i.v;
                              console.log('[delta append追加]', i.v);
                            }
                          }
                        } else if (shuju?.v?.message?.content?.parts?.[0] && shuju.v.message.author.role === 'assistant') {
                          quanwen += shuju.v.message.content.parts[0];
                          console.log('[message.parts追加]', shuju.v.message.content.parts[0]);
                        } else if (typeof shuju?.v === 'string') {
                          quanwen += shuju.v;
                          console.log('[v字符串追加]', shuju.v);
                        }
                        if (shuju?.type === 'message_stream_complete' || shuju?.message?.status === 'finished_successfully') {
                          window.zuihouHuifu = quanwen;
                          console.log('[流结束 by type]', window.zuihouHuifu);
                        }
                      } catch (cuowu) {
                        console.warn('[解析失败]', hang, cuowu?.message);
                      }
                    }
                  }
                } catch (e) {
                  console.error('[reader异常]', e?.message);
                }
                if (quanwen) {
                  window.zuihouHuifu = quanwen;
                  console.log('[流结束兜底]', window.zuihouHuifu);
                }
                console.log('[完整内容]', window.zuihouHuifu);
                return fanhui;
              }
              return yuanshiFetch(...canshu);
            };
          })();
        """
        biaoqian.run_js(zhuru_js)

        duihua_biaoqian_map[duihua_id] = biaoqian
        logger.info(f"给 {duihua_id} 创建页面成功了喵！")
        return biaoqian

    except Exception as e:
        logger.error(f"给 {duihua_id} 创建页面失败了喵qwq: {e}")
        return None

def tiwen_gpt(wenti: str, biaoqian: ChromiumPage) -> Optional[str]:
    """同步提问 ChatGPT"""
    if not biaoqian:
        raise Exception("这是无效的标签页对象喵")

    try:
        logger.info(f"输入来了喵！: {wenti}")
        wenti_anquan = (
            wenti.replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("${", "\\${")
        )

        fasong_js = r"""
          (async () => {
              const bianjiqi = document.querySelector('#prompt-textarea');
              if (!bianjiqi) throw new Error("找不到输入框 #prompt-textarea");
              bianjiqi.innerText = "__CONTENT__";
              bianjiqi.dispatchEvent(new Event('input', { bubbles: true }));
              bianjiqi.dispatchEvent(new Event('change', { bubbles: true }));
              await new Promise(r => setTimeout(r, 500));

              const fasongAnniu = document.querySelector('#composer-submit-button');
              if (!fasongAnniu) throw new Error("找不到发送按钮 #composer-submit-button");
              await new Promise(r => {
                  const jiancha = setInterval(() => {
                      if (!fasongAnniu.disabled) {
                          clearInterval(jiancha);
                          r();
                      }
                  }, 100);
              });
              fasongAnniu.click();
          })();
        """.replace("__CONTENT__", wenti_anquan)

        biaoqian.run_js("window.zuihouHuifu = '';")
        biaoqian.console.clear()
        biaoqian.run_js(fasong_js)

        zuihou_neirong = ""
        start = time.time()

        while time.time() - start < peizhi.response_timeout:
            neirong = biaoqian.run_js("return window.zuihouHuifu || '';")
            if neirong and neirong != zuihou_neirong:
                logger.info(f"获取到了喵！: {neirong[:50]}...")
                zuihou_neirong = neirong
                biaoqian.console.clear()

                # 等待内容稳定
                stable_start = time.time()
                stable = neirong
                while time.time() - stable_start < 2:
                    time.sleep(0.2)
                    current = biaoqian.run_js(
                        "return window.zuihouHuifu || '';")
                    if current != stable:
                        stable = current
                        stable_start = time.time()

                return stable

            time.sleep(0.5)

        return zuihou_neirong or None

    except Exception as e:
        logger.error(f"提问失败了喵qwq: {e}")
        return None


def guanbi_liulanqi():
    """同步关闭浏览器"""
    global liulanqi, biaoqian, yichushihua
    try:
        if liulanqi:
            liulanqi.quit()
    except Exception as e:
        logger.warning(f"关闭浏览器出错了喵qwq: {e}")
    finally:
        liulanqi = None
        duihua_biaoqian_map.clear()
        yichushihua = False
        logger.info("ChatGPT 处理器已关闭了喵~")


@qudong.on_startup
async def kaishi_gpt():
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        success = await loop.run_in_executor(pool, chushihua_liulanqi_jincheng)
    logger.info("初始化成功了喵~" if success else "初始化失败了喵qwq")


@qudong.on_shutdown
async def guanbi_gpt():
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, guanbi_liulanqi)
    logger.info("已关闭喵~")


async def handle_gpt_request(matcher: Matcher, event: Event, wenti: str):
    """处理GPT请求、获取回答并发送"""
    if not yichushihua:
        await matcher.finish("模块还没就绪喵~")

    try:
        loop = asyncio.get_event_loop()
        duihua_id = event.get_session_id()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            dangqian_biaoqian = await loop.run_in_executor(pool, huoqu_huo_chuangjian_biaoqian, duihua_id)

        if not dangqian_biaoqian:
            await matcher.finish("创建会话失败了喵qwq")

        logger.info(f"要开始为对话 {duihua_id} 处理问题了喵~: {wenti}")
        with concurrent.futures.ThreadPoolExecutor() as pool:
            huida = await loop.run_in_executor(pool, tiwen_gpt, wenti, dangqian_biaoqian)

        logger.info(f"尝试发送喵！: {huida}")

        if huida:
            neirong = MessageFormatter.gezhihua_gpt_huida(huida, wenti)
            await matcher.finish(neirong)
        else:
            await matcher.finish("没能返回有效回答喵qwq")

    except Exception as e:
        logger.error(f"处理失败了喵qwq: {e}")
        # await matcher.finish("GPT 模块异常")

# 响应器1：处理群聊中的 /gpt 命令
gpt_group = on_command("gpt", rule=is_group_message, priority=10, block=True)

# 响应器2：处理私聊中的所有消息，创建一个新的 Matcher，不需要命令前缀
gpt_private = on_message(rule=is_private_message, priority=99, block=True)

# 处理器1：绑定到 gpt_group 响应器
@gpt_group.handle()
async def gpt_group_handler(matcher: Matcher, event: V11MessageEvent, args: Message = CommandArg()):
    """群聊中的 /gpt 命令处理器"""
    wenti = args.extract_plain_text().strip()
    if not wenti:
        await matcher.finish("发送空白内容打咩")
    # 在内部调用封装好的核心逻辑
    await handle_gpt_request(matcher, event, wenti)

# 处理器2：绑定到 gpt_private 响应器
@gpt_private.handle()
async def gpt_private_handler(matcher: Matcher, event: V11MessageEvent):
    """私聊中的消息处理器"""
    wenti = event.get_plaintext().strip()
    # 过滤掉可能是其他命令的消息
    command_start = list(get_driver().config.command_start)
    if not wenti or (command_start and wenti.startswith(tuple(command_start))):
        return
    # 在内部调用封装好的核心逻辑
    await handle_gpt_request(matcher, event, wenti)
