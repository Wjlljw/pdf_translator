# PDF 批量翻译工具 - Hugging Face 版本

## 🎉 已更新支持 Hugging Face API

工具已更新，现在支持使用 Hugging Face API 进行翻译！

## 🚀 快速开始

### 方法 1：使用环境变量（最简单）

```bash
# 1. 解压工具
tar -xzf pdf_translator_huggingface.tar.gz
cd pdf_translator_release/

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置 Hugging Face Token
export HF_TOKEN="hf_your_token_here"

# 4. 运行翻译
python translate_pdfs.py papers/ -c config_huggingface.json
```

### 方法 2：使用配置脚本

```bash
# 1. 运行配置脚本
./setup_huggingface.sh

# 2. 按提示输入您的 HF_TOKEN

# 3. 运行翻译
python translate_pdfs.py papers/ -c config_huggingface.json
```

### 方法 3：修改配置文件

```bash
# 1. 编辑配置文件
nano config_huggingface.json

# 2. 填入您的 Token
{
  "api": {
    "api_key": "hf_your_token_here",
    ...
  }
}

# 3. 运行翻译
python translate_pdfs.py papers/ -c config_huggingface.json
```

## 📋 API 配置详情

### Hugging Face API 设置

```json
{
  "api": {
    "provider": "huggingface",
    "model": "deepseek-ai/DeepSeek-V3-0324:fireworks-ai",
    "api_key": "",
    "base_url": "https://router.huggingface.co/v1",
    "max_tokens": 4000,
    "temperature": 0.3
  }
}
```

### 参数说明

| 参数 | 说明 | 值 |
|------|------|-----|
| `provider` | API 提供商 | `huggingface` |
| `model` | 模型名称 | `deepseek-ai/DeepSeek-V3-0324:fireworks-ai` |
| `api_key` | HF Token | 留空则从环境变量 `HF_TOKEN` 读取 |
| `base_url` | API 地址 | `https://router.huggingface.co/v1` |
| `max_tokens` | 最大 token 数 | `4000` |
| `temperature` | 生成温度 | `0.3` (推荐 0.1-0.3) |

## 🔑 获取 Hugging Face Token

1. 访问 https://huggingface.co/
2. 注册/登录账号
3. 进入 Settings → Access Tokens
4. 点击 "New token"
5. 选择 "Read" 权限
6. 复制生成的 Token (格式: `hf_xxxxxxxxxxxxx`)

## 💡 使用示例

### 示例 1：翻译单个目录

```bash
# 设置 Token
export HF_TOKEN="hf_xxxxxxxxxxxxx"

# 创建测试目录
mkdir my_papers
cp paper1.pdf my_papers/

# 运行翻译
python translate_pdfs.py my_papers/ -c config_huggingface.json

# 查看结果
ls my_papers/
# 输出：
# paper1.pdf
# paper1_chn.pdf  ← 翻译结果
```

### 示例 2：递归翻译多个子目录

```bash
# 文件结构
research/
├── 2023/
│   ├── paper1.pdf
│   └── paper2.pdf
└── 2024/
    ├── paper3.pdf
    └── paper4.pdf

# 递归翻译
export HF_TOKEN="hf_xxxxxxxxxxxxx"
python translate_pdfs.py research/ -r -c config_huggingface.json
```

### 示例 3：一次性设置 Token 并运行

```bash
HF_TOKEN="hf_xxxxxxxxxxxxx" python translate_pdfs.py papers/ -c config_huggingface.json
```

## 🔄 环境变量优先级

工具会按以下顺序查找 API Key：

1. 配置文件 `config_huggingface.json` 中的 `api.api_key`
2. 环境变量 `HF_TOKEN` ← **推荐使用**
3. 环境变量 `DEEPSEEK_API_KEY`
4. 环境变量 `OPENAI_API_KEY`

## 📊 支持的 API

工具现在支持以下 API（使用不同的配置文件）：

| API | 配置文件 | 环境变量 |
|-----|---------|---------|
| Hugging Face | `config_huggingface.json` | `HF_TOKEN` |
| DeepSeek | `config.example.json` | `DEEPSEEK_API_KEY` |
| OpenAI | `config.json` | `OPENAI_API_KEY` |

## 🎯 完整工作流程

```bash
# 1. 解压工具包
tar -xzf pdf_translator_huggingface.tar.gz
cd pdf_translator_release/

# 2. 安装依赖（首次使用）
pip install -r requirements.txt

# 3. 设置 HF Token
export HF_TOKEN="hf_your_token_here"

# 4. 准备 PDF 文件
mkdir papers
cp /path/to/your/*.pdf papers/

# 5. 运行翻译
python translate_pdfs.py papers/ -c config_huggingface.json

# 6. 查看结果
ls papers/
# 原文件: paper.pdf
# 译文件: paper_chn.pdf
# 日志: translation_log_*.txt
```

## 📁 文件说明

### 新增文件

- **config_huggingface.json** - Hugging Face API 配置文件
- **HUGGINGFACE_SETUP.md** - 详细的 HF API 配置说明
- **setup_huggingface.sh** - 快速配置脚本
- **HUGGINGFACE_README.md** - 本文件

### 核心文件（已更新）

- **src/translator.py** - 已支持 HF_TOKEN 环境变量
- **src/batch_processor.py** - 已支持 HF_TOKEN 环境变量

## ⚙️ 高级配置

### 调整翻译质量

```json
{
  "api": {
    "temperature": 0.1  // 降低温度提高准确性（0.1-0.3）
  },
  "translation": {
    "chunk_size": 2000  // 减小块大小提高质量
  }
}
```

### 调整翻译速度

```json
{
  "api": {
    "temperature": 0.3  // 稍高温度加快速度
  },
  "translation": {
    "chunk_size": 3000  // 增大块大小减少 API 调用
  }
}
```

## 💰 成本说明

使用 Hugging Face Router 调用 DeepSeek-V3：

- 通常比直接使用 OpenAI 更经济
- 具体价格请查看 Hugging Face 和 Fireworks AI 定价
- 预估：标准论文（10-20页）约 ¥0.10-0.20

## ❓ 常见问题

### Q1: 如何永久保存 HF_TOKEN？

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
echo 'export HF_TOKEN="hf_your_token"' >> ~/.bashrc
source ~/.bashrc
```

### Q2: Token 格式是什么？

```
正确格式: hf_xxxxxxxxxxxxxxxxxxxxx
错误格式: xxxxxxxxxxxxxxxxxxxxx (缺少 hf_ 前缀)
```

### Q3: 如何验证 Token 是否有效？

```bash
# 检查环境变量
echo $HF_TOKEN

# 运行测试翻译
python translate_pdfs.py sample_pdfs/ -c config_huggingface.json
```

### Q4: 可以使用其他模型吗？

可以！修改 `config_huggingface.json` 中的 `model` 参数：

```json
{
  "api": {
    "model": "meta-llama/Llama-3.1-70B-Instruct"
  }
}
```

## 📚 更多文档

- **README.md** - 完整使用文档
- **QUICKSTART.md** - 快速开始指南
- **HUGGINGFACE_SETUP.md** - HF API 详细配置
- **DESIGN.md** - 技术设计文档
- **DEMO.md** - 使用演示

## ✅ 测试验证

工具已通过以下测试：

- ✅ Hugging Face API 集成
- ✅ HF_TOKEN 环境变量读取
- ✅ 完整翻译流程
- ✅ 多 API 兼容性

## 🎉 开始使用

现在您可以使用 Hugging Face API 进行 PDF 批量翻译了！

```bash
export HF_TOKEN="hf_your_token"
python translate_pdfs.py papers/ -c config_huggingface.json
```

**祝您使用愉快！Happy Translating! 📚✨**

