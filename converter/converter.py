import json
import base64
import math
from io import BytesIO
from dataclasses import dataclass
from typing import List, Optional
import numpy as np

from .utils import decrypt_aes128, build_key_box, process_chunk
from ncm.ncm import NCMFile

# 密钥常量
AES_CORE_KEY = bytes([0x68, 0x7A, 0x48, 0x52, 0x41, 0x6D, 0x73, 0x6F, 0x35, 0x6B, 0x49, 0x6E, 0x62, 0x61, 0x78, 0x57])
AES_MODIFY_KEY = bytes([0x23, 0x31, 0x34, 0x6C, 0x6A, 0x6B, 0x5F, 0x21, 0x5C, 0x5D, 0x26, 0x30, 0x55, 0x3C, 0x27, 0x28])

@dataclass
class Artist:
    name: str
    id: float
    
    @classmethod
    def from_json(cls, data: list) -> 'Artist':
        return cls(name=data[0], id=data[1])

@dataclass
class Album:
    id: float
    name: str
    cover_url: str
    
    def to_json(self) -> str:
        return json.dumps({
            'albumId': self.id,
            'album': self.name,
            'albumPic': self.cover_url
        })

@dataclass
class Meta:
    id: float
    name: str
    album: Optional[Album]
    artists: List[Artist]
    bit_rate: float
    duration: float
    format: str
    comment: str = ''
    
    def to_json(self) -> str:
        return json.dumps({
            'musicId': self.id,
            'musicName': self.name,
            'artist': [[a.name, a.id] for a in self.artists],
            'bitrate': self.bit_rate,
            'duration': self.duration,
            'format': self.format
        })

class Converter:
    def __init__(self, ncm_file: NCMFile):
        self.ncm_file = ncm_file
        self.key_data: Optional[bytes] = None
        self.meta_data: Optional[Meta] = None
        self.music_data: Optional[bytes] = None
        
    def handle_key(self) -> None:
        """处理密钥数据"""
        tmp = bytes(b ^ 0x64 for b in self.ncm_file.key.detail)
        
        decrypted_data = decrypt_aes128(AES_CORE_KEY, tmp)
        self.key_data = decrypted_data  # 不再切片，保留完整密钥
        
    def handle_meta(self) -> None:
        """处理元数据"""
        if self.ncm_file.meta.length <= 0:
            # 处理没有元数据的情况
            format_type = "flac"
            if self.ncm_file.fd.tell() < 16 * 1024 * 1024:  # 16MB
                format_type = "mp3"
            self.meta_data = Meta(
                id=0, name="", album=None, 
                artists=[], bit_rate=0, 
                duration=0, format=format_type
            )
            return

        # 解密元数据
        tmp = bytes(b ^ 0x63 for b in self.ncm_file.meta.detail)
        
        # 跳过 "163 key(Don't modify):" (22字节)
        b64_data = tmp[22:]
        decoded_data = base64.b64decode(b64_data)
        
        decrypted_data = decrypt_aes128(AES_MODIFY_KEY, decoded_data)
        # 跳过 "music:" (6字节)
        json_data = json.loads(decrypted_data[6:])
        
        # 解析数据
        album = Album(
            id=json_data.get('albumId', 0),
            name=json_data.get('album', ''),
            cover_url=json_data.get('albumPic', '')
        )
        
        self.meta_data = Meta(
            id=json_data.get('musicId', 0),
            name=json_data.get('musicName', ''),
            album=album,
            artists=[Artist.from_json(a) for a in json_data.get('artist', [])],
            bit_rate=json_data.get('bitrate', 0),
            duration=json_data.get('duration', 0),
            format=json_data.get('format', ''),
            comment=tmp.decode('utf-8', errors='ignore')
        )

    def handle_music(self) -> None:
        """处理音乐数据"""
        if not self.key_data:
            self.handle_key()
            
        # 使用完整密钥的后半部分构建密钥盒
        box = np.array(build_key_box(self.key_data[17:]), dtype=np.uint8)
        n = 0x8000  # 32KB 缓冲区
        result = bytearray()
        
        # 将音乐数据转换为 numpy 数组进行处理
        data = BytesIO(self.ncm_file.music.detail)
        
        while True:
            chunk = data.read(n)
            if not chunk:
                break
            
            # 使用 Numba 加速的函数处理数据块
            chunk_array = np.frombuffer(chunk, dtype=np.uint8)
            processed = process_chunk(chunk_array, box)
            result.extend(processed)
        
        self.music_data = bytes(result)
        
    def handle_all(self) -> None:
        """处理所有数据"""
        self.handle_key()
        self.handle_meta()
        self.handle_music()
