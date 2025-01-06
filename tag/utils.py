import requests
from typing import Optional
from PIL import Image
from io import BytesIO

def fetch_url(url: str, timeout: int = 30) -> Optional[bytes]:
    """从URL获取数据"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"下载封面图片失败: {e}")
        return None

def is_png(data: bytes) -> bool:
    """检查是否为PNG格式"""
    PNG_HEADER = b'\x89PNG\r\n\x1a\n'
    return data[:8] == PNG_HEADER if len(data) >= 8 else False

def get_image_mime(data: bytes) -> str:
    """获取图片MIME类型"""
    try:
        image = Image.open(BytesIO(data))
        return f"image/{image.format.lower()}"
    except:
        return "image/jpeg"  # 默认返回JPEG
