"""
PDF 解析模块
提取 PDF 文本、图片、格式信息
"""

import fitz  # PyMuPDF
import pdfplumber
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class PDFElement:
    """PDF 元素基类"""
    page_num: int
    bbox: Tuple[float, float, float, float]  # (x0, y0, x1, y1)


@dataclass
class TextBlock(PDFElement):
    """文本块"""
    text: str
    font_size: float = 12.0
    font_name: str = ""
    is_bold: bool = False
    is_italic: bool = False


@dataclass
class ImageBlock(PDFElement):
    """图片块"""
    image_data: bytes = field(repr=False)
    width: float = 0
    height: float = 0
    image_format: str = ""


@dataclass
class FormulaBlock(PDFElement):
    """公式块"""
    formula: str
    is_inline: bool = True


@dataclass
class PDFDocument:
    """PDF 文档结构"""
    filename: str
    total_pages: int
    elements: List[PDFElement] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


class PDFParser:
    """PDF 解析器"""
    
    def __init__(self, preserve_images: bool = True, preserve_formulas: bool = True):
        """
        初始化解析器
        
        Args:
            preserve_images: 是否保留图片
            preserve_formulas: 是否保留公式
        """
        self.preserve_images = preserve_images
        self.preserve_formulas = preserve_formulas
    
    def parse(self, pdf_path: str) -> PDFDocument:
        """
        解析 PDF 文件
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            PDFDocument 对象
        """
        print(f"正在解析 PDF: {pdf_path}")
        
        doc = fitz.open(pdf_path)
        pdf_doc = PDFDocument(
            filename=pdf_path,
            total_pages=len(doc),
            metadata=doc.metadata
        )
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 提取文本块
            text_blocks = self._extract_text_blocks(page, page_num)
            pdf_doc.elements.extend(text_blocks)
            
            # 提取图片
            if self.preserve_images:
                image_blocks = self._extract_images(page, page_num)
                pdf_doc.elements.extend(image_blocks)
        
        doc.close()
        
        # 按页码和位置排序
        pdf_doc.elements.sort(key=lambda e: (e.page_num, e.bbox[1], e.bbox[0]))
        
        print(f"解析完成: {len(pdf_doc.elements)} 个元素")
        return pdf_doc
    
    def extract_text(self, pdf_path: str) -> str:
        """
        提取 PDF 的纯文本内容
        
        Args:
            pdf_path: PDF 文件路径
            
        Returns:
            提取的文本
        """
        text_parts = []
        
        try:
            # 使用 pdfplumber 提取文本（更好的文本提取质量）
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
        except Exception as e:
            print(f"pdfplumber 提取失败，使用 PyMuPDF: {e}")
            # 备用方案：使用 PyMuPDF
            doc = fitz.open(pdf_path)
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
        
        full_text = "\n\n".join(text_parts)
        
        # 清理文本
        full_text = self._clean_text(full_text)
        
        return full_text
    
    def _extract_text_blocks(self, page: fitz.Page, page_num: int) -> List[TextBlock]:
        """提取页面的文本块"""
        blocks = []
        
        # 获取文本块（带格式信息）
        text_dict = page.get_text("dict")
        
        for block in text_dict.get("blocks", []):
            if block.get("type") == 0:  # 文本块
                for line in block.get("lines", []):
                    line_text = ""
                    font_size = 12.0
                    font_name = ""
                    
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")
                        font_size = span.get("size", 12.0)
                        font_name = span.get("font", "")
                    
                    if line_text.strip():
                        bbox = tuple(line.get("bbox", (0, 0, 0, 0)))
                        blocks.append(TextBlock(
                            page_num=page_num,
                            bbox=bbox,
                            text=line_text,
                            font_size=font_size,
                            font_name=font_name,
                            is_bold="bold" in font_name.lower(),
                            is_italic="italic" in font_name.lower()
                        ))
        
        return blocks
    
    def _extract_images(self, page: fitz.Page, page_num: int) -> List[ImageBlock]:
        """提取页面的图片"""
        images = []
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                
                image_data = base_image["image"]
                image_format = base_image["ext"]
                
                # 获取图片位置（近似）
                # 注意：精确的图片位置需要更复杂的解析
                bbox = (0, 0, 100, 100)  # 占位符
                
                images.append(ImageBlock(
                    page_num=page_num,
                    bbox=bbox,
                    image_data=image_data,
                    image_format=image_format
                ))
            except Exception as e:
                print(f"提取图片失败 (page {page_num}, img {img_index}): {e}")
        
        return images
    
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
    
    def identify_formulas(self, text: str) -> List[Tuple[str, int, int]]:
        """
        识别文本中的公式
        
        Args:
            text: 文本内容
            
        Returns:
            (公式, 起始位置, 结束位置) 的列表
        """
        formulas = []
        
        # 识别 LaTeX 公式
        # 行内公式: $...$
        for match in re.finditer(r'\$([^\$]+)\$', text):
            formulas.append((match.group(0), match.start(), match.end()))
        
        # 行间公式: $$...$$
        for match in re.finditer(r'\$\$([^\$]+)\$\$', text):
            formulas.append((match.group(0), match.start(), match.end()))
        
        # 识别常见的数学符号密集区域
        # 如: α, β, γ, ∑, ∫, ∂, ∇ 等
        math_pattern = r'[α-ωΑ-Ω∑∫∂∇±≤≥≈≠∞√∏]+'
        for match in re.finditer(math_pattern, text):
            formulas.append((match.group(0), match.start(), match.end()))
        
        return formulas


def test_parser():
    """测试解析器"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python pdf_parser.py <pdf_file>")
        return
    
    pdf_path = sys.argv[1]
    parser = PDFParser()
    
    # 测试文本提取
    text = parser.extract_text(pdf_path)
    print("=" * 50)
    print("提取的文本:")
    print("=" * 50)
    print(text[:1000])  # 只显示前1000字符
    print("...")
    print(f"\n总字符数: {len(text)}")
    
    # 测试结构化解析
    doc = parser.parse(pdf_path)
    print("\n" + "=" * 50)
    print("文档结构:")
    print("=" * 50)
    print(f"文件名: {doc.filename}")
    print(f"总页数: {doc.total_pages}")
    print(f"元素数: {len(doc.elements)}")
    
    # 统计元素类型
    text_blocks = sum(1 for e in doc.elements if isinstance(e, TextBlock))
    image_blocks = sum(1 for e in doc.elements if isinstance(e, ImageBlock))
    print(f"文本块: {text_blocks}")
    print(f"图片块: {image_blocks}")


if __name__ == "__main__":
    test_parser()

