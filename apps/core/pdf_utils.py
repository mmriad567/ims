from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


def get_pdf_styles():
    """Return a dict of ReportLab paragraph styles for headers and text."""
    styles = getSampleStyleSheet()
    return {
        'title': ParagraphStyle(name='Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16, spaceAfter=6),
        'subtitle': ParagraphStyle(name='Subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, spaceAfter=10),
        'footer': styles['Italic']
    }


def get_base_pdf_story(title_text, subtitle_texts):
    """Return a list of Flowables for the PDF header (title + subtitles + spacer)."""
    styles = get_pdf_styles()
    story = [Paragraph(title_text, styles['title'])]
    for text in subtitle_texts:
        story.append(Paragraph(text, styles['subtitle']))
    story.append(Spacer(1, 10))
    return story


def get_styled_table(data, col_widths=None):
    """Return a Table with standard styling (blue header, grid, zebra stripes)."""
    table = Table(data, repeatRows=1, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return table


def add_footer_to_story(story):
    """Append generation timestamp to the PDF story."""
    styles = get_pdf_styles()
    timestamp = datetime.now().strftime('%d %B %Y, %I:%M %p')
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"Generated on {timestamp}", styles['footer']))


def build_pdf(buffer, story):
    """Build the PDF into the given BytesIO buffer."""
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )
    doc.build(story)
