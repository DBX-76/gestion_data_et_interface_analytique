#!/usr/bin/env python3
"""
Script to convert README.md to PDF using WeasyPrint
"""

import markdown
import weasyprint
from pathlib import Path

def convert_readme_to_pdf():
    """Convert README.md to PDF"""

    # Read the README.md file
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("❌ README.md not found!")
        return

    with open(readme_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

    # Add some basic CSS styling
    html_with_css = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Rescue Operations Data Platform - Documentation</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
            h3 {{ color: #7f8c8d; }}
            code {{ background-color: #f8f8f8; padding: 2px 4px; border-radius: 3px; }}
            pre {{ background-color: #f8f8f8; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            blockquote {{ border-left: 4px solid #3498db; padding-left: 10px; margin-left: 0; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .emoji {{ font-size: 1.2em; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Convert HTML to PDF
    pdf_path = Path("README.pdf")
    weasyprint.HTML(string=html_with_css).write_pdf(str(pdf_path))

    print(f"✅ README.md converted to PDF: {pdf_path.absolute()}")

if __name__ == "__main__":
    convert_readme_to_pdf()