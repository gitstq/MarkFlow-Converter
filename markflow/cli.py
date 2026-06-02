"""命令行接口模块"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from markflow import __version__
from markflow.config import Config
from markflow.converter import MarkFlowConverter
from markflow.watcher import FileWatcher

app = typer.Typer(
    name="markflow",
    help="轻量级Markdown与PDF双向转换工具",
    add_completion=False,
)
console = Console()


def version_callback(value: bool):
    """版本信息回调"""
    if value:
        console.print(f"[bold blue]MarkFlow[/bold blue] 版本 {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v",
        callback=version_callback,
        is_eager=True,
        help="显示版本信息"
    ),
):
    """MarkFlow - 轻量级Markdown与PDF双向转换工具"""
    pass


@app.command(name="md2pdf")
def md_to_pdf(
    input_path: Path = typer.Argument(..., help="输入Markdown文件路径"),
    output_path: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="输出PDF文件路径（默认: 输出目录/输入文件名.pdf）"
    ),
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c",
        help="配置文件路径"
    ),
    page_size: str = typer.Option(
        "A4", "--page-size", "-p",
        help="页面大小 (A4, A3, Letter)"
    ),
    orientation: str = typer.Option(
        "portrait", "--orientation",
        help="页面方向 (portrait, landscape)"
    ),
):
    """将Markdown文件转换为PDF"""
    try:
        # 加载配置
        config = Config.from_file(config_path) if config_path else Config()
        config.pdf_page_size = page_size
        config.pdf_orientation = orientation
        
        # 执行转换
        converter = MarkFlowConverter(config)
        result = converter.md_to_pdf(input_path, output_path)
        
        console.print(Panel(
            f"[green]✓ 转换成功[/green]\n"
            f"[dim]输出文件:[/dim] {result}",
            title="MarkFlow",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel(
            f"[red]✗ 转换失败[/red]\n"
            f"[dim]错误信息:[/dim] {e}",
            title="MarkFlow",
            border_style="red"
        ))
        raise typer.Exit(1)


@app.command(name="pdf2md")
def pdf_to_md(
    input_path: Path = typer.Argument(..., help="输入PDF文件路径"),
    output_path: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="输出Markdown文件路径（默认: 输出目录/输入文件名.md）"
    ),
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c",
        help="配置文件路径"
    ),
):
    """将PDF文件转换为Markdown"""
    try:
        config = Config.from_file(config_path) if config_path else Config()
        converter = MarkFlowConverter(config)
        result = converter.pdf_to_md(input_path, output_path)
        
        console.print(Panel(
            f"[green]✓ 转换成功[/green]\n"
            f"[dim]输出文件:[/dim] {result}",
            title="MarkFlow",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel(
            f"[red]✗ 转换失败[/red]\n"
            f"[dim]错误信息:[/dim] {e}",
            title="MarkFlow",
            border_style="red"
        ))
        raise typer.Exit(1)


@app.command(name="batch")
def batch_convert(
    input_dir: Path = typer.Argument(..., help="输入目录"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="输出目录（默认: ./output）"
    ),
    pattern: str = typer.Option(
        "*.md", "--pattern",
        help="文件匹配模式"
    ),
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c",
        help="配置文件路径"
    ),
):
    """批量转换目录中的文件"""
    try:
        config = Config.from_file(config_path) if config_path else Config()
        if output_dir:
            config.output_dir = output_dir
        
        converter = MarkFlowConverter(config)
        results = converter.batch_convert(input_dir, config.output_dir, pattern)
        
        console.print(Panel(
            f"[green]✓ 批量转换完成[/green]\n"
            f"[dim]成功转换:[/dim] {len(results)} 个文件",
            title="MarkFlow",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel(
            f"[red]✗ 批量转换失败[/red]\n"
            f"[dim]错误信息:[/dim] {e}",
            title="MarkFlow",
            border_style="red"
        ))
        raise typer.Exit(1)


@app.command(name="watch")
def watch_directory(
    watch_dir: Path = typer.Argument(..., help="要监控的目录"),
    config_path: Optional[Path] = typer.Option(
        None, "--config", "-c",
        help="配置文件路径"
    ),
    recursive: bool = typer.Option(
        True, "--recursive/--no-recursive",
        help="是否递归监控子目录"
    ),
):
    """监控目录，自动转换新文件或修改的文件"""
    try:
        config = Config.from_file(config_path) if config_path else Config()
        
        watcher = FileWatcher(watch_dir, config, recursive)
        watcher.start()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 已停止监控[/yellow]")
    except Exception as e:
        console.print(Panel(
            f"[red]✗ 监控失败[/red]\n"
            f"[dim]错误信息:[/dim] {e}",
            title="MarkFlow",
            border_style="red"
        ))
        raise typer.Exit(1)


@app.command(name="init")
def init_config(
    output_path: Path = typer.Option(
        "./markflow.json", "--output", "-o",
        help="配置文件输出路径"
    ),
):
    """初始化配置文件"""
    try:
        config = Config()
        config.to_file(output_path)
        
        console.print(Panel(
            f"[green]✓ 配置文件已创建[/green]\n"
            f"[dim]路径:[/dim] {output_path.absolute()}",
            title="MarkFlow",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel(
            f"[red]✗ 创建失败[/red]\n"
            f"[dim]错误信息:[/dim] {e}",
            title="MarkFlow",
            border_style="red"
        ))
        raise typer.Exit(1)


@app.command(name="demo")
def create_demo():
    """创建示例Markdown文件"""
    demo_content = '''# MarkFlow 示例文档

欢迎使用 **MarkFlow**！这是一个轻量级的Markdown与PDF双向转换工具。

## 功能特性

- ✅ Markdown转PDF（支持Mermaid图表）
- ✅ PDF转Markdown
- ✅ 批量转换
- ✅ 目录监控
- ✅ 中文排版优化

## 代码示例

```python
def hello_markflow():
    print("Hello, MarkFlow!")
    return "轻量级文档转换工具"
```

## Mermaid图表示例

```mermaid
graph TD
    A[开始] --> B{判断}
    B -->|条件1| C[处理1]
    B -->|条件2| D[处理2]
    C --> E[结束]
    D --> E
```

## 表格示例

| 功能 | 状态 | 说明 |
|------|------|------|
| MD转PDF | ✅ | 支持Mermaid图表 |
| PDF转MD | ✅ | 保留文档结构 |
| 批量转换 | ✅ | 支持通配符匹配 |
| 目录监控 | ✅ | 自动转换新文件 |

## 引用

> MarkFlow让文档转换变得简单高效！

---

**感谢使用 MarkFlow！**
'''
    
    demo_path = Path("./markflow-demo.md")
    demo_path.write_text(demo_content, encoding="utf-8")
    
    console.print(Panel(
        f"[green]✓ 示例文件已创建[/green]\n"
        f"[dim]路径:[/dim] {demo_path.absolute()}\n\n"
        f"[dim]运行以下命令转换为PDF:[/dim]\n"
        f"[cyan]markflow md2pdf {demo_path}[/cyan]",
        title="MarkFlow",
        border_style="green"
    ))


def main():
    """CLI入口点"""
    app()


if __name__ == "__main__":
    main()
