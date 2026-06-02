"""HTML模板模块"""

from markflow.config import Config


def get_html_template(config: Config) -> str:
    """获取HTML模板"""
    
    page_width, page_height = config.get_page_dimensions()
    margin_pt = config.pdf_margin_top * 28.35  # cm to points
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ title }}}}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/{config.code_highlight_theme}.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        @page {{
            size: {config.pdf_page_size} {config.pdf_orientation};
            margin: {config.pdf_margin_top}cm {config.pdf_margin_right}cm {config.pdf_margin_bottom}cm {config.pdf_margin_left}cm;
        }}
        
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: "{config.font_main}", "Noto Sans CJK SC", "Source Han Sans SC", "Microsoft YaHei", "PingFang SC", sans-serif;
            font-size: {config.font_size_body}pt;
            line-height: 1.8;
            color: #333;
            max-width: 100%;
            margin: 0 auto;
            padding: 0;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        
        /* 标题样式 */
        h1, h2, h3, h4, h5, h6 {{
            font-weight: 600;
            line-height: 1.4;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
            color: #222;
            page-break-after: avoid;
        }}
        
        h1 {{
            font-size: 2em;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 0.3em;
        }}
        
        h2 {{
            font-size: 1.5em;
            border-bottom: 1px solid #e8e8e8;
            padding-bottom: 0.2em;
        }}
        
        h3 {{
            font-size: 1.25em;
        }}
        
        h4 {{
            font-size: 1.1em;
        }}
        
        /* 段落 */
        p {{
            margin: 0.8em 0;
            text-align: justify;
        }}
        
        /* 链接 */
        a {{
            color: #0366d6;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        /* 代码块 */
        pre {{
            background-color: #f6f8fa;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            font-family: "{config.font_mono}", "SF Mono", "Fira Code", "Consolas", monospace;
            font-size: {config.font_size_code}pt;
            line-height: 1.5;
            margin: 1em 0;
            page-break-inside: avoid;
        }}
        
        code {{
            font-family: "{config.font_mono}", "SF Mono", "Fira Code", "Consolas", monospace;
            font-size: 0.9em;
            background-color: rgba(175, 184, 193, 0.2);
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        
        /* 表格 */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            page-break-inside: avoid;
        }}
        
        th, td {{
            border: 1px solid #d0d7de;
            padding: 8px 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #f6f8fa;
            font-weight: 600;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        /* 列表 */
        ul, ol {{
            padding-left: 2em;
            margin: 0.8em 0;
        }}
        
        li {{
            margin: 0.3em 0;
        }}
        
        /* 引用块 */
        blockquote {{
            border-left: 4px solid #d0d7de;
            padding-left: 1em;
            margin: 1em 0;
            color: #656d76;
        }}
        
        /* 图片 */
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
            page-break-inside: avoid;
        }}
        
        /* Mermaid图表 */
        .mermaid-diagram {{
            text-align: center;
            margin: 1.5em 0;
            page-break-inside: avoid;
        }}
        
        .mermaid-diagram img {{
            max-width: 100%;
            height: auto;
        }}
        
        /* 水平线 */
        hr {{
            border: none;
            border-top: 1px solid #e1e4e8;
            margin: 2em 0;
        }}
        
        /* 目录 */
        .toc {{
            background-color: #f6f8fa;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            padding: 1em 1.5em;
            margin: 1.5em 0;
        }}
        
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .toc li {{
            margin: 0.4em 0;
        }}
        
        .toc a {{
            color: #333;
        }}
        
        /* 打印优化 */
        @media print {{
            body {{
                font-size: 11pt;
            }}
            
            pre {{
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            
            a {{
                color: #333;
            }}
            
            a[href]:after {{
                content: " (" attr(href) ")";
                font-size: 0.8em;
                color: #666;
            }}
        }}
    </style>
</head>
<body>
    <div class="content">
        {{{{ content | safe }}}}
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            hljs.highlightAll();
        }});
    </script>
</body>
</html>
'''
