"""Mermaid图表渲染模块"""

import base64
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


class MermaidRenderer:
    """Mermaid图表渲染器"""
    
    def __init__(self, theme: str = "default", scale: float = 1.5):
        self.theme = theme
        self.scale = scale
        self.cache_dir = Path(tempfile.gettempdir()) / "markflow_mermaid_cache"
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, code: str) -> str:
        """生成缓存键"""
        content = f"{code}:{self.theme}:{self.scale}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _check_mmdc(self) -> bool:
        """检查是否安装了mmdc"""
        try:
            subprocess.run(
                ["mmdc", "--version"],
                capture_output=True,
                check=True,
                timeout=5
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def render(self, code: str) -> Optional[Path]:
        """
        渲染Mermaid图表为PNG图片
        
        Args:
            code: Mermaid图表代码
            
        Returns:
            生成的图片路径，失败返回None
        """
        cache_key = self._get_cache_key(code)
        cache_path = self.cache_dir / f"{cache_key}.png"
        
        # 检查缓存
        if cache_path.exists():
            return cache_path
        
        # 检查mmdc是否可用
        if not self._check_mmdc():
            console.print(
                "[yellow]⚠️  未检测到mmdc，跳过Mermaid渲染[/yellow]\n"
                "[dim]提示: 运行 `npm install -g @mermaid-js/mermaid-cli` 安装[/dim]"
            )
            return None
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".mmd",
            delete=False,
            encoding="utf-8"
        ) as f:
            f.write(code)
            mmd_path = Path(f.name)
        
        try:
            # 构建mmdc命令
            cmd = [
                "mmdc",
                "-i", str(mmd_path),
                "-o", str(cache_path),
                "-t", self.theme,
                "-s", str(self.scale),
                "-b", "white",
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and cache_path.exists():
                return cache_path
            else:
                console.print(f"[red]Mermaid渲染失败: {result.stderr}[/red]")
                return None
                
        except subprocess.TimeoutExpired:
            console.print("[red]Mermaid渲染超时[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Mermaid渲染错误: {e}[/red]")
            return None
        finally:
            # 清理临时文件
            if mmd_path.exists():
                mmd_path.unlink()
    
    def render_svg(self, code: str) -> Optional[str]:
        """
        渲染Mermaid图表为SVG字符串
        
        Args:
            code: Mermaid图表代码
            
        Returns:
            SVG字符串，失败返回None
        """
        cache_key = self._get_cache_key(code) + "_svg"
        cache_path = self.cache_dir / f"{cache_key}.svg"
        
        # 检查缓存
        if cache_path.exists():
            return cache_path.read_text(encoding="utf-8")
        
        # 检查mmdc是否可用
        if not self._check_mmdc():
            return None
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".mmd",
            delete=False,
            encoding="utf-8"
        ) as f:
            f.write(code)
            mmd_path = Path(f.name)
        
        try:
            cmd = [
                "mmdc",
                "-i", str(mmd_path),
                "-o", str(cache_path),
                "-t", self.theme,
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and cache_path.exists():
                return cache_path.read_text(encoding="utf-8")
            else:
                return None
                
        except Exception:
            return None
        finally:
            if mmd_path.exists():
                mmd_path.unlink()
    
    def extract_mermaid_blocks(self, markdown: str) -> list:
        """
        提取Markdown中的Mermaid代码块
        
        Args:
            markdown: Markdown文本
            
        Returns:
            Mermaid代码块列表 [(代码, 占位符), ...]
        """
        pattern = r'```mermaid\n(.*?)```'
        matches = re.findall(pattern, markdown, re.DOTALL)
        
        blocks = []
        for i, code in enumerate(matches):
            placeholder = f"<!-- MERMAID_DIAGRAM_{i} -->"
            blocks.append((code.strip(), placeholder))
        
        return blocks


class SimpleMermaidRenderer:
    """简化版Mermaid渲染器（使用在线API）"""
    
    def __init__(self, theme: str = "default", scale: float = 1.5):
        self.theme = theme
        self.scale = scale
    
    def render(self, code: str) -> Optional[Path]:
        """使用Mermaid.ink API渲染图表"""
        import urllib.request
        import urllib.parse
        
        try:
            # 使用Mermaid.ink服务
            encoded = base64.b64encode(code.encode()).decode()
            url = f"https://mermaid.ink/img/{encoded}?theme={self.theme}&scale={self.scale}"
            
            with tempfile.NamedTemporaryFile(
                suffix=".png",
                delete=False
            ) as f:
                urllib.request.urlretrieve(url, f.name)
                return Path(f.name)
        except Exception as e:
            console.print(f"[yellow]在线Mermaid渲染失败: {e}[/yellow]")
            return None
