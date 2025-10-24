"""
PDF 生成模块 v3
支持文本、图像、表格的混合渲染
"""

import os
import re
from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PDFGeneratorV3:
    """支持图像和表格的 PDF 生成器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化生成器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.page_width, self.page_height = A4
        self.margin = 2 * cm
        self.content_width = self.page_width - 2 * self.margin
        
        # 注册中文字体
        self._register_fonts()
        
        # 创建样式
        self.styles = self._create_styles()
    
    def _register_fonts(self):
        """注册中文字体"""
        font_paths = [
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/truetype/arphic/uming.ttc',
            '/System/Library/Fonts/PingFang.ttc',
            'C:\\Windows\\Fonts\\msyh.ttc',
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    print(f"成功注册字体: {font_path}")
                    return
                except Exception as e:
                    print(f"注册字体失败 {font_path}: {e}")
        
        print("警告: 未找到中文字体，可能无法正确显示中文")
    
    def _create_styles(self):
        """创建文档样式"""
        styles = getSampleStyleSheet()
        
        # 标题样式
        styles.add(ParagraphStyle(
            name='ChineseHeading1',
            parent=styles['Heading1'],
            fontName='ChineseFont',
            fontSize=20,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=20,
            textColor=colors.HexColor('#1a1a2e')
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseHeading2',
            parent=styles['Heading2'],
            fontName='ChineseFont',
            fontSize=16,
            leading=22,
            spaceAfter=14,
            textColor=colors.HexColor('#16213e')
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseHeading3',
            parent=styles['Heading3'],
            fontName='ChineseFont',
            fontSize=14,
            leading=20,
            spaceAfter=12,
            textColor=colors.HexColor('#0f3460')
        ))
        
        # 正文样式
        styles.add(ParagraphStyle(
            name='ChineseBody',
            parent=styles['BodyText'],
            fontName='ChineseFont',
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            firstLineIndent=22,  # 首行缩进
            spaceAfter=10
        ))
        
        # 公式样式
        styles.add(ParagraphStyle(
            name='Formula',
            parent=styles['BodyText'],
            fontName='ChineseFont',
            fontSize=11,
            leading=16,
            alignment=TA_CENTER,
            fontStyle='italic',
            spaceAfter=12,
            spaceBefore=12
        ))
        
        return styles
    
    def generate_from_markdown(self, markdown_text: str, output_path: str, images: List[str] = None, tables: List[Any] = None):
        """
        从 Markdown 文本生成 PDF（支持图像和表格）
        
        Args:
            markdown_text: Markdown 格式的文本
            output_path: 输出 PDF 路径
            images: 图像路径列表
            tables: 表格数据列表
        """
        print(f"正在生成 PDF: {output_path}")
        
        # 创建 PDF 文档
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        # 构建内容
        story = []
        
        # 解析 Markdown 并生成内容
        sections = self._parse_markdown(markdown_text)
        
        image_index = 0
        table_index = 0
        
        for section in sections:
            if section['type'] == 'heading1':
                story.append(Paragraph(section['content'], self.styles['ChineseHeading1']))
                story.append(Spacer(1, 0.3 * cm))
            
            elif section['type'] == 'heading2':
                story.append(Paragraph(section['content'], self.styles['ChineseHeading2']))
                story.append(Spacer(1, 0.2 * cm))
            
            elif section['type'] == 'heading3':
                story.append(Paragraph(section['content'], self.styles['ChineseHeading3']))
                story.append(Spacer(1, 0.15 * cm))
            
            elif section['type'] == 'paragraph':
                # 处理行内公式
                content = self._process_inline_formulas(section['content'])
                story.append(Paragraph(content, self.styles['ChineseBody']))
            
            elif section['type'] == 'formula_block':
                # 转换 LaTeX 符号
                formula = self._latex_to_unicode(section['content'])
                story.append(Paragraph(formula, self.styles['Formula']))
            
            elif section['type'] == 'image_placeholder':
                # 插入图像
                if images and image_index < len(images):
                    img_path = images[image_index]
                    if os.path.exists(img_path):
                        try:
                            img = Image(img_path)
                            # 调整图像大小以适应页面宽度
                            img_width, img_height = img.imageWidth, img.imageHeight
                            if img_width > self.content_width:
                                ratio = self.content_width / img_width
                                img.drawWidth = self.content_width
                                img.drawHeight = img_height * ratio
                            story.append(img)
                            story.append(Spacer(1, 0.3 * cm))
                        except Exception as e:
                            print(f"插入图像失败 {img_path}: {e}")
                    image_index += 1
            
            elif section['type'] == 'table_placeholder':
                # 插入表格
                if tables and table_index < len(tables):
                    table_data = tables[table_index]
                    if table_data:
                        table = self._create_table(table_data)
                        story.append(table)
                        story.append(Spacer(1, 0.3 * cm))
                    table_index += 1
        
        # 生成 PDF
        doc.build(story)
        print(f"PDF 生成成功: {output_path}")
    
    def generate_from_elements(self, elements: List[Any], translated_texts: Dict[int, str], output_path: str):
        """
        从解析的元素列表生成 PDF
        
        Args:
            elements: PDF 元素列表（TextElement, ImageElement, TableElement）
            translated_texts: 翻译后的文本字典 {元素索引: 翻译文本}
            output_path: 输出 PDF 路径
        """
        print(f"正在生成 PDF: {output_path}")
        
        # 创建 PDF 文档
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        story = []
        current_page = -1
        
        for i, elem in enumerate(elements):
            # 检测换页
            if elem.page_num > current_page:
                if current_page >= 0:
                    story.append(PageBreak())
                current_page = elem.page_num
            
            if elem.element_type == 'text':
                # 获取翻译文本
                text = translated_texts.get(i, elem.text)
                
                # 处理 Markdown 格式
                if text.startswith('# '):
                    style = self.styles['ChineseHeading1']
                    text = text[2:].strip()
                elif text.startswith('## '):
                    style = self.styles['ChineseHeading2']
                    text = text[3:].strip()
                elif text.startswith('### '):
                    style = self.styles['ChineseHeading3']
                    text = text[4:].strip()
                elif elem.is_heading:
                    style = self.styles['ChineseHeading2']
                else:
                    style = self.styles['ChineseBody']
                    text = self._process_inline_formulas(text)
                
                story.append(Paragraph(text, style))
                story.append(Spacer(1, 0.1 * cm))
            
            elif elem.element_type == 'image':
                # 插入图像
                if os.path.exists(elem.image_path):
                    try:
                        img = Image(elem.image_path)
                        # 调整图像大小
                        if img.imageWidth > self.content_width:
                            ratio = self.content_width / img.imageWidth
                            img.drawWidth = self.content_width
                            img.drawHeight = img.imageHeight * ratio
                        else:
                            img.drawWidth = img.imageWidth
                            img.drawHeight = img.imageHeight
                        
                        story.append(img)
                        story.append(Spacer(1, 0.3 * cm))
                    except Exception as e:
                        print(f"插入图像失败 {elem.image_path}: {e}")
            
            elif elem.element_type == 'table':
                # 插入表格
                table = self._create_table_from_element(elem, translated_texts, i)
                if table:
                    story.append(table)
                    story.append(Spacer(1, 0.3 * cm))
        
        # 生成 PDF
        doc.build(story)
        print(f"PDF 生成成功: {output_path}")
    
    def _parse_markdown(self, text: str) -> List[Dict]:
        """解析 Markdown 文本"""
        sections = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # 检测多行行间公式
            if line == '$$':
                formula_lines = []
                i += 1
                while i < len(lines):
                    if lines[i].strip() == '$$':
                        break
                    formula_lines.append(lines[i].strip())
                    i += 1
                formula = ' '.join(formula_lines).strip()
                sections.append({'type': 'formula_block', 'content': formula})
                i += 1
                continue
            
            # 检测单行行间公式
            if line.startswith('$$') and line.endswith('$$') and len(line) > 4:
                formula = line[2:-2].strip()
                sections.append({'type': 'formula_block', 'content': formula})
                i += 1
                continue
            
            # 检测 Markdown 标题
            if line.startswith('# '):
                sections.append({'type': 'heading1', 'content': line[2:].strip()})
                i += 1
                continue
            
            if line.startswith('## '):
                sections.append({'type': 'heading2', 'content': line[3:].strip()})
                i += 1
                continue
            
            if line.startswith('### '):
                sections.append({'type': 'heading3', 'content': line[4:].strip()})
                i += 1
                continue
            
            # 检测图像占位符
            if line.startswith('[IMAGE'):
                sections.append({'type': 'image_placeholder', 'content': line})
                i += 1
                continue
            
            # 检测表格占位符
            if line.startswith('[TABLE'):
                sections.append({'type': 'table_placeholder', 'content': line})
                i += 1
                continue
            
            # 普通段落
            para_lines = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line or next_line.startswith('#') or next_line == '$$' or next_line.startswith('['):
                    break
                para_lines.append(next_line)
                i += 1
            
            paragraph = ' '.join(para_lines)
            sections.append({'type': 'paragraph', 'content': paragraph})
        
        return sections
    
    def _process_inline_formulas(self, text: str) -> str:
        """处理行内公式"""
        # 查找 $...$ 格式的行内公式
        def replace_formula(match):
            formula = match.group(1)
            # 转换 LaTeX 符号
            formula = self._latex_to_unicode(formula)
            return f'<i>{formula}</i>'
        
        text = re.sub(r'\$([^\$]+)\$', replace_formula, text)
        return text
    
    def _latex_to_unicode(self, latex_text: str) -> str:
        """将 LaTeX 符号转换为 Unicode"""
        # LaTeX 符号映射表
        latex_symbols = {
            # 希腊字母（小写）
            r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ',
            r'\epsilon': 'ε', r'\zeta': 'ζ', r'\eta': 'η', r'\theta': 'θ',
            r'\iota': 'ι', r'\kappa': 'κ', r'\lambda': 'λ', r'\mu': 'μ',
            r'\nu': 'ν', r'\xi': 'ξ', r'\pi': 'π', r'\rho': 'ρ',
            r'\sigma': 'σ', r'\tau': 'τ', r'\upsilon': 'υ', r'\phi': 'φ',
            r'\chi': 'χ', r'\psi': 'ψ', r'\omega': 'ω',
            
            # 希腊字母（大写）
            r'\Gamma': 'Γ', r'\Delta': 'Δ', r'\Theta': 'Θ', r'\Lambda': 'Λ',
            r'\Xi': 'Ξ', r'\Pi': 'Π', r'\Sigma': 'Σ', r'\Phi': 'Φ',
            r'\Psi': 'Ψ', r'\Omega': 'Ω',
            
            # 数学运算符
            r'\nabla': '∇', r'\partial': '∂', r'\infty': '∞',
            r'\sum': '∑', r'\prod': '∏', r'\int': '∫',
            r'\pm': '±', r'\mp': '∓', r'\times': '×', r'\div': '÷',
            r'\cdot': '·', r'\circ': '∘',
            
            # 关系符号
            r'\leq': '≤', r'\geq': '≥', r'\neq': '≠', r'\approx': '≈',
            r'\equiv': '≡', r'\sim': '∼', r'\propto': '∝',
            r'\in': '∈', r'\notin': '∉', r'\subset': '⊂', r'\supset': '⊃',
            
            # 箭头
            r'\rightarrow': '→', r'\leftarrow': '←', r'\Rightarrow': '⇒', r'\Leftarrow': '⇐',
            r'\leftrightarrow': '↔', r'\Leftrightarrow': '⇔',
            
            # 集合符号
            r'\mathbb{R}': 'ℝ', r'\mathbb{N}': 'ℕ', r'\mathbb{Z}': 'ℤ',
            r'\mathbb{Q}': 'ℚ', r'\mathbb{C}': 'ℂ', r'\mathbb{E}': '𝔼',
            
            # 其他符号
            r'\sqrt': '√', r'\emptyset': '∅', r'\forall': '∀', r'\exists': '∃',
            r'\neg': '¬', r'\wedge': '∧', r'\vee': '∨',
        }
        
        # 替换符号
        for latex, unicode_char in latex_symbols.items():
            latex_text = latex_text.replace(latex, unicode_char)
        
        # 处理下标和上标
        latex_text = re.sub(r'_\{([^}]+)\}', r'_\1', latex_text)
        latex_text = re.sub(r'\^\{([^}]+)\}', r'^\1', latex_text)
        
        # 处理分数
        latex_text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', latex_text)
        
        # 移除常见的 LaTeX 命令
        latex_text = re.sub(r'\\left[\(\[\{]', lambda m: m.group(0)[-1], latex_text)
        latex_text = re.sub(r'\\right[\)\]\}]', lambda m: m.group(0)[-1], latex_text)
        latex_text = latex_text.replace(r'\,', ' ')
        latex_text = latex_text.replace(r'\;', ' ')
        latex_text = latex_text.replace(r'\quad', '  ')
        latex_text = latex_text.replace(r'\qquad', '    ')
        
        # 移除剩余的反斜杠命令
        latex_text = re.sub(r'\\[a-zA-Z]+', '', latex_text)
        
        return latex_text
    
    def _create_table(self, table_data: List[List[str]]) -> Table:
        """创建表格"""
        if not table_data:
            return None
        
        # 创建表格
        table = Table(table_data)
        
        # 设置表格样式
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        return table
    
    def _create_table_from_element(self, elem: Any, translated_texts: Dict, elem_index: int) -> Table:
        """从表格元素创建表格"""
        table_data = []
        
        # 添加表头
        if elem.header:
            table_data.append(elem.header)
        
        # 添加数据行
        table_data.extend(elem.data)
        
        return self._create_table(table_data)


def test_generator_v3():
    """测试生成器 v3"""
    generator = PDFGeneratorV3()
    
    # 测试 Markdown 生成
    markdown_text = """# 测试文档

## 第一章

这是一个段落，包含行内公式 $x^2 + y^2 = z^2$。

$$
\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}
$$

### 1.1 小节

另一个段落。

[IMAGE]

[TABLE]
"""
    
    # 测试图像
    test_images = []
    
    # 测试表格
    test_tables = [
        [['列1', '列2', '列3'],
         ['数据1', '数据2', '数据3'],
         ['数据4', '数据5', '数据6']]
    ]
    
    output_path = "/tmp/test_generator_v3.pdf"
    generator.generate_from_markdown(markdown_text, output_path, test_images, test_tables)
    print(f"测试 PDF 已生成: {output_path}")


if __name__ == "__main__":
    test_generator_v3()

