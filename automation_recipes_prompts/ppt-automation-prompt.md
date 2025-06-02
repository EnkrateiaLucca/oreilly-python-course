# Prompt 1
Please write a Python script that performs the following tasks:

- Accesses the "input" folder and reads all Excel files within it.
- For each file, it retrieves the financial data located in the first worksheet, from column A to P, and excludes any rows with missing values.
- Group the entire data by the "Product" column (C) and sum up the sales column (J) for each group.
- Using the grouped data, the script should create a chart using the seaborn library for each file, and save it in the "charts" folder. If the folder does not exist, the script should create it. . The chart should include a title, appropriate axis labels, and a legend.
- The script should then create a new PowerPoint presentation, insert a slide for each chart, and above the chart, include a title. The title should be the respective excel file name without file extension. And make sure that the chart and title do not overlap
- The PowerPoint presentation should be saved in the same directory as the input files and named "financial_data.pptx".
- The script should be robust and handle any potential errors gracefully, providing appropriate error messages and notifications, and also by including proper error handling mechanisms.

Input data example in here: 

- https://github.com/Sven-Bo/automate-office-tasks-using-chatgpt-python/tree/master/02_Automate_PowerPoint/input

# Prompt 2

Please save the final PowerPoint presentation in the same directory as the Python script

```python
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches

# Determine the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

input_folder = os.path.join(script_dir, 'input')
charts_folder = os.path.join(script_dir, 'charts')
ppt_file = 'financial_data.pptx'

# Create the charts folder if it doesn't exist
if not os.path.exists(charts_folder):
    os.mkdir(charts_folder)

# Create a new PowerPoint presentation
prs = Presentation()

# Iterate through all Excel files in the input folder
for excel_file in os.listdir(input_folder):
    if not excel_file.endswith('.xlsx'):
        continue

    # Read the financial data from the first worksheet of the Excel file
    file_path = os.path.join(input_folder, excel_file)
    df = pd.read_excel(file_path, sheet_name=0, usecols="A:P")
    df = df.dropna()

    # Group the data by the "Product" column and sum up the "Sales" column
    grouped = df.groupby('Product').sum()['Sales']

    # Create a chart using the seaborn library
    sns.barplot(x=grouped.index, y=grouped.values)
    plt.title(excel_file)
    plt.xlabel('Product')
    plt.ylabel('Sales')
    plt.tight_layout()

    # Save the chart to the charts folder
    chart_file = excel_file.replace('.xlsx', '.png')
    chart_path = os.path.join(charts_folder, chart_file)
    plt.savefig(chart_path)

    # Add a slide to the PowerPoint presentation and insert the chart and title
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    title = slide.shapes.title
    title.text = excel_file.replace('.xlsx','')

    chart_file = chart_path
    left = Inches(0.5)
    top = Inches(1)
    width = Inches(9)
    height = Inches(6)
    slide.shapes.add_picture(chart_file, left, top, width=width, height=height)

# Save the PowerPoint presentation in the same directory as the script
ppt_path = os.path.join(script_dir, ppt_file)
prs.save(ppt_path)
```
