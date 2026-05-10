"""
串口通信模块 - 最小化版本
"""
import serial
import serial.tools.list_ports


class SerialPort:
    """串口通信类 - 最小化实现"""

    def __init__(self, port: str = None, baudrate: int = 115200, timeout: float = 0.2):
        """
        初始化串口参数

        Args:
            port: 串口号，如 'COM1' 或 '/dev/ttyUSB0'
            baudrate: 波特率，默认 115200
            timeout: 读超时时间（秒），默认 0.2
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._ser = None

    def open(self) -> bool:
        """
        打开串口

        Returns:
            bool: 打开成功返回 True
        """
        if self._ser and self._ser.is_open:
            return True

        try:
            self._ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
            )
            return True
        except serial.SerialException as e:
            print(f"打开串口失败: {e}")
            return False

    def close(self):
        """关闭串口"""
        if self._ser:
            try:
                self._ser.close()
            except:
                pass
            self._ser = None

    def write(self, data: bytes) -> int:
        """
        发送数据

        Args:
            data: 要发送的字节数据

        Returns:
            int: 发送的字节数
        """
        if not self.is_open():
            raise serial.SerialException("串口未打开")
        return self._ser.write(data)

    def is_open(self) -> bool:
        """检查串口是否打开"""
        return self._ser is not None and self._ser.is_open

    @staticmethod
    def list_ports() -> list:
        """
        列出所有可用串口

        Returns:
            list: 可用串口信息列表，每个元素为 (端口名, 描述, 硬件ID)
        """
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append((port.device, port.description, port.hwid))
        return ports
