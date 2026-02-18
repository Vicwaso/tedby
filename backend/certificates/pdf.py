from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

def build_pin_certificate_pdf(full_name: str, pin: str, gen_email: str) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    y = height - 30 * mm
    c.setFont("Helvetica-Bold", 18)
    c.drawString(25 * mm, y, "PIN Certificate")

    y -= 12 * mm
    c.setFont("Helvetica", 10)
    c.drawString(25 * mm, y, "Kenya Revenue Authority")
    y -= 5 * mm
    c.drawString(25 * mm, y, "Website: www.kra.go.ke")
    y -= 5 * mm
    c.drawString(25 * mm, y, "Contact: +254 (0)20 4999 999 / 020 4998 000")

    y -= 12 * mm
    c.setFont("Helvetica", 11)
    c.drawString(25 * mm, y, "Certificate Date:")
    c.drawString(65 * mm, y, "")

    y -= 18 * mm
    c.setFont("Helvetica-Bold", 24)
    c.drawString(25 * mm, y, f"PIN: {pin}")

    y -= 16 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(25 * mm, y, "Taxpayer Details")
    y -= 8 * mm
    c.setFont("Helvetica", 11)
    c.drawString(25 * mm, y, f"Full Name: {full_name}")
    y -= 6 * mm
    c.drawString(25 * mm, y, f"Generated Email: {gen_email}")

    y -= 14 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(25 * mm, y, "Tax Obligations (Sample)")
    y -= 8 * mm
    c.setFont("Helvetica", 10)
    c.drawString(25 * mm, y, "- Income Tax")
    y -= 5 * mm
    c.drawString(25 * mm, y, "- VAT")
    y -= 5 * mm
    c.drawString(25 * mm, y, "- PAYE")

    y -= 14 * mm
    c.setFont("Helvetica", 9)
    c.drawString(25 * mm, y, "Disclaimer: This certificate is generated for informational purposes based on provided data.")

    c.showPage()
    c.save()
    return buf.getvalue()
