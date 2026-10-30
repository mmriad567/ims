from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable


def get_pdf_styles():
    """Return a dict of ReportLab paragraph styles for headers and text."""
    styles = getSampleStyleSheet()
    return {
        'title': ParagraphStyle(name='Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16, spaceAfter=6),
        'subtitle': ParagraphStyle(name='Subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, spaceAfter=10),
        'footer': styles['Italic']
    }


def get_base_pdf_story(title_text, subtitle_texts):
    """Return a list of Flowables for the PDF header (title + subtitles + separator line)."""
    styles = get_pdf_styles()
    story = [Paragraph(title_text, styles['title'])]
    for text in subtitle_texts:
        story.append(Paragraph(text, styles['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceBefore=5, spaceAfter=15))
    return story


def get_styled_table(data, col_widths=None):
    """Return a Table with professional styling (clean borders, good padding)."""
    table = Table(data, repeatRows=1, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    return table


def add_footer_to_story(story):
    """Append generation timestamp to the PDF story."""
    styles = get_pdf_styles()
    timestamp = datetime.now().strftime('%d %B %Y, %I:%M %p')
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Generated on {timestamp}", styles['footer']))


def build_pdf(buffer, story, signature_labels=None):
    """Build the PDF and optionally draw signatures at the bottom of every page."""
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=20*mm, bottomMargin=35*mm
    )

    def draw_page_footer(canvas, doc):
        """Draw the generation timestamp and optional signature lines on each page."""
        canvas.saveState()
        timestamp = datetime.now().strftime('%d %B %Y, %I:%M %p')
        canvas.setFont('Helvetica-Oblique', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(A4[0]/2.0, 15*mm, f"Generated on {timestamp}")

        if signature_labels:
            canvas.setFont('Helvetica', 10)
            canvas.setFillColor(colors.black)
            canvas.line(25*mm, 30*mm, 75*mm, 30*mm)
            canvas.drawCentredString(50*mm, 25*mm, signature_labels[0])
            canvas.line(135*mm, 30*mm, 185*mm, 30*mm)
            canvas.drawCentredString(160*mm, 25*mm, signature_labels[1])
        canvas.restoreState()

    doc.build(story, onFirstPage=draw_page_footer, onLaterPages=draw_page_footer)
