"""Utility script to generate authentic binary .docx and .pdf fixtures for DocuLens AI."""
import os
import docx
import fitz

def create_complete_contract_docx(output_path: str):
    """Generates a styled DOCX version of the Master Cloud Services Agreement."""
    doc = docx.Document()
    doc.add_heading("MASTER CLOUD SERVICES AGREEMENT", level=0)
    
    doc.add_paragraph("This Master Cloud Services Agreement ('Agreement') is executed on October 1, 2026, by and between Nexus Global Enterprise Corp ('Customer'), with offices at 500 Market Street, San Francisco, CA, and CloudMatrix Technologies Inc. ('Provider'), with offices at 100 Tech Parkway, Austin, TX.")
    
    doc.add_heading("1. Services and Obligations", level=1)
    doc.add_paragraph("Provider agrees to deliver enterprise multi-tenant cloud hosting, database management, and 24/7 technical monitoring. Provider covenants that the hosted platform shall maintain a 99.9% monthly uptime service level agreement (SLA), excluding scheduled maintenance windows announced at least 72 hours in advance.")
    
    doc.add_heading("2. Fees and Payment Terms", level=1)
    doc.add_paragraph("Customer agrees to pay an annual subscription fee of $48,000 USD, billed in quarterly installments of $12,000 USD. All undisputed invoices shall be due and payable within thirty (30) calendar days from receipt of invoice (Net 30) via wire transfer or ACH. Undisputed late balances shall accrue interest at 1.0% per month or the maximum legal rate.")
    
    doc.add_heading("3. Term and Renewal", level=1)
    doc.add_paragraph("The initial term of this Agreement shall commence on November 1, 2026, and shall continue for a duration of two (2) years. Thereafter, this Agreement shall automatically renew for successive one (1) year terms unless either party provides written notice of non-renewal at least sixty (60) days prior to the expiration of the current term.")
    
    doc.add_heading("4. Termination", level=1)
    doc.add_paragraph("Either party may terminate this Agreement without cause upon ninety (90) days prior written notice to the other party. Either party may terminate immediately for cause if the other party breaches any material term and fails to cure such breach within thirty (30) days of receiving written notice specifying the breach.")
    
    doc.add_heading("5. Dispute Resolution", level=1)
    doc.add_paragraph("In the event of any controversy, claim, or dispute arising out of or relating to this Agreement, the parties shall first engage in executive escalation in good faith for fifteen (15) business days. If unresolved, the dispute shall be finally settled by binding arbitration administered by the American Arbitration Association (AAA) under its Commercial Arbitration Rules, before a single arbitrator in Wilmington, Delaware.")
    
    doc.add_heading("6. Governing Law and Jurisdiction", level=1)
    doc.add_paragraph("This Agreement shall be governed by, interpreted, and enforced in accordance with the substantive laws of the State of Delaware, without regard to conflict of law principles.")
    
    doc.save(output_path)
    print(f"Generated DOCX: {output_path}")

def create_medical_report_pdf(output_path: str):
    """Generates an authentic PDF version of the Clinical Laboratory Report using PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    
    text_content = """METRO HEALTH DIAGNOSTIC LABORATORIES
PATIENT LABORATORY REPORT - COMPREHENSIVE METABOLIC PANEL

Patient Name: Jane Doe         Patient ID: PT-99201      DOB: 05/14/1982      Sex: Female
Ordering Physician: Dr. Marcus Vance, MD               Specimen Date: 09/28/2026 08:15 AM
Report Date: October 1, 2026                          Status: Final Result

-----------------------------------------------------------------------------------------
TEST NAME                 RESULT     UNITS       REFERENCE INTERVAL   LAB FLAG
-----------------------------------------------------------------------------------------
Fasting Blood Glucose     118        mg/dL       70 - 99              H
Hemoglobin A1c            6.8        %           4.0 - 5.6            H
Total Cholesterol         185        mg/dL       125 - 200            Normal
Serum Sodium              140        mmol/L      135 - 145            Normal
Serum Potassium           3.5        mmol/L      3.5 - 5.0            Normal
Serum Creatinine          0.85       mg/dL       0.60 - 1.20          Normal
Hemoglobin                13.4       g/dL        12.0 - 16.0          Normal
White Blood Cell Count    6.5        x10^3/uL    4.5 - 11.0           Normal
Platelet Count            120        x10^3/uL    150 - 450            L
-----------------------------------------------------------------------------------------

LABORATORY COMMENTS & CLINICAL REMARKS:
Specimen received at 4°C without hemolysis. Fasting interval verified as 12 hours.
Values marked 'H' indicate parameters exceeding institutional reference thresholds.
Values marked 'L' indicate parameters below reference thresholds.
Verified by Clinical Pathologist Dr. Elena Rostova, MD, PhD.
"""
    # Insert text into page
    rect = fitz.Rect(40, 50, 560, 780)
    page.insert_textbox(rect, text_content, fontsize=9.5, fontname="courier")
    doc.save(output_path)
    doc.close()
    print(f"Generated PDF: {output_path}")

def create_study_notes_pdf(output_path: str):
    """Generates an authentic PDF version of the Compiler Design Study Material."""
    doc = fitz.open()
    page = doc.new_page()
    
    text_content = """DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING
COURSE CS-401: COMPILER DESIGN AND OPTIMIZATION
MODULE 4: INTERMEDIATE CODE GENERATION & SYNTAX-DIRECTED TRANSLATION

1. Overview of Intermediate Representations (IR)
Intermediate Representation (IR) is an abstract machine representation positioned between
the front-end (lexical analysis, parsing, semantic analysis) and the back-end (instruction
selection, register allocation, machine code generation) of a compiler. Using an IR provides
machine independence: targeting a new CPU architecture requires only rewriting the back-end
without modifying lexical or parsing stages.

2. Key Definitions and Structures
- Three-Address Code (TAC): An abstract language where every instruction contains at most
  one operator on the right-hand side and at most three address operands. Canonical form:
  x = y op z, or unary x = op y.
- Quadruples: A record structure representation of TAC with four distinct fields:
  (op, arg1, arg2, result). For example, t1 = a + b is stored as (+, a, b, t1).
- Triples: A representation avoiding explicit temporary variable names by referencing
  temporary results by their statement index array position: (op, arg1, arg2).
- Abstract Syntax Tree (AST): A condensed hierarchical tree representation of source syntax
  where internal nodes represent operators and leaf nodes represent operands.

3. Translation of Expressions and Equations
Consider the high-level arithmetic expression: result = (a + b) * (c - d) + (a + b).
In Three-Address Code with Common Subexpression Elimination (CSE):
Step 1: Compute temporary addition t1 = a + b
Step 2: Compute temporary subtraction t2 = c - d
Step 3: Compute multiplication t3 = t1 * t2
Step 4: Reuse previously computed t1 for final addition t4 = t3 + t1
Step 5: Assign final value result = t4
This translation reduces total arithmetic operations from four down to three through DAG reuse.

4. Control Flow and Boolean Expressions
Control flow statements (such as if-then-else and while loops) are translated into conditional
jumps 'if condition goto L1' and unconditional jumps 'goto L2'. Backpatching is a single-pass
technique where target branch labels are left empty during initial code emission and filled in
once target statement addresses become known.
"""
    rect = fitz.Rect(40, 50, 560, 780)
    page.insert_textbox(rect, text_content, fontsize=9.5, fontname="courier")
    doc.save(output_path)
    doc.close()
    print(f"Generated Study PDF: {output_path}")

if __name__ == "__main__":
    fixtures_dir = os.path.join(os.path.dirname(__file__), "demo_fixtures")
    os.makedirs(fixtures_dir, exist_ok=True)
    
    create_complete_contract_docx(os.path.join(fixtures_dir, "02_complete_contract.docx"))
    create_medical_report_pdf(os.path.join(fixtures_dir, "04_medical_report_standard.pdf"))
    create_study_notes_pdf(os.path.join(fixtures_dir, "06_study_notes_compiler.pdf"))
