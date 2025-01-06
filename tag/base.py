from abc import ABC, abstractmethod
from typing import List

class Tagger(ABC):
    """标签处理基类"""
    
    @abstractmethod
    def set_cover(self, cover: bytes, mime: str) -> None:
        """设置封面图片"""
        pass
        
    @abstractmethod
    def set_cover_url(self, cover_url: str) -> None:
        """设置封面图片URL"""
        pass
        
    @abstractmethod
    def set_title(self, title: str) -> None:
        """设置标题"""
        pass
        
    @abstractmethod
    def set_album(self, album: str) -> None:
        """设置专辑名"""
        pass
        
    @abstractmethod
    def set_artist(self, artists: List[str]) -> None:
        """设置艺术家"""
        pass
        
    @abstractmethod
    def set_comment(self, comment: str) -> None:
        """设置评论"""
        pass
        
    @abstractmethod
    def save(self) -> None:
        """保存更改"""
        pass
