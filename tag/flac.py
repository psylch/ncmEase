from mutagen.flac import FLAC, Picture
from .base import Tagger
from typing import List

class FLACTagger(Tagger):
    def __init__(self, path: str):
        self.tag = FLAC(path)
            
    def set_cover(self, cover: bytes, mime: str) -> None:
        picture = Picture()
        picture.type = 3  # 封面图片
        picture.mime = mime
        picture.desc = 'Cover'
        picture.data = cover
        
        self.tag.add_picture(picture)
        
    def set_cover_url(self, cover_url: str) -> None:
        picture = Picture()
        picture.type = 3
        picture.mime = '-->'
        picture.desc = 'Cover'
        picture.data = cover_url.encode()
        
        self.tag.add_picture(picture)
        
    def set_title(self, title: str) -> None:
        self.tag['title'] = title
        
    def set_album(self, album: str) -> None:
        self.tag['album'] = album
        
    def set_artist(self, artists: List[str]) -> None:
        self.tag['artist'] = artists
        
    def set_comment(self, comment: str) -> None:
        self.tag['comment'] = comment
        
    def save(self) -> None:
        self.tag.save()
