"""文件监控模块"""

import time
from pathlib import Path
from typing import Callable, Optional, Set

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
from rich.console import Console

from markflow.converter import MarkFlowConverter
from markflow.config import Config

console = Console()


class MarkdownHandler(FileSystemEventHandler):
    """Markdown文件变化处理器"""
    
    def __init__(
        self,
        converter: MarkFlowConverter,
        callback: Optional[Callable[[Path], None]] = None,
        extensions: Optional[Set[str]] = None
    ):
        self.converter = converter
        self.callback = callback
        self.extensions = extensions or {'.md', '.markdown'}
        self._processed_files: Set[str] = set()
    
    def on_created(self, event):
        """文件创建事件"""
        if not event.is_directory:
            self._handle_file(Path(event.src_path))
    
    def on_modified(self, event):
        """文件修改事件"""
        if not event.is_directory:
            self._handle_file(Path(event.src_path))
    
    def _handle_file(self, file_path: Path):
        """处理文件"""
        if file_path.suffix.lower() not in self.extensions:
            return
        
        # 防抖处理
        file_id = f"{file_path}:{file_path.stat().st_mtime}"
        if file_id in self._processed_files:
            return
        
        self._processed_files.add(file_id)
        
        # 清理旧记录
        if len(self._processed_files) > 1000:
            self._processed_files.clear()
        
        console.print(f"\n[blue]📝 检测到文件变化: {file_path.name}[/blue]")
        
        try:
            output_path = self.converter.md_to_pdf(file_path)
            
            if self.callback:
                self.callback(output_path)
                
        except Exception as e:
            console.print(f"[red]✗ 转换失败: {e}[/red]")


class FileWatcher:
    """文件监控器"""
    
    def __init__(
        self,
        watch_dir: Path,
        config: Optional[Config] = None,
        recursive: bool = True
    ):
        self.watch_dir = Path(watch_dir)
        self.config = config or Config()
        self.recursive = recursive
        self.converter = MarkFlowConverter(self.config)
        self.observer: Optional[Observer] = None
        self.running = False
    
    def start(self, callback: Optional[Callable[[Path], None]] = None):
        """开始监控"""
        if not self.watch_dir.exists():
            raise FileNotFoundError(f"监控目录不存在: {self.watch_dir}")
        
        self.running = True
        
        # 设置事件处理器
        event_handler = MarkdownHandler(self.converter, callback)
        
        # 创建观察者
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.watch_dir), recursive=self.recursive)
        self.observer.start()
        
        console.print(f"[green]👁️  开始监控目录: {self.watch_dir}[/green]")
        console.print("[dim]按 Ctrl+C 停止监控[/dim]\n")
        
        try:
            while self.running:
                time.sleep(self.config.watch_interval)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """停止监控"""
        self.running = False
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        console.print("\n[yellow]👋 监控已停止[/yellow]")
