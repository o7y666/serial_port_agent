"""
Claude API 客户端封装
"""
from anthropic import Anthropic
from anthropic.types import Message
from .config import ANTHROPIC_API_KEY, DEFAULT_MODEL


def _get_first_text(response: Message) -> str:
    """从 Claude 响应中提取第一个文本块的内容"""
    for block in response.content:
        # 跳过 ThinkingBlock (扩展思考)
        if hasattr(block, 'thinking'):
            continue
        # 直接检查类型名包含 "Text"
        if type(block).__name__.endswith('TextBlock'):
            return block.text.strip()
    return ""


class LLMClient:
    """Claude API 客户端"""

    def __init__(self, api_key: str = None, model: str = None):
        """
        初始化 LLM 客户端

        Args:
            api_key: Anthropic API Key，默认从环境变量读取
            model: 使用的模型，默认 claude-opus-4-6
        """
        self.client = Anthropic(api_key=api_key or ANTHROPIC_API_KEY)
        self.model = model or DEFAULT_MODEL

    def generate_at_command(self, user_request: str) -> str:
        """
        根据用户需求生成 AT 指令

        Args:
            user_request: 用户用自然语言描述的需求

        Returns:
            str: 生成的 AT 指令
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=64,
            system="你是一个串口通信助手。用户用自然语言描述需求，你只返回一个 AT 指令字符串，不要任何解释，不要任何多余文字。例如用户说\"开灯\"，你只返回：AT+LED=ON",
            messages=[
                {"role": "user", "content": user_request}
            ]
        )
        return _get_first_text(response)

    def analyze_response(self, mcu_response: str, original_request: str) -> str:
        """
        分析 MCU 响应，判断指令是否执行成功

        Args:
            mcu_response: MCU 返回的原始响应
            original_request: 用户的原始需求

        Returns:
            str: 分析结果（中文说明）
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[
                {"role": "user", "content": f"原始请求: {original_request}\nMCU响应: {mcu_response}\n请判断是否成功并给出简洁的中文说明。"}
            ]
        )
        return _get_first_text(response)