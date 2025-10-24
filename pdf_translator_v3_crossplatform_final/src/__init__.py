"""
PDF 批量翻译工具
"""

from .pdf_parser import PDFParser
from .translator import Translator, TextChunker
from .pdf_generator import PDFGenerator
from .batch_processor import BatchProcessor

__version__ = "1.0.0"
__all__ = ['PDFParser', 'Translator', 'TextChunker', 'PDFGenerator', 'BatchProcessor']

