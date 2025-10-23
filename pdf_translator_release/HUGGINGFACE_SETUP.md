# Hugging Face API 配置说明

本工具已支持使用 Hugging Face API 进行翻译。

## 配置方法

### 方式 1：使用环境变量（推荐）

```bash
# 设置 Hugging Face Token
export HF_TOKEN="hf_your_token_here"

# 使用 Hugging Face 配置文件运行
python translate_pdfs.py papers/ -c config_huggingface.json
```

### 方式 2：修改配置文件

编辑 `config_huggingface.json`：

```json
{
  "api": {
    "provider": "huggingface",
    "model": "deepseek-ai/DeepSeek-V3-0324:fireworks-ai",
    "api_key": "hf_your_token_here",
    "base_url": "https://router.huggingface.co/v1",
    "max_tokens": 4000,
    "temperature": 0.3
  }
}
```

## API 参数说明

### API 配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `provider` | API 提供商 | `huggingface` |
| `model` | 模型名称 | `deepseek-ai/DeepSeek-V3-0324:fireworks-ai` |
| `api_key` | Hugging Face Token | 从环境变量 `HF_TOKEN` 读取 |
| `base_url` | API 基础 URL | `https://router.huggingface.co/v1` |
| `max_tokens` | 最大生成 token 数 | `4000` |
| `temperature` | 生成温度（0-1） | `0.3` |

### 支持的模型

Hugging Face Router 支持多种模型，您可以根据需要修改 `model` 参数：

```json
{
  "api": {
    "model": "deepseek-ai/DeepSeek-V3-0324:fireworks-ai"
  }
}
```

其他可用模型示例：
- `meta-llama/Llama-3.1-70B-Instruct`
- `mistralai/Mixtral-8x7B-Instruct-v0.1`
- 等等（请参考 Hugging Face 文档）

## 获取 Hugging Face Token

1. 访问 [Hugging Face](https://huggingface.co/)
2. 注册并登录账号
3. 进入 Settings → Access Tokens
4. 创建新的 Token（选择 "Read" 权限即可）
5. 复制 Token（格式：`hf_xxxxxxxxxxxxx`）

## 完整使用示例

### 步骤 1：设置 Token

```bash
export HF_TOKEN="hf_xxxxxxxxxxxxx"
```

### 步骤 2：准备 PDF 文件

```bash
mkdir papers
cp your_paper.pdf papers/
```

### 步骤 3：运行翻译

```bash
python translate_pdfs.py papers/ -c config_huggingface.json
```

### 步骤 4：查看结果

```bash
ls papers/
# 输出：
# your_paper.pdf
# your_paper_chn.pdf  ← 翻译结果
```

## 环境变量优先级

工具会按以下顺序查找 API Key：

1. 配置文件中的 `api.api_key`
2. 环境变量 `HF_TOKEN`
3. 环境变量 `DEEPSEEK_API_KEY`
4. 环境变量 `OPENAI_API_KEY`
5. 系统预配置（如果有）

## 成本说明

Hugging Face API 的定价取决于您选择的模型和提供商。请查看 [Hugging Face Pricing](https://huggingface.co/pricing) 了解详情。

使用 DeepSeek-V3 模型通过 Hugging Face Router：
- 通常比直接使用 OpenAI API 更经济
- 具体价格请参考 Hugging Face 和 Fireworks AI 的定价

## 故障排除

### 问题 1：Token 无效

```bash
# 检查环境变量是否设置
echo $HF_TOKEN

# 确保 Token 格式正确（以 hf_ 开头）
```

### 问题 2：模型不可用

```bash
# 检查模型名称是否正确
# 确保模型在 Hugging Face Router 中可用
```

### 问题 3：API 调用失败

```bash
# 检查网络连接
# 查看日志文件了解详细错误信息
```

## 与其他 API 的对比

| 特性 | Hugging Face | DeepSeek | OpenAI |
|------|--------------|----------|--------|
| 模型选择 | 多种开源模型 | DeepSeek 系列 | GPT 系列 |
| 价格 | 较低 | 极低 | 较高 |
| 质量 | 优秀 | 优秀 | 最佳 |
| 速度 | 快 | 快 | 快 |

## 推荐配置

### 高质量翻译

```json
{
  "api": {
    "model": "deepseek-ai/DeepSeek-V3-0324:fireworks-ai",
    "temperature": 0.1,
    "max_tokens": 4000
  },
  "translation": {
    "chunk_size": 2000
  }
}
```

### 快速翻译

```json
{
  "api": {
    "model": "deepseek-ai/DeepSeek-V3-0324:fireworks-ai",
    "temperature": 0.3,
    "max_tokens": 4000
  },
  "translation": {
    "chunk_size": 3000
  }
}
```

## 总结

使用 Hugging Face API 的优势：

✅ **多模型选择** - 可以选择不同的开源模型  
✅ **成本效益** - 通常比商业 API 更经济  
✅ **灵活性** - 支持多种提供商和模型  
✅ **兼容性** - 使用标准 OpenAI 格式，无需修改代码  

现在您可以使用 Hugging Face API 进行 PDF 翻译了！

