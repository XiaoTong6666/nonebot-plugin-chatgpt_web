from pydantic import BaseModel
from typing import Optional
import os


class Config(BaseModel):
    """GPT Bot Plugin Config - 增强调试版本"""

    # Chromium浏览器路径
    chromium_path: str = "/usr/bin/chromium"

    # 用户数据目录
    user_data_path: str = os.path.expanduser("~/.config/chromium")

    # 是否在启动时自动初始化
    auto_init_on_startup: bool = True

    # 超时时间设置
    page_load_timeout: int = 30
    element_timeout: int = 10
    response_timeout: int = 60

    # 响应长度限制
    max_response_length: int = 2000
    max_question_length: int = 500

    # 重试配置
    max_retries: int = 3
    retry_delay: int = 5

    # 浏览器配置
    headless: bool = False
    debug: bool = True  # 默认开启调试模式

    # 浏览器窗口大小
    window_width: int = 1920
    window_height: int = 1080

    # 用户代理
    user_agent: Optional[str] = None

    # 代理设置
    proxy: Optional[str] = None

    # 新增调试选项
    verbose_logging: bool = True  # 详细日志
    save_screenshots: bool = True  # 保存截图用于调试
    console_output: bool = True  # 输出浏览器控制台信息

    # 群聊共享模式开关
    # 如果设置为 True，则一个群内的所有人共用一个ChatGPT会话（标签页）
    # 如果设置为 False，则群内的每个人都有自己独立的会话（标签页）
    group_shared_mode: bool = True

    # 对话持久化功能
    persist_conversations: bool = True
    conversation_mapping_file: str = "data/gpt_duihua.json"
