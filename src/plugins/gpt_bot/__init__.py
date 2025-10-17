import os
import time
import asyncio
import concurrent.futures
import json
from typing import Optional, Dict, Set
from nonebot import on_command, get_plugin_config, get_driver, on_message
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message, Event, Bot
from nonebot.params import CommandArg
from nonebot.matcher import Matcher
from nonebot.log import logger
from nonebot.rule import Rule
from DrissionPage import Chromium, ChromiumOptions, ChromiumPage
from .config import Config
from .message_formatter import MessageFormatter
from nonebot.adapters.onebot.v11 import MessageEvent as V11MessageEvent, Bot as V11Bot

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
locked_sessions: Set[str] = set()
zhanghao_cookie_list: Optional[list] = None
duihua_id_to_url_map: Dict[str, str] = {}

def zai_ru_zhanghao_cookie():
    """在启动时从文件加载账号Cookie"""
    global zhanghao_cookie_list
    wenjian_lujing = peizhi.account_cookie
    if os.path.exists(wenjian_lujing):
        try:
            with open(wenjian_lujing, "r", encoding="utf-8") as f:
                zhanghao_cookie_list = json.load(f)
            logger.info(f"成功加载了 {len(zhanghao_cookie_list)} 条Cookie喵~")
        except Exception as e:
            logger.error(f"加载账号Cookie文件失败了喵qwq: {e}")
            zhanghao_cookie_list = None
    else:
        logger.warning(f"没找到账号Cookie文件喵: {wenjian_lujing}")
        zhanghao_cookie_list = None

def zai_ru_duihua_ying_she():
    """在启动时从文件加载对话ID与URL的映射关系"""
    global duihua_id_to_url_map
    wenjian_lujing = peizhi.conversation_mapping_file
    if os.path.exists(wenjian_lujing):
        try:
            with open(wenjian_lujing, "r", encoding="utf-8") as f:
                duihua_id_to_url_map = json.load(f)
            logger.info(f"成功加载了 {len(duihua_id_to_url_map)} 条对话映射喵~")
        except Exception as e:
            logger.error(f"加载对话映射文件失败了喵qwq: {e}")
    else:
        logger.info("没找到对话映射文件，将创建新的喵~")

# 保存对话映射文件
def bao_cun_duihua_ying_she():
    """在关闭时将对话ID与URL的映射关系保存到文件"""
    wenjian_lujing = peizhi.conversation_mapping_file
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(wenjian_lujing), exist_ok=True)
        with open(wenjian_lujing, "w", encoding="utf-8") as f:
            json.dump(duihua_id_to_url_map, f, ensure_ascii=False, indent=4)
        logger.info(f"成功保存了 {len(duihua_id_to_url_map)} 条对话映射喵~")
    except Exception as e:
        logger.error(f"保存对话映射文件失败了喵qwq: {e}")


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
    """规则：判断消息是否来自真实的群聊（排除临时会话）"""
    return (
        event.message_type == "group" and
        hasattr(event, 'group_id') and
        event.user_id != event.group_id
    )

def is_mention_or_reply_to_me(bot: V11Bot, event: V11MessageEvent) -> bool:
    """
    规则：判断消息是否 @机器人 或 回复机器人
    """
    # 检查消息中是否有 @我 的信息
    if event.is_tome():
        return True

    # 检查消息是否回复了我
    if event.reply and event.reply.sender.user_id == int(bot.self_id):
        return True

    return False

def chushihua_liulanqi_jincheng() -> bool:
    """仅同步初始化浏览器进程，不创建标签页"""
    global liulanqi, yichushihua
    try:
        if yichushihua:
          return True
        logger.info("在初始化 Chromium 进程喵ing...")
        co = ChromiumOptions().set_browser_path(peizhi.chromium_path)
        co.set_user_data_path(peizhi.user_data_path)
        if peizhi.proxy:
            logger.info(f"检测到代理配置，正在设置代理喵: {peizhi.proxy}")
            # 使用 set_proxy() 方法传递代理
            co.set_proxy(peizhi.proxy)
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
    mubiao_url = "https://chatgpt.com"
    # 如果开启了持久化，并且映射表中存在该对话ID，则使用已记录的URL
    if peizhi.persist_conversations and duihua_id in duihua_id_to_url_map:
        mubiao_url = duihua_id_to_url_map[duihua_id]
        logger.info(f"找到了持久化的对话URL，正在导航喵: {mubiao_url}")

    try:
        logger.info(f"在给 {duihua_id} 创建新标签页喵ing...")
        biaoqian = liulanqi.new_tab()  # 先创建空白标签页
        # 检查全局变量中是否有已加载的Cookie
        if zhanghao_cookie_list:
            logger.info("检测到Cookie，正在尝试注入喵...")
            try:
                # 使用 set.cookies() 方法注入
                biaoqian.set.cookies(zhanghao_cookie_list)
                logger.info("Cookie注入成功了喵！")
            except Exception as e:
                logger.error(f"Cookie注入失败了喵qwq: {e}")
        logger.info(f"正在导航到 URL: {mubiao_url}")
        biaoqian.get(mubiao_url)  # 使用 get() 方法进行导航
        biaoqian.ele("#prompt-textarea", timeout=peizhi.element_timeout)

        zhuru_js = r"""
          (async () => {
            // 用于最终回复给用户的干净文本
            window.zuihouHuifu = "";
            // 用于调试的完整原始日志
            window.zuihouHuifu_raw_log = "";

            const yuanshiFetch = window.fetch;
            window.fetch = async (...canshu) => {
              const [lianjie, xuanxiang] = canshu;
              if (lianjie.includes('/backend-api/f/conversation') && xuanxiang?.method === 'POST') {
                const fanhui = await yuanshiFetch(...canshu);
                const fuben = fanhui.clone();
                const duzhe = fuben.body.getReader();
                const bianmaqi = new TextDecoder("utf-8");

                // 双轨制
                let quanwen = "";           // 干净文本
                let quanwen_raw = "";       // 原始文本

                let buffer = "";

                // 用于过滤垃圾字符和引用标记的正则表达式
                const garbageRegex = /[\uE000-\uF8FF]|(cite|turn|search|news|academ\w*)(\d*)/g;

                try {
                  while (true) {
                    const { value: zhi, done: wancheng } = await duzhe.read();
                    if (wancheng) break;
                    buffer += bianmaqi.decode(zhi, { stream: true });
                    const hangshu = buffer.split('\n');
                    if (!buffer.endsWith('\n')) buffer = hangshu.pop();
                    else buffer = "";
                    for (const hangRaw of hangshu) {
                      if (!hangRaw || !hangRaw.startsWith('data: ') || hangRaw.includes('[DONE]')) continue;

                      try {
                        const shuju = JSON.parse(hangRaw.replace(/^data:\s*/, ''));
                        let text_piece = '';
                        let text_piece_raw = ''; // 原始片段

                        const operations = shuju.v || (shuju.o === 'patch' ? shuju.v : null);

                        // --- 轨道一：精确提取干净文本 ---
                        if (Array.isArray(operations)) {
                            for (const op of operations) {
                                if (op.o === 'append' && (op.p === '/message/content/parts/0' || op.p === '/message/content/text') && typeof op.v === 'string') {
                                    text_piece += op.v;
                                }
                            }
                        } else if (typeof shuju.v === 'string') {
                            text_piece = shuju.v;
                        }

                        if (text_piece) {
                            const clean_piece = text_piece.replace(garbageRegex, '');
                            if (clean_piece) {
                                quanwen += clean_piece;
                            }
                        }

                        // --- 轨道二：捕获所有文本片段用于调试 ---
                        if (Array.isArray(operations)) {
                          for (const i of operations) {
                            if (i?.o === 'append' && typeof i.v === 'string') {
                              text_piece_raw += i.v;
                            }
                          }
                        } else if (shuju?.v?.message?.content?.parts?.[0]) {
                          text_piece_raw += shuju.v.message.content.parts[0];
                        } else if (typeof shuju?.v === 'string') {
                          text_piece_raw += shuju.v;
                        }

                        if (text_piece_raw) {
                            quanwen_raw += text_piece_raw;
                        }

                        //结束流处理
                        if (shuju?.type === 'message_stream_complete' || shuju?.message?.status === 'finished_successfully') {
                          window.zuihouHuifu = quanwen.trim();
                          window.zuihouHuifu_raw_log = quanwen_raw.trim();
                        }
                      } catch (cuowu) {}
                    }
                  }
                } catch (e) {}

                if (quanwen) {
                  window.zuihouHuifu = quanwen.trim();
                }
                if (quanwen_raw) {
                  window.zuihouHuifu_raw_log = quanwen_raw.trim();
                }

                // 在控制台同时打印干净版和原始版，方便对比
                console.log('最终干净内容:', window.zuihouHuifu);
                console.log('最终原始日志:', window.zuihouHuifu_raw_log);

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
              bianjiqi.innerText = `__CONTENT__`;
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
    if success:
        # 根据配置加载对话映射文件
        if peizhi.persist_conversations:
            zai_ru_duihua_ying_she()

        # 根据配置加载Cookie
        if peizhi.account_cookie:
            zai_ru_zhanghao_cookie()

@qudong.on_shutdown
async def guanbi_gpt():
    if peizhi.persist_conversations:
        bao_cun_duihua_ying_she()
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, guanbi_liulanqi)
    logger.info("已关闭喵~")


async def handle_gpt_request(matcher: Matcher, event: V11MessageEvent, wenti: str):
    """处理GPT请求、获取回答并发送（支持群聊共享模式）"""

    # --- 根据配置决定会话ID ---
    duihua_id: str
    is_real_group = event.message_type == "group" and event.user_id != event.group_id

    if is_real_group and peizhi.group_shared_mode:
        # 如果是真实群聊，并且开启了共享模式，则使用群号作为ID
        duihua_id = f"group_{event.group_id}"
    else:
        # 其他情况（私聊、临时会话、或群聊关闭共享模式），使用原来的会话ID
        duihua_id = event.get_session_id()

    # 检查会话是否已被锁定
    if duihua_id in locked_sessions:
        await matcher.finish("本喵还在思考上一个问题，请稍等一下喵~")
        return

    if not yichushihua:
        await matcher.finish("模块还没就绪喵~")

    # 加锁，并使用 try...finally 确保锁一定会被释放
    try:
        locked_sessions.add(duihua_id)

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            dangqian_biaoqian = await loop.run_in_executor(pool, huoqu_huo_chuangjian_biaoqian, duihua_id)

        if not dangqian_biaoqian:
            await matcher.finish("创建会话失败了喵qwq")

        logger.info(f"要开始为对话 {duihua_id} 处理问题了喵~: {wenti}")
        with concurrent.futures.ThreadPoolExecutor() as pool:
            huida = await loop.run_in_executor(pool, tiwen_gpt, wenti, dangqian_biaoqian)

        logger.info(f"尝试发送喵！: {huida}")

        if huida:
            # 如果开启持久化，则在得到回答后，获取并更新URL
            if peizhi.persist_conversations:
                try:
                    # 在后台线程中执行，不阻塞回复
                    def geng_xin_url_ying_she():
                        current_url = dangqian_biaoqian.run_js("return window.location.href;")
                        # 只有当URL是有效的会话URL时才更新
                        if "/c/" in current_url and duihua_id_to_url_map.get(duihua_id) != current_url:
                            duihua_id_to_url_map[duihua_id] = current_url
                            logger.info(f"为 {duihua_id} 更新/保存了对话URL喵: {current_url}")

                    loop.run_in_executor(None, geng_xin_url_ying_she)
                except Exception as e:
                    logger.warning(f"获取或更新URL失败喵qwq: {e}")

            neirong_liebiao = MessageFormatter.gezhihua_gpt_huida(huida, wenti, zui_da_changdu=peizhi.max_response_length)
            for i, neirong in enumerate(neirong_liebiao):
                if i < len(neirong_liebiao) - 1:
                    await matcher.send(neirong)
                    await asyncio.sleep(1)
                else:
                    await matcher.finish(neirong)
        else:
            await matcher.finish("没能返回有效回答喵qwq")

    except Exception as e:
        logger.error(f"处理失败了喵qwq: {e}")
    finally:
        if duihua_id in locked_sessions:
            locked_sessions.remove(duihua_id)
            logger.info(f"对话 {duihua_id} 的锁已释放喵~")

# 响应器1：处理群聊中的 /gpt 命令
gpt_group = on_command("gpt", rule=is_group_message, priority=10, block=True)

# 响应器2：处理私聊中的所有消息，创建一个新的 Matcher，不需要命令前缀
gpt_private = on_message(rule=is_private_message, priority=99, block=True)

# 响应器3：处理群聊中的 @ 和 回复
gpt_mention = on_message(
    # 使用 Rule() 包装函数后再进行组合
    rule=Rule(is_group_message) & Rule(is_mention_or_reply_to_me),
    priority=12,
    block=True
)

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

@gpt_mention.handle()
async def gpt_mention_handler(matcher: Matcher, bot: V11Bot, event: V11MessageEvent):
    """群聊中 @机器人 或 回复机器人 的处理器"""
    # 提取纯文本消息
    wenti = event.get_plaintext().strip()

    # 清理 @信息获取机器人的所有昵称配置
    nicknames = get_driver().config.nickname
    if isinstance(nicknames, str):
        nicknames = {nicknames}

    # 移除 @昵称 的部分
    for nickname in nicknames:
        if wenti.startswith(f"@{nickname}"):
            wenti = wenti.replace(f"@{nickname}", "", 1).strip()
            break # 找到并移除后就停止

    # 如果清理后问题为空，则不响应
    if not wenti:
        return

    # 调用封装好的核心逻辑
    await handle_gpt_request(matcher, event, wenti)
