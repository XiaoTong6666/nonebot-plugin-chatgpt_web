"""消息格式化工具"""

import re
from typing import Optional, Union
from nonebot.adapters import Message, MessageSegment


class MessageFormatter:
    """消息格式化器"""

    @staticmethod
    def gezhihua_gpt_huida(huida: str, wenti: str = "", zui_da_changdu: int = 2000) -> str:
        """
        格式化GPT响应消息

        Args:
            huida: GPT的原始响应
            wenti: 用户的问题
            zui_da_changdu: 最大消息长度

        Returns:
            格式化后的消息
        """
        if not huida or not huida.strip():
            return "❌ ChatGPT未返回有效回答"

        # 清理响应文本
        qingli_huida = MessageFormatter._qingli_huida(huida)

        # 如果响应过长，进行智能截断
        if len(qingli_huida) > zui_da_changdu:
            qingli_huida = MessageFormatter._zhineng_jieduan(qingli_huida, zui_da_changdu)

        return qingli_huida

    @staticmethod
    def _qingli_huida(huida: str) -> str:
        """清理响应文本"""
        qingli = re.sub(r'\n\s*\n\s*\n', '\n\n', huida)
        qingli = qingli.strip()
        if qingli.startswith('"') and qingli.endswith('"'):
            qingli = qingli[1:-1].strip()
        return qingli

    @staticmethod
    def _zhineng_jieduan(wenzi: str, zui_da_changdu: int) -> str:
        """智能截断文本，尽量在句子边界截断"""
        if len(wenzi) <= zui_da_changdu:
            return wenzi

        jieduan_tishi = "\n\n...(回答过长，已截断)"
        kexy_changdu = zui_da_changdu - len(jieduan_tishi)
        if kexy_changdu <= 0:
            return wenzi[:zui_da_changdu]

        duan_wenzi = wenzi[:kexy_changdu]
        jiezhi_fuhao = ['.', '。', '!', '！', '?', '？', '\n\n']
        zuijia_qie = -1

        for fuhao in jiezhi_fuhao:
            pos = duan_wenzi.rfind(fuhao)
            if pos > kexy_changdu * 0.7:
                zuijia_qie = max(zuijia_qie, pos + 1)

        if zuijia_qie > 0:
            return wenzi[:zuijia_qie].rstrip() + jieduan_tishi
        else:
            last_space = duan_wenzi.rfind(' ')
            if last_space > kexy_changdu * 0.8:
                return wenzi[:last_space] + jieduan_tishi
            else:
                return duan_wenzi + jieduan_tishi

    @staticmethod
    def gezhihua_cuowu_xiaoxi(cuowu_leixing: str, xiangqing: str = "") -> str:
        """格式化错误消息"""
        cuowu_dict = {
            "init_failed": "ChatGPT初始化失败",
            "connection_lost": "ChatGPT连接断开",
            "timeout": "ChatGPT响应超时",
            "invalid_question": "问题格式无效",
            "question_too_long": "问题过长",
            "no_response": "ChatGPT未返回回答",
            "network_error": "网络连接出错",
            "login_required": "需要登录ChatGPT账号",
            "unknown": "未知错误"
        }

        base_msg = cuowu_dict.get(cuowu_leixing, cuowu_dict["unknown"])
        if xiangqing:
            return f"{base_msg}\n详情：{xiangqing}"
        else:
            return base_msg

    @staticmethod
    def gezhihua_zhuangtai_xiaoxi(zhuangtai: str, xiangqing: dict = None) -> str:
        """格式化状态消息"""
        emoji_dict = {
            "initializing": "🚀",
            "ready": "🟢",
            "connecting": "🔄",
            "error": "🔴",
            "offline": "⚫"
        }

        biao_qing = emoji_dict.get(zhuangtai, "ℹ️")

        if zhuangtai == "ready":
            msg = f"{biao_qing} ChatGPT连接正常"
        elif zhuangtai == "initializing":
            msg = f"{biao_qing} ChatGPT正在初始化..."
        elif zhuangtai == "connecting":
            msg = f"{biao_qing} ChatGPT正在连接..."
        elif zhuangtai == "error":
            msg = f"{biao_qing} ChatGPT连接异常"
        elif zhuangtai == "offline":
            msg = f"{biao_qing} ChatGPT离线"
        else:
            msg = f"{biao_qing} ChatGPT状态：{zhuangtai}"

        if xiangqing:
            line_list = []
            if "browser_status" in xiangqing:
                line_list.append(f"浏览器：{xiangqing['browser_status']}")
            if "page_status" in xiangqing:
                line_list.append(f"页面：{xiangqing['page_status']}")
            if "last_activity" in xiangqing:
                line_list.append(f"最后活动：{xiangqing['last_activity']}")
            if line_list:
                msg += "\n" + "\n".join(line_list)

        return msg

    @staticmethod
    def chuangjian_bangzhu_xiaoxi() -> str:
        """创建帮助消息"""
        return """ChatGPT Bot 使用指南

基本命令：
/gpt <问题> - 向ChatGPT提问
/gpt_status - 检查连接状态
/gpt_restart - 重启连接
"""
