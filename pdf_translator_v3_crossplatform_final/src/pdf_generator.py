"""
PDF 生成模块
根据翻译结果生成新的 PDF 文件
"""

import fitz  # PyMuPDF
import os
from typing import List, Dict, Optional
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER


class PDFGenerator:
    """PDF 生成器"""
    
    def __init__(self, config: Dict):
        """
        初始化生成器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.setup_fonts()
    
    def setup_fonts(self):
        """设置中文字体"""
        try:
            # 尝试注册常见的中文字体
            font_paths = [
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
                '/usr/share/fonts/truetype/arphic/uming.ttc',
                '/System/Library/Fonts/STHeiti Light.ttc',  # macOS
                'C:/Windows/Fonts/msyh.ttc',  # Windows
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('Chinese', font_path))
                        print(f"成功注册字体: {font_path}")
                        return
                    except Exception as e:
                        print(f"注册字体失败 {font_path}: {e}")
                        continue
            
            print("警告: 未找到中文字体，将使用默认字体")
        except Exception as e:
            print(f"字体设置错误: {e}")
    
    def generate_simple_pdf(self, translated_text: str, output_path: str, 
                           original_pdf_path: Optional[str] = None):
        """
        生成简单的 PDF（纯文本，不保留复杂格式）
        
        Args:
            translated_text: 翻译后的文本
            output_path: 输出文件路径
            original_pdf_path: 原始 PDF 路径（用于提取元数据）
        """
        print(f"正在生成 PDF: {output_path}")
        
        # 创建 PDF 文档
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # 准备样式
        styles = self._create_styles()
        
        # 构建内容
        story = []
        
        # 分段处理文本
        paragraphs = translated_text.split('\n\n')
        
        for para_text in paragraphs:
            if not para_text.strip():
                continue
            
            # 判断段落类型
            if self._is_title(para_text):
                style = styles['Title']
            elif self._is_heading(para_text):
                style = styles['Heading']
            else:
                style = styles['Normal']
            
            # 创建段落
            para = Paragraph(para_text.strip(), style)
            story.append(para)
            story.append(Spacer(1, 0.2 * inch))
        
        # 生成 PDF
        try:
            doc.build(story)
            print(f"PDF 生成成功: {output_path}")
        except Exception as e:
            print(f"PDF 生成失败: {e}")
            raise
    
    def generate_formatted_pdf(self, original_pdf_path: str, translated_text: str, 
                              output_path: str):
        """
        生成保留格式的 PDF（使用 PyMuPDF）
        
        Args:
            original_pdf_path: 原始 PDF 路径
            translated_text: 翻译后的文本
            output_path: 输出文件路径
        """
        print(f"正在生成格式化 PDF: {output_path}")
        
        # 打开原始 PDF
        original_doc = fitz.open(original_pdf_path)
        
        # 创建新文档
        new_doc = fitz.open()
        
        # 分段翻译文本
        paragraphs = translated_text.split('\n\n')
        para_index = 0
        
        for page_num in range(len(original_doc)):
            original_page = original_doc[page_num]
            
            # 创建新页面（相同尺寸）
            new_page = new_doc.new_page(
                width=original_page.rect.width,
                height=original_page.rect.height
            )
            
            # 复制图片（如果有）
            self._copy_images(original_page, new_page)
            
            # 获取原始页面的文本块
            blocks = original_page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block.get("type") == 0:  # 文本块
                    if para_index < len(paragraphs):
                        # 获取文本块的位置和字体信息
                        bbox = block["bbox"]
                        
                        # 获取字体信息
                        font_size = 12
                        if block.get("lines"):
                            first_line = block["lines"][0]
                            if first_line.get("spans"):
                                font_size = first_line["spans"][0].get("size", 12)
                        
                        # 插入翻译后的文本
                        try:
                            new_page.insert_textbox(
                                bbox,
                                paragraphs[para_index],
                                fontsize=font_size,
                                fontname="china-s",  # 中文字体
                                align=fitz.TEXT_ALIGN_LEFT
                            )
                        except Exception as e:
                            # 如果中文字体失败，使用默认字体
                            new_page.insert_textbox(
                                bbox,
                                paragraphs[para_index],
                                fontsize=font_size,
                                align=fitz.TEXT_ALIGN_LEFT
                            )
                        
                        para_index += 1
        
        # 保存新文档
        new_doc.save(output_path)
        new_doc.close()
        original_doc.close()
        
        print(f"格式化 PDF 生成成功: {output_path}")
    
    def _copy_images(self, source_page: fitz.Page, target_page: fitz.Page):
        """从源页面复制图片到目标页面"""
        try:
            image_list = source_page.get_images()
            
            for img in image_list:
                xref = img[0]
                # 获取图片
                base_image = source_page.parent.extract_image(xref)
                image_bytes = base_image["image"]
                
                # 在目标页面插入图片
                # 注意：这是简化版本，实际位置可能需要更精确的计算
                target_page.insert_image(
                    target_page.rect,
                    stream=image_bytes
                )
        except Exception as e:
            print(f"复制图片时出错: {e}")
    
    def _create_styles(self) -> Dict:
        """创建段落样式"""
        styles = getSampleStyleSheet()
        
        # 尝试使用中文字体
        try:
            font_name = 'Chinese'
            pdfmetrics.getFont(font_name)
        except:
            font_name = 'Helvetica'
        
        # 修改现有的正文样式
        styles['Normal'].fontName = font_name
        styles['Normal'].fontSize = 11
        styles['Normal'].leading = 16
        styles['Normal'].alignment = TA_JUSTIFY
        styles['Normal'].spaceAfter = 6
        
        # 修改现有的标题样式
        styles['Title'].fontName = font_name
        styles['Title'].fontSize = 18
        styles['Title'].leading = 22
        styles['Title'].alignment = TA_CENTER
        styles['Title'].spaceAfter = 12
        
        # 添加自定义小标题样式
        if 'Heading' not in styles:
            styles.add(ParagraphStyle(
                name='Heading',
                parent=styles['Heading2'],
                fontName=font_name,
                fontSize=14,
                leading=18,
                spaceAfter=8,
                textColor='#000000',
            ))
        
        return styles
    
    def _is_title(self, text: str) -> bool:
        """判断是否为标题"""
        # 简单启发式：短文本且全大写或首字母大写
        return len(text) < 100 and (text.isupper() or text.istitle())
    
    def _is_heading(self, text: str) -> bool:
        """判断是否为小标题"""
        # 简单启发式：以数字或特殊标记开头
        import re
        return bool(re.match(r'^(\d+\.|\d+\)|\*|\-|#)', text.strip()))


def test_generator():
    """测试生成器"""
    config = {}
    generator = PDFGenerator(config)
    
    # 测试文本
    test_text = """机器学习简介

机器学习是人工智能的一个子集，专注于开发算法和统计模型。

1. 监督学习
监督学习使用标记的训练数据来学习输入和输出之间的映射关系。

2. 无监督学习
无监督学习从未标记的数据中发现隐藏的模式和结构。

结论

机器学习在现代技术中扮演着重要角色。"""
    
    output_path = "/home/ubuntu/pdf_translator/test_output.pdf"
    generator.generate_simple_pdf(test_text, output_path)
    print(f"测试 PDF 已生成: {output_path}")


if __name__ == "__main__":
    test_generator()

