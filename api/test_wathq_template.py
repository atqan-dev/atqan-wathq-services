#!/usr/bin/env python3
"""
Test script for the new WATHQ PDF template
"""

from pathlib import Path

from app.services.wathq_pdf_service import pdf_service


def test_wathq_template():
    """Test the new WATHQ modern template with sample data"""

    # Sample WATHQ data (similar to what would come from live/offline API)
    sample_wathq_data = {
        "service_name": "السجل التجاري ( التشريعات الجديدة )",
        "cr_number": "1010711252",
        "company_name": "شركة مجموعة توثيق العدل للتطوير والاستثمار العقاري",
        "legal_form": "شركة ذات مسؤولية محدودة",
        "capital": "1000000 ريال سعودي",
        "main_activity": "التطوير والاستثمار العقاري",
        "establishment_date": "2020-01-15",
        "expiry_date": "2030-01-15",
        "address": "الرياض، المملكة العربية السعودية",
        "status": "نشط",
        "owners": [
            {
                "name": "أحمد محمد العلي",
                "nationality": "سعودي",
                "id_number": "1234567890",
                "position": "مدير عام",
            }
        ],
        "managers": [{"name": "فاطمة أحمد السالم", "position": "مدير مالي"}],
        "description": "هذه وثيقة السجل التجاري ( التشريعات الجديدة ) الصادرة من منصة وثق الإلكترونية",
    }

    print("Testing WATHQ Modern Template...")

    # Test 1: Generate HTML preview
    print("1. Generating HTML preview...")
    try:
        html_content = pdf_service.preview_wathq_html(
            wathq_data=sample_wathq_data,
            document_title="السجل التجاري ( التشريعات الجديدة ) - شركة مجموعة توثيق العدل",
            show_watermark=True,
            watermark_text="وثق",
            show_signature=True,
            show_raw_data=False,
        )

        # Save HTML preview
        preview_path = Path("wathq_preview.html")
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"✓ HTML preview saved to: {preview_path.absolute()}")

    except Exception as e:
        print(f"✗ HTML preview failed: {e}")

    # Test 2: Generate PDF bytes
    print("2. Generating PDF...")
    try:
        pdf_bytes = pdf_service.generate_wathq_pdf_bytes(
            wathq_data=sample_wathq_data,
            document_title="السجل التجاري ( التشريعات الجديدة ) - شركة مجموعة توثيق العدل",
            show_watermark=True,
            watermark_text="وثق",
            show_signature=True,
        )

        # Save PDF file
        pdf_path = Path("wathq_sample.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        print(
            f"✓ PDF generated successfully: {pdf_path.absolute()} ({len(pdf_bytes)} bytes)"
        )

    except Exception as e:
        print(f"✗ PDF generation failed: {e}")

    # Test 3: Test with minimal data
    print("3. Testing with minimal data...")
    try:
        minimal_data = {
            "service_name": "خدمة وثق",
            "description": "بيانات أساسية من منصة وثق",
        }

        html_minimal = pdf_service.preview_wathq_html(
            wathq_data=minimal_data,
            document_title="وثيقة بسيطة",
            show_raw_data=True,  # Show JSON data for debugging
        )

        minimal_path = Path("wathq_minimal_preview.html")
        with open(minimal_path, "w", encoding="utf-8") as f:
            f.write(html_minimal)
        print(f"✓ Minimal data test successful: {minimal_path.absolute()}")

    except Exception as e:
        print(f"✗ Minimal data test failed: {e}")

    print("\nTemplate testing completed!")
    print("Files generated:")
    print("- wathq_preview.html (Full data HTML preview)")
    print("- wathq_sample.pdf (Full data PDF)")
    print("- wathq_minimal_preview.html (Minimal data with JSON)")


if __name__ == "__main__":
    test_wathq_template()
