from typing import Optional
from .base import Tagger
from .mp3 import MP3Tagger
from .flac import FLACTagger
from .utils import fetch_url, get_image_mime
from converter.converter import Meta

class TaggingError(Exception):
    """标签处理错误"""
    pass

def create_tagger(path: str, format: str) -> Tagger:
    """创建对应格式的标签处理器"""
    format = format.lower()
    if format == 'mp3':
        return MP3Tagger(path)
    elif format == 'flac':
        return FLACTagger(path)
    else:
        raise TaggingError(f"不支持的格式: {format}")

def tag_audio_file(tagger: Tagger, img_data: Optional[bytes], meta: Meta) -> None:
    """处理音频文件标签"""
    try:
        # 处理封面图片
        if img_data and len(img_data) > 0:  # 确保有封面数据
            mime = get_image_mime(img_data)
            print(f"添加封面图片: {mime}, 大小: {len(img_data)/1024:.1f}KB")
            tagger.set_cover(img_data, mime)
        elif meta.album and meta.album.cover_url:
            print(f"从URL下载封面: {meta.album.cover_url}")
            img_data = fetch_url(meta.album.cover_url)
            if img_data:
                mime = get_image_mime(img_data)
                print(f"添加下载的封面: {mime}, 大小: {len(img_data)/1024:.1f}KB")
                tagger.set_cover(img_data, mime)
            else:
                print("封面下载失败，使用URL作为封面链接")
                tagger.set_cover_url(meta.album.cover_url)
        
        # 设置其他标签
        if meta.name:
            tagger.set_title(meta.name)
            
        if meta.album and meta.album.name:
            tagger.set_album(meta.album.name)
            
        if meta.artists:
            artist_names = [artist.name for artist in meta.artists]
            tagger.set_artist(artist_names)
            
        if meta.comment:
            tagger.set_comment(meta.comment)
            
        tagger.save()
        print("标签添加完成")
        
    except Exception as e:
        print(f"添加标签时出错: {str(e)}")
        raise
