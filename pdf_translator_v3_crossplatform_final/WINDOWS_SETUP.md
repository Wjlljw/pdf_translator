# Windows 平台使用指南

## 📋 系统要求

- Windows 7 或更高版本
- Python 3.7 或更高版本
- 已安装中文字体（通常 Windows 自带）

## 🚀 安装步骤

### 1. 安装 Python

如果还没有安装 Python，请从官网下载：
https://www.python.org/downloads/

**重要**：安装时勾选 "Add Python to PATH"

### 2. 解压工具

```cmd
# 使用 7-Zip 或 WinRAR 解压
# 或使用 PowerShell
tar -xzf pdf_translator_final_fixed.tar.gz
cd pdf_translator_release
```

### 3. 安装依赖

```cmd
pip install -r requirements.txt
```

如果遇到网络问题，可以使用国内镜像：

```cmd
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 配置 API Key

#### 方式 1：环境变量（推荐）

在 PowerShell 中：

```powershell
$env:HF_TOKEN="your_huggingface_token"
```

在 CMD 中：

```cmd
set HF_TOKEN=your_huggingface_token
```

#### 方式 2：配置文件

编辑 `config_huggingface.json`，添加 API Key：

```json
{
  "api": {
    "provider": "huggingface",
    "model": "deepseek-ai/DeepSeek-V3-0324:fireworks-ai",
    "api_key": "your_token_here",
    "base_url": "https://router.huggingface.co/v1"
  }
}
```

### 5. 翻译 PDF

```cmd
# 翻译单个文件
python translate_pdfs.py paper.pdf -c config_huggingface.json

# 翻译整个文件夹
python translate_pdfs.py C:\Users\YourName\Documents\papers -c config_huggingface.json

# 递归处理子文件夹
python translate_pdfs.py C:\Users\YourName\Documents\papers -r -c config_huggingface.json
```

## 🔧 字体配置

### Windows 默认支持的中文字体

工具会自动检测并使用以下字体（按优先级）：

1. **微软雅黑** (msyh.ttc) - 推荐
2. **宋体** (simsun.ttc)
3. **黑体** (simhei.ttf)
4. **楷体** (simkai.ttf)

这些字体通常已经安装在 Windows 系统中。

### 检查字体是否存在

在文件资源管理器中访问：

```
C:\Windows\Fonts\
```

确认以下文件存在：
- `msyh.ttc` (微软雅黑)
- `simsun.ttc` (宋体)

### 如果字体缺失

如果您的系统缺少中文字体，请：

1. 下载字体文件（如微软雅黑）
2. 双击字体文件
3. 点击"安装"按钮
4. 重新运行翻译工具

## 🐛 常见问题

### 问题 1：找不到 Python

**错误信息**：
```
'python' 不是内部或外部命令
```

**解决方案**：
1. 重新安装 Python，勾选 "Add Python to PATH"
2. 或使用完整路径：
   ```cmd
   C:\Python39\python.exe translate_pdfs.py paper.pdf
   ```

### 问题 2：pip 安装失败

**错误信息**：
```
Could not find a version that satisfies the requirement
```

**解决方案**：
1. 升级 pip：
   ```cmd
   python -m pip install --upgrade pip
   ```
2. 使用国内镜像：
   ```cmd
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

### 问题 3：字体注册失败

**错误信息**：
```
警告: 未找到中文字体
```

**解决方案**：
1. 检查 `C:\Windows\Fonts\` 目录
2. 确认 `msyh.ttc` 或 `simsun.ttc` 存在
3. 如果不存在，安装微软雅黑字体
4. 重启命令行窗口

### 问题 4：路径包含中文

**错误信息**：
```
UnicodeDecodeError
```

**解决方案**：
1. 将 PDF 文件移动到英文路径
2. 或使用原始字符串：
   ```python
   python translate_pdfs.py r"C:\用户\文档\paper.pdf"
   ```

### 问题 5：权限不足

**错误信息**：
```
PermissionError: [WinError 5] 拒绝访问
```

**解决方案**：
1. 以管理员身份运行 PowerShell 或 CMD
2. 或将文件移动到用户目录（如 `C:\Users\YourName\Documents\`）

## 💡 Windows 特定提示

### 1. 路径分隔符

Windows 使用反斜杠 `\`，但在命令中可以使用正斜杠 `/`：

```cmd
# 两种方式都可以
python translate_pdfs.py C:\papers\paper.pdf
python translate_pdfs.py C:/papers/paper.pdf
```

### 2. 长路径支持

如果路径超过 260 字符，需要启用长路径支持：

1. 打开注册表编辑器（regedit）
2. 导航到：`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
3. 设置 `LongPathsEnabled` 为 `1`
4. 重启计算机

### 3. 批处理脚本

创建 `translate.bat` 文件，方便批量处理：

```batch
@echo off
set HF_TOKEN=your_token_here
python translate_pdfs.py %1 -c config_huggingface.json
pause
```

使用方法：
```cmd
translate.bat paper.pdf
```

### 4. PowerShell 脚本

创建 `translate.ps1` 文件：

```powershell
param(
    [string]$InputPath
)

$env:HF_TOKEN = "your_token_here"
python translate_pdfs.py $InputPath -c config_huggingface.json
```

使用方法：
```powershell
.\translate.ps1 paper.pdf
```

## 📊 性能优化

### 1. 使用 SSD

将 PDF 文件放在 SSD 上可以提升处理速度。

### 2. 关闭杀毒软件

翻译时临时关闭杀毒软件可以避免文件扫描延迟。

### 3. 增加虚拟内存

处理大文件时，增加虚拟内存可以避免内存不足：

1. 右键"此电脑" → 属性
2. 高级系统设置 → 性能设置
3. 高级 → 虚拟内存 → 更改
4. 设置为系统推荐值的 1.5 倍

## 🎯 完整示例

### 示例 1：翻译桌面上的 PDF

```cmd
# 设置 API Key
set HF_TOKEN=hf_your_token_here

# 翻译文件
python translate_pdfs.py C:\Users\YourName\Desktop\paper.pdf -c config_huggingface.json

# 查看结果
# 输出文件: C:\Users\YourName\Desktop\paper_chn.pdf
```

### 示例 2：批量翻译文档文件夹

```cmd
# 设置 API Key
set HF_TOKEN=hf_your_token_here

# 批量翻译
python translate_pdfs.py C:\Users\YourName\Documents\papers -r -c config_huggingface.json

# 所有 PDF 都会生成对应的 _chn.pdf 文件
```

### 示例 3：使用配置文件

编辑 `config_huggingface.json`：

```json
{
  "api": {
    "provider": "huggingface",
    "model": "deepseek-ai/DeepSeek-V3-0324:fireworks-ai",
    "api_key": "hf_your_token_here",
    "base_url": "https://router.huggingface.co/v1",
    "max_tokens": 4000,
    "temperature": 0.3
  },
  "translation": {
    "chunk_size": 2000,
    "preserve_images": true,
    "preserve_formulas": true
  }
}
```

然后运行：

```cmd
python translate_pdfs.py paper.pdf -c config_huggingface.json
```

## 📞 技术支持

### 查看日志

翻译过程中会生成日志文件：

```
translation_log_YYYYMMDD_HHMMSS.txt
```

如果遇到问题，请查看日志文件中的错误信息。

### 测试安装

运行以下命令测试安装是否正确：

```cmd
python -c "import PyMuPDF, pdfplumber, reportlab; print('所有依赖已安装')"
```

### 检查字体

运行以下命令检查字体是否正确注册：

```cmd
python -c "from src.pdf_generator_enhanced import EnhancedPDFGenerator; gen = EnhancedPDFGenerator(); print('字体注册成功')"
```

## 🎁 Windows 专用工具

### 图形界面（可选）

如果您不习惯命令行，可以创建一个简单的图形界面：

创建 `gui.py` 文件：

```python
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def translate_pdf():
    file_path = filedialog.askopenfilename(
        title="选择 PDF 文件",
        filetypes=[("PDF 文件", "*.pdf")]
    )
    
    if file_path:
        api_key = entry_api_key.get()
        if not api_key:
            messagebox.showerror("错误", "请输入 API Key")
            return
        
        os.environ['HF_TOKEN'] = api_key
        
        try:
            subprocess.run([
                "python", "translate_pdfs.py", 
                file_path, 
                "-c", "config_huggingface.json"
            ], check=True)
            messagebox.showinfo("成功", "翻译完成！")
        except Exception as e:
            messagebox.showerror("错误", str(e))

# 创建窗口
root = tk.Tk()
root.title("PDF 翻译工具")
root.geometry("400x150")

# API Key 输入
tk.Label(root, text="API Key:").pack(pady=10)
entry_api_key = tk.Entry(root, width=50)
entry_api_key.pack()

# 翻译按钮
btn_translate = tk.Button(root, text="选择 PDF 并翻译", command=translate_pdf)
btn_translate.pack(pady=20)

root.mainloop()
```

运行图形界面：

```cmd
python gui.py
```

---

**Windows 平台完全支持！** 🎉

如有任何问题，请参考本文档或查看日志文件。

