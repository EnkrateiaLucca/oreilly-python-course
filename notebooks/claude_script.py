# /// script
# dependencies = [
#   "numpy",
#   "matplotlib",
#   "pandas", 
#   "reportlab",
# ]
# ///

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import io

# Generate synthetic data
np.random.seed(42)
dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
values = np.cumsum(np.random.randn(len(dates))) + 100
data = pd.DataFrame({'date': dates, 'value': values})

# Create visualization
plt.figure(figsize=(10, 6))
plt.plot(data['date'], data['value'])
plt.title('Time Series Analysis')
plt.xlabel('Date')
plt.ylabel('Value')
plt.xticks(rotation=45)
plt.tight_layout()

# Save plot to bytes buffer
img_buffer = io.BytesIO()
plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
img_buffer.seek(0)

# Create PDF
c = canvas.Canvas("report.pdf", pagesize=letter)
width, height = letter

# Add title
c.setFont("Helvetica-Bold", 16)
c.drawString(72, height - 72, "Data Analysis Report")

# Add text
c.setFont("Helvetica", 12)
c.drawString(72, height - 100, f"Data points: {len(data)}")
c.drawString(72, height - 120, f"Average value: {data['value'].mean():.2f}")
c.drawString(72, height - 140, f"Standard deviation: {data['value'].std():.2f}")

# Add plot
c.drawImage(ImageReader(img_buffer), 72, height - 500, width=450, height=300)

c.save()
print("Report generated as report.pdf")