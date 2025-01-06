from pathlib import Path
from typing import List, Union

def clean(path: Union[str, Path]) -> str:
    """规范化路径字符串"""
    return str(Path(path).resolve())

def join(*paths: Union[str, Path]) -> str:
    """连接路径"""
    return str(Path(*paths))

def base(path: Union[str, Path]) -> str:
    """返回路径的最后一个部分"""
    return Path(path).name

def ext(path: Union[str, Path]) -> str:
    """返回文件扩展名"""
    return Path(path).suffix

def dir_path(path: Union[str, Path]) -> str:
    """返回路径的目录部分"""
    return str(Path(path).parent)

# 使用示例：
if __name__ == "__main__":
    # 清理路径
    print(clean("./folder/../test.txt"))  # 输出规范化的路径
    
    # 连接路径
    print(join("folder", "subfolder", "file.txt"))  # 使用系统适当的分隔符连接
    
    # 获取文件名
    print(base("/path/to/file.txt"))  # 输出: file.txt
    
    # 获取扩展名
    print(ext("file.txt"))  # 输出: .txt
    
    # 获取目录
    print(dir_path("/path/to/file.txt"))  # 输出: /path/to
