# 📄 Building a Simple Report-Style PDF with **ReportLab**

You’re about to walk through every line of a small script that spits out a finished PDF—title page, paragraph, table, bar chart, and even a little “logo” drawn on the page. No prior ReportLab or PDF-generation experience required. Just follow along, run the code cells, and a fresh `sample_report.pdf` will appear on your desktop.

---

## Prerequisites

```bash
# Run this once in a terminal or Jupyter cell
pip install reportlab
```

That’s it. ReportLab is pure-Python, no system libraries to compile.

---

## 1. Imports and Dependencies

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, Circle
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics import renderPDF
from reportlab.lib.enums import TA_CENTER
import os
```

**What’s going on?**

* **`platypus`** — ReportLab’s “build-a-document” framework. You feed it “flowables” (Paragraphs, Tables, etc.) and it lays them out.
* **`lib.pagesizes.letter`** — A tuple with width & height in points (1 pt = 1/72 inch).
* **`Drawing`, `Rect`, `Circle`, `VerticalBarChart`** — Shapes and charts live in the graphics sub-package.
* **`os`** — Only used to figure out where your Desktop folder lives.

---

## 2. Decide Where to Save the PDF

```python
desktop_path = os.path.expanduser("~/Desktop")   # Works on macOS & Linux
filename = os.path.join(desktop_path, "sample_report.pdf")
```

The `~` expands to your home directory. If you’re on Windows, swap `~/Desktop` for something like `C:/Users/<YOU>/Desktop` or just any folder you have write access to.

---

## 3. Create the **SimpleDocTemplate**

```python
doc = SimpleDocTemplate(
    filename,
    pagesize=letter,
    topMargin=0.5 * inch      # ½-inch top margin
)
story = []  # A plain Python list that will hold our “flowables”
```

`SimpleDocTemplate` is the easiest wrapper around a PDF file. When we later call `doc.build(story)`, it writes the whole thing out.

---

## 4. Define Text Styles

```python
styles = getSampleStyleSheet()  # Built-in defaults

title_style = ParagraphStyle(
    "CustomTitle",
    parent=styles["Heading1"],
    fontSize=24,
    spaceAfter=30,          # pts of space below
    alignment=TA_CENTER,
    textColor=colors.darkblue
)

subtitle_style = ParagraphStyle(
    "CustomSubtitle",
    parent=styles["Heading2"],
    fontSize=16,
    spaceAfter=20,
    alignment=TA_CENTER,
    textColor=colors.grey
)
```

Paragraph styles decide **font, size, colour, alignment, spacing,** everything. We inherit from the default headings but tweak what we need.

---

## 5. Add Title, Subtitle, and Body Text

```python
from reportlab.platypus import Paragraph, Spacer

# Title & subtitle
story.append(Paragraph("Company Annual Report", title_style))
story.append(Paragraph("Financial Performance Overview 2024", subtitle_style))

# Blank vertical space (exactly 20 pts tall)
story.append(Spacer(1, 20))

# Body paragraph
paragraph_text = """
This comprehensive report presents our company's outstanding performance throughout 2024. 
Our strategic initiatives have resulted in significant growth across all key metrics, 
demonstrating our commitment to excellence and innovation. The following data showcases 
our achievements in revenue, customer satisfaction, and market expansion. We continue 
to build on our strong foundation while exploring new opportunities for sustainable growth.
"""
story.append(Paragraph(paragraph_text, styles["Normal"]))
story.append(Spacer(1, 20))
```

*Don’t overthink `Spacer`—it’s literally an invisible rectangle that forces vertical breathing room.*

---

## 6. Build a Quick Table

```python
table_data = [
    ["Quarter", "Revenue ($M)", "Growth (%)"],
    ["Q1 2024", "125.4", "12.3"],
    ["Q2 2024", "142.8", "18.7"],
    ["Q3 2024", "156.2", "15.2"],
    ["Q4 2024", "178.9", "22.1"],
]

table = Table(table_data, colWidths=[1.5 * inch] * 3)

table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),   # Header row fill
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("ALIGN",     (0, 0), (-1, -1), "CENTER"),
    ("FONTNAME",  (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE",  (0, 0), (-1, 0), 12),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
    ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
    ("GRID", (0, 0), (-1, -1), 1, colors.black),
]))
story.append(table)
story.append(Spacer(1, 30))
```

Coordinate scheme: `(col, row)`, zero-based. `(0,0)` is top-left. `(-1,0)` means “last column in row 0”. Styling is chainable; set as many rules as you want in a single shot.

---

## 7. Draw a Bar Chart and a Simple “Logo”

```python
drawing = Drawing(400, 200)  # Canvas for vector graphics

# Faux logo: blue rectangle + orange circle
drawing.add(Rect(10, 150, 60, 30, fillColor=colors.darkblue, strokeColor=colors.black))
drawing.add(Circle(90, 165, 15, fillColor=colors.orange, strokeColor=colors.black))

# Vertical bar chart
chart = VerticalBarChart()
chart.x, chart.y = 120, 50
chart.width, chart.height = 250, 125
chart.data = [[125.4, 142.8, 156.2, 178.9]]
chart.categoryAxis.categoryNames = ["Q1", "Q2", "Q3", "Q4"]

chart.valueAxis.valueMin = 0
chart.valueAxis.valueMax = 200
chart.bars[0].fillColor = colors.darkblue
chart.bars[0].strokeColor = colors.black

drawing.add(chart)
story.append(drawing)
```

### What’s a `Drawing`?

Think of it as an SVG-ish container. Anything you add lives in its own coordinate system (origin at bottom-left). When we tuck the entire `Drawing` into `story`, ReportLab converts it to PDF vector commands.

---

## 8. Compile Everything into the PDF

```python
doc.build(story)
print(f"PDF generated successfully ⇒ {filename}")
```

`build()` chews through the flowables top-to-bottom, lays them out, writes pages, and closes the file. If there’s any error in your flowables, you’ll see it now.

---

## 9. Wrap It in a Function (Optional but Clean)

```python
def create_pdf():
    # all the code above goes here
    pass

if __name__ == "__main__":
    create_pdf()
```

This “main guard” means:

* Running the script normally (`python myscript.py`) → it executes.
* Importing the script from **another** Python file → it does **not** auto-run and make random PDFs.

In a Jupyter notebook you can **skip** the guard and just call `create_pdf()` directly.

---

## 🏁 Test It

```python
create_pdf()
```

Head to your desktop—`sample_report.pdf` should be waiting. Open it. You’ll see:

1. **Dark-blue title** centered, size 24 pt
2. **Grey subtitle** just below, size 16 pt
3. A paragraph of body text
4. A light-grey table of quarterly numbers
5. A mini “logo” plus a bar chart showing revenue growth

If something’s off (table columns mis-aligned, fonts ugly, chart too small), tweak numbers and rerun. PDF generation is instant, so experiment fearlessly.

---