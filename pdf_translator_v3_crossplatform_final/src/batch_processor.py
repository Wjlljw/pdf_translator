"""
批量处理模块
扫描目录并批量翻译 PDF 文件
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

try:
    from .pdf_parser import PDFParser
    from .translator import Translator, TextChunker
    from .pdf_generator_enhanced import EnhancedPDFGenerator
except ImportError:
    from pdf_parser import PDFParser
    from translator import Translator, TextChunker
    from pdf_generator_enhanced import EnhancedPDFGenerator


class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化批量处理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        
        # 初始化各个组件
        self.parser = PDFParser(
            preserve_images=self.config['translation']['preserve_images'],
            preserve_formulas=self.config['translation']['preserve_formulas']
        )
        self.translator = Translator(self.config)
        self.chunker = TextChunker(
            chunk_size=self.config['translation']['chunk_size'],
            overlap=self.config['translation'].get('context_overlap', 200)
        )
        self.generator = EnhancedPDFGenerator(self.config)
        
        # 缓存目录
        self.cache_dir = Path(".cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # 日志
        self.log_file = None
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 验证必要的配置
        if not config.get('api', {}).get('api_key'):
            # 尝试从环境变量获取
            api_key = (
                os.getenv('HF_TOKEN') or 
                os.getenv('DEEPSEEK_API_KEY') or 
                os.getenv('OPENAI_API_KEY')
            )
            if api_key:
                config['api']['api_key'] = api_key
            else:
                print("警告: 未配置 API Key，将使用系统预配置的 API")
                # 不抛出异常，允许使用系统预配置
        
        return config
    
    def process_directory(self, directory: str, recursive: bool = False):
        """
        处理目录下的所有 PDF 文件
        
        Args:
            directory: 目录路径
            recursive: 是否递归处理子目录
        """
        # 初始化日志
        self._init_log(directory)
        
        # 查找所有 PDF 文件
        pdf_files = self._find_pdf_files(directory, recursive)
        
        if not pdf_files:
            print(f"在 {directory} 中未找到 PDF 文件")
            return
        
        print(f"找到 {len(pdf_files)} 个 PDF 文件")
        self._log(f"找到 {len(pdf_files)} 个 PDF 文件")
        
        # 处理每个文件
        success_count = 0
        failed_files = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n{'='*60}")
            print(f"处理文件 [{i}/{len(pdf_files)}]: {pdf_file}")
            print(f"{'='*60}")
            
            try:
                self.process_file(pdf_file)
                success_count += 1
                print(f"✓ 成功翻译: {pdf_file}")
                self._log(f"✓ 成功: {pdf_file}")
            except Exception as e:
                print(f"✗ 翻译失败: {pdf_file}")
                print(f"  错误: {str(e)}")
                failed_files.append((pdf_file, str(e)))
                self._log(f"✗ 失败: {pdf_file} - {str(e)}")
        
        # 输出总结
        print(f"\n{'='*60}")
        print("处理完成")
        print(f"{'='*60}")
        print(f"成功: {success_count}/{len(pdf_files)}")
        print(f"失败: {len(failed_files)}/{len(pdf_files)}")
        
        if failed_files:
            print("\n失败的文件:")
            for file, error in failed_files:
                print(f"  - {file}")
                print(f"    {error}")
        
        self._log(f"\n总结: 成功 {success_count}/{len(pdf_files)}, 失败 {len(failed_files)}/{len(pdf_files)}")
    
    def process_file(self, pdf_path: str):
        """
        处理单个 PDF 文件
        
        Args:
            pdf_path: PDF 文件路径
        """
        start_time = time.time()
        
        # 生成输出文件名
        output_path = self._generate_output_path(pdf_path)
        
        # 检查是否已经翻译过
        if os.path.exists(output_path):
            print(f"文件已存在，跳过: {output_path}")
            return
        
        # 检查缓存
        cache_key = self._get_cache_key(pdf_path)
        cached_translation = self._load_from_cache(cache_key)
        
        if cached_translation:
            print("使用缓存的翻译结果")
            translated_text = cached_translation
        else:
            # 步骤 1: 提取文本
            print("步骤 1/4: 提取文本...")
            text = self.parser.extract_text(pdf_path)
            print(f"  提取了 {len(text)} 个字符")
            
            # 步骤 2: 分块
            print("步骤 2/4: 文本分块...")
            chunks = self.chunker.chunk_text(text)
            print(f"  分成 {len(chunks)} 个块")
            
            # 步骤 3: 翻译
            print("步骤 3/4: 翻译中...")
            translated_chunks = self.translator.translate_chunks(
                chunks,
                progress_callback=self._print_progress
            )
            
            # 合并翻译结果
            translated_text = "\n\n".join(translated_chunks)
            
            # 保存到缓存
            self._save_to_cache(cache_key, translated_text)
        
        # 步骤 4: 生成 PDF
        print("步骤 4/4: 生成 PDF...")
        self.generator.generate_from_markdown(
            translated_text,
            output_path,
            original_pdf_path=pdf_path
        )
        
        elapsed_time = time.time() - start_time
        print(f"完成! 用时: {elapsed_time:.2f} 秒")
        print(f"输出文件: {output_path}")
    
    def _find_pdf_files(self, directory: str, recursive: bool) -> List[str]:
        """查找 PDF 文件"""
        pdf_files = []
        
        if recursive:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.pdf') and not file.endswith('_chn.pdf'):
                        pdf_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory):
                if file.lower().endswith('.pdf') and not file.endswith('_chn.pdf'):
                    pdf_files.append(os.path.join(directory, file))
        
        return sorted(pdf_files)
    
    def _generate_output_path(self, input_path: str) -> str:
        """生成输出文件路径"""
        path = Path(input_path)
        suffix = self.config['output']['suffix']
        output_name = f"{path.stem}{suffix}.pdf"
        return str(path.parent / output_name)
    
    def _get_cache_key(self, pdf_path: str) -> str:
        """生成缓存键"""
        import hashlib
        
        # 使用文件路径和修改时间生成唯一键
        mtime = os.path.getmtime(pdf_path)
        key_str = f"{pdf_path}_{mtime}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[str]:
        """从缓存加载"""
        if not self.config['processing']['cache_enabled']:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.txt"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"加载缓存失败: {e}")
        
        return None
    
    def _save_to_cache(self, cache_key: str, content: str):
        """保存到缓存"""
        if not self.config['processing']['cache_enabled']:
            return
        
        cache_file = self.cache_dir / f"{cache_key}.txt"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"保存缓存失败: {e}")
    
    def _print_progress(self, current: int, total: int):
        """打印进度"""
        percentage = (current / total) * 100
        print(f"  进度: {current}/{total} ({percentage:.1f}%)")
    
    def _init_log(self, directory: str):
        """初始化日志文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"translation_log_{timestamp}.txt"
        self.log_file = os.path.join(directory, log_filename)
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"PDF 批量翻译日志\n")
            f.write(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"目录: {directory}\n")
            f.write(f"{'='*60}\n\n")
    
    def _log(self, message: str):
        """写入日志"""
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量翻译 PDF 文件')
    parser.add_argument('directory', help='包含 PDF 文件的目录')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    parser.add_argument('-c', '--config', default='config.json', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    if not os.path.isdir(args.directory):
        print(f"错误: 目录不存在: {args.directory}")
        return
    
    # 创建处理器并执行
    try:
        processor = BatchProcessor(args.config)
        processor.process_directory(args.directory, args.recursive)
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

