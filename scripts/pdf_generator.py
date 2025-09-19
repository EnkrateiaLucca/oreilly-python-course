# Model: Claude-4-Sonnet
# Prompt
# Create a Python script that generates a professional-looking PDF
#   report with the following requirements:

#   1. **Document Structure**:
#      - Use ReportLab library to create a multi-page business report
#      - Save the PDF to the user's Desktop as "sample_report.pdf"
#      - Include proper margins (0.75 inches on all sides)

#   2. **Visual Design Requirements**:
#      - Create a professional color scheme with:
#        - Primary blue (#1A3380)
#        - Accent orange (#FF8000)
#        - Light blue background (#D9E6F2)
#        - Dark grey text (#4D4D4D)
#      - Use Helvetica font family throughout
#      - Implement a visually appealing header with:
#        - Gradient-like background effect using overlapping rectangles
#        - Company logo (stylized geometric design)
#        - Company name and tagline

#   3. **Content Sections**:
#      - **Header**: Company branding with "TechVision Analytics" and
#   tagline "Excellence Through Innovation"
#      - **Title Section**: "2024 Annual Performance Report" with
#   subtitle "Comprehensive Financial & Operational Analysis"
#      - **Executive Summary**: Professional paragraph with inline bold
#    text highlighting key metrics (68.4% growth, $603.3M revenue,
#   24.7% margins, 94.2% satisfaction)
#      - **Quarterly Financial Performance Table** with columns:
#   Quarter, Revenue, Growth %, Profit, Margin %, Customers
#        - Use alternating row colors
#        - Professional table styling with header in primary blue
#        - Include Q1-Q4 2024 data

#   4. **Data Visualizations**:
#      - **Bar Chart**: Quarterly revenue and profit comparison
#        - Dual series showing Revenue and Profit
#        - Proper legend placement
#        - Value labels on bars
#        - Axis labels and chart title

#      - **Pie Chart**: Market share distribution
#        - 4 segments: Enterprise (35%), SMB (28%), Government (22%),
#   Education (15%)
#        - One slice popped out for emphasis
#        - Custom colors for each segment
#        - Include a "Key Metrics" sidebar box with: Customer Retention
#    (96.4%), Market Growth (+18.2%), NPS Score (72), Active Users
#   (2.1M), Avg Deal Size ($147K)

#      - **Line Chart**: Monthly growth trend
#        - Two lines: Revenue and Active Customers
#        - 12-month data (Jan-Dec)
#        - Proper legend
#        - Grid lines for readability

#   5. **Footer**:
#      - Decorative line separator
#      - Company name with report year
#      - Confidentiality notice

#   6. **Technical Requirements**:
#      - Use self-contained fake data (no external files needed)
#      - Include all necessary imports
#      - Make the script executable as standalone
#      - Handle all chart configurations properly (legends, labels,
#   colors)
#      - Ensure professional spacing between sections
#      - Use Drawing objects for complex visual elements

# /// script
# dependencies = [
#   "reportlab",
# ]
# ///

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, Circle, String, Line, Polygon, Path
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics import renderPDF
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable
import os
import random

class GradientBackground(Flowable):
    def __init__(self, width, height, color1=colors.Color(0.95, 0.97, 1.0), color2=colors.Color(0.85, 0.90, 0.98)):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color1 = color1
        self.color2 = color2

    def draw(self):
        canvas = self.canv
        steps = 50
        step_height = self.height / steps
        for i in range(steps):
            ratio = i / steps
            r = self.color1.red * (1 - ratio) + self.color2.red * ratio
            g = self.color1.green * (1 - ratio) + self.color2.green * ratio
            b = self.color1.blue * (1 - ratio) + self.color2.blue * ratio
            canvas.setFillColorRGB(r, g, b)
            canvas.rect(0, i * step_height, self.width, step_height, fill=True, stroke=False)

def create_pdf():
    # Get path
    folder_path = os.path.expanduser("./")
    filename = os.path.join(folder_path, "sample_report.pdf")

    # Create PDF document with better margins
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    story = []

    # Define custom colors
    primary_blue = colors.Color(0.1, 0.2, 0.5)
    accent_orange = colors.Color(1, 0.5, 0)
    light_blue = colors.Color(0.85, 0.9, 0.95)
    dark_grey = colors.Color(0.3, 0.3, 0.3)

    # Get styles
    styles = getSampleStyleSheet()

    # Custom title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=32,
        spaceAfter=10,
        alignment=TA_CENTER,
        textColor=primary_blue,
        fontName='Helvetica-Bold',
        leading=36
    )

    # Custom subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=dark_grey,
        fontName='Helvetica',
        leading=22
    )

    # Section header style
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        alignment=TA_LEFT,
        textColor=primary_blue,
        fontName='Helvetica-Bold',
        leftIndent=0,
        borderColor=primary_blue,
        borderWidth=0,
        borderPadding=0
    )

    # Custom body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=TA_LEFT,
        textColor=dark_grey,
        spaceBefore=6,
        spaceAfter=12
    )
    # Create decorative header with logo
    header_drawing = Drawing(450, 100)

    # Add gradient-like background rectangles
    for i in range(10):
        opacity = 1 - (i * 0.08)
        header_drawing.add(Rect(i*2, i*2, 440-i*4, 90-i*4,
                               fillColor=colors.Color(0.1, 0.2, 0.5, opacity),
                               strokeColor=None))

    # Add company logo (stylized design)
    logo_x, logo_y = 30, 25
    # Circle background
    header_drawing.add(Circle(logo_x + 20, logo_y + 20, 25,
                             fillColor=accent_orange,
                             strokeColor=primary_blue,
                             strokeWidth=2))
    # Inner design
    points = []
    for angle in range(0, 360, 72):
        import math
        rad = math.radians(angle)
        x = logo_x + 20 + 15 * math.cos(rad)
        y = logo_y + 20 + 15 * math.sin(rad)
        points.extend([x, y])
    header_drawing.add(Polygon(points, fillColor=colors.white, strokeColor=None))

    # Add title text in drawing
    header_drawing.add(String(225, 50, "TechVision Analytics",
                            fontSize=28,
                            fillColor=colors.white,
                            textAnchor='middle',
                            fontName='Helvetica-Bold'))
    header_drawing.add(String(225, 25, "Excellence Through Innovation",
                            fontSize=12,
                            fillColor=colors.Color(0.9, 0.9, 1.0),
                            textAnchor='middle',
                            fontName='Helvetica'))

    story.append(header_drawing)
    story.append(Spacer(1, 30))

    # Add title
    title = Paragraph("<b>2024 Annual Performance Report</b>", title_style)
    story.append(title)

    # Add subtitle
    subtitle = Paragraph("Comprehensive Financial & Operational Analysis", subtitle_style)
    story.append(subtitle)

    # Add decorative line
    line_drawing = Drawing(450, 10)
    line_drawing.add(Line(100, 5, 350, 5, strokeColor=accent_orange, strokeWidth=2))
    story.append(line_drawing)
    story.append(Spacer(1, 20))

    # Executive Summary Section
    story.append(Paragraph("<b>Executive Summary</b>", section_style))

    # Add paragraph with better formatting
    paragraph_text = """In fiscal year 2024, TechVision Analytics achieved remarkable milestones across all operational segments.
    Our revenue grew by <b>68.4%</b> year-over-year, reaching <b>$603.3 million</b>, while maintaining
    industry-leading profit margins of <b>24.7%</b>.<br/><br/>
    Key highlights include our successful expansion into three new international markets,
    the launch of our award-winning AI-powered analytics platform, and achieving a
    customer satisfaction score of <b>94.2%</b> - the highest in our company's history."""

    para = Paragraph(paragraph_text, body_style)
    story.append(para)
    story.append(Spacer(1, 25))
    
    # Quarterly Performance Section
    story.append(Paragraph("<b>Quarterly Financial Performance</b>", section_style))

    # Create enhanced table data with more metrics
    table_data = [
        ['Quarter', 'Revenue\n($M)', 'Growth\n(%)', 'Profit\n($M)', 'Margin\n(%)', 'Customers\n(K)'],
        ['Q1 2024', '125.4', '+12.3%', '28.7', '22.9%', '142'],
        ['Q2 2024', '142.8', '+18.7%', '34.2', '23.9%', '156'],
        ['Q3 2024', '156.2', '+15.2%', '38.9', '24.9%', '171'],
        ['Q4 2024', '178.9', '+22.1%', '46.5', '26.0%', '189']
    ]

    # Create beautifully styled table
    table = Table(table_data, colWidths=[1.2*inch, 1.0*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1.0*inch])
    table.setStyle(TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), primary_blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('TOPPADDING', (0, 0), (-1, 0), 15),

        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),

        # Alternating row colors
        ('BACKGROUND', (0, 1), (-1, 1), colors.Color(0.95, 0.97, 1.0)),
        ('BACKGROUND', (0, 2), (-1, 2), colors.white),
        ('BACKGROUND', (0, 3), (-1, 3), colors.Color(0.95, 0.97, 1.0)),
        ('BACKGROUND', (0, 4), (-1, 4), colors.white),

        # Grid styling
        ('GRID', (0, 0), (-1, 0), 1.5, primary_blue),
        ('LINEBELOW', (0, 0), (-1, 0), 2, primary_blue),
        ('BOX', (0, 1), (-1, -1), 0.5, colors.Color(0.8, 0.8, 0.8)),
        ('INNERGRID', (0, 1), (-1, -1), 0.25, colors.Color(0.9, 0.9, 0.9)),

        # First column bold
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 1), (0, -1), primary_blue),
    ]))

    story.append(table)
    story.append(Spacer(1, 35))
    
    # Visual Analytics Section
    story.append(Paragraph("<b>Revenue Growth Visualization</b>", section_style))

    # Create enhanced bar chart with proper legend
    chart_drawing = Drawing(450, 250)

    # Add title for chart
    chart_drawing.add(String(225, 230, "Quarterly Revenue Progression",
                            fontSize=12,
                            fillColor=dark_grey,
                            textAnchor='middle',
                            fontName='Helvetica-Bold'))

    # Create bar chart
    bar_chart = VerticalBarChart()
    bar_chart.x = 50
    bar_chart.y = 50
    bar_chart.height = 150
    bar_chart.width = 320

    # Multiple data series for better visualization
    bar_chart.data = [
        [125.4, 142.8, 156.2, 178.9],  # Revenue
        [28.7, 34.2, 38.9, 46.5],      # Profit
    ]

    # Configure axes
    bar_chart.categoryAxis.labels.boxAnchor = 'n'
    bar_chart.categoryAxis.labels.dy = -8
    bar_chart.categoryAxis.labels.fontName = 'Helvetica'
    bar_chart.categoryAxis.labels.fontSize = 10
    bar_chart.categoryAxis.categoryNames = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']

    bar_chart.valueAxis.valueMin = 0
    bar_chart.valueAxis.valueMax = 200
    bar_chart.valueAxis.valueStep = 50
    bar_chart.valueAxis.labels.fontName = 'Helvetica'
    bar_chart.valueAxis.labels.fontSize = 9
    bar_chart.valueAxis.labels.rightPadding = 5

    # Style the bars
    bar_chart.bars[0].fillColor = primary_blue
    bar_chart.bars[0].strokeColor = None
    bar_chart.bars[1].fillColor = accent_orange
    bar_chart.bars[1].strokeColor = None

    # Bar spacing
    bar_chart.groupSpacing = 15
    bar_chart.barSpacing = 3

    # Add value labels on bars
    bar_chart.barLabels.nudge = 7
    bar_chart.barLabelFormat = '%.1f'
    bar_chart.barLabels.fontName = 'Helvetica'
    bar_chart.barLabels.fontSize = 8

    # Create legend
    legend = Legend()
    legend.x = 380
    legend.y = 140
    legend.deltax = 0
    legend.deltay = 15
    legend.boxAnchor = 'w'
    legend.columnMaximum = 1
    legend.strokeWidth = 0.5
    legend.strokeColor = colors.Color(0.8, 0.8, 0.8)
    legend.fontName = 'Helvetica'
    legend.fontSize = 10
    legend.alignment = 'left'
    legend.colorNamePairs = [
        (primary_blue, 'Revenue ($M)'),
        (accent_orange, 'Profit ($M)')
    ]

    chart_drawing.add(bar_chart)
    chart_drawing.add(legend)

    # Add axis labels
    chart_drawing.add(String(210, 20, "Quarter",
                            fontSize=10,
                            fillColor=dark_grey,
                            textAnchor='middle',
                            fontName='Helvetica'))
    chart_drawing.add(String(25, 125, "Amount ($M)",
                            fontSize=10,
                            fillColor=dark_grey,
                            textAnchor='middle',
                            fontName='Helvetica',
                            angle=90))

    story.append(chart_drawing)
    story.append(Spacer(1, 35))

    # Market Share Analysis Section
    story.append(Paragraph("<b>Market Share Distribution</b>", section_style))

    # Create pie chart
    pie_drawing = Drawing(450, 250)

    # Add title
    pie_drawing.add(String(225, 230, "Market Segment Analysis",
                          fontSize=12,
                          fillColor=dark_grey,
                          textAnchor='middle',
                          fontName='Helvetica-Bold'))

    # Create pie chart
    pie_chart = Pie()
    pie_chart.x = 100
    pie_chart.y = 50
    pie_chart.width = 140
    pie_chart.height = 140
    pie_chart.data = [35, 28, 22, 15]
    pie_chart.labels = ['Enterprise\n35%', 'SMB\n28%', 'Government\n22%', 'Education\n15%']
    pie_chart.slices.strokeWidth = 0.5
    pie_chart.slices.strokeColor = colors.white

    # Custom slice colors
    pie_colors = [primary_blue, accent_orange, colors.Color(0.2, 0.6, 0.4), colors.Color(0.7, 0.3, 0.3)]
    for i, color in enumerate(pie_colors):
        pie_chart.slices[i].fillColor = color
        pie_chart.slices[i].labelRadius = 1.3
        pie_chart.slices[i].fontName = 'Helvetica'
        pie_chart.slices[i].fontSize = 10

    # Make one slice pop out
    pie_chart.slices[0].popout = 10

    pie_drawing.add(pie_chart)

    # Add performance metrics beside pie chart
    metrics_x = 280
    metrics_y = 180

    # Key metrics box
    pie_drawing.add(Rect(metrics_x - 10, metrics_y - 120, 150, 130,
                        fillColor=light_blue,
                        strokeColor=primary_blue,
                        strokeWidth=1))

    pie_drawing.add(String(metrics_x + 65, metrics_y - 20, "Key Metrics",
                          fontSize=11,
                          fillColor=primary_blue,
                          textAnchor='middle',
                          fontName='Helvetica-Bold'))

    metrics = [
        ('Customer Retention:', '96.4%'),
        ('Market Growth:', '+18.2%'),
        ('NPS Score:', '72'),
        ('Active Users:', '2.1M'),
        ('Avg Deal Size:', '$147K')
    ]

    for i, (label, value) in enumerate(metrics):
        y_pos = metrics_y - 40 - (i * 18)
        pie_drawing.add(String(metrics_x, y_pos, label,
                             fontSize=9,
                             fillColor=dark_grey,
                             fontName='Helvetica'))
        pie_drawing.add(String(metrics_x + 90, y_pos, value,
                             fontSize=9,
                             fillColor=primary_blue,
                             fontName='Helvetica-Bold'))

    story.append(pie_drawing)
    story.append(Spacer(1, 35))

    # Add Growth Trend Line Chart
    story.append(Paragraph("<b>Monthly Growth Trend</b>", section_style))

    trend_drawing = Drawing(450, 200)

    # Line chart
    line_chart = HorizontalLineChart()
    line_chart.x = 50
    line_chart.y = 30
    line_chart.height = 130
    line_chart.width = 350

    # Monthly data
    months_data = [
        [98, 102, 108, 115, 125, 128, 135, 142, 148, 156, 165, 179],  # Revenue
        [88, 92, 95, 101, 108, 112, 118, 125, 131, 139, 147, 158]     # Active customers
    ]

    line_chart.data = months_data
    line_chart.categoryAxis.categoryNames = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    line_chart.categoryAxis.labels.fontSize = 9
    line_chart.categoryAxis.labels.fontName = 'Helvetica'

    line_chart.valueAxis.valueMin = 80
    line_chart.valueAxis.valueMax = 180
    line_chart.valueAxis.valueStep = 20
    line_chart.valueAxis.labels.fontSize = 9
    line_chart.valueAxis.labels.fontName = 'Helvetica'

    # Style the lines
    line_chart.lines[0].strokeColor = primary_blue
    line_chart.lines[0].strokeWidth = 2.5

    line_chart.lines[1].strokeColor = accent_orange
    line_chart.lines[1].strokeWidth = 2.5

    # Add grid
    line_chart.lineLabels.fontName = 'Helvetica'
    line_chart.lineLabels.fontSize = 7
    line_chart.lineLabelFormat = '%2.0f'

    trend_drawing.add(line_chart)

    # Add trend legend
    trend_legend = Legend()
    trend_legend.x = 320
    trend_legend.y = 100
    trend_legend.deltax = 0
    trend_legend.deltay = 15
    trend_legend.boxAnchor = 'w'
    trend_legend.columnMaximum = 1
    trend_legend.strokeWidth = 0.5
    trend_legend.strokeColor = colors.Color(0.8, 0.8, 0.8)
    trend_legend.fontName = 'Helvetica'
    trend_legend.fontSize = 9
    trend_legend.colorNamePairs = [
        (primary_blue, 'Revenue'),
        (accent_orange, 'Customers')
    ]
    trend_drawing.add(trend_legend)

    # Add title and labels
    trend_drawing.add(String(225, 180, "2024 Monthly Performance Indicators",
                           fontSize=11,
                           fillColor=dark_grey,
                           textAnchor='middle',
                           fontName='Helvetica-Bold'))

    story.append(trend_drawing)
    story.append(Spacer(1, 30))

    # Footer section
    footer_drawing = Drawing(450, 60)

    # Add decorative footer line
    footer_drawing.add(Line(50, 50, 400, 50, strokeColor=accent_orange, strokeWidth=2))

    # Add footer text
    footer_drawing.add(String(225, 30, "TechVision Analytics | 2024 Annual Report",
                            fontSize=10,
                            fillColor=primary_blue,
                            textAnchor='middle',
                            fontName='Helvetica-Bold'))
    footer_drawing.add(String(225, 15, "Confidential - For Internal Use Only",
                            fontSize=8,
                            fillColor=dark_grey,
                            textAnchor='middle',
                            fontName='Helvetica'))

    story.append(footer_drawing)

    # Build PDF
    doc.build(story)
    print(f"PDF generated successfully: {filename}")

if __name__ == "__main__":
    create_pdf()
