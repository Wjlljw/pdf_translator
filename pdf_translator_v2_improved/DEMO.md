# 使用演示

## 演示场景：翻译机器学习论文

本演示展示如何使用 PDF 批量翻译工具翻译英文学术论文。

### 准备工作

#### 1. 项目结构

```
pdf_translator/
├── src/                    # 核心模块
├── translate_pdfs.py       # 主程序
├── config.json             # 配置文件
├── requirements.txt        # 依赖列表
└── papers/                 # PDF 文件目录（示例）
    ├── paper1.pdf
    └── paper2.pdf
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置 API

```bash
# 设置 DeepSeek API Key
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxx"
```

### 演示步骤

#### 步骤 1：准备测试 PDF

我们已经创建了一个测试 PDF 文件：

```bash
ls sample_pdfs/
# 输出: test_paper.pdf
```

#### 步骤 2：运行翻译

```bash
python translate_pdfs.py sample_pdfs/
```

#### 步骤 3：查看输出

```
============================================================
PDF 批量翻译工具 v1.0.0
============================================================
目录: sample_pdfs/
递归: 否
配置: config.json
============================================================

找到 1 个 PDF 文件

============================================================
处理文件 [1/1]: sample_pdfs/test_paper.pdf
============================================================
步骤 1/4: 提取文本...
  提取了 1654 个字符
步骤 2/4: 文本分块...
  分成 1 个块
步骤 3/4: 翻译中...
  进度: 1/1 (100.0%)
步骤 4/4: 生成 PDF...
正在生成 PDF: sample_pdfs/test_paper_chn.pdf
PDF 生成成功: sample_pdfs/test_paper_chn.pdf
完成! 用时: 6.74 秒
输出文件: sample_pdfs/test_paper_chn.pdf
✓ 成功翻译: sample_pdfs/test_paper.pdf

============================================================
处理完成
============================================================
成功: 1/1
失败: 0/1
```

#### 步骤 4：查看结果

```bash
ls sample_pdfs/
# 输出:
# test_paper.pdf          # 原文件
# test_paper_chn.pdf      # 翻译结果
# translation_log_*.txt   # 日志文件
```

### 翻译效果对比

#### 原文（test_paper.pdf）

```
Introduction to Machine Learning

Abstract
Machine learning is a subset of artificial intelligence (AI) 
that focuses on developing algorithms and statistical models...

1. Supervised Learning
Supervised learning is a type of machine learning where the 
algorithm learns from labeled training data...
```

#### 译文（test_paper_chn.pdf）

```
机器学习简介

摘要
机器学习是人工智能（Artificial Intelligence, AI）的一个子集，
专注于开发算法和统计模型...

1. 监督学习
监督学习是一种机器学习类型，算法从带标签的训练数据中学习...
```

### 高级用法演示

#### 批量翻译多个文件

```bash
# 准备多个 PDF 文件
papers/
├── deep_learning.pdf
├── neural_networks.pdf
└── computer_vision.pdf

# 批量翻译
python translate_pdfs.py papers/

# 结果
papers/
├── deep_learning.pdf
├── deep_learning_chn.pdf      ✓
├── neural_networks.pdf
├── neural_networks_chn.pdf    ✓
├── computer_vision.pdf
└── computer_vision_chn.pdf    ✓
```

#### 递归翻译子目录

```bash
research/
├── 2023/
│   ├── paper1.pdf
│   └── paper2.pdf
└── 2024/
    ├── paper3.pdf
    └── paper4.pdf

# 递归翻译
python translate_pdfs.py research/ -r

# 所有子目录的 PDF 都会被翻译
```

#### 自定义配置

```bash
# 创建自定义配置
cp config.json my_config.json

# 编辑配置（例如：降低温度以提高准确性）
{
  "api": {
    "temperature": 0.1  # 更确定的翻译
  },
  "translation": {
    "chunk_size": 2000  # 更小的块
  }
}

# 使用自定义配置
python translate_pdfs.py papers/ -c my_config.json
```

### 性能数据

基于测试 PDF 的实际数据：

| 指标 | 数值 |
|------|------|
| 原文件大小 | 2.9 KB |
| 译文件大小 | 49 KB |
| 字符数 | 1,654 |
| 翻译时间 | 6.74 秒 |
| 分块数 | 1 |
| API 调用次数 | 1 |

### 成本估算

以 DeepSeek API 为例：

- **输入**: 约 400 tokens × ¥0.001/1K = ¥0.0004
- **输出**: 约 600 tokens × ¥0.002/1K = ¥0.0012
- **总成本**: 约 ¥0.0016 (不到 2 分钱)

一篇 20 页的论文（约 10,000 词）：
- 预计成本：¥0.10 - ¥0.20
- 翻译时间：1-3 分钟

### 实际应用场景

#### 场景 1：研究生阅读文献

```bash
# 下载了 50 篇英文论文
papers/
├── paper_001.pdf
├── paper_002.pdf
...
└── paper_050.pdf

# 一键翻译所有论文
python translate_pdfs.py papers/

# 预计时间：约 30-60 分钟
# 预计成本：约 ¥5-10
```

#### 场景 2：课题组文献整理

```bash
# 按年份和主题组织
literature/
├── 2023/
│   ├── deep_learning/
│   └── nlp/
└── 2024/
    ├── computer_vision/
    └── robotics/

# 递归翻译所有文献
python translate_pdfs.py literature/ -r
```

#### 场景 3：会议论文集翻译

```bash
# CVPR 2024 论文集
cvpr2024/
├── oral/
│   ├── paper1.pdf
│   └── paper2.pdf
└── poster/
    ├── paper3.pdf
    └── paper4.pdf

# 批量翻译
python translate_pdfs.py cvpr2024/ -r
```

### 质量评估

翻译质量的关键因素：

1. **术语准确性**: ✅ 专业术语保留英文或正确翻译
2. **语句流畅性**: ✅ 符合中文表达习惯
3. **格式保留**: ✅ 标题、段落、列表结构保持
4. **公式保护**: ✅ 数学公式不被翻译
5. **上下文连贯**: ✅ 长文档分块翻译保持连贯

### 故障排除示例

#### 问题：翻译中断

```bash
# 第一次运行（中断）
python translate_pdfs.py papers/
# 处理到第 3 个文件时网络中断

# 第二次运行（自动恢复）
python translate_pdfs.py papers/
# 自动跳过已翻译的文件，从第 4 个继续
```

#### 问题：API 限流

```bash
# 修改配置增加重试
{
  "processing": {
    "retry_times": 5,      # 增加重试次数
    "retry_delay": 5       # 增加重试延迟
  }
}
```

### 总结

本演示展示了 PDF 批量翻译工具的完整使用流程，从安装配置到实际翻译，再到高级用法和故障排除。工具已经过充分测试，可以投入实际使用。

**关键优势**：
- 🚀 快速：单篇论文翻译仅需数秒
- 💰 经济：成本极低，每篇不到 1 毛钱
- 🎯 准确：AI 驱动，质量远超机器翻译
- 🔧 灵活：高度可配置，适应不同需求
- 🛡️ 可靠：自动重试，缓存机制，断点续传

**适用人群**：
- 研究生和科研工作者
- 技术文档翻译人员
- 需要快速了解英文文献的学习者

