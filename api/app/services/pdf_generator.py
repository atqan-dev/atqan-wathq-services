"""
PDF generation service using WeasyPrint for converting HTML/CSS to PDF.
"""

import os
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID

from jinja2 import Template


class PdfGeneratorService:
    """Service for generating PDFs from HTML templates."""

    def __init__(self, output_dir: str = "uploads/generated_pdfs"):
        """
        Initialize PDF generator service.

        Args:
            output_dir: Directory to store generated PDFs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_pdf(
        self,
        html_content: str,
        css_content: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None,
        page_size: str = "A4",
        page_orientation: str = "portrait",
    ) -> tuple[str, int, bytes]:
        """
        Generate PDF from HTML/CSS content.

        Args:
            html_content: HTML template content
            css_content: CSS styling content
            data: Data to inject into template
            filename: Output filename (auto-generated if not provided)
            page_size: Page size (A4, Letter, etc.)
            page_orientation: portrait or landscape

        Returns:
            Tuple of (file_path, file_size, pdf_bytes)
        """
        try:
            # Try to import WeasyPrint
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
        except ImportError:
            # Fallback: Return HTML as is for preview
            return self._generate_html_fallback(
                html_content, css_content, data, filename
            )

        # Render template with data
        if data:
            html_content = self._render_template(html_content, data)

        # Prepare full HTML with CSS
        full_html = self._build_full_html(
            html_content, css_content, page_size, page_orientation
        )

        # Generate filename
        if not filename:
            filename = f"pdf_{uuid.uuid4()}.pdf"
        elif not filename.endswith(".pdf"):
            filename = f"{filename}.pdf"

        # Generate PDF
        font_config = FontConfiguration()
        pdf_bytes = HTML(string=full_html).write_pdf(
            font_config=font_config
        )

        # Save to file
        file_path = self.output_dir / filename
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)

        file_size = len(pdf_bytes)

        return str(file_path), file_size, pdf_bytes

    def generate_pdf_stream(
        self,
        html_content: str,
        css_content: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        page_size: str = "A4",
        page_orientation: str = "portrait",
    ) -> bytes:
        """
        Generate PDF and return as bytes without saving to disk.

        Args:
            html_content: HTML template content
            css_content: CSS styling content
            data: Data to inject into template
            page_size: Page size
            page_orientation: portrait or landscape

        Returns:
            PDF content as bytes
        """
        try:
            from weasyprint import HTML
            from weasyprint.text.fonts import FontConfiguration
        except ImportError:
            # Return HTML as bytes if WeasyPrint not available
            html = self._build_full_html(
                html_content, css_content, page_size, page_orientation
            )
            return html.encode("utf-8")

        # Render template with data
        if data:
            html_content = self._render_template(html_content, data)

        # Prepare full HTML
        full_html = self._build_full_html(
            html_content, css_content, page_size, page_orientation
        )

        # Generate PDF
        font_config = FontConfiguration()
        pdf_bytes = HTML(string=full_html).write_pdf(
            font_config=font_config
        )

        return pdf_bytes

    def _render_template(
        self, html_content: str, data: Dict[str, Any]
    ) -> str:
        """
        Render Jinja2 template with provided data.
        Supports both {variable} and {{ variable }} syntax.

        Args:
            html_content: HTML template with Jinja2 placeholders
            data: Data dictionary

        Returns:
            Rendered HTML
        """
        import re
        
        # Convert single curly braces {var} to double {{ var }}
        # This regex looks for {word} but not {{ or }}
        def replace_single_braces(match):
            var_name = match.group(1)
            return f"{{{{ {var_name} }}}}"
        
        # Replace {variable} with {{ variable }} (but not already doubled)
        html_content = re.sub(r'(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})', replace_single_braces, html_content)
        
        # Now render with Jinja2
        template = Template(html_content)
        return template.render(**data)

    def _build_full_html(
        self,
        html_content: str,
        css_content: Optional[str],
        page_size: str,
        page_orientation: str,
    ) -> str:
        """
        Build complete HTML document with CSS and page settings.

        Args:
            html_content: Body HTML content
            css_content: CSS styling
            page_size: Page size
            page_orientation: Page orientation

        Returns:
            Complete HTML document
        """
        # Page size CSS
        page_css = self._get_page_css(page_size, page_orientation)

        # Build complete HTML
        full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated PDF</title>
    <style>
        {page_css}
        
        /* Reset and base styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', 'Helvetica', sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        
        {css_content or ''}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
        """

        return full_html

    def _get_page_css(
        self, page_size: str, page_orientation: str
    ) -> str:
        """
        Get CSS for page configuration.

        Args:
            page_size: Page size (A4, Letter, etc.)
            page_orientation: portrait or landscape

        Returns:
            CSS string for @page rule
        """
        # Map page sizes to dimensions
        page_sizes = {
            "A4": "210mm 297mm",
            "Letter": "8.5in 11in",
            "Legal": "8.5in 14in",
            "A3": "297mm 420mm",
            "A5": "148mm 210mm",
        }

        size = page_sizes.get(page_size, page_sizes["A4"])

        if page_orientation == "landscape":
            # Swap dimensions for landscape
            if "mm" in size:
                w, h = size.split()
                size = f"{h} {w}"
            elif "in" in size:
                w, h = size.split()
                size = f"{h} {w}"

        return f"""
        @page {{
            size: {size};
            margin: 20mm;
        }}
        """

    def _generate_html_fallback(
        self,
        html_content: str,
        css_content: Optional[str],
        data: Optional[Dict[str, Any]],
        filename: Optional[str],
    ) -> tuple[str, int, bytes]:
        """
        Fallback method when WeasyPrint is not available.
        Saves HTML file instead of PDF.

        Args:
            html_content: HTML content
            css_content: CSS content
            data: Template data
            filename: Output filename

        Returns:
            Tuple of (file_path, file_size, html_bytes)
        """
        # Render template with data
        if data:
            html_content = self._render_template(html_content, data)

        # Build full HTML
        full_html = self._build_full_html(
            html_content, css_content, "A4", "portrait"
        )

        # Generate filename
        if not filename:
            filename = f"html_{uuid.uuid4()}.html"
        elif not filename.endswith(".html"):
            filename = f"{filename}.html"

        # Save to file
        file_path = self.output_dir / filename
        html_bytes = full_html.encode("utf-8")
        
        with open(file_path, "wb") as f:
            f.write(html_bytes)

        file_size = len(html_bytes)

        return str(file_path), file_size, html_bytes

    def delete_pdf(self, file_path: str) -> bool:
        """
        Delete a generated PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            True if deleted successfully
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                return True
        except Exception:
            pass
        return False

    def get_pdf_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Dictionary with file info or None
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                stat = path.stat()
                return {
                    "filename": path.name,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime),
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                }
        except Exception:
            pass
        return None


# Singleton instance
pdf_generator = PdfGeneratorService()
