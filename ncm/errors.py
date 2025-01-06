class NCMError(Exception):
    """NCM基础异常类"""
    pass

class NCMFormatError(NCMError):
    """文件不是NCM格式"""
    pass

class NCMExtError(NCMError):
    """文件扩展名不是.ncm"""
    pass

class NCMMagicHeaderError(NCMError):
    """文件头不匹配"""
    pass