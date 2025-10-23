#!/usr/bin/env python3
"""
PDF 批量翻译工具 - 主程序入口

使用方法:
    python translate_pdfs.py <目录路径> [选项]

示例:
    # 翻译当前目录下的所有 PDF
    python translate_pdfs.py ./papers/
    
    # 递归翻译子目录
    python translate_pdfs.py ./papers/ -r
    
    # 使用自定义配置文件
    python translate_pdfs.py ./papers/ -c my_config.json
"""

import sys
import os
import argparse

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from batch_processor import BatchProcessor


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='批量翻译 PDF 论文工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s ./papers/              # 翻译指定目录下的所有 PDF
  %(prog)s ./papers/ -r           # 递归处理子目录
  %(prog)s ./papers/ -c config.json  # 使用自定义配置

配置:
  在使用前，请确保已配置 API Key:
  1. 在 config.json 中设置 api.api_key
  2. 或设置环境变量: export DEEPSEEK_API_KEY=your_key
        """
    )
    
    parser.add_argument(
        'directory',
        help='包含 PDF 文件的目录路径'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='递归处理子目录中的 PDF 文件'
    )
    
    parser.add_argument(
        '-c', '--config',
        default='config.json',
        help='配置文件路径 (默认: config.json)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    args = parser.parse_args()
    
    # 验证目录
    if not os.path.isdir(args.directory):
        print(f"错误: 目录不存在: {args.directory}")
        sys.exit(1)
    
    # 验证配置文件
    if not os.path.exists(args.config):
        print(f"错误: 配置文件不存在: {args.config}")
        print(f"请确保 {args.config} 存在，或使用 -c 指定配置文件路径")
        sys.exit(1)
    
    # 打印欢迎信息
    print("=" * 60)
    print("PDF 批量翻译工具 v1.0.0")
    print("=" * 60)
    print(f"目录: {args.directory}")
    print(f"递归: {'是' if args.recursive else '否'}")
    print(f"配置: {args.config}")
    print("=" * 60)
    print()
    
    # 创建处理器并执行
    try:
        processor = BatchProcessor(args.config)
        processor.process_directory(args.directory, args.recursive)
    except KeyboardInterrupt:
        print("\n\n用户中断，程序退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

