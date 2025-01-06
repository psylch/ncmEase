import os
import struct
from typing import Tuple, Optional
from .errors import NCMExtError, NCMMagicHeaderError

class Data:
    """数据结构类"""
    def __init__(self):
        self.length: int = 0
        self.detail: bytes = b''

class NCMFile:
    # 魔数头部常量
    MAGIC_HEADER1 = 0x4e455443
    MAGIC_HEADER2 = 0x4d414446

    def __init__(self, ncm_path: str):
        self.path = os.path.abspath(ncm_path)
        self.file_dir = os.path.dirname(self.path)
        self.file_name = os.path.basename(self.path)
        self.ext = os.path.splitext(self.path)[1]
        self.fd: Optional[int] = None
        self.valid: bool = False
        
        # 数据部分
        self.key = Data()
        self.meta = Data()
        self.cover = Data()
        self.music = Data()
        
        # 打开文件
        self.fd = open(self.path, 'rb')

    def validate(self) -> None:
        """验证文件格式"""
        if self.ext.lower() != '.ncm':
            raise NCMExtError("文件扩展名必须是.ncm")
        
        self.check_header()
        self.valid = True

    def check_header(self) -> None:
        """检查文件魔数头"""
        self.fd.seek(0)
        m1 = struct.unpack('<I', self.fd.read(4))[0]
        m2 = struct.unpack('<I', self.fd.read(4))[0]
        
        if m1 != self.MAGIC_HEADER1 or m2 != self.MAGIC_HEADER2:
            raise NCMMagicHeaderError("文件头不匹配")

    def _get_data(self, offset: int) -> Tuple[bytes, int]:
        """读取数据块"""
        self.fd.seek(offset)
        length = struct.unpack('<I', self.fd.read(4))[0]
        data = self.fd.read(length)
        return data, length

    def get_key(self) -> None:
        """获取密钥数据"""
        data, length = self._get_data(10)  # 4*2 + 2
        self.key.length = length
        self.key.detail = data

    def get_meta(self) -> None:
        """获取元数据"""
        offset = 10 + 4 + self.key.length  # 4*2 + 2 + 4 + key_length
        data, length = self._get_data(offset)
        self.meta.length = length
        self.meta.detail = data

    def get_cover(self) -> None:
        """获取封面数据"""
        offset = 10 + 4 + self.key.length + 4 + self.meta.length + 9
        data, length = self._get_data(offset)
        self.cover.length = length
        self.cover.detail = data

    # def get_music_data(self) -> None:
    #     """获取音乐数据"""
    #     offset = 10 + 4 + self.key.length + 4 + self.meta.length + 9 + 4 + self.cover.length
    #     self.fd.seek(offset)
        
    #     self.music.detail = b''
    #     while True:
    #         chunk = self.fd.read(1024)
    #         if not chunk:
    #             break
    #         self.music.detail += chunk
    #         self.music.length += len(chunk)

    def get_music_data(self) -> None:
        """获取音乐数据"""
        # 计算正确的偏移量
        offset = 10 + 4 + self.key.length + 4 + self.meta.length + 9 + 4 + self.cover.length
        self.fd.seek(offset)
        
        # 使用更高效的方式读取数据
        self.music.detail = bytearray()
        self.music.length = 0
        
        # 获取文件剩余大小
        current_pos = self.fd.tell()
        self.fd.seek(0, 2)  # 移动到文件末尾
        file_size = self.fd.tell()
        remaining_size = file_size - current_pos
        self.fd.seek(current_pos)  # 回到之前的位置

        # 使用固定大小的缓冲区读取
        buffer_size = 8192  # 8KB 缓冲区
        bytes_read = 0
        
        print(f"开始读取音乐数据，总大小约 {remaining_size / 1024 / 1024:.2f} MB")
        
        while bytes_read < remaining_size:
            chunk_size = min(buffer_size, remaining_size - bytes_read)
            chunk = self.fd.read(chunk_size)
            if not chunk:
                break
            
            self.music.detail.extend(chunk)
            bytes_read += len(chunk)
            
            # 打印进度
            if bytes_read % (1024 * 1024) < buffer_size:  # 每读取1MB打印一次
                print(f"已读取: {bytes_read / 1024 / 1024:.2f} MB / {remaining_size / 1024 / 1024:.2f} MB")
        
        self.music.length = bytes_read
        print(f"音乐数据读取完成，总大小: {self.music.length / 1024 / 1024:.2f} MB")

    def parse(self) -> None:
        """解析整个NCM文件"""
        try:
            self.validate()
            self.get_key()
            self.get_meta()
            self.get_cover()
            self.get_music_data()
        except Exception as e:
            raise Exception(f"解析NCM文件失败: {str(e)}")

    def close(self) -> None:
        """关闭文件"""
        if self.fd:
            self.fd.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()