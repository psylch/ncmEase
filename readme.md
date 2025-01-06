# NCM Music Converter & Organizer

一个用于转换和整理网易云音乐 NCM 文件的 Python 工具。
其中NCM文件转换相关代码是在[ncmdump](https://github.com/taurusxin/ncmdump.git)基础上修改的

## 功能特点

- 将 NCM 文件转换为原始音频格式（FLAC/MP3）
- 保留音乐标签信息（标题、艺术家、专辑、封面等）
- 自动整理多人合作歌曲的文件夹结构
- 支持批量处理
- 多线程并行处理
- 进度显示和详细日志输出

## 安装

1. 克隆仓库：
```bash
git clone [repository_url]
cd ncm-converter
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```python
python main.py
```

默认会处理指定目录下的所有 NCM 文件。

### 文件夹结构处理

工具会自动处理以下情况：

原始结构：
```
音乐人1,音乐人2/专辑/歌曲.ncm
音乐人1/专辑/歌曲2.ncm
音乐人1/专辑/歌曲3.ncm
```

处理后：
```
音乐人1/专辑/歌曲.flac
音乐人1/专辑/歌曲2.flac
音乐人1/专辑/歌曲3.flac
```

### 配置选项

在 `main.py` 中可以修改以下参数：

```python
merge_album_folders(
    music_root,        # 音乐文件根目录
    convert_ncm=True,  # 是否转换NCM文件
    max_workers=4      # 并行处理的线程数
)
```

## 依赖项

- pycryptodome: NCM 文件解密
- numpy: 数据处理
- tqdm: 进度条显示
- mutagen: 音频标签处理
- requests: 下载封面图片
- pillow: 图片处理

## 注意事项

1. 确保有足够的磁盘空间（FLAC 文件通常比 NCM 文件大）
2. 建议先备份重要文件
3. 转换过程中请勿移动或删除源文件
4. 程序会自动删除处理完成的 NCM 文件
5. 程序会自动删除空文件夹
## 常见问题

1. **Q: 转换后的文件在哪里？**  
   A: 转换后的文件会保存在原 NCM 文件的相同目录下，但扩展名改为 .flac 或 .mp3

2. **Q: 为什么有些文件转换失败？**  
   A: 可能是文件损坏或格式不正确，程序会保留原始 NCM 文件以供检查

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

[MIT License](LICENSE)
