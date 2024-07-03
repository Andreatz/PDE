import argparse
import os

from pathlib import Path
from PyPDF2 import PdfWriter, PdfReader

def pdf_extraction(pdfile_path: Path, first_page: int, last_page: int, output_folder: Path = None, together: bool = False):
    """
    Extract specific pages from a PDF file.

    Args:
        pdfile_path (Path): Path to the input PDF file.
        first_page (int): First page to extract (1-based index).
        last_page (int): Last page to extract (1-based index).
        output_folder (Path, optional): Path to the folder where extracted files should be saved. Default is the parent directory of the input PDF file.
        together (bool, optional): Whether to extract the pages together into a single file. Default is False.

    Returns:
        Path: Path to the output file or directory where pages were extracted.
    """
    pdf_reader = PdfReader(pdfile_path)
    patent_name = pdfile_path.stem
    output_dir = output_folder if output_folder else pdfile_path.parent

    if together:
        # Extract pages together into a single PDF file
        output_path = os.path.join(output_dir, f"{patent_name}_extracted.pdf")  
        pdf_writer = PdfWriter()
    
    for page_num in range(first_page - 1, last_page):
        if together:
            # Add each page to the PdfWriter object for combined extraction
            pdf_writer.add_page(pdf_reader.pages[page_num])
        else:
            # Extract each page separately
            single_page_writer = PdfWriter()
            single_page_writer.add_page(pdf_reader.pages[page_num])
            output_path = os.path.join(output_dir, f'{patent_name}_page_{page_num + 1}.pdf')
            with open(output_path, 'wb') as out_file:
                single_page_writer.write(out_file)
    
    if together:
        # Write the combined PDF file
        with open(output_path, 'wb') as out_file:
            pdf_writer.write(out_file)
    
    # Return the output path or directory where files were saved
    return output_path if together else output_dir

def main():
    parser = argparse.ArgumentParser(description="Extraction of specific pages from a PDF.")
    parser.add_argument("-p", "--pdf_path", type=Path, required=True, help="Path to the PDF file")
    parser.add_argument("-s", "--start_page", type=int, help="First page to extract (1-based index).")
    parser.add_argument("-e", "--end_page", type=int, help="Last page to extract (1-based index).")
    parser.add_argument("-o", "--output_folder", type=Path, default=None, help="Specify the path where the files should be saved. Default = working directory.")
    parser.add_argument("-t", "--together", action="store_true", help="Extract the pages together into a single file.")
    args = parser.parse_args()

    if args.start_page is None or args.end_page is None:
        parser.error("Both --start-page (-s) and --end-page (-e) must be provided.")

    pdf_extraction(
        pdfile_path=args.pdf_path,
        first_page=args.start_page,
        last_page=args.end_page,
        output_folder=args.output_folder,
        together=args.together
    )

if __name__ == "__main__":
    main()