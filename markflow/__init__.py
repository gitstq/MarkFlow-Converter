"""
MarkFlow - 轻量级Markdown与PDF双向转换工具

支持功能：
- Markdown转PDF（支持Mermaid图表、代码高亮）
- PDF转Markdown（保留结构）
- 批量转换
- 目录监控自动转换
- 中文排版优化
"""

__version__ = "1.0.0"
__author__ = "MarkFlow Team"
__license__ = "MIT"

from markflow.converter import MarkFlowConverter
from markflow.config import Config

__all__ = ["MarkFlowConverter", "Config"]
