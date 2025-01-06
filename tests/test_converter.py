import os
import sys
import pytest
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# 获取测试文件的绝对路径
TEST_DIR = Path(__file__).parent
TEST_FILE = TEST_DIR / "files" / "test.ncm"

# 修改导入路径
from ncm.ncm import NCMFile
from converter.converter import Converter

@pytest.fixture(scope="session")
def ncm_file():
    """整个测试会话只创建一次 NCMFile 实例"""
    if not TEST_FILE.exists():
        pytest.skip(f"测试文件不存在: {TEST_FILE}")
    ncm = NCMFile(str(TEST_FILE))
    ncm.parse()  # 预先解析
    return ncm

@pytest.fixture(scope="session")
def converter(ncm_file):
    """整个测试会话只创建一次 Converter 实例"""
    return Converter(ncm_file)

def test_handle_key(converter):
    converter.handle_key()
    assert converter.key_data is not None
    print(f"Key data length: {len(converter.key_data)}")

def test_handle_meta(converter):
    converter.handle_meta()
    assert converter.meta_data is not None
    if converter.meta_data:
        print(f"Music name: {converter.meta_data.name}")
        print(f"Format: {converter.meta_data.format}")

def test_handle_music(converter):
    converter.handle_music()
    assert converter.music_data is not None
    assert len(converter.music_data) > 0
    
    # 使用正确的扩展名
    ext = converter.meta_data.format.lower() if converter.meta_data else 'mp3'
    output_path = TEST_DIR / "files" / f"output.{ext}"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, "wb") as f:
        f.write(converter.music_data)
    assert output_path.exists()
    print(f"已保存音乐文件到: {output_path}")
    print(f"文件大小: {len(converter.music_data) / (1024*1024):.2f} MB")

def test_handle_all(converter):
    converter.handle_all()
    assert converter.key_data is not None
    assert converter.meta_data is not None
    assert converter.music_data is not None
