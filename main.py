import os
from PyPDF2 import PdfReader, PdfWriter

def merge_pdfs(input_folder, output_filename):
    """Merge all PDF files from input_folder into a single PDF file."""
    pdf_writer = PdfWriter()
    
    pdf_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
    pdf_files.sort()
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_folder, pdf_file)
        print(f"Adding {pdf_file}...")
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
    
    with open(output_filename, 'wb') as output_file:
        pdf_writer.write(output_file)
    
    print(f"Successfully merged {len(pdf_files)} PDFs into {output_filename}")

if __name__ == "__main__":
    input_folder = "files"
    output_filename = "merged_pdfs.pdf"
    merge_pdfs(input_folder, output_filename)