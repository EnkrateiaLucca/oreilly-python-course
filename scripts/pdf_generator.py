# Model: Claude-4
# Prompt
# "Generate a Python script that creates a self-contained PDF document using reportlab. The script should include:
# - A title and a subtitle with different font sizes and styles.
# - A paragraph of placeholder text.
# - A table with sample data (3 columns, 5 rows).
# - A simple bar chart generated within the script.
# - A logo or shape (such as a rectangle or circle) drawn directly on the PDF.  
# The script should not require any external data sources and should generate a complete, properly formatted PDF file when executed."

# save this script in my desktop folder

# /// script
# dependencies = [
#   "reportlab",
# ]
# ///

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, Circle
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

def create_pdf():
    # Get desktop path
    desktop_path = os.path.expanduser("~/Desktop")
    filename = os.path.join(desktop_path, "sample_report.pdf")
    
    # Create PDF document
    doc = SimpleDocTemplate(filename, pagesize=letter, topMargin=0.5*inch)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    # Custom subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    # Add title
    title = Paragraph("Company Annual Report", title_style)
    story.append(title)
    
    # Add subtitle
    subtitle = Paragraph("Financial Performance Overview 2024", subtitle_style)
    story.append(subtitle)
    
    # Add spacer
    story.append(Spacer(1, 20))
    
    # Add paragraph
    paragraph_text = """
    This comprehensive report presents our company's outstanding performance throughout 2024. 
    Our strategic initiatives have resulted in significant growth across all key metrics, 
    demonstrating our commitment to excellence and innovation. The following data showcases 
    our achievements in revenue, customer satisfaction, and market expansion. We continue 
    to build on our strong foundation while exploring new opportunities for sustainable growth.
    """
    para = Paragraph(paragraph_text, styles['Normal'])
    story.append(para)
    story.append(Spacer(1, 20))
    
    # Create table data
    table_data = [
        ['Quarter', 'Revenue ($M)', 'Growth (%)'],
        ['Q1 2024', '125.4', '12.3'],
        ['Q2 2024', '142.8', '18.7'],
        ['Q3 2024', '156.2', '15.2'],
        ['Q4 2024', '178.9', '22.1']
    ]
    
    # Create table
    table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))
    
    # Create bar chart
    drawing = Drawing(400, 200)
    
    # Add logo shapes
    logo_rect = Rect(10, 150, 60, 30, fillColor=colors.darkblue, strokeColor=colors.black)
    logo_circle = Circle(90, 165, 15, fillColor=colors.orange, strokeColor=colors.black)
    drawing.add(logo_rect)
    drawing.add(logo_circle)
    
    # Create bar chart
    chart = VerticalBarChart()
    chart.x = 120
    chart.y = 50
    chart.height = 125
    chart.width = 250
    chart.data = [[125.4, 142.8, 156.2, 178.9]]
    chart.categoryAxis.labels.boxAnchor = 'ne'
    chart.categoryAxis.labels.dx = 8
    chart.categoryAxis.labels.dy = -2
    chart.categoryAxis.labels.angle = 30
    chart.categoryAxis.categoryNames = ['Q1', 'Q2', 'Q3', 'Q4']
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 200
    chart.bars[0].fillColor = colors.darkblue
    chart.bars[0].strokeColor = colors.black
    
    drawing.add(chart)
    story.append(drawing)
    
    # Build PDF
    doc.build(story)
    print(f"PDF generated successfully: {filename}")

if __name__ == "__main__":
    create_pdf()
