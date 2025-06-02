# /// script
# dependencies = [
#   "fpdf2",
# ]
# ///

from fpdf import FPDF
import argparse
from datetime import datetime
import os

def create_contract_pdf(output_path, party_a="John Doe", party_b="Jane Smith"):
    # Create a PDF instance
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='', size=12)
    
    # Title
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Sample Contract Agreement", ln=True, align='C')
    pdf.ln(10)
    
    # Contract text
    pdf.set_font("Arial", size=12)
    current_date = datetime.now().strftime("%dth day of %B %Y")
    
    contract_text = f"""This Contract Agreement is made on this {current_date}, between:
Party A: {party_a}, residing at 123 Example Street, Sample City.
Party B: {party_b}, residing at 456 Business Avenue, Business City.
Whereas Party A agrees to provide consulting services to Party B for a period of six months,
starting from {(datetime.now().replace(day=5)).strftime("%B %d, %Y")}, under the following terms:
1. Scope of Services:
   Party A will provide business consulting services, including but not limited to market
   analysis, strategy planning, and financial guidance.
2. Payment Terms:
   Party B agrees to pay Party A a monthly fee of $5,000, payable on the first day of each month.
3. Confidentiality:
   Both parties agree to keep confidential all business and proprietary information exchanged
   during the course of this agreement.
4. Termination Clause:
   Either party may terminate this agreement with a 30-day written notice.
Signed and agreed upon by:
Party A: {party_a}         Party B: {party_b}
Date: {datetime.now().strftime("%B %d, %Y")}
"""
    # Add contract text
    pdf.multi_cell(0, 7, contract_text)
    pdf.ln(10)
    
    # Add a table title
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(200, 10, "Payment Schedule", ln=True, align='C')
    pdf.ln(5)
    
    # Table headers
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(50, 10, "Month", border=1, align='C')
    pdf.cell(50, 10, "Due Date", border=1, align='C')
    pdf.cell(50, 10, "Amount ($)", border=1, align='C')
    pdf.ln()
    
    # Generate payment schedule for 6 months
    start_date = datetime.now().replace(day=5)
    payment_schedule = []
    for i in range(6):
        month_date = start_date.replace(month=start_date.month + i)
        payment_schedule.append((
            month_date.strftime("%B"),
            month_date.strftime("%Y-%m-%d"),
            "$5,000"
        ))
    
    # Table data
    pdf.set_font("Arial", size=12)
    for row in payment_schedule:
        for item in row:
            pdf.cell(50, 10, str(item), border=1, align='C')
        pdf.ln()
    
    # Save the PDF
    pdf.output(output_path)
    print(f"Contract PDF created successfully at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Generate a sample contract PDF')
    parser.add_argument('--output', default='sample_contract.pdf',
                       help='Output path for the PDF file (default: sample_contract.pdf)')
    parser.add_argument('--party-a', default='John Doe',
                       help='Name of Party A (default: John Doe)')
    parser.add_argument('--party-b', default='Jane Smith',
                       help='Name of Party B (default: Jane Smith)')
    
    args = parser.parse_args()
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    
    create_contract_pdf(args.output, args.party_a, args.party_b)

if __name__ == "__main__":
    main()