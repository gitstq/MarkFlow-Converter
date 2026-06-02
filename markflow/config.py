"""配置管理模块"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List
import json


@dataclass
class Config:
    """MarkFlow配置类"""
    
    # 输出设置
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    template_dir: Optional[Path] = None
    
    # PDF设置
    pdf_page_size: str = "A4"  # A4, A3, Letter
    pdf_orientation: str = "portrait"  # portrait, landscape
    pdf_margin_top: float = 2.5  # cm
    pdf_margin_bottom: float = 2.5  # cm
    pdf_margin_left: float = 2.5  # cm
    pdf_margin_right: float = 2.5  # cm
    
    # 字体设置（中文优化）
    font_main: str = "Noto Sans CJK SC"
    font_mono: str = "Noto Sans Mono"
    font_size_body: int = 11
    font_size_code: int = 9
    
    # Mermaid图表设置
    mermaid_enabled: bool = True
    mermaid_theme: str = "default"  # default, dark, forest, neutral
    mermaid_scale: float = 1.5
    
    # 代码高亮设置
    code_highlight_theme: str = "github"
    code_line_numbers: bool = True
    
    # 处理设置
    batch_size: int = 10
    watch_interval: float = 1.0  # 秒
    
    # 高级设置
    preserve_toc: bool = True
    extract_images: bool = True
    image_quality: int = 90
    
    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """从JSON文件加载配置"""
        if not config_path.exists():
            return cls()
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 转换路径字符串为Path对象
        if "output_dir" in data:
            data["output_dir"] = Path(data["output_dir"])
        if "template_dir" in data and data["template_dir"]:
            data["template_dir"] = Path(data["template_dir"])
        
        return cls(**data)
    
    def to_file(self, config_path: Path) -> None:
        """保存配置到JSON文件"""
        data = {
            "output_dir": str(self.output_dir),
            "template_dir": str(self.template_dir) if self.template_dir else None,
            "pdf_page_size": self.pdf_page_size,
            "pdf_orientation": self.pdf_orientation,
            "pdf_margin_top": self.pdf_margin_top,
            "pdf_margin_bottom": self.pdf_margin_bottom,
            "pdf_margin_left": self.pdf_margin_left,
            "pdf_margin_right": self.pdf_margin_right,
            "font_main": self.font_main,
            "font_mono": self.font_mono,
            "font_size_body": self.font_size_body,
            "font_size_code": self.font_size_code,
            "mermaid_enabled": self.mermaid_enabled,
            "mermaid_theme": self.mermaid_theme,
            "mermaid_scale": self.mermaid_scale,
            "code_highlight_theme": self.code_highlight_theme,
            "code_line_numbers": self.code_line_numbers,
            "batch_size": self.batch_size,
            "watch_interval": self.watch_interval,
            "preserve_toc": self.preserve_toc,
            "extract_images": self.extract_images,
            "image_quality": self.image_quality,
        }
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_page_dimensions(self) -> tuple:
        """获取页面尺寸（单位：点）"""
        dimensions = {
            "A4": (595, 842),
            "A3": (842, 1191),
            "Letter": (612, 792),
        }
        width, height = dimensions.get(self.pdf_page_size, dimensions["A4"])
        
        if self.pdf_orientation == "landscape":
            width, height = height, width
        
        return width, height
