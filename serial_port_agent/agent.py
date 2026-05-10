"""
Serial Agent - AI 指令生成与执行
"""
import time
from .serial_port import SerialPort
from .llm_client import LLMClient
from .config import DEFAULT_TIMEOUT


class SerialAgent:
    """串口 AI 代理"""

    def __init__(self, serial_port: SerialPort, llm_client: LLMClient):
        """
        初始化 Agent

        Args:
            serial_port: SerialPort 实例
            llm_client: LLMClient 实例
        """
        self.serial = serial_port
        self.llm = llm_client

    def execute(self, user_request: str, timeout: float = None) -> str:
        """
        执行用户请求

        Args:
            user_request: 用户用自然语言描述的需求
            timeout: 等待 MCU 响应的超时时间（秒）

        Returns:
            str: 执行结果（成功/失败说明）
        """
        if timeout is None:
            timeout = DEFAULT_TIMEOUT

        # 检查串口是否打开
        if not self.serial.is_open():
            return "错误: 串口未打开，请先使用 open 命令"

        # 1. 生成 AT 指令
        at_cmd = self.llm.generate_at_command(user_request)
        if not at_cmd:
            return "错误: 无法生成有效指令"

        # 2. 发送指令
        print(f"发送: {at_cmd}")
        self.serial.write((at_cmd + "\r\n").encode('utf-8'))

        # 3. 等待响应
        response = self._wait_response(timeout)

        # 4. 分析响应
        result = self.llm.analyze_response(response, user_request)
        return result

    def _wait_response(self, timeout: float) -> str:
        """
        等待 MCU 响应

        Args:
            timeout: 超时时间（秒）

        Returns:
            str: MCU 响应内容
        """
        start = time.time()
        buffer = b""

        while time.time() - start < timeout:
            if self.serial._ser.in_waiting > 0:
                data = self.serial._ser.read(self.serial._ser.in_waiting)
                buffer += data
                # 尝试解码
                try:
                    text = buffer.decode('utf-8', errors='replace')
                    # 检查是否接收完整（换行符结尾）
                    if '\r\n' in text or '\n' in text:
                        return text.strip()
                except:
                    pass
            time.sleep(0.01)

        # 超时后返回已接收的内容
        if buffer:
            return buffer.decode('utf-8', errors='replace').strip()
        return "超时无响应"