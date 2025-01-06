#!/usr/bin/env python3
import argparse
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional
from pathlib import Path

from ncm.ncm import NCMFile
from converter.converter import Converter
from tag.tag import create_tagger, tag_audio_file
from path.path_utils import clean, join, base, dir_path

class NCMConverter:
    def __init__(self):
        self.version = "0.1.0"
        self.thread_pool: Optional[ThreadPoolExecutor] = None
    
    def convert_file(self, file_path: str, output_dir: str, add_tags: bool = True) -> None:
        """转换单个NCM文件"""
        try:
            print(f"开始转换: {file_path}")
            
            # 使用上下文管理器处理NCM文件
            with NCMFile(file_path) as ncm_file:
                ncm_file.parse()
                
                # 转换
                converter = Converter(ncm_file)
                converter.handle_all()
                
                # 处理输出路径
                if not output_dir:
                    output_dir = dir_path(file_path)
                    
                file_name = base(file_path).replace('.ncm', '')
                output_path = join(output_dir, f"{file_name}.{converter.meta_data.format}")
                
                # 确保输出目录存在
                os.makedirs(dir_path(output_path), exist_ok=True)
                
                # 写入文件
                print(f"写入文件: {output_path}")
                with open(output_path, 'wb') as f:
                    f.write(converter.music_data)
                
                # 添加标签
                if add_tags and converter.meta_data:
                    try:
                        print(f"添加标签: {output_path}")
                        tagger = create_tagger(output_path, converter.meta_data.format)
                        tag_audio_file(tagger, ncm_file.cover.detail, converter.meta_data)
                    except Exception as tag_error:
                        print(f"添加标签失败: {str(tag_error)}")
                        print("继续保留已转换的音频文件...")
                
            print(f"转换完成: {output_path}")
                
        except Exception as e:
            print(f"转换文件失败 {file_path}: {str(e)}")

    def find_ncm_files(self, directory: str, depth: int) -> List[str]:
        """递归查找NCM文件"""
        if depth <= 0:
            return []
            
        result = []
        try:
            for entry in os.scandir(directory):
                if entry.is_file() and entry.name.lower().endswith('.ncm'):
                    result.append(clean(entry.path))
                elif entry.is_dir() and depth > 1:
                    result.extend(self.find_ncm_files(entry.path, depth - 1))
        except Exception as e:
            print(f"查找目录失败 {directory}: {str(e)}")
            
        return result

    def process_path(self, path: str, depth: int) -> List[str]:
        """处理输入路径，返回所有需要处理的文件"""
        path = clean(path)
        if os.path.isfile(path):
            return [path] if path.lower().endswith('.ncm') else []
        elif os.path.isdir(path):
            return self.find_ncm_files(path, depth)
        return []

    def run(self, args: argparse.Namespace) -> None:
        """主运行函数"""
        print(f"NCM转换器 v{self.version}")
        print(f"线程数: {args.thread}")
        
        # 处理输出目录
        if args.output:
            os.makedirs(args.output, exist_ok=True)
        
        # 收集所有需要处理的文件
        all_files = []
        for input_path in args.input:
            files = self.process_path(input_path, args.depth)
            all_files.extend(files)
            
        if not all_files:
            print("未找到NCM文件")
            return
            
        print(f"找到 {len(all_files)} 个NCM文件")
        
        # 使用线程池处理文件
        with ThreadPoolExecutor(max_workers=args.thread) as self.thread_pool:
            futures = [
                self.thread_pool.submit(
                    self.convert_file,
                    file_path,
                    args.output,
                    args.tag
                )
                for file_path in all_files
            ]
            
            # 等待所有任务完成
            for _ in futures:
                _.result()
        
        print("所有文件处理完成")

def main():
    parser = argparse.ArgumentParser(description='NCM音乐格式转换器')
    parser.add_argument('input', nargs='+', help='输入文件或目录路径')
    parser.add_argument('-o', '--output', default='', help='输出目录')
    parser.add_argument('-t', '--tag', action='store_true', default=True, help='是否添加音乐标签')
    parser.add_argument('-d', '--depth', type=int, default=5, help='查找文件的最大深度 (默认: 5)')
    parser.add_argument('-n', '--thread', type=int, default=4, help='最大线程数 (默认: 4)')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {NCMConverter().version}')
    
    args = parser.parse_args()
    
    try:
        converter = NCMConverter()
        converter.run(args)
    except KeyboardInterrupt:
        print("\n转换已取消")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == '__main__':
    main()