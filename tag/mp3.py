from mutagen.id3 import ID3, APIC, TIT2, TALB, TPE1, COMM
from .base import Tagger
from typing import List

class MP3Tagger(Tagger):
    def __init__(self, path: str):
        try:
            self.tag = ID3(path)
        except:
            self.tag = ID3()
            
    def set_cover(self, cover: bytes, mime: str) -> None:
        self.tag.add(
            APIC(
                encoding=3,
                mime=mime,
                type=3,  # 3 是封面图片
                desc='Cover',
                data=cover
            )
        )
        
    def set_cover_url(self, cover_url: str) -> None:
        self.tag.add(
            APIC(
                encoding=3,
                mime='-->',
                type=3,
                desc='Cover',
                data=cover_url.encode()
            )
        )
        
    def set_title(self, title: str) -> None:
        self.tag.add(TIT2(encoding=3, text=title))
        
    def set_album(self, album: str) -> None:
        self.tag.add(TALB(encoding=3, text=album))
        
    def set_artist(self, artists: List[str]) -> None:
        self.tag.add(TPE1(encoding=3, text=artists))
        
    def set_comment(self, comment: str) -> None:
        self.tag.add(COMM(encoding=3, lang='XXX', desc='', text=comment))
        
    def save(self) -> None:
        self.tag.save()
