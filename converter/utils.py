from Crypto.Cipher import AES
from numba import njit
import numpy as np

def decrypt_aes128(key: bytes, data: bytes) -> bytes:
    """AES-128 ECB模式解密"""
    # 确保数据长度是16的倍数
    data = data[:(len(data) // AES.block_size) * AES.block_size]
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_data = cipher.decrypt(data)
    
    # 处理PKCS7 padding
    padding_length = decrypted_data[-1]
    return decrypted_data[:-padding_length]

def build_key_box(key: bytes) -> bytearray:
    """构建密钥盒"""
    box = bytearray(range(256))
    key_len = len(key)
    c = 0
    last_byte = 0
    key_offset = 0
    
    for i in range(256):
        c = (box[i] + last_byte + key[key_offset]) & 0xff
        key_offset += 1
        if key_offset >= key_len:
            key_offset = 0
        box[i], box[c] = box[c], box[i]
        last_byte = c
    
    return box

@njit
def process_chunk(chunk: np.ndarray, box: np.ndarray) -> np.ndarray:
    """使用 Numba 加速的数据块处理"""
    result = np.empty_like(chunk)
    for i in range(len(chunk)):
        j = (i + 1) & 0xff
        result[i] = chunk[i] ^ box[(box[j] + box[(box[j] + j) & 0xff]) & 0xff]
    return result
