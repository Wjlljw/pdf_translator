"""
批量处理模块 v3
支持保留图像和表格的 PDF 翻译
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Optional

try:
    from .pdf_parser_enhanced import EnhancedPDFParser, TextElement, ImageElement, TableElement
    from .pdf_generator_v3 import PDFGeneratorV3
    from .translator import Translator, TextChunker
except ImportError:
    from pdf_parser_enhanced import EnhancedPDFParser, TextElement, ImageElement, TableElement
    from pdf_generator_v3 import PDFGeneratorV3
    from translator import Translator, TextChunker


class BatchProcessorV3:
    """支持图像和表格的批量处理器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化批量处理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        
        # 初始化组件
        self.parser = EnhancedPDFParser()
        self.translator = Translator(self.config)
        self.generator = PDFGeneratorV3(self.config)
        self.chunker = TextChunker()
        
        # 缓存目录
        self.cache_dir = self.config.get('cache', {}).get('dir', '.cache')
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _load_config(self, config_path: str = None) -> Dict:
        """加载配置文件"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def process_pdf(self, pdf_path: str, output_path: str = None) -> bool:
        """
        处理单个 PDF 文件
        
        Args:
            pdf_path: 输入 PDF 路径
            output_path: 输出 PDF 路径（可选）
            
        Returns:
            是否成功
        """
        try:
            print(f"\n{'='*60}")
            print(f"处理文件: {pdf_path}")
            print('='*60)
            
            # 生成输出路径
            if not output_path:
                pdf_dir = os.path.dirname(pdf_path)
                pdf_name = Path(pdf_path).stem
                output_path = os.path.join(pdf_dir, f"{pdf_name}_chn.pdf")
            
            # 步骤 1: 解析 PDF
            print("步骤 1/4: 解析 PDF...")
            start_time = time.time()
            elements = self.parser.parse(pdf_path)
            print(f"  用时: {time.time() - start_time:.2f} 秒")
            
            # 步骤 2: 提取和翻译文本
            print("步骤 2/4: 翻译文本...")
            start_time = time.time()
            translated_texts = self._translate_elements(elements, pdf_path)
            print(f"  用时: {time.time() - start_time:.2f} 秒")
            
            # 步骤 3: 生成 PDF
            print("步骤 3/4: 生成 PDF...")
            start_time = time.time()
            self.generator.generate_from_elements(elements, translated_texts, output_path)
            print(f"  用时: {time.time() - start_time:.2f} 秒")
            
            print(f"\n✓ 成功翻译: {pdf_path}")
            print(f"  输出文件: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"\n✗ 处理失败: {pdf_path}")
            print(f"  错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _translate_elements(self, elements: List, pdf_path: str) -> Dict[int, str]:
        """
        翻译文本元素
        
        Args:
            elements: 元素列表
            pdf_path: PDF 文件路径（用于缓存）
            
        Returns:
            翻译文本字典 {元素索引: 翻译文本}
        """
        translated_texts = {}
        
        # 提取所有文本元素
        text_elements = []
        text_indices = []
        
        for i, elem in enumerate(elements):
            if isinstance(elem, TextElement):
                text_elements.append(elem.text)
                text_indices.append(i)
        
        if not text_elements:
            print("  警告: 未找到文本元素")
            return translated_texts
        
        print(f"  找到 {len(text_elements)} 个文本元素")
        
        # 合并文本进行翻译
        full_text = '\n\n'.join(text_elements)
        
        # 检查缓存
        cache_key = self._get_cache_key(full_text)
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.txt")
        
        if os.path.exists(cache_path):
            print("  使用缓存的翻译结果")
            with open(cache_path, 'r', encoding='utf-8') as f:
                translated_full = f.read()
        else:
            # 翻译文本
            print("  正在翻译...")
            
            # 分块翻译
            chunks = self.chunker.chunk_text(full_text)
            print(f"  分成 {len(chunks)} 个块")
            
            translated_chunks = []
            for i, chunk in enumerate(chunks):
                print(f"  进度: {i + 1}/{len(chunks)} ({(i + 1) / len(chunks) * 100:.1f}%)")
                translated = self.translator.translate_text(chunk)
                translated_chunks.append(translated)
                time.sleep(0.5)  # 避免 API 限流
            
            translated_full = '\n\n'.join(translated_chunks)
            
            # 保存到缓存
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(translated_full)
        
        # 将翻译结果分配回各个元素
        # 简单策略：按段落分割
        translated_paragraphs = translated_full.split('\n\n')
        
        for i, text_index in enumerate(text_indices):
            if i < len(translated_paragraphs):
                translated_texts[text_index] = translated_paragraphs[i].strip()
            else:
                # 如果翻译段落不够，使用原文
                translated_texts[text_index] = elements[text_index].text
        
        return translated_texts
    
    def _get_cache_key(self, text: str) -> str:
        """生成缓存键"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def process_directory(self, directory: str, recursive: bool = False) -> Dict[str, int]:
        """
        批量处理目录下的 PDF 文件
        
        Args:
            directory: 目录路径
            recursive: 是否递归处理子目录
            
        Returns:
            统计信息 {'success': 成功数, 'failed': 失败数}
        """
        print(f"\n{'='*60}")
        print(f"批量处理目录: {directory}")
        print(f"递归处理: {'是' if recursive else '否'}")
        print('='*60)
        
        # 查找 PDF 文件
        if recursive:
            pdf_files = list(Path(directory).rglob('*.pdf'))
        else:
            pdf_files = list(Path(directory).glob('*.pdf'))
        
        # 过滤已翻译的文件
        pdf_files = [f for f in pdf_files if not f.stem.endswith('_chn')]
        
        print(f"找到 {len(pdf_files)} 个 PDF 文件\n")
        
        stats = {'success': 0, 'failed': 0}
        
        for i, pdf_path in enumerate(pdf_files):
            print(f"\n[{i + 1}/{len(pdf_files)}] 处理: {pdf_path.name}")
            
            if self.process_pdf(str(pdf_path)):
                stats['success'] += 1
            else:
                stats['failed'] += 1
        
        # 打印统计信息
        print(f"\n{'='*60}")
        print("处理完成")
        print('='*60)
        print(f"成功: {stats['success']}/{len(pdf_files)}")
        print(f"失败: {stats['failed']}/{len(pdf_files)}")
        
        return stats


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PDF 批量翻译工具 v3 (支持图像和表格)')
    parser.add_argument('input', help='输入 PDF 文件或目录')
    parser.add_argument('-o', '--output', help='输出 PDF 文件路径')
    parser.add_argument('-c', '--config', help='配置文件路径')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = BatchProcessorV3(args.config)
    
    # 处理输入
    if os.path.isfile(args.input):
        # 处理单个文件
        processor.process_pdf(args.input, args.output)
    elif os.path.isdir(args.input):
        # 处理目录
        processor.process_directory(args.input, args.recursive)
    else:
        print(f"错误: 输入路径不存在: {args.input}")


if __name__ == "__main__":
    main()

