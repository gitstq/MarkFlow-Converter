"""核心转换模块"""

import re
import tempfile
from pathlib import Path
from typing import Optional, Union, List
import base64

import markdown
from markdown.extensions import fenced_code, tables, toc
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from markflow.config import Config
from markflow.mermaid_renderer import MermaidRenderer, SimpleMermaidRenderer
from markflow.html_template import get_html_template

console = Console()


class MarkFlowConverter:
    """MarkFlow核心转换器"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.mermaid_renderer = MermaidRenderer(
            theme=self.config.mermaid_theme,
            scale=self.config.mermaid_scale
        )
        self.simple_mermaid = SimpleMermaidRenderer(
            theme=self.config.mermaid_theme,
            scale=self.config.mermaid_scale
        )
        
        # 初始化Markdown解析器
        self.md = markdown.Markdown(extensions=[
            fenced_code.FencedCodeExtension(),
            tables.TableExtension(),
            toc.TocExtension(marker='[TOC]', title='目录'),
            'fenced_code',
            'tables',
            'toc',
            'nl2br',
        ])
    
    def md_to_html(self, md_content: str) -> str:
        """Markdown转HTML"""
        # 处理Mermaid图表
        mermaid_blocks = self.mermaid_renderer.extract_mermaid_blocks(md_content)
        
        for i, (code, placeholder) in enumerate(mermaid_blocks):
            # 尝试本地渲染
            img_path = self.mermaid_renderer.render(code)
            
            if img_path is None:
                # 尝试在线渲染
                img_path = self.simple_mermaid.render(code)
            
            if img_path:
                # 读取图片并转为base64
                with open(img_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                
                img_html = f'<div class="mermaid-diagram"><img src="data:image/png;base64,{img_data}" alt="Mermaid Diagram"></div>'
                md_content = md_content.replace(f"```mermaid\n{code}\n```", img_html)
            else:
                # 渲染失败，保留代码块
                console.print(f"[yellow]⚠️  图表 {i+1} 渲染失败，保留原始代码[/yellow]")
        
        # 转换Markdown为HTML
        html_content = self.md.convert(md_content)
        self.md.reset()
        
        return html_content
    
    def md_to_pdf(self, input_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Markdown转PDF
        
        Args:
            input_path: 输入Markdown文件路径
            output_path: 输出PDF文件路径（可选）
            
        Returns:
            输出PDF文件路径
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        if output_path is None:
            output_path = self.config.output_dir / f"{input_path.stem}.pdf"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # 读取Markdown
            task = progress.add_task("📖 读取Markdown文件...", total=None)
            md_content = input_path.read_text(encoding="utf-8")
            
            # 转换为HTML
            progress.update(task, description="🎨 转换为HTML...")
            html_content = self.md_to_html(md_content)
            
            # 应用模板
            progress.update(task, description="📄 生成PDF文档...")
            template = get_html_template(self.config)
            full_html = template.replace("{{ content | safe }}", html_content)
            full_html = full_html.replace("{{ title }}", input_path.stem)
            
            # 使用Playwright或WeasyPrint生成PDF
            try:
                self._html_to_pdf_playwright(full_html, output_path)
            except Exception as e:
                console.print(f"[yellow]Playwright失败，尝试备用方案: {e}[/yellow]")
                self._html_to_pdf_weasyprint(full_html, output_path)
            
            progress.update(task, description="✅ 转换完成!")
        
        console.print(f"[green]✓ PDF已生成: {output_path}[/green]")
        return output_path
    
    def _html_to_pdf_playwright(self, html_content: str, output_path: Path) -> None:
        """使用Playwright将HTML转为PDF"""
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # 加载HTML内容
            page.set_content(html_content)
            
            # 等待页面渲染完成
            page.wait_for_load_state("networkidle")
            
            # 生成PDF
            page.pdf(
                path=str(output_path),
                format=self.config.pdf_page_size,
                landscape=self.config.pdf_orientation == "landscape",
                margin={
                    "top": f"{self.config.pdf_margin_top}cm",
                    "bottom": f"{self.config.pdf_margin_bottom}cm",
                    "left": f"{self.config.pdf_margin_left}cm",
                    "right": f"{self.config.pdf_margin_right}cm",
                },
                print_background=True,
            )
            
            browser.close()
    
    def _html_to_pdf_weasyprint(self, html_content: str, output_path: Path) -> None:
        """使用WeasyPrint将HTML转为PDF（备用方案）"""
        from weasyprint import HTML, CSS
        
        html = HTML(string=html_content)
        html.write_pdf(str(output_path))
    
    def pdf_to_md(self, input_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None) -> Path:
        """
        PDF转Markdown
        
        Args:
            input_path: 输入PDF文件路径
            output_path: 输出Markdown文件路径（可选）
            
        Returns:
            输出Markdown文件路径
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        if output_path is None:
            output_path = self.config.output_dir / f"{input_path.stem}.md"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("📖 读取PDF文件...", total=None)
            
            # 使用PyMuPDF提取文本
            import fitz  # PyMuPDF
            
            doc = fitz.open(str(input_path))
            md_content = []
            
            for page_num in range(len(doc)):
                progress.update(task, description=f"📝 处理第 {page_num + 1}/{len(doc)} 页...")
                page = doc[page_num]
                
                # 提取文本
                text = page.get_text()
                
                # 简单格式化
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        md_content.append(line)
                
                md_content.append("\n---\n")  # 分页标记
            
            doc.close()
            
            # 保存Markdown
            progress.update(task, description="💾 保存Markdown文件...")
            output_path.write_text("\n\n".join(md_content), encoding="utf-8")
            
            progress.update(task, description="✅ 转换完成!")
        
        console.print(f"[green]✓ Markdown已生成: {output_path}[/green]")
        return output_path
    
    def batch_convert(self, input_dir: Union[str, Path], output_dir: Optional[Union[str, Path]] = None, pattern: str = "*.md") -> List[Path]:
        """
        批量转换
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录（可选）
            pattern: 文件匹配模式
            
        Returns:
            输出文件路径列表
        """
        input_dir = Path(input_dir)
        
        if output_dir:
            output_dir = Path(output_dir)
        else:
            output_dir = self.config.output_dir
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files = list(input_dir.glob(pattern))
        results = []
        
        console.print(f"[blue]📁 找到 {len(files)} 个文件待转换[/blue]")
        
        for i, file_path in enumerate(files, 1):
            console.print(f"\n[cyan]({i}/{len(files)}) 处理: {file_path.name}[/cyan]")
            
            try:
                if file_path.suffix.lower() == '.md':
                    result = self.md_to_pdf(file_path, output_dir / f"{file_path.stem}.pdf")
                    results.append(result)
                elif file_path.suffix.lower() == '.pdf':
                    result = self.pdf_to_md(file_path, output_dir / f"{file_path.stem}.md")
                    results.append(result)
            except Exception as e:
                console.print(f"[red]✗ 转换失败: {e}[/red]")
        
        console.print(f"\n[green]✅ 批量转换完成! 成功 {len(results)}/{len(files)}[/green]")
        return results
