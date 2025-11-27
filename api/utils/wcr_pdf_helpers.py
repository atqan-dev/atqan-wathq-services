import base64
from typing import Optional, Dict, Any
from pathlib import Path
import io
from PIL import Image


class PDFHelper:
    """Helper class for PDF generation tasks"""

    @staticmethod
    def image_to_base64(image_path: str, resize: Optional[tuple] = None) -> str:
        """
        Convert image to base64 with optional resizing

        Args:
            image_path: Path to image file
            resize: Optional tuple (width, height) to resize image

        Returns:
            Base64 encoded string
        """
        img = Image.open(image_path)

        if resize:
            img = img.resize(resize, Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format=img.format or "PNG")
        img_bytes = buffer.getvalue()

        return base64.b64encode(img_bytes).decode("utf-8")

    @staticmethod
    def create_html_table(headers: list, data: list) -> str:
        """
        Create HTML table string from headers and data

        Args:
            headers: List of header strings
            data: List of lists containing row data

        Returns:
            HTML table string
        """
        html = '<table class="data-table">\n<thead>\n<tr>\n'

        for header in headers:
            html += f"<th>{header}</th>\n"

        html += "</tr>\n</thead>\n<tbody>\n"

        for row in data:
            html += "<tr>\n"
            for cell in row:
                html += f"<td>{cell}</td>\n"
            html += "</tr>\n"

        html += "</tbody>\n</table>"

        return html

    @staticmethod
    def format_arabic_date(date_str: str) -> str:
        """
        Format date for Arabic display

        Args:
            date_str: Date string in format YYYY-MM-DD

        Returns:
            Formatted Arabic date string
        """
        from datetime import datetime

        months_ar = {
            1: "يناير",
            2: "فبراير",
            3: "مارس",
            4: "أبريل",
            5: "مايو",
            6: "يونيو",
            7: "يوليو",
            8: "أغسطس",
            9: "سبتمبر",
            10: "أكتوبر",
            11: "نوفمبر",
            12: "ديسمبر",
        }

        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{date_obj.day} {months_ar[date_obj.month]} {date_obj.year}"

    @staticmethod
    def create_styled_paragraph(text: str, style: str = "normal") -> str:
        """
        Create styled HTML paragraph

        Args:
            text: Paragraph text
            style: Style type (normal, bold, centered, highlight)

        Returns:
            Styled HTML paragraph
        """
        styles = {
            "normal": "<p>{}</p>",
            "bold": "<p style='font-weight: bold;'>{}</p>",
            "centered": "<p style='text-align: center;'>{}</p>",
            "highlight": "<p style='background: #fff3cd; padding: 10px; border-right: 4px solid #f39c12;'>{}</p>",
            "title": "<h2 style='color: #003366; border-bottom: 2px solid #f39c12; padding-bottom: 10px;'>{}</h2>",
        }

        return styles.get(style, styles["normal"]).format(text)

    @staticmethod
    def create_info_box(title: str, content: Dict[str, str]) -> str:
        """
        Create an information box with title and key-value pairs

        Args:
            title: Box title
            content: Dictionary of key-value pairs

        Returns:
            HTML info box
        """
        html = f"""
        <div style="border: 2px solid #003366; border-radius: 5px; padding: 20px; margin: 20px 0; background: #f8f9fa;">
            <h3 style="color: #003366; margin-bottom: 15px; border-bottom: 2px solid #f39c12; padding-bottom: 10px;">{title}</h3>
        """

        for key, value in content.items():
            html += f"""
            <div style="margin: 10px 0; display: flex; justify-content: space-between;">
                <span style="font-weight: bold; color: #003366;">{key}:</span>
                <span>{value}</span>
            </div>
            """

        html += "</div>"
        return html

    @staticmethod
    def create_list(items: list, ordered: bool = False) -> str:
        """
        Create HTML list

        Args:
            items: List of items
            ordered: If True, creates ordered list, else unordered

        Returns:
            HTML list string
        """
        tag = "ol" if ordered else "ul"
        html = f"<{tag} style='margin: 20px 0; padding-right: 30px; line-height: 2;'>\n"

        for item in items:
            html += f"<li>{item}</li>\n"

        html += f"</{tag}>"
        return html
