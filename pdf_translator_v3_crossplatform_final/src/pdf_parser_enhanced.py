"""
增强的 PDF 解析模块
支持提取文本、图像、表格及其位置信息
"""

import fitz  # PyMuPDF
import pdfplumber
import os
import re
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PDFElement:
    """PDF 元素基类"""
    page_num: int
    bbox: Tuple[float, float, float, float]  # (x0, y0, x1, y1)
    element_type: str  # 'text', 'image', 'table'


@dataclass
class TextElement(PDFElement):
    """文本元素"""
    text: str
    font_size: float = 12.0
    is_heading: bool = False
    element_type: str = field(default='text', init=False)


@dataclass
class ImageElement(PDFElement):
    """图像元素"""
    image_path: str  # 保存的图像文件路径
    width: float = 0
    height: float = 0
    element_type: str = field(default='image', init=False)


@dataclass
class TableElement(PDFElement):
    """表格元素"""
    data: List[List[str]]  # 表格数据（二维列表）
    header: Optional[List[str]] = None
    element_type: str = field(default='table', init=False)


class EnhancedPDFParser:
    """增强的 PDF 解析器"""
    
    def __init__(self, output_dir: str = None):
        """
        初始化解析器
        
        Args:
            output_dir: 输出目录（用于保存提取的图像）
        """
        self.output_dir = output_dir or "/tmp/pdf_extraction"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def parse(self, pdf_path: str) -> List[PDFElement]:
        """
        解析 PDF 文件，提取所有元素
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            元素列表（按页面和位置排序）
        """
        print(f"正在解析 PDF: {pdf_path}")
        
        elements = []
        
        # 使用 PyMuPDF 提取文本和图像
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 提取文本块
            text_elements = self._extract_text_elements(page, page_num)
            elements.extend(text_elements)
            
            # 提取图像
            image_elements = self._extract_images(page, page_num, pdf_path)
            elements.extend(image_elements)
        
        doc.close()
        
        # 使用 pdfplumber 提取表格
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    table_elements = self._extract_tables(page, page_num)
                    elements.extend(table_elements)
        except Exception as e:
            print(f"表格提取失败: {e}")
        
        # 按页码和Y坐标排序
        elements.sort(key=lambda e: (e.page_num, e.bbox[1], e.bbox[0]))
        
        print(f"解析完成: {len(elements)} 个元素")
        self._print_statistics(elements)
        
        return elements
    
    def extract_text_simple(self, pdf_path: str) -> str:
        """
        简单提取 PDF 的纯文本内容（用于快速翻译）
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            提取的文本
        """
        text_parts = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
        except Exception as e:
            print(f"pdfplumber 提取失败，使用 PyMuPDF: {e}")
            doc = fitz.open(pdf_path)
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
        
        full_text = "\n\n".join(text_parts)
        full_text = self._clean_text(full_text)
        
        return full_text
    
    def _extract_text_elements(self, page: fitz.Page, page_num: int) -> List[TextElement]:
        """提取页面的文本元素"""
        elements = []
        
        # 获取文本块（带格式信息）
        text_dict = page.get_text("dict")
        page_height = page.rect.height
        
        for block in text_dict.get("blocks", []):
            if block.get("type") == 0:  # 文本块
                for line in block.get("lines", []):
                    line_text = ""
                    font_size = 12.0
                    
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                        font_size = max(font_size, span.get("size", 12.0))
                    
                    if line_text.strip():
                        bbox = tuple(line.get("bbox", (0, 0, 0, 0)))
                        
                        # 判断是否为标题（基于字体大小）
                        is_heading = font_size > 14
                        
                        elements.append(TextElement(
                            page_num=page_num,
                            bbox=bbox,
                            text=line_text.strip(),
                            font_size=font_size,
                            is_heading=is_heading
                        ))
        
        return elements
    
    def _extract_images(self, page: fitz.Page, page_num: int, pdf_path: str) -> List[ImageElement]:
        """提取页面的图像"""
        elements = []
        image_list = page.get_images(full=True)
        
        pdf_name = Path(pdf_path).stem
        page_images_dir = os.path.join(self.output_dir, f"{pdf_name}_images")
        os.makedirs(page_images_dir, exist_ok=True)
        
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                
                image_data = base_image["image"]
                image_ext = base_image["ext"]
                
                # 保存图像
                image_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
                image_path = os.path.join(page_images_dir, image_filename)
                
                with open(image_path, "wb") as img_file:
                    img_file.write(image_data)
                
                # 获取图像在页面上的位置
                # 查找图像的矩形区域
                img_rects = page.get_image_rects(xref)
                if img_rects:
                    rect = img_rects[0]
                    bbox = (rect.x0, rect.y0, rect.x1, rect.y1)
                    width = rect.width
                    height = rect.height
                else:
                    # 如果无法获取位置，使用默认值
                    bbox = (0, 0, 100, 100)
                    width = 100
                    height = 100
                
                elements.append(ImageElement(
                    page_num=page_num,
                    bbox=bbox,
                    image_path=image_path,
                    width=width,
                    height=height
                ))
                
                print(f"  提取图像: page {page_num + 1}, img {img_index + 1} -> {image_path}")
                
            except Exception as e:
                print(f"  提取图像失败 (page {page_num + 1}, img {img_index + 1}): {e}")
        
        return elements
    
    def _extract_tables(self, page: Any, page_num: int) -> List[TableElement]:
        """提取页面的表格"""
        elements = []
        
        try:
            tables = page.extract_tables()
            
            for table_index, table in enumerate(tables):
                if not table or len(table) == 0:
                    continue
                
                # 获取表格边界
                # pdfplumber 的表格对象包含边界信息
                table_obj = page.find_tables()[table_index]
                bbox = table_obj.bbox  # (x0, y0, x1, y1)
                
                # 第一行可能是表头
                header = table[0] if table else None
                data = table[1:] if len(table) > 1 else table
                
                elements.append(TableElement(
                    page_num=page_num,
                    bbox=bbox,
                    data=data,
                    header=header
                ))
                
                print(f"  提取表格: page {page_num + 1}, table {table_index + 1}, size {len(table)}x{len(table[0]) if table else 0}")
                
        except Exception as e:
            print(f"  提取表格失败 (page {page_num + 1}): {e}")
        
        return elements
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余的空白
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # 移除页眉页脚（简单启发式）
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # 跳过可能是页码的行
            if re.match(r'^\s*\d+\s*$', line):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _print_statistics(self, elements: List[PDFElement]):
        """打印统计信息"""
        text_count = sum(1 for e in elements if isinstance(e, TextElement))
        image_count = sum(1 for e in elements if isinstance(e, ImageElement))
        table_count = sum(1 for e in elements if isinstance(e, TableElement))
        
        print(f"  - 文本元素: {text_count}")
        print(f"  - 图像元素: {image_count}")
        print(f"  - 表格元素: {table_count}")


def test_enhanced_parser():
    """测试增强解析器"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python pdf_parser_enhanced.py <pdf_file>")
        return
    
    pdf_path = sys.argv[1]
    parser = EnhancedPDFParser()
    
    # 测试结构化解析
    elements = parser.parse(pdf_path)
    
    print("\n" + "=" * 60)
    print("元素详情（前10个）:")
    print("=" * 60)
    
    for i, elem in enumerate(elements[:10]):
        print(f"\n[{i + 1}] {elem.element_type.upper()}")
        print(f"  页码: {elem.page_num + 1}")
        print(f"  位置: {elem.bbox}")
        
        if isinstance(elem, TextElement):
            print(f"  文本: {elem.text[:100]}...")
            print(f"  字体大小: {elem.font_size}")
            print(f"  是否标题: {elem.is_heading}")
        elif isinstance(elem, ImageElement):
            print(f"  图像路径: {elem.image_path}")
            print(f"  尺寸: {elem.width} x {elem.height}")
        elif isinstance(elem, TableElement):
            print(f"  表格大小: {len(elem.data)} 行 x {len(elem.data[0]) if elem.data else 0} 列")
            if elem.header:
                print(f"  表头: {elem.header}")


if __name__ == "__main__":
    test_enhanced_parser()

