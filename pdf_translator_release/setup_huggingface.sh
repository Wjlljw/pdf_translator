#!/bin/bash
# Hugging Face API 快速配置脚本

echo "=========================================="
echo "PDF 翻译工具 - Hugging Face API 配置"
echo "=========================================="
echo

# 检查是否已设置 HF_TOKEN
if [ -z "$HF_TOKEN" ]; then
    echo "请输入您的 Hugging Face Token (格式: hf_xxxxx):"
    read -r token
    export HF_TOKEN="$token"
    echo
    echo "✓ HF_TOKEN 已设置"
    echo
    echo "提示: 要永久保存，请将以下内容添加到 ~/.bashrc 或 ~/.zshrc:"
    echo "export HF_TOKEN=\"$token\""
else
    echo "✓ 检测到已设置的 HF_TOKEN"
fi

echo
echo "=========================================="
echo "配置完成！"
echo "=========================================="
echo
echo "现在您可以运行翻译："
echo "  python translate_pdfs.py papers/ -c config_huggingface.json"
echo
echo "或者使用环境变量："
echo "  HF_TOKEN=\"your_token\" python translate_pdfs.py papers/ -c config_huggingface.json"
echo

