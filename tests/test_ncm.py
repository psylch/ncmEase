import os
import pytest
from ncm.ncm import NCMFile
from ncm.errors import NCMExtError, NCMMagicHeaderError
import time

# 获取测试文件的绝对路径
TEST_FILE = os.path.join(os.path.dirname(__file__), 'files', 'test.ncm')

def test_ncm_basic():
    """测试基本的 NCM 文件操作"""
    assert os.path.exists(TEST_FILE), "测试文件不存在"
    
    ncm = NCMFile(TEST_FILE)
    try:
        # 测试文件头验证
        ncm.validate()
        assert ncm.valid == True
        print("✓ 文件头验证通过")
        
        # 测试密钥获取
        ncm.get_key()
        assert ncm.key.length > 0
        assert len(ncm.key.detail) > 0
        print(f"✓ 成功获取密钥，长度: {ncm.key.length}")
        
        # 测试元数据获取
        ncm.get_meta()
        assert ncm.meta.length > 0
        assert len(ncm.meta.detail) > 0
        print(f"✓ 成功获取元数据，长度: {ncm.meta.length}")
        
        # 测试封面获取
        ncm.get_cover()
        assert ncm.cover.length > 0
        assert len(ncm.cover.detail) > 0
        print(f"✓ 成功获取封面，长度: {ncm.cover.length}")
        
        # 测试音乐数据获取
        ncm.get_music_data()
        assert ncm.music.length > 0
        assert len(ncm.music.detail) > 0
        print(f"✓ 成功获取音乐数据，长度: {ncm.music.length}")
        
    finally:
        ncm.close()

def test_invalid_extension():
    """测试无效的文件扩展名"""
    # 创建一个临时的非 NCM 文件
    test_file = "tests/files/test.txt"
    with open(test_file, "w") as f:
        f.write("This is not a NCM file")
    
    try:
        with pytest.raises(NCMExtError):
            NCMFile(test_file).validate()
        print("✓ 成功检测到无效的文件扩展名")
    finally:
        os.remove(test_file)

def test_invalid_magic_header():
    """测试无效的文件魔数"""
    # 创建一个假的 NCM 文件
    fake_ncm = "tests/files/fake.ncm"
    
    # 确保目录存在
    os.makedirs(os.path.dirname(fake_ncm), exist_ok=True)
    
    try:
        # 创建测试文件
        with open(fake_ncm, "wb") as f:
            f.write(b"This is not a valid NCM file")
        
        # 测试文件验证
        ncm = None
        with pytest.raises(NCMMagicHeaderError):
            ncm = NCMFile(fake_ncm)
            ncm.validate()
        
        # 确保文件被关闭
        if ncm:
            ncm.close()
            
        print("✓ 成功检测到无效的文件魔数")
    
    finally:
        # 等待一小段时间确保文件被完全关闭
        time.sleep(0.1)
        
        # 尝试多次删除文件
        for _ in range(3):
            try:
                if os.path.exists(fake_ncm):
                    os.close(os.open(fake_ncm, os.O_RDONLY))  # 确保文件句柄被关闭
                    os.remove(fake_ncm)
                break
            except PermissionError:
                time.sleep(0.1)

def test_complete_parse():
    """测试完整的解析流程"""
    with NCMFile(TEST_FILE) as ncm:
        ncm.parse()
        assert ncm.valid
        assert ncm.key.length > 0
        assert ncm.meta.length > 0
        assert ncm.cover.length > 0
        assert ncm.music.length > 0
        print("✓ 完整解析流程测试通过")