2️⃣ Financial & Data Analysis Automation
“Generate a Python script that performs financial analysis on a CSV file containing stock trading data. The dataset includes columns: Date, Stock Symbol, Open Price, Close Price, Volume, Moving Average (50-day), and RSI (Relative Strength Index). The script should:”

Detailed Steps in the Prompt:
	1.	Load & Clean Data: Use pandas to load the CSV, handle missing values, and ensure data types are correct.
	2.	Key Financial Metrics Calculation:
	•	Compute daily returns and rolling volatility.
	•	Calculate a simple moving average (SMA) and exponential moving average (EMA) for each stock.
	•	Generate Bollinger Bands for price movement analysis.
	•	Compute Relative Strength Index (RSI) and MACD for trend analysis.
	3.	Visualization & Reporting:
	•	Use matplotlib and seaborn to generate:
	•	Line charts for stock prices over time.
	•	A candlestick chart using mplfinance.
	•	A heatmap of correlations between different stock metrics.
	•	Save these charts as PNG images.
	4.	Export Analysis Report:
	•	Generate an Excel report with the analyzed data and charts.
	•	Use xlsxwriter to format and insert images into the Excel file.