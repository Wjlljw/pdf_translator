# PDF 批量翻译工具

一个强大的 Python 工具，用于批量翻译英文 PDF 论文为中文，支持 AI 驱动的高质量翻译，自动处理长文档，保留格式和公式。

## 功能特点

✅ **批量处理** - 自动扫描目录下所有 PDF 文件并批量翻译  
✅ **智能分块** - 自动将长文档分块处理，避免 AI token 限制  
✅ **上下文保持** - 分块翻译时保持上下文连贯性  
✅ **格式保留** - 尽可能保留原文档的标题、段落结构  
✅ **公式保护** - 识别并保留 LaTeX 数学公式  
✅ **断点续传** - 支持缓存机制，翻译中断可继续  
✅ **进度跟踪** - 实时显示翻译进度和日志记录  
✅ **错误重试** - 自动重试失败的 API 调用  
✅ **多 API 支持** - 支持 DeepSeek、OpenAI 等兼容 API

## 系统要求

- Python 3.8+
- 操作系统：Linux / macOS / Windows
- 依赖库：PyMuPDF, pdfplumber, openai, reportlab

## 安装步骤

### 1. 克隆或下载项目

```bash
cd /path/to/your/workspace
# 如果已有项目文件，直接进入目录
cd pdf_translator
```

### 2. 安装依赖

```bash
pip install pymupdf pdfplumber openai reportlab python-dotenv
```

### 3. 安装中文字体（Linux）

```bash
sudo apt-get update
sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei
```

macOS 和 Windows 通常已包含中文字体，无需额外安装。

## 配置说明

### 配置文件：`config.json`

在使用前，需要配置 API 密钥和翻译参数：

```json
{
  "api": {
    "provider": "deepseek",
    "model": "deepseek-chat",
    "api_key": "YOUR_API_KEY_HERE",
    "base_url": "https://api.deepseek.com",
    "max_tokens": 4000,
    "temperature": 0.3
  },
  "translation": {
    "source_lang": "en",
    "target_lang": "zh",
    "chunk_size": 2500,
    "preserve_formulas": true,
    "preserve_images": true,
    "context_overlap": 200
  },
  "output": {
    "suffix": "_chn",
    "format": "pdf",
    "keep_original_layout": true
  },
  "processing": {
    "max_concurrent": 1,
    "retry_times": 3,
    "retry_delay": 2,
    "cache_enabled": true
  }
}
```

### 配置项说明

#### API 配置 (`api`)

- **provider**: API 提供商（`deepseek` / `openai`）
- **model**: 使用的模型名称
  - DeepSeek: `deepseek-chat`
  - OpenAI: `gpt-4`, `gpt-3.5-turbo` 等
- **api_key**: API 密钥（必填）
- **base_url**: API 基础 URL
  - DeepSeek: `https://api.deepseek.com`
  - OpenAI: 留空或 `https://api.openai.com/v1`
- **max_tokens**: 最大生成 token 数
- **temperature**: 生成温度（0-1，越低越确定）

#### 翻译配置 (`translation`)

- **source_lang**: 源语言代码（`en` = 英文）
- **target_lang**: 目标语言代码（`zh` = 中文）
- **chunk_size**: 每个文本块的最大字符数
- **preserve_formulas**: 是否保留数学公式
- **preserve_images**: 是否保留图片
- **context_overlap**: 块之间的上下文重叠字符数

#### 输出配置 (`output`)

- **suffix**: 输出文件名后缀（默认 `_chn`）
- **format**: 输出格式（目前仅支持 `pdf`）
- **keep_original_layout**: 是否尽量保持原始布局

#### 处理配置 (`processing`)

- **max_concurrent**: 最大并发处理数（建议设为 1）
- **retry_times**: API 调用失败重试次数
- **retry_delay**: 重试延迟（秒）
- **cache_enabled**: 是否启用缓存

### 环境变量方式配置（推荐）

为了安全，建议使用环境变量配置 API Key：

```bash
# 使用 DeepSeek
export DEEPSEEK_API_KEY="your_deepseek_api_key"

# 或使用 OpenAI
export OPENAI_API_KEY="your_openai_api_key"
```

## 使用方法

### 基本用法

```bash
python translate_pdfs.py <PDF目录路径>
```

### 示例

#### 1. 翻译当前目录下的所有 PDF

```bash
python translate_pdfs.py ./papers/
```

#### 2. 递归翻译子目录中的 PDF

```bash
python translate_pdfs.py ./papers/ -r
```

#### 3. 使用自定义配置文件

```bash
python translate_pdfs.py ./papers/ -c my_config.json
```

#### 4. 完整示例

```bash
# 设置 API Key
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxx"

# 翻译指定目录
python translate_pdfs.py ~/Documents/research_papers/ -r

# 翻译结果将保存为：
# 原文件: paper1.pdf → 翻译: paper1_chn.pdf
# 原文件: paper2.pdf → 翻译: paper2_chn.pdf
```

### 命令行参数

```
usage: translate_pdfs.py [-h] [-r] [-c CONFIG] [-v] directory

批量翻译 PDF 论文工具

positional arguments:
  directory             包含 PDF 文件的目录路径

optional arguments:
  -h, --help            显示帮助信息
  -r, --recursive       递归处理子目录中的 PDF 文件
  -c CONFIG, --config CONFIG
                        配置文件路径 (默认: config.json)
  -v, --version         显示版本信息
```

## 工作流程

1. **扫描目录** - 查找所有 PDF 文件（跳过已翻译的 `*_chn.pdf`）
2. **提取文本** - 使用 pdfplumber 和 PyMuPDF 提取文本内容
3. **智能分块** - 按段落和大小将文本分成多个块
4. **调用 AI 翻译** - 逐块调用 AI API 进行翻译
5. **生成 PDF** - 将翻译结果生成新的 PDF 文件
6. **保存日志** - 记录处理过程和结果

## 输出说明

### 文件命名

- 原文件：`research_paper.pdf`
- 翻译文件：`research_paper_chn.pdf`（默认后缀 `_chn`）

### 日志文件

每次运行会在目标目录生成日志文件：

```
translation_log_20231023_143022.txt
```

日志内容包括：
- 处理的文件列表
- 成功/失败状态
- 错误信息
- 处理时间

### 缓存机制

翻译结果会缓存在 `.cache/` 目录下，如果翻译中断，重新运行时会自动使用缓存，避免重复翻译。

## 常见问题

### 1. API Key 配置问题

**问题**: `ValueError: 未配置 API Key`

**解决方案**:
```bash
# 方法 1: 环境变量
export DEEPSEEK_API_KEY="your_key"

# 方法 2: 配置文件
# 在 config.json 中设置 api.api_key
```

### 2. 中文字体显示问题

**问题**: 生成的 PDF 中文显示为方框

**解决方案**:
```bash
# Linux
sudo apt-get install fonts-wqy-microhei

# macOS (通常无需操作)
# Windows (通常无需操作)
```

### 3. 翻译质量不佳

**解决方案**:
- 调整 `temperature` 参数（降低到 0.1-0.3）
- 使用更强大的模型（如 GPT-4）
- 减小 `chunk_size` 以提供更多上下文

### 4. API 调用超时

**解决方案**:
- 检查网络连接
- 增加 `retry_times` 和 `retry_delay`
- 减小 `chunk_size` 降低单次请求大小

### 5. 内存不足

**问题**: 处理大型 PDF 时内存溢出

**解决方案**:
- 减小 `chunk_size`
- 关闭缓存 (`cache_enabled: false`)
- 分批处理文件

## 技术架构

### 核心模块

```
pdf_translator/
├── src/
│   ├── pdf_parser.py       # PDF 解析模块
│   ├── translator.py       # AI 翻译引擎
│   ├── pdf_generator.py    # PDF 生成模块
│   └── batch_processor.py  # 批量处理器
├── translate_pdfs.py       # 主程序入口
├── config.json             # 配置文件
└── README.md               # 使用文档
```

### 技术栈

- **PDF 处理**: PyMuPDF (fitz), pdfplumber
- **AI 集成**: OpenAI SDK (兼容 DeepSeek)
- **PDF 生成**: ReportLab
- **文本处理**: 正则表达式、自然段落分割

## 性能优化建议

### 1. 并发处理

虽然支持并发，但建议设置 `max_concurrent: 1` 以避免 API 限流。

### 2. 缓存策略

启用缓存可以显著减少重复翻译的成本和时间。

### 3. 分块大小

- 较小的块（1500-2000）：更精确，但调用次数多
- 较大的块（3000-4000）：更快，但可能超出 token 限制

### 4. 成本估算

以 DeepSeek 为例：
- 输入：¥0.001 / 1K tokens
- 输出：¥0.002 / 1K tokens
- 一篇 10 页论文约 5000 词，成本约 ¥0.05-0.10

## 限制与注意事项

### 当前限制

1. **格式保留**: 复杂的表格和多栏布局可能无法完美保留
2. **图片处理**: 图片中的文字不会被翻译
3. **公式识别**: 仅支持 LaTeX 格式的公式识别
4. **扫描版 PDF**: 不支持扫描版 PDF（需要 OCR）

### 使用建议

1. **备份原文件**: 翻译前建议备份原始 PDF
2. **检查结果**: 翻译后应人工检查关键内容
3. **专业术语**: 对于特定领域，可能需要人工校对术语翻译
4. **版权注意**: 仅用于个人学习研究，不得用于商业用途

## 高级用法

### 自定义翻译提示词

编辑 `src/translator.py` 中的 `_build_system_prompt()` 方法，可以自定义翻译风格和要求。

### 支持其他语言

修改 `config.json` 中的 `source_lang` 和 `target_lang`：

```json
{
  "translation": {
    "source_lang": "en",
    "target_lang": "ja"  // 翻译为日文
  }
}
```

### 集成到工作流

```bash
# 定时任务示例（每天凌晨翻译新论文）
0 0 * * * cd /path/to/pdf_translator && python translate_pdfs.py ~/papers/ >> cron.log 2>&1
```

## 故障排除

### 调试模式

如果遇到问题，可以查看详细错误信息：

```bash
python translate_pdfs.py ./papers/ 2>&1 | tee debug.log
```

### 测试单个模块

```bash
# 测试 PDF 解析
python src/pdf_parser.py test.pdf

# 测试翻译器
python src/translator.py

# 测试 PDF 生成
python src/pdf_generator.py
```

## 更新日志

### v1.0.0 (2024-10-23)

- ✨ 首次发布
- ✅ 支持批量 PDF 翻译
- ✅ 智能文本分块
- ✅ 公式和格式保留
- ✅ 缓存和断点续传
- ✅ 支持 DeepSeek 和 OpenAI API

## 贡献指南

欢迎提交问题报告和改进建议！

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件

---

**祝您使用愉快！Happy Translating! 📚✨**

