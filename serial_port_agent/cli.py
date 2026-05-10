"""
命令行交互界面
"""
import sys
import threading
import time
from typing import Optional
from .serial_port import SerialPort


class SerialCLI:
    """串口命令行交互界面"""

    def __init__(self):
        self.serial: Optional[SerialPort] = None
        self.running = False
        self.local_echo = True
        self._recv_thread = None
        self._running_recv = False

    def print_ports(self):
        """打印所有可用串口"""
        ports = SerialPort.list_ports()
        if not ports:
            print("没有找到可用的串口")
            return

        print(f"\n找到 {len(ports)} 个串口:")
        print("-" * 60)
        for port, desc, hwid in ports:
            print(f"  {port:10} - {desc}")
            print(f"             HWID: {hwid}")
        print("-" * 60)

    def cmd_open(self, args):
        """打开串口"""
        if len(args) < 1:
            print("用法: open <串口号> [波特率]")
            return

        port = args[0]
        baudrate = int(args[1]) if len(args) > 1 else 115200

        if self.serial:
            self.serial.close()

        self.serial = SerialPort(port=port, baudrate=baudrate, timeout=0.2)

        if self.serial.open():
            print(f"成功打开串口 {port} @ {baudrate} bps")
            self._start_recv()
        else:
            print(f"打开串口 {port} 失败")
            self.serial = None

    def _start_recv(self):
        """启动接收线程（轮询方式）"""
        self._running_recv = True
        self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def _recv_loop(self):
        """接收数据循环"""
        while self._running_recv:
            try:
                if self.serial and self.serial.is_open():
                    num = self.serial._ser.in_waiting
                    if num > 0:
                        data = self.serial._ser.read(num)
                        self._on_recv(data)
                time.sleep(0.01)
            except Exception as e:
                if self._running_recv:
                    print(f"\n接收出错: {e}")
                break

    def _on_recv(self, data: bytes):
        """收到数据的处理"""
        try:
            text = data.decode('utf-8', errors='replace')
            print(f"\r收到: {text}", end='', flush=True)
            if self.local_echo:
                print("> ", end='', flush=True)
        except:
            print(f"\r收到 (HEX): {data.hex(' ').upper()}", end='', flush=True)
            if self.local_echo:
                print("> ", end='', flush=True)

    def cmd_close(self, args):
        """关闭串口"""
        self._running_recv = False
        if self._recv_thread and self._recv_thread.is_alive():
            self._recv_thread.join(timeout=1)
        self._recv_thread = None

        if self.serial:
            self.serial.close()
            print("串口已关闭")
            self.serial = None
        else:
            print("串口未打开")

    def cmd_send(self, args):
        """发送数据"""
        if not self.serial or not self.serial.is_open():
            print("串口未打开")
            return

        if len(args) < 1:
            print("用法: send <字符串>")
            return

        data = ' '.join(args)
        self.serial.write((data + '\r\n').encode('utf-8'))
        print(f"发送: {data}")

    def cmd_send_hex(self, args):
        """发送十六进制数据"""
        if not self.serial or not self.serial.is_open():
            print("串口未打开")
            return

        if len(args) < 1:
            print("用法: sendhex <十六进制数据> (如: 01 02 03 0A)")
            return

        hex_str = ''.join(args).replace(' ', '')
        try:
            data = bytes.fromhex(hex_str)
            self.serial.write(data)
            print(f"发送十六进制: {data.hex(' ').upper()}")
        except ValueError:
            print("无效的十六进制数据")

    def cmd_list(self, args):
        """列出串口"""
        self.print_ports()

    def cmd_status(self, args):
        """查看状态"""
        if self.serial and self.serial.is_open():
            print(f"串口状态: 已打开")
            print(f"  端口: {self.serial.port}")
            print(f"  波特率: {self.serial.baudrate}")
        else:
            print("串口状态: 未打开")

    def cmd_help(self, args):
        """显示帮助"""
        print("\n可用命令:")
        print("  list                - 列出所有可用串口")
        print("  open <port> [baud]  - 打开串口 (如: open COM1 115200)")
        print("  close               - 关闭串口")
        print("  send <string>       - 发送字符串")
        print("  sendhex <hex>       - 发送十六进制数据 (如: sendhex 01 02 0A)")
        print("  status              - 查看串口状态")
        print("  echo on|off         - 开启/关闭本地回显")
        print("  help                - 显示此帮助")
        print("  quit                - 退出程序")
        print()

    def cmd_echo(self, args):
        """设置回显"""
        if len(args) < 1:
            print(f"本地回显: {'开启' if self.local_echo else '关闭'}")
            return

        if args[0].lower() == 'on':
            self.local_echo = True
            print("本地回显已开启")
        elif args[0].lower() == 'off':
            self.local_echo = False
            print("本地回显已关闭")
        else:
            print("用法: echo on|off")

    def cmd_quit(self, args):
        """退出"""
        self.running = False
        self._running_recv = False
        if self._recv_thread and self._recv_thread.is_alive():
            self._recv_thread.join(timeout=1)
        if self.serial:
            self.serial.close()
        print("退出程序")

    def run(self):
        """运行命令行界面"""
        self.running = True
        print("=" * 60)
        print("串口助手 CLI - 输入 help 查看可用命令")
        print("=" * 60)

        self.cmd_list([])

        while self.running:
            try:
                if self.local_echo:
                    print("> ", end='', flush=True)

                cmd = input()
                if not cmd.strip():
                    continue

                parts = cmd.split()
                command = parts[0].lower()
                args = parts[1:]

                if command == 'list':
                    self.cmd_list(args)
                elif command == 'open':
                    self.cmd_open(args)
                elif command == 'close':
                    self.cmd_close(args)
                elif command == 'send':
                    self.cmd_send(args)
                elif command == 'sendhex':
                    self.cmd_send_hex(args)
                elif command == 'status':
                    self.cmd_status(args)
                elif command == 'echo':
                    self.cmd_echo(args)
                elif command == 'help':
                    self.cmd_help(args)
                elif command == 'quit' or command == 'exit':
                    self.cmd_quit(args)
                    break
                else:
                    print(f"未知命令: {command}，输入 help 查看可用命令")

            except KeyboardInterrupt:
                print("\nCtrl+C 退出...")
                self.cmd_quit([])
                break
            except Exception as e:
                print(f"错误: {e}")


def main():
    cli = SerialCLI()
    cli.run()


if __name__ == '__main__':
    main()
