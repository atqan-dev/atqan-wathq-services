"""
Examples of how to use the WATHQ PDF generation system
"""

from pathlib import Path

from app.models.wathq_pdf_data import InfoBox, InfoBoxItem, WathqPDFData
from app.services.wathq_pdf_service import pdf_service


def example_basic_document():
    """Example: Create a basic document"""

    pdf_data = WathqPDFData(
        document_title="تقرير شهري",
        main_content="""
        <p>هذا تقرير شهري يحتوي على معلومات مهمة حول أداء الشركة.</p>
        <p>تم إعداد هذا التقرير بتاريخ اليوم ويشمل جميع الأقسام.</p>
        """,
        show_signature=True,
        signature_label_1="المدير العام",
        signature_label_2="مدير المالية",
    )

    # Generate PDF bytes
    pdf_bytes = pdf_service.generate_pdf_bytes(pdf_data)

    # Save to file
    output_path = Path("output/basic_document.pdf")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"Basic document saved to: {output_path}")


def example_document_with_table():
    """Example: Create document with data table"""

    pdf_data = WathqPDFData(
        document_title="تقرير المبيعات الشهرية",
        main_content="""
        <p>يسرنا أن نقدم لكم تقرير المبيعات للشهر الحالي.</p>
        <p>يحتوي هذا التقرير على تفاصيل جميع العمليات التجارية.</p>
        """,
        show_table=True,
        table_title="بيانات المبيعات",
        table_headers=["اسم المنتج", "الكمية", "السعر", "الإجمالي"],
        table_data=[
            ["منتج أ", "100", "50 ريال", "5,000 ريال"],
            ["منتج ب", "75", "80 ريال", "6,000 ريال"],
            ["منتج ج", "200", "25 ريال", "5,000 ريال"],
        ],
        show_signature=True,
    )

    pdf_bytes = pdf_service.generate_pdf_bytes(pdf_data)

    output_path = Path("output/sales_report.pdf")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"Sales report saved to: {output_path}")


def example_commercial_registration():
    """Example: Create Commercial Registration document"""

    # Sample CR data (would normally come from WATHQ API)
    cr_data = {
        "cr_number": "1010123456",
        "company_name": "شركة الأعمال المتقدمة المحدودة",
        "legal_form": "شركة ذات مسؤولية محدودة",
        "capital": "1,000,000 ريال سعودي",
        "main_activity": "تجارة التجزئة",
        "establishment_date": "2020-01-15",
        "expiry_date": "2025-01-15",
        "address": "الرياض، المملكة العربية السعودية",
    }

    # Create CR PDF data
    pdf_data = pdf_service.create_commercial_registration_pdf(cr_data)

    pdf_bytes = pdf_service.generate_pdf_bytes(pdf_data)

    output_path = Path("output/commercial_registration.pdf")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"Commercial Registration saved to: {output_path}")


def example_multi_section_document():
    """Example: Create document with multiple sections"""

    sections_data = [
        {
            "title": "المقدمة",
            "content": "<p>هذا القسم يحتوي على مقدمة الوثيقة.</p>",
            "page_break": False,
        },
        {
            "title": "التفاصيل الرئيسية",
            "content": """
            <p>هذا القسم يحتوي على التفاصيل الرئيسية للموضوع.</p>
            <ul>
                <li>النقطة الأولى</li>
                <li>النقطة الثانية</li>
                <li>النقطة الثالثة</li>
            </ul>
            """,
            "page_break": True,
        },
        {
            "title": "الخلاصة",
            "content": "<p>هذا القسم يحتوي على خلاصة الوثيقة والتوصيات.</p>",
            "page_break": True,
        },
    ]

    pdf_data = pdf_service.create_multi_section_document(
        sections_data=sections_data,
        document_title="وثيقة متعددة الأقسام",
        show_signature=True,
        show_page_numbers=True,
    )

    pdf_bytes = pdf_service.generate_pdf_bytes(pdf_data)

    output_path = Path("output/multi_section_document.pdf")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"Multi-section document saved to: {output_path}")


def example_custom_info_boxes():
    """Example: Create document with custom info boxes"""

    # Create info boxes
    info_boxes = [
        InfoBox(
            title="معلومات الشركة",
            items=[
                InfoBoxItem(label="اسم الشركة", value="شركة التقنية المتقدمة"),
                InfoBoxItem(label="رقم السجل التجاري", value="1010123456"),
                InfoBoxItem(label="تاريخ التأسيس", value="15 يناير 2020"),
            ],
        ),
        InfoBox(
            title="معلومات الاتصال",
            items=[
                InfoBoxItem(label="الهاتف", value="0112345678"),
                InfoBoxItem(label="البريد الإلكتروني", value="info@company.com"),
                InfoBoxItem(label="العنوان", value="الرياض، السعودية"),
            ],
        ),
    ]

    pdf_data = WathqPDFData(
        document_title="ملف الشركة الشامل",
        main_content="<p>هذه الوثيقة تحتوي على معلومات شاملة عن الشركة.</p>",
        info_boxes=info_boxes,
        show_signature=True,
    )

    pdf_bytes = pdf_service.generate_pdf_bytes(pdf_data)

    output_path = Path("output/company_profile.pdf")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"Company profile saved to: {output_path}")


def example_with_logo():
    """Example: Create document with logo"""

    pdf_data = WathqPDFData(
        document_title="وثيقة رسمية مع الشعار",
        main_content="<p>هذه وثيقة رسمية تحتوي على شعار الشركة.</p>",
        # You would set logo_base64 or logo_url here
        # logo_url="path/to/logo.png",
        show_signature=True,
    )

    # Add logo from file if it exists
    logo_path = "assets/logo.png"
    if Path(logo_path).exists():
        pdf_data = pdf_service.add_logo_from_file(pdf_data, logo_path)

    pdf_bytes = pdf_service.generate_pdf_bytes(pdf_data)

    output_path = Path("output/document_with_logo.pdf")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"Document with logo saved to: {output_path}")


def example_html_preview():
    """Example: Generate HTML preview"""

    pdf_data = WathqPDFData(
        document_title="معاينة HTML",
        main_content="<p>هذا مثال على معاينة HTML قبل إنشاء PDF.</p>",
        show_signature=True,
    )

    html_content = pdf_service.preview_html(pdf_data)

    output_path = Path("output/preview.html")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML preview saved to: {output_path}")


def run_all_examples():
    """Run all examples"""
    print("Running PDF generation examples...")

    try:
        example_basic_document()
        example_document_with_table()
        example_commercial_registration()
        example_multi_section_document()
        example_custom_info_boxes()
        example_with_logo()
        example_html_preview()

        print("\n✅ All examples completed successfully!")
        print("Check the 'output' directory for generated files.")

    except Exception as e:
        print(f"❌ Error running examples: {e}")


if __name__ == "__main__":
    run_all_examples()
