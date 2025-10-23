"""
翻译引擎模块
支持调用 DeepSeek API 进行文本翻译
"""

import os
import time
import json
import re
from typing import List, Dict, Optional
from openai import OpenAI


class Translator:
    """AI 翻译引擎"""
    
    def __init__(self, config: Dict):
        """
        初始化翻译器
        
        Args:
            config: 配置字典
        """
        self.config = config
        api_config = config.get('api', {})
        
        # 初始化 OpenAI 客户端（兼容多种 API）
        # 支持：Hugging Face, DeepSeek, OpenAI 等
        api_key = (
            api_config.get('api_key') or 
            os.getenv('HF_TOKEN') or 
            os.getenv('DEEPSEEK_API_KEY') or 
            os.getenv('OPENAI_API_KEY')
        )
        
        base_url = api_config.get('base_url') or None  # None 使用默认 OpenAI URL
        
        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            # 使用系统预配置（环境变量已设置）
            self.client = OpenAI()
        
        self.model = api_config.get('model', 'deepseek-ai/DeepSeek-V3-0324:fireworks-ai')
        self.max_tokens = api_config.get('max_tokens', 4000)
        self.temperature = api_config.get('temperature', 0.3)
        
        trans_config = config.get('translation', {})
        self.chunk_size = trans_config.get('chunk_size', 2500)
        self.source_lang = trans_config.get('source_lang', 'en')
        self.target_lang = trans_config.get('target_lang', 'zh')
        
        proc_config = config.get('processing', {})
        self.retry_times = proc_config.get('retry_times', 3)
        self.retry_delay = proc_config.get('retry_delay', 2)
        
    def translate_text(self, text: str, context: str = "") -> str:
        """
        翻译单个文本块
        
        Args:
            text: 要翻译的文本
            context: 上下文信息（可选）
            
        Returns:
            翻译后的文本
        """
        if not text.strip():
            return text
            
        # 构建提示词
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(text, context)
        
        # 调用 API 进行翻译
        for attempt in range(self.retry_times):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                
                translated = response.choices[0].message.content.strip()
                return translated
                
            except Exception as e:
                print(f"翻译失败 (尝试 {attempt + 1}/{self.retry_times}): {str(e)}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise Exception(f"翻译失败，已重试 {self.retry_times} 次: {str(e)}")
    
    def translate_chunks(self, chunks: List[str], progress_callback=None) -> List[str]:
        """
        翻译多个文本块
        
        Args:
            chunks: 文本块列表
            progress_callback: 进度回调函数
            
        Returns:
            翻译后的文本块列表
        """
        translated_chunks = []
        context = ""
        
        for i, chunk in enumerate(chunks):
            if progress_callback:
                progress_callback(i + 1, len(chunks))
            
            # 翻译当前块
            translated = self.translate_text(chunk, context)
            translated_chunks.append(translated)
            
            # 更新上下文（使用当前块的最后部分）
            context = self._extract_context(chunk)
            
            # 避免 API 限流
            if i < len(chunks) - 1:
                time.sleep(0.5)
        
        return translated_chunks
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return f"""你是一个专业的学术论文翻译助手。请将{self._get_lang_name(self.source_lang)}文本翻译成{self._get_lang_name(self.target_lang)}。

翻译要求：
1. 保持学术论文的专业性和准确性
2. 保留所有 LaTeX 公式（用 $ 或 $$ 包围的内容）不要翻译
3. 保留所有引用标记如 [1], (Smith et al., 2020) 等
4. 保留专业术语的英文原文（可在首次出现时用括号标注）
5. 保持原文的段落结构和格式
6. 对于图表标题，翻译为中文但保留 "Figure" 和 "Table" 的编号格式
7. 只输出翻译结果，不要添加任何解释或说明"""
    
    def _build_user_prompt(self, text: str, context: str) -> str:
        """构建用户提示词"""
        if context:
            return f"""上下文（仅供参考，不需要翻译）：
{context}

请翻译以下内容：
{text}"""
        else:
            return f"请翻译以下内容：\n{text}"
    
    def _extract_context(self, text: str, max_length: int = 200) -> str:
        """提取文本的最后部分作为上下文"""
        if len(text) <= max_length:
            return text
        return "..." + text[-max_length:]
    
    def _get_lang_name(self, lang_code: str) -> str:
        """获取语言名称"""
        lang_map = {
            'en': '英文',
            'zh': '中文',
            'ja': '日文',
            'ko': '韩文',
            'fr': '法文',
            'de': '德文',
            'es': '西班牙文'
        }
        return lang_map.get(lang_code, lang_code)


class TextChunker:
    """文本分块器"""
    
    def __init__(self, chunk_size: int = 2500, overlap: int = 200):
        """
        初始化分块器
        
        Args:
            chunk_size: 每块的最大字符数
            overlap: 块之间的重叠字符数
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """
        将文本分块
        
        Args:
            text: 要分块的文本
            
        Returns:
            文本块列表
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        paragraphs = self._split_paragraphs(text)
        
        current_chunk = ""
        for para in paragraphs:
            # 如果单个段落超过块大小，需要强制分割
            if len(para) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                
                # 分割长段落
                sub_chunks = self._split_long_paragraph(para)
                chunks.extend(sub_chunks[:-1])
                current_chunk = sub_chunks[-1] if sub_chunks else ""
            
            # 如果添加当前段落会超过块大小
            elif len(current_chunk) + len(para) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para
            else:
                current_chunk += ("\n\n" if current_chunk else "") + para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """按段落分割文本"""
        # 按双换行符分割
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """分割过长的段落"""
        chunks = []
        sentences = re.split(r'([.!?]+\s+)', paragraph)
        
        current_chunk = ""
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            separator = sentences[i + 1] if i + 1 < len(sentences) else ""
            
            if len(current_chunk) + len(sentence) + len(separator) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence + separator
            else:
                current_chunk += sentence + separator
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks if chunks else [paragraph]


def test_translator():
    """测试翻译器"""
    config = {
        "api": {
            "model": "deepseek-chat",
            "api_key": os.getenv('DEEPSEEK_API_KEY', ''),
            "base_url": "https://api.deepseek.com"
        },
        "translation": {
            "chunk_size": 2500
        },
        "processing": {
            "retry_times": 3
        }
    }
    
    translator = Translator(config)
    
    # 测试文本
    test_text = """
    Machine learning is a subset of artificial intelligence that focuses on 
    developing algorithms and statistical models. The formula for gradient 
    descent is: $\\theta_{t+1} = \\theta_t - \\alpha \\nabla J(\\theta_t)$.
    """
    
    print("原文:", test_text)
    result = translator.translate_text(test_text)
    print("译文:", result)


if __name__ == "__main__":
    test_translator()

