# PDF 批量翻译工具 - 技术方案设计

## 项目目标

开发一个自动化工具,批量翻译目录下的英文 PDF 论文为中文,解决以下问题:
1. 避免长文本翻译中断和内容遗漏
2. 自动拼接翻译结果
3. 保持原文格式、公式、图片
4. 批量处理,无需人工干预

## 技术架构

### 核心模块

1. **PDF 解析模块** (`pdf_parser.py`)
   - 提取文本内容(按段落/章节分块)
   - 识别和保留公式(LaTeX 格式)
   - 提取图片和位置信息
   - 保存文档结构元数据

2. **翻译引擎模块** (`translator.py`)
   - 支持 DeepSeek API 调用
   - 智能分块翻译(避免超长文本)
   - 错误重试机制
   - 翻译进度跟踪

3. **PDF 生成模块** (`pdf_generator.py`)
   - 根据翻译结果重建 PDF
   - 保持原始布局和格式
   - 嵌入图片和公式
   - 字体和样式处理

4. **批量处理模块** (`batch_processor.py`)
   - 扫描目录下所有 PDF 文件
   - 并发/顺序处理控制
   - 进度显示和日志记录
   - 错误处理和恢复

## 技术选型

### PDF 处理
- **PyMuPDF (fitz)**: 高性能 PDF 解析和生成
- **pdfplumber**: 文本提取和布局分析
- **reportlab**: PDF 生成备用方案

### AI API 集成
- **OpenAI 兼容接口**: 支持 DeepSeek-V3 等模型
- **请求库**: requests / openai SDK

### 文本处理
- **正则表达式**: 识别 LaTeX 公式
- **markdown**: 保持文档结构

## 关键技术难点及解决方案

### 1. 格式保留策略

**问题**: PDF 格式复杂,完美保留原始布局非常困难

**解决方案**:
- **方案 A (推荐)**: 双层 PDF 方法
  - 保留原始 PDF 作为背景图层
  - 在上层覆盖翻译后的文本
  - 优点: 完美保留格式
  - 缺点: 文件较大,文本不可完全编辑

- **方案 B**: 结构化重建
  - 提取文本、样式、布局信息
  - 翻译后按原结构重新生成
  - 优点: 文件小,可编辑
  - 缺点: 复杂布局可能失真

**实施**: 优先实现方案 B,提供方案 A 作为选项

### 2. 长文本分块翻译

**问题**: AI API 有 token 限制,长论文需要分块处理

**解决方案**:
- 按段落/章节智能分块(每块 2000-3000 词)
- 保持上下文连贯性(前一块的最后一段作为下一块的上下文)
- 翻译时保留公式、引用等特殊标记

### 3. 公式和图片处理

**公式处理**:
- 识别 LaTeX 公式或数学符号密集区域
- 翻译时标记为 `[FORMULA_N]` 占位符
- 生成 PDF 时还原公式

**图片处理**:
- 提取图片及位置信息
- 翻译时跳过图片
- 生成 PDF 时在相同位置插入原图

### 4. API 调用优化

- 实现指数退避重试机制
- 并发控制(避免 API 限流)
- 缓存已翻译内容(断点续传)
- 成本估算和进度显示

## 配置文件设计

```json
{
  "api": {
    "provider": "deepseek",
    "model": "deepseek-chat",
    "api_key": "YOUR_API_KEY",
    "base_url": "https://api.deepseek.com/v1",
    "max_tokens": 4000,
    "temperature": 0.3
  },
  "translation": {
    "source_lang": "en",
    "target_lang": "zh",
    "chunk_size": 2500,
    "preserve_formulas": true,
    "preserve_images": true
  },
  "output": {
    "suffix": "_chn",
    "format": "pdf",
    "keep_original_layout": true
  },
  "processing": {
    "max_concurrent": 3,
    "retry_times": 3,
    "cache_enabled": true
  }
}
```

## 使用流程

1. 配置 API Key 和参数
2. 运行命令: `python translate_pdfs.py /path/to/pdfs/`
3. 工具自动扫描并翻译所有 PDF
4. 翻译结果保存为 `原文件名_chn.pdf`
5. 生成日志文件记录处理详情

## 下一步实施计划

1. 开发核心翻译引擎
2. 实现 PDF 解析功能
3. 实现 PDF 生成功能
4. 集成批量处理逻辑
5. 测试和优化

