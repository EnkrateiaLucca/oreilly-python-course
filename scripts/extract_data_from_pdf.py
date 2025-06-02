# /// script
# dependencies = [
#   "pymupdf",
#   "pdfplumber",
# ]
# ///

import fitz  # PyMuPDF
import pdfplumber
import csv
import argparse

def extract_text_from_pdf(pdf_path, text_output_path):
    """Extracts text from a PDF and saves it to a text file."""
    with fitz.open(pdf_path) as doc, open(text_output_path, 'w', encoding='utf-8') as text_file:
        for page in doc:
            text = page.get_text("text")  # Extract text from the page
            text_file.write(text + '\n' + '-'*80 + '\n')  # Separate pages
    print(f"Text extracted and saved to {text_output_path}")

def extract_tables_from_pdf(pdf_path, csv_output_path):
    """Extracts tables from a PDF and saves them as CSV files."""
    with pdfplumber.open(pdf_path) as pdf:
        tables = []
        for i, page in enumerate(pdf.pages):
            extracted_tables = page.extract_tables()
            if extracted_tables:
                tables.extend(extracted_tables)
    
    if tables:
        with open(csv_output_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            for table in tables:
                for row in table:
                    writer.writerow(row)
        print(f"Tables extracted and saved to {csv_output_path}")
    else:
        print("No tables found in the PDF.")

def main():
    parser = argparse.ArgumentParser(description='Extract text and tables from PDF files')
    parser.add_argument('pdf_path', help='Path to the input PDF file')
    parser.add_argument('--text-output', default='extracted_text.txt', 
                       help='Path for the extracted text output (default: extracted_text.txt)')
    parser.add_argument('--csv-output', default='extracted_tables.csv',
                       help='Path for the extracted tables output (default: extracted_tables.csv)')
    
    args = parser.parse_args()
    
    extract_text_from_pdf(args.pdf_path, args.text_output)
    extract_tables_from_pdf(args.pdf_path, args.csv_output)

if __name__ == "__main__":
    main()