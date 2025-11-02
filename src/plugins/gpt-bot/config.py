from enum import Enum
from pydantic import BaseModel
from typing import Optional
import os

class MergeForwardMode(str, Enum):
    """合并转发模式"""
    auto = "auto"
    always = "always"
    never = "never"


class Config(BaseModel):

    chromium_path: str = "/usr/bin/chromium"
    user_data_path: str = os.path.expanduser("~/.config/chromium")

    # 等待页面元素加载的超时时间
    element_timeout: int = 20
    # 等待ChatGPT生成回答的超时时间
    response_timeout: int = 70

    # 单条消息的最大长度（用于自动分段）
    max_response_length: int = 2000

    # 群聊共享模式：True=群内共用会话, False=群内每人独立会话
    group_shared_mode: bool = True

    # 对话持久化功能
    persist_conversations: bool = True
    # 持久化文件路径
    conversation_mapping_file: str = "data/gpt_duihua.json"
    # 透明代理配置 格式: "protocol://ip:port"
    proxy: Optional[str] = None
    # 账号配置cookie
    account_cookie: str = "data/zhanghao_cookies.json"

    # 合并转发配置
    merge_forward_mode: MergeForwardMode = MergeForwardMode.auto
    merge_forward_threshold: int = 1500
    merge_forward_nickname: str = "ChatGPT"
