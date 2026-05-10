"""
配置管理模块
从 .env 文件加载环境变量
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件（优先查找当前目录，再查找上级目录）
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Claude API 配置
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
DEFAULT_MODEL = "claude-opus-4-6"

# 串口配置
DEFAULT_BAUDRATE = 115200
DEFAULT_TIMEOUT = 3.0  # MCU 响应超时（秒）