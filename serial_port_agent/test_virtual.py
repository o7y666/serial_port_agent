"""
虚拟串口测试
使用 pyserial 的 Radio Rear_COM 接口创建虚拟串口对进行测试
"""
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from .serial_port import SerialPort
import threading
import time


def test_virtual_ports():
    """测试虚拟串口配对"""

    # 在 Windows 上可以使用 com0com 或 Virtual Serial Port Driver
    # 这里演示如何创建和使用虚拟串口

    print("虚拟串口测试需要以下条件之一:")
    print("1. Windows: 安装 com0com 或 Virtual Serial Port Driver")
    print("2. Linux: 使用 socat 创建虚拟串口对")
    print()
    print("Linux 创建虚拟串口对示例:")
    print("  socat -d -d pty,raw,echo=0,link=/tmp/virtual0 pty,raw,echo=0,link=/tmp/virtual1")
    print()
    print("=" * 60)
    print("如果你已经创建了虚拟串口对，可以使用以下命令测试:")
    print("  python -m serial_port_agent.cli")
    print("=" * 60)

    # 列出实际可用的串口
    print("\n当前系统可用的串口:")
    ports = SerialPort.list_ports()
    if ports:
        for port, desc, hwid in ports:
            print(f"  {port}: {desc}")
    else:
        print("  没有找到串口")


def loopback_test(port1: str, port2: str):
    """
    回环测试 - 需要两个串口互相连接

    Args:
        port1: 第一个串口
        port2: 第二个串口
    """
    print(f"回环测试: {port1} <-> {port2}")

    received = threading.Event()
    received_data = []

    def recv_callback(data):
        received_data.append(data)
        received.set()

    # 打开两个串口
    ser1 = SerialPort(port=port1, baudrate=115200)
    ser2 = SerialPort(port=port2, baudrate=115200)

    if not ser1.open() or not ser2.open():
        print("无法打开串口")
        return

    # 启动接收线程
    ser1.start_recv(recv_callback)

    # 发送测试数据
    test_data = b"Hello Serial Port!"
    print(f"发送: {test_data}")
    ser2.write(test_data)

    # 等待接收
    if received.wait(timeout=2):
        print(f"收到: {received_data[0]}")
        if received_data[0] == test_data:
            print("回环测试成功!")
        else:
            print("数据不匹配")
    else:
        print("接收超时")

    # 清理
    ser1.close()
    ser2.close()


if __name__ == '__main__':
    test_virtual_ports()
