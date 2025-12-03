#!/usr/bin/env python3
"""
Debug script for PDF generation issues
"""

import sys
import traceback
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


def test_template_rendering():
    """Test if the template can be rendered without errors"""
    try:
        from app.models.wathq_pdf_data import WathqCommercialRegistrationPDF
        from app.services.wathq_pdf_service import pdf_service

        print("1. Testing template loading...")
        template = pdf_service.load_template("wathq-modern-template.html")
        print("✓ Template loaded successfully")

        print("2. Testing basic data model...")
        # Create minimal test data
        test_data = WathqCommercialRegistrationPDF(
            main_content="<p>Test content</p>",
            cr_number="1010711252",
            company_name="Test Company",
            wathq_data={"test": "data"},
        )
        print("✓ Data model created successfully")

        print("3. Testing template rendering...")
        html_content = template.render(**test_data.dict())
        print("✓ Template rendered successfully")
        print(f"HTML length: {len(html_content)} characters")

        print("4. Testing PDF generation...")
        pdf_bytes = pdf_service.generate_pdf_bytes(
            test_data, "wathq-modern-template.html"
        )
        print(f"✓ PDF generated successfully: {len(pdf_bytes)} bytes")

        # Save test files
        with open("test_output.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("✓ HTML saved to test_output.html")

        with open("test_output.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("✓ PDF saved to test_output.pdf")

        return True

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        return False


def test_with_real_data():
    """Test with sample CR data"""
    try:
        from app.services.wathq_pdf_service import pdf_service

        print("\n5. Testing with sample CR data...")

        # Sample CR data
        sample_cr_data = {
            "cr_number": "1010711252",
            "company_name": "شركة مجموعة توثيق العدل للتطوير والاستثمار العقاري",
            "legal_form": "شركة ذات مسؤولية محدودة",
            "capital": "1000000 ريال سعودي",
            "main_activity": "التطوير والاستثمار العقاري",
            "establishment_date": "2020-01-15",
            "expiry_date": "2030-01-15",
            "address": "الرياض، المملكة العربية السعودية",
            "status": "نشط",
        }

        # Create PDF data
        pdf_data = pdf_service.create_commercial_registration_pdf(sample_cr_data)
        print("✓ CR PDF data created successfully")

        # Generate PDF
        pdf_bytes = pdf_service.generate_pdf_bytes(
            pdf_data, "wathq-modern-template.html"
        )
        print(f"✓ CR PDF generated successfully: {len(pdf_bytes)} bytes")

        # Save CR PDF
        with open("test_cr_output.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("✓ CR PDF saved to test_cr_output.pdf")

        return True

    except Exception as e:
        print(f"✗ CR Test Error: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=== PDF Generation Debug Test ===\n")

    success1 = test_template_rendering()
    success2 = test_with_real_data()

    if success1 and success2:
        print("\n🎉 All tests passed! PDF generation is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
