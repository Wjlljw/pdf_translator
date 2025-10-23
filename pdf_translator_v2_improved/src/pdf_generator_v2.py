"""
改进的 PDF 生成模块
支持 LaTeX 公式渲染和 Markdown 格式
"""

import os
import re
import subprocess
from typing import Dict, Optional, List, Tuple
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor


class ImprovedPDFGenerator:
    """改进的 PDF 生成器，支持 LaTeX 公式和规范格式"""
    
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
    
    def generate_pdf(self, translated_text: str, output_path: str, 
                    original_pdf_path: Optional[str] = None):
        """
        生成 PDF（支持 LaTeX 公式和 Markdown 格式）
        
        Args:
            translated_text: 翻译后的文本
            output_path: 输出文件路径
            original_pdf_path: 原始 PDF 路径（用于提取元数据）
        """
        print(f"正在生成 PDF: {output_path}")
        
        # 预处理文本：处理 LaTeX 公式和 Markdown 格式
        processed_text = self._preprocess_text(translated_text)
        
        # 解析文档结构
        sections = self._parse_document_structure(processed_text)
        
        # 创建 PDF 文档
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )
        
        # 准备样式
        styles = self._create_styles()
        
        # 构建内容
        story = []
        
        for section in sections:
            section_type = section['type']
            content = section['content']
            
            if section_type == 'title':
                para = Paragraph(content, styles['Title'])
                story.append(para)
                story.append(Spacer(1, 0.5 * cm))
            
            elif section_type == 'heading1':
                para = Paragraph(content, styles['Heading1'])
                story.append(para)
                story.append(Spacer(1, 0.3 * cm))
            
            elif section_type == 'heading2':
                para = Paragraph(content, styles['Heading2'])
                story.append(para)
                story.append(Spacer(1, 0.25 * cm))
            
            elif section_type == 'heading3':
                para = Paragraph(content, styles['Heading3'])
                story.append(para)
                story.append(Spacer(1, 0.2 * cm))
            
            elif section_type == 'formula_block':
                # 行间公式：居中显示，使用特殊样式
                # 转换 LaTeX 符号为 Unicode
                unicode_formula = self._latex_to_unicode(content)
                # 转义 XML 特殊字符
                unicode_formula = unicode_formula.replace('&', '&amp;')
                unicode_formula = unicode_formula.replace('<', '&lt;')
                unicode_formula = unicode_formula.replace('>', '&gt;')
                formula_text = f"<i>{unicode_formula}</i>"
                para = Paragraph(formula_text, styles['Formula'])
                story.append(para)
                story.append(Spacer(1, 0.3 * cm))
            
            elif section_type == 'paragraph':
                # 处理段落中的行内公式
                processed_content = self._format_inline_formulas(content)
                para = Paragraph(processed_content, styles['Normal'])
                story.append(para)
                story.append(Spacer(1, 0.2 * cm))
            
            elif section_type == 'list_item':
                para = Paragraph(f"• {content}", styles['ListItem'])
                story.append(para)
                story.append(Spacer(1, 0.1 * cm))
        
        # 生成 PDF
        try:
            doc.build(story)
            print(f"PDF 生成成功: {output_path}")
        except Exception as e:
            print(f"PDF 生成失败: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """
        预处理文本：清理和规范化
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        # 移除多余的空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 规范化 Markdown 标题（确保 # 后有空格）
        text = re.sub(r'^(#{1,6})([^#\s])', r'\1 \2', text, flags=re.MULTILINE)
        
        return text
    
    def _parse_document_structure(self, text: str) -> List[Dict]:
        """
        解析文档结构
        
        Args:
            text: 文本内容
            
        Returns:
            结构化的段落列表
        """
        sections = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # 检测多行行间公式（$$ 单独占一行）
            if line == '$$':
                formula_lines = []
                i += 1
                while i < len(lines):
                    if lines[i].strip() == '$$':
                        # 找到结束标记
                        break
                    formula_lines.append(lines[i].strip())
                    i += 1
                formula = ' '.join(formula_lines).strip()
                sections.append({
                    'type': 'formula_block',
                    'content': formula
                })
                i += 1  # 跳过结束的 $$
                continue
            
            # 检测单行行间公式（$$ ... $$ 在同一行）
            if line.startswith('$$') and line.endswith('$$') and len(line) > 4:
                formula = line[2:-2].strip()
                sections.append({
                    'type': 'formula_block',
                    'content': formula
                })
                i += 1
                continue
            
            # 检测 Markdown 标题
            if line.startswith('# '):
                sections.append({
                    'type': 'heading1',
                    'content': line[2:].strip()
                })
                i += 1
                continue
            
            if line.startswith('## '):
                sections.append({
                    'type': 'heading2',
                    'content': line[3:].strip()
                })
                i += 1
                continue
            
            if line.startswith('### '):
                sections.append({
                    'type': 'heading3',
                    'content': line[4:].strip()
                })
                i += 1
                continue
            
            # 检测列表项
            if re.match(r'^[\-\*\+]\s+', line):
                content = re.sub(r'^[\-\*\+]\s+', '', line)
                sections.append({
                    'type': 'list_item',
                    'content': content
                })
                i += 1
                continue
            
            # 检测数字列表
            if re.match(r'^\d+\.\s+', line):
                content = re.sub(r'^\d+\.\s+', '', line)
                sections.append({
                    'type': 'list_item',
                    'content': content
                })
                i += 1
                continue
            
            # 普通段落：收集连续的非空行
            para_lines = [line]
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                # 如果遇到空行、标题、公式或列表，停止
                if (not next_line or 
                    next_line.startswith('#') or 
                    next_line.startswith('$$') or
                    re.match(r'^[\-\*\+\d]\s+', next_line)):
                    break
                para_lines.append(next_line)
                i += 1
            
            paragraph = ' '.join(para_lines)
            sections.append({
                'type': 'paragraph',
                'content': paragraph
            })
        
        return sections
    
    def _latex_to_unicode(self, latex_text: str) -> str:
        """
        将常见的 LaTeX 符号转换为 Unicode 字符
        
        Args:
            latex_text: LaTeX 文本
            
        Returns:
            转换后的 Unicode 文本
        """
        # LaTeX 符号到 Unicode 的映射
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
            r'\Xi': 'Ξ', r'\Pi': 'Π', r'\Sigma': 'Σ', r'\Upsilon': 'Υ',
            r'\Phi': 'Φ', r'\Psi': 'Ψ', r'\Omega': 'Ω',
            
            # 数学运算符
            r'\nabla': '∇', r'\partial': '∂', r'\infty': '∞',
            r'\sum': '∑', r'\prod': '∏', r'\int': '∫',
            r'\pm': '±', r'\mp': '∓', r'\times': '×', r'\div': '÷',
            r'\cdot': '·', r'\ast': '*', r'\star': '⋆',
            
            # 关系符号
            r'\leq': '≤', r'\geq': '≥', r'\neq': '≠', r'\approx': '≈',
            r'\equiv': '≡', r'\sim': '∼', r'\propto': '∝',
            r'\in': '∈', r'\notin': '∉', r'\subset': '⊂', r'\supset': '⊃',
            r'\subseteq': '⊆', r'\supseteq': '⊇',
            
            # 箭头
            r'\rightarrow': '→', r'\leftarrow': '←', r'\Rightarrow': '⇒',
            r'\Leftarrow': '⇐', r'\leftrightarrow': '↔',
            
            # 其他符号
            r'\forall': '∀', r'\exists': '∃', r'\neg': '¬',
            r'\wedge': '∧', r'\vee': '∨', r'\cap': '∩', r'\cup': '∪',
            r'\emptyset': '∅', r'\mathbb{R}': 'ℝ', r'\mathbb{N}': 'ℕ',
            r'\mathbb{Z}': 'ℤ', r'\mathbb{Q}': 'ℚ', r'\mathbb{C}': 'ℂ',
            r'\mathbb{E}': '𝔼', r'\mathcal{L}': 'ℒ',
        }
        
        # 替换 LaTeX 符号
        for latex, unicode_char in latex_symbols.items():
            latex_text = latex_text.replace(latex, unicode_char)
        
        # 处理下标 _{...}
        latex_text = re.sub(r'_\{([^}]+)\}', r'_\1', latex_text)
        latex_text = re.sub(r'_([a-zA-Z0-9])', r'_\1', latex_text)
        
        # 处理上标 ^{...}
        latex_text = re.sub(r'\^\{([^}]+)\}', r'^\1', latex_text)
        latex_text = re.sub(r'\^([a-zA-Z0-9])', r'^\1', latex_text)
        
        # 移除常见的 LaTeX 命令
        latex_text = re.sub(r'\\left\(', '(', latex_text)
        latex_text = re.sub(r'\\right\)', ')', latex_text)
        latex_text = re.sub(r'\\left\[', '[', latex_text)
        latex_text = re.sub(r'\\right\]', ']', latex_text)
        latex_text = re.sub(r'\\left\{', '{', latex_text)
        latex_text = re.sub(r'\\right\}', '}', latex_text)
        latex_text = re.sub(r'\\left\|', '|', latex_text)
        latex_text = re.sub(r'\\right\|', '|', latex_text)
        
        # 处理分数 \frac{a}{b}
        latex_text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', latex_text)
        
        # 处理 \text{...}
        latex_text = re.sub(r'\\text\{([^}]+)\}', r'\1', latex_text)
        
        # 处理 \mathbf{...} 和 \mathrm{...}
        latex_text = re.sub(r'\\mathbf\{([^}]+)\}', r'\1', latex_text)
        latex_text = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', latex_text)
        
        # 移除剩余的反斜杠
        latex_text = re.sub(r'\\([a-zA-Z]+)', r'\1', latex_text)
        
        return latex_text
    
    def _format_inline_formulas(self, text: str) -> str:
        """
        格式化行内公式（用斜体表示）
        
        Args:
            text: 包含行内公式的文本
            
        Returns:
            格式化后的文本
        """
        # 将 $...$ 转换为斜体
        def replace_formula(match):
            formula = match.group(1)
            # 转换 LaTeX 符号为 Unicode
            formula = self._latex_to_unicode(formula)
            # 转义 XML 特殊字符
            formula = formula.replace('&', '&amp;')
            formula = formula.replace('<', '&lt;')
            formula = formula.replace('>', '&gt;')
            return f'<i>{formula}</i>'
        
        text = re.sub(r'\$([^\$]+)\$', replace_formula, text)
        
        return text
    
    def _create_styles(self) -> Dict:
        """创建段落样式"""
        styles = getSampleStyleSheet()
        
        # 尝试使用中文字体
        try:
            font_name = 'Chinese'
            pdfmetrics.getFont(font_name)
        except:
            font_name = 'Helvetica'
        
        # 正文样式
        styles['Normal'].fontName = font_name
        styles['Normal'].fontSize = 11
        styles['Normal'].leading = 18
        styles['Normal'].alignment = TA_JUSTIFY
        styles['Normal'].spaceAfter = 6
        styles['Normal'].firstLineIndent = 0.5 * cm
        
        # 标题样式
        styles['Title'].fontName = font_name
        styles['Title'].fontSize = 20
        styles['Title'].leading = 26
        styles['Title'].alignment = TA_CENTER
        styles['Title'].spaceAfter = 12
        styles['Title'].textColor = HexColor('#000000')
        styles['Title'].fontName = font_name
        
        # 一级标题
        styles['Heading1'].fontName = font_name
        styles['Heading1'].fontSize = 16
        styles['Heading1'].leading = 22
        styles['Heading1'].spaceAfter = 10
        styles['Heading1'].textColor = HexColor('#000000')
        
        # 二级标题
        styles['Heading2'].fontName = font_name
        styles['Heading2'].fontSize = 14
        styles['Heading2'].leading = 20
        styles['Heading2'].spaceAfter = 8
        styles['Heading2'].textColor = HexColor('#333333')
        
        # 三级标题
        styles['Heading3'].fontName = font_name
        styles['Heading3'].fontSize = 12
        styles['Heading3'].leading = 18
        styles['Heading3'].spaceAfter = 6
        styles['Heading3'].textColor = HexColor('#666666')
        
        # 公式样式（居中、斜体）
        styles.add(ParagraphStyle(
            name='Formula',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=11,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=10,
            spaceBefore=10,
            firstLineIndent=0,
        ))
        
        # 列表项样式
        styles.add(ParagraphStyle(
            name='ListItem',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=11,
            leading=16,
            leftIndent=0.5 * cm,
            firstLineIndent=0,
            spaceAfter=4,
        ))
        
        return styles


def test_improved_generator():
    """测试改进的生成器"""
    config = {}
    generator = ImprovedPDFGenerator(config)
    
    # 测试文本（包含 LaTeX 公式和 Markdown 格式）
    test_text = """# 机器学习中的优化方法

## 1. 梯度下降法

梯度下降是一种常用的优化算法。给定损失函数 $L(\theta)$，我们通过迭代更新参数：

$$\theta_{t+1} = \theta_t - \eta \nabla L(\theta_t)$$

其中 $\eta$ 是学习率，$\nabla L(\theta_t)$ 是梯度。

### 1.1 随机梯度下降

随机梯度下降（SGD）在每次迭代中只使用一个样本来计算梯度：

$$\theta_{t+1} = \theta_t - \eta \nabla L_i(\theta_t)$$

## 2. 动量方法

动量方法通过累积历史梯度来加速收敛：

$$v_{t+1} = \beta v_t + \nabla L(\theta_t)$$
$$\theta_{t+1} = \theta_t - \eta v_{t+1}$$

其中 $\beta$ 是动量系数，通常取 $\beta = 0.9$。

## 3. 总结

- 梯度下降是基础优化方法
- 动量方法可以加速收敛
- 学习率 $\eta$ 的选择很重要
"""
    
    output_path = "/home/ubuntu/pdf_translator/test_improved_output.pdf"
    generator.generate_pdf(test_text, output_path)
    print(f"测试 PDF 已生成: {output_path}")


if __name__ == "__main__":
    test_improved_generator()

