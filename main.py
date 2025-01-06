import os
import sys
import shutil
from pathlib import Path
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from core import NCMConverter

# 设置控制台输出编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def remove_empty_dirs(path: str) -> None:
    """递归删除空文件夹"""
    try:
        for dirpath in sorted(Path(path).glob('**/*'), reverse=True):
            if dirpath.is_dir():
                try:
                    if not any(dirpath.iterdir()):
                        print(f"删除空文件夹: {dirpath}")
                        dirpath.rmdir()
                except Exception as e:
                    print(f"删除文件夹失败 {dirpath}: {e}")
    except Exception as e:
        print(f"清理空文件夹时出错: {e}")

def process_single_file(file_path: Path, root_dir: Path, ncm_converter: Optional[NCMConverter]) -> None:
    """处理单个文件"""
    try:
        # 获取相对路径
        rel_path = file_path.relative_to(root_dir)
        parts = rel_path.parts
        
        # 检查路径格式
        if len(parts) < 3:
            print(f"跳过不符合格式的文件: {file_path}")
            return
        
        # 确定是否需要移动文件
        needs_move = ',' in parts[0]
        target_path = file_path
        
        if needs_move:
            # 获取第一个艺术家名称
            main_artist = parts[0].split(',')[0]
            target_path = root_dir / main_artist / parts[1] / parts[2]
            
            # 确保目标目录存在
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 处理文件名冲突
            if target_path.exists() and target_path != file_path:
                stem = target_path.stem
                suffix = target_path.suffix
                counter = 1
                while target_path.exists():
                    target_path = target_path.with_name(f"{stem}_{counter}{suffix}")
                    counter += 1
        
        # 如果是NCM文件，进行转换
        if ncm_converter and file_path.suffix.lower() == '.ncm':
            try:
                print(f"\n转换文件: {file_path}")
                
                # 转换文件
                ncm_converter.convert_file(
                    file_path=str(file_path),
                    output_dir=str(target_path.parent),
                    add_tags=True
                )
                
                # 检查转换后的文件
                expected_flac = file_path.with_suffix('.flac')
                if expected_flac.exists():
                    print(f"转换成功: {expected_flac}")
                    # 删除原NCM文件
                    file_path.unlink()
                    print(f"已删除原文件: {file_path}")
                else:
                    print(f"警告: 未找到转换后的文件: {expected_flac}")
                    
            except Exception as e:
                print(f"转换失败 {file_path}: {e}")
                return
        
        # 如果需要移动且文件还存在（转换失败的情况）
        if needs_move and file_path.exists() and target_path != file_path:
            print(f"移动文件: {file_path} -> {target_path}")
            shutil.move(str(file_path), str(target_path))
        
        # 如果发生了移动，尝试删除空目录
        if needs_move:
            try:
                old_dir = file_path.parent
                if old_dir.exists() and not any(old_dir.iterdir()):
                    print(f"删除空目录: {old_dir}")
                    old_dir.rmdir()
            except Exception as e:
                print(f"删除空目录失败 {old_dir}: {e}")
                
    except Exception as e:
        print(f"处理文件失败 {file_path}: {e}")

def collect_ncm_files(root_dir: Path) -> List[Path]:
    """收集所有需要处理的NCM文件"""
    try:
        return list(root_dir.rglob('*.ncm'))
    except Exception as e:
        print(f"Collect Files Failed: {e}")
        return []

def merge_album_folders(root_dir: str, convert_ncm: bool = True, max_workers: int = 4) -> None:
    """
    合并同一专辑下的所有歌曲到主艺术家文件夹，并可选择性地转换NCM文件
    """
    root_path = Path(root_dir)
    if not root_path.exists():
        print(f"目录不存在: {root_dir}")
        return
        
    # 创建NCM转换器实例
    ncm_converter = NCMConverter() if convert_ncm else None
    
    # 收集所有NCM文件
    print("扫描文件中...")
    all_files = collect_ncm_files(root_path)
    
    if not all_files:
        print("未找到NCM文件")
        return
        
    print(f"找到 {len(all_files)} 个NCM文件")
    
    # 使用线程池处理文件
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 使用tqdm显示进度
        list(tqdm(
            executor.map(
                lambda f: process_single_file(f, root_path, ncm_converter),
                all_files
            ),
            total=len(all_files),
            desc="处理文件中"
        ))
    
    # 最后清理空文件夹
    print("清理空文件夹...")
    remove_empty_dirs(root_dir)
    print("处理完成!")

if __name__ == "__main__":
    try:
        # 在这里指定你的音乐文件根目录
        music_root = r"D:\CloudMusic\tets"
        
        # 合并文件夹并转换NCM文件
        merge_album_folders(
            music_root,
            convert_ncm=True,
            max_workers=4
        )
    except KeyboardInterrupt:
        print("\n操作已取消")
    except Exception as e:
        print(f"程序执行出错: {e}")