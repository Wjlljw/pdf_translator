# 快速开始指南

## 5 分钟快速上手

### 第一步：安装依赖

```bash
pip install pymupdf pdfplumber openai reportlab python-dotenv
```

### 第二步：配置 API Key

选择以下任一方式：

**方式 1：环境变量（推荐）**

```bash
export DEEPSEEK_API_KEY="sk-your-api-key-here"
```

**方式 2：配置文件**

编辑 `config.json`，填入你的 API Key：

```json
{
  "api": {
    "api_key": "sk-your-api-key-here"
  }
}
```

### 第三步：准备 PDF 文件

将要翻译的英文 PDF 论文放入一个目录，例如：

```
papers/
├── paper1.pdf
├── paper2.pdf
└── paper3.pdf
```

### 第四步：运行翻译

```bash
python translate_pdfs.py papers/
```

### 第五步：查看结果

翻译完成后，在同一目录下会生成中文版本：

```
papers/
├── paper1.pdf
├── paper1_chn.pdf  ← 翻译结果
├── paper2.pdf
├── paper2_chn.pdf  ← 翻译结果
├── paper3.pdf
└── paper3_chn.pdf  ← 翻译结果
```

## 常用命令

```bash
# 翻译当前目录
python translate_pdfs.py ./

# 翻译指定目录
python translate_pdfs.py ~/Documents/papers/

# 递归翻译子目录
python translate_pdfs.py ~/Documents/papers/ -r

# 使用自定义配置
python translate_pdfs.py papers/ -c my_config.json
```

## 获取 DeepSeek API Key

1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册账号并登录
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制 Key 并配置到工具中

## 示例输出

```
============================================================
PDF 批量翻译工具 v1.0.0
============================================================
目录: papers/
递归: 否
配置: config.json
============================================================

找到 3 个 PDF 文件

============================================================
处理文件 [1/3]: papers/paper1.pdf
============================================================
步骤 1/4: 提取文本...
  提取了 5432 个字符
步骤 2/4: 文本分块...
  分成 3 个块
步骤 3/4: 翻译中...
  进度: 1/3 (33.3%)
  进度: 2/3 (66.7%)
  进度: 3/3 (100.0%)
步骤 4/4: 生成 PDF...
完成! 用时: 15.23 秒
输出文件: papers/paper1_chn.pdf
✓ 成功翻译: papers/paper1.pdf

============================================================
处理完成
============================================================
成功: 3/3
失败: 0/3
```

## 下一步

- 查看完整文档：[README.md](README.md)
- 调整配置参数以优化翻译质量
- 查看生成的日志文件了解详细信息

## 遇到问题？

**问题 1：找不到 API Key**

```bash
# 确保环境变量已设置
echo $DEEPSEEK_API_KEY

# 或检查配置文件
cat config.json | grep api_key
```

**问题 2：翻译失败**

检查：
- 网络连接是否正常
- API Key 是否有效
- 是否有足够的 API 额度

**问题 3：中文显示异常**

```bash
# Linux 安装中文字体
sudo apt-get install fonts-wqy-microhei
```

更多问题请查看 [README.md](README.md) 的"常见问题"章节。

