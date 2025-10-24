"""
PDF 生成模块（增强版）
基于 v2，添加图像和表格支持
"""

import os
import re
import fitz  # PyMuPDF
import pdfplumber
from typing import List, Dict, Tuple
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class EnhancedPDFGenerator:
    """增强的 PDF 生成器（基于 v2 + 图像表格支持）"""
    
    def __init__(self, config: Dict = None):
        """初始化生成器"""
        self.config = config or {}
        self.page_width, self.page_height = A4
        self.margin = 2 * cm
        self.content_width = self.page_width - 2 * self.margin
        
        # 注册中文字体
        self._register_fonts()
        
        # 创建样式
        self.styles = self._create_styles()
        
        # 图像和表格缓存
        self.images = []
        self.tables = []
    
    def _register_fonts(self):
        """注册中文字体（跨平台支持）"""
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
        import platform
        
        # 根据操作系统选择字体路径
        system = platform.system()
        
        if system == 'Windows':
            # Windows 字体路径
            font_paths = [
                'C:/Windows/Fonts/msyh.ttc',      # 微软雅黑
                'C:/Windows/Fonts/simsun.ttc',    # 宋体
                'C:/Windows/Fonts/simhei.ttf',    # 黑体
                'C:/Windows/Fonts/simkai.ttf',    # 楷体
            ]
        elif system == 'Darwin':  # macOS
            # macOS 字体路径
            font_paths = [
                '/System/Library/Fonts/PingFang.ttc',
                '/Library/Fonts/Songti.ttc',
                '/System/Library/Fonts/STHeiti Light.ttc',
            ]
        else:  # Linux
            # Linux 字体路径
            font_paths = [
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                '/usr/share/fonts/truetype/arphic/uming.ttc',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            ]
        
        # 尝试注册字体
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # 注册常规字体
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    # 注册字体家族（粗体、斜体都使用同一字体）
                    registerFontFamily(
                        'ChineseFont',
                        normal='ChineseFont',
                        bold='ChineseFont',
                        italic='ChineseFont',
                        boldItalic='ChineseFont'
                    )
                    print(f"成功注册字体: {font_path} (系统: {system})")
                    return
                except Exception as e:
                    print(f"字体注册失败: {font_path}, 错误: {e}")
                    pass
        
        # 如果所有字体都失败，使用 Helvetica 作为后备
        print(f"警告: 未找到中文字体，使用默认字体 (系统: {system})")
        print("请确保系统已安装中文字体")
        # 注册后备字体家族
        registerFontFamily(
            'ChineseFont',
            normal='Helvetica',
            bold='Helvetica-Bold',
            italic='Helvetica-Oblique',
            boldItalic='Helvetica-BoldOblique'
        )
    
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
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseHeading2',
            parent=styles['Heading2'],
            fontName='ChineseFont',
            fontSize=16,
            leading=22,
            spaceAfter=14,
        ))
        
        styles.add(ParagraphStyle(
            name='ChineseHeading3',
            parent=styles['Heading3'],
            fontName='ChineseFont',
            fontSize=14,
            leading=20,
            spaceAfter=12,
        ))
        
        # 正文样式
        styles.add(ParagraphStyle(
            name='ChineseBody',
            parent=styles['BodyText'],
            fontName='ChineseFont',
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            firstLineIndent=22,
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
    
    def extract_images_and_tables(self, pdf_path: str):
        """
        从原始 PDF 提取图像和表格
        
        Args:
            pdf_path: 原始 PDF 路径
        """
        print(f"  提取图像和表格...")
        
        # 提取图像
        self.images = self._extract_images(pdf_path)
        print(f"    找到 {len(self.images)} 个图像")
        
        # 提取表格
        self.tables = self._extract_tables(pdf_path)
        print(f"    找到 {len(self.tables)} 个表格")
    
    def _extract_images(self, pdf_path: str) -> List[str]:
        """提取 PDF 中的图像"""
        images = []
        
        try:
            doc = fitz.open(pdf_path)
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_dir = f"/tmp/{pdf_name}_images"
            os.makedirs(output_dir, exist_ok=True)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_data = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        image_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
                        image_path = os.path.join(output_dir, image_filename)
                        
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_data)
                        
                        images.append(image_path)
                    except:
                        pass
            
            doc.close()
        except Exception as e:
            print(f"    图像提取失败: {e}")
        
        return images
    
    def _extract_tables(self, pdf_path: str) -> List[List[List[str]]]:
        """提取 PDF 中的表格"""
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
        except Exception as e:
            print(f"    表格提取失败: {e}")
        
        return tables
    
    def generate_from_markdown(self, markdown_text: str, output_path: str, original_pdf_path: str = None):
        """
        从 Markdown 文本生成 PDF（支持图像和表格）
        
        Args:
            markdown_text: Markdown 格式的文本
            output_path: 输出 PDF 路径
            original_pdf_path: 原始 PDF 路径（用于提取图像和表格）
        """
        print(f"正在生成 PDF: {output_path}")
        
        # 如果提供了原始 PDF，提取图像和表格
        if original_pdf_path and os.path.exists(original_pdf_path):
            self.extract_images_and_tables(original_pdf_path)
        
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
                content = self._process_inline_formulas(section['content'])
                story.append(Paragraph(content, self.styles['ChineseBody']))
            
            elif section['type'] == 'formula_block':
                formula = self._latex_to_unicode(section['content'])
                story.append(Paragraph(formula, self.styles['Formula']))
            
            elif section['type'] == 'figure_reference':
                # 检测到图表引用，插入图像
                if image_index < len(self.images):
                    img_path = self.images[image_index]
                    if os.path.exists(img_path):
                        try:
                            img = Image(img_path)
                            # 调整大小
                            if img.imageWidth > self.content_width:
                                ratio = self.content_width / img.imageWidth
                                img.drawWidth = self.content_width
                                img.drawHeight = img.imageHeight * ratio
                            story.append(img)
                            story.append(Spacer(1, 0.3 * cm))
                        except:
                            pass
                    image_index += 1
                # 同时保留图表标题
                content = self._process_inline_formulas(section['content'])
                story.append(Paragraph(content, self.styles['ChineseBody']))
            
            elif section['type'] == 'table_reference':
                # 检测到表格引用，插入表格
                if table_index < len(self.tables):
                    table_data = self.tables[table_index]
                    if table_data:
                        table = self._create_table(table_data)
                        story.append(table)
                        story.append(Spacer(1, 0.3 * cm))
                    table_index += 1
                # 同时保留表格标题
                content = self._process_inline_formulas(section['content'])
                story.append(Paragraph(content, self.styles['ChineseBody']))
        
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
            
            # 检测图表引用（Figure, 图）
            if re.search(r'(Figure|图|Fig\.)\s*\d+', line, re.IGNORECASE):
                sections.append({'type': 'figure_reference', 'content': line})
                i += 1
                continue
            
            # 检测表格引用（Table, 表）
            if re.search(r'(Table|表)\s*\d+', line, re.IGNORECASE):
                sections.append({'type': 'table_reference', 'content': line})
                i += 1
                continue
            
            # 普通段落
            para_lines = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line or next_line.startswith('#') or next_line == '$$' or \
                   re.search(r'(Figure|Table|图|表)\s*\d+', next_line, re.IGNORECASE):
                    break
                para_lines.append(next_line)
                i += 1
            
            paragraph = ' '.join(para_lines)
            sections.append({'type': 'paragraph', 'content': paragraph})
        
        return sections
    
    def _process_inline_formulas(self, text: str) -> str:
        """处理行内公式"""
        def replace_formula(match):
            formula = match.group(1)
            formula = self._latex_to_unicode(formula)
            return f'<i>{formula}</i>'
        
        text = re.sub(r'\$([^\$]+)\$', replace_formula, text)
        return text
    
    def _latex_to_unicode(self, latex_text: str) -> str:
        """将 LaTeX 符号转换为 Unicode"""
        latex_symbols = {
            r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ', r'\delta': 'δ',
            r'\epsilon': 'ε', r'\zeta': 'ζ', r'\eta': 'η', r'\theta': 'θ',
            r'\iota': 'ι', r'\kappa': 'κ', r'\lambda': 'λ', r'\mu': 'μ',
            r'\nu': 'ν', r'\xi': 'ξ', r'\pi': 'π', r'\rho': 'ρ',
            r'\sigma': 'σ', r'\tau': 'τ', r'\upsilon': 'υ', r'\phi': 'φ',
            r'\chi': 'χ', r'\psi': 'ψ', r'\omega': 'ω',
            r'\Gamma': 'Γ', r'\Delta': 'Δ', r'\Theta': 'Θ', r'\Lambda': 'Λ',
            r'\Xi': 'Ξ', r'\Pi': 'Π', r'\Sigma': 'Σ', r'\Phi': 'Φ',
            r'\Psi': 'Ψ', r'\Omega': 'Ω',
            r'\nabla': '∇', r'\partial': '∂', r'\infty': '∞',
            r'\sum': '∑', r'\prod': '∏', r'\int': '∫',
            r'\pm': '±', r'\mp': '∓', r'\times': '×', r'\div': '÷',
            r'\cdot': '·', r'\circ': '∘',
            r'\leq': '≤', r'\geq': '≥', r'\neq': '≠', r'\approx': '≈',
            r'\equiv': '≡', r'\sim': '∼', r'\propto': '∝',
            r'\in': '∈', r'\notin': '∉', r'\subset': '⊂', r'\supset': '⊃',
            r'\rightarrow': '→', r'\leftarrow': '←', r'\Rightarrow': '⇒',
            r'\mathbb{R}': 'ℝ', r'\mathbb{N}': 'ℕ', r'\mathbb{Z}': 'ℤ',
            r'\mathbb{Q}': 'ℚ', r'\mathbb{C}': 'ℂ', r'\mathbb{E}': '𝔼',
            r'\sqrt': '√', r'\emptyset': '∅', r'\forall': '∀', r'\exists': '∃',
        }
        
        for latex, unicode_char in latex_symbols.items():
            latex_text = latex_text.replace(latex, unicode_char)
        
        latex_text = re.sub(r'_\{([^}]+)\}', r'_\1', latex_text)
        latex_text = re.sub(r'\^\{([^}]+)\}', r'^\1', latex_text)
        latex_text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', latex_text)
        latex_text = re.sub(r'\\left[\(\[\{]', lambda m: m.group(0)[-1], latex_text)
        latex_text = re.sub(r'\\right[\)\]\}]', lambda m: m.group(0)[-1], latex_text)
        latex_text = re.sub(r'\\[a-zA-Z]+', '', latex_text)
        
        return latex_text
    
    def _create_table(self, table_data: List[List[str]]) -> Table:
        """创建表格"""
        if not table_data:
            return None
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        return table

