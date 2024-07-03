import argparse
import csv
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from utils.cleaner import folder_cleaner
from utils.decimer import SMILES_prediction
from utils.folder_check import create_folder_in_working_directory
from utils.pdf_splitter import pdf_extraction
from utils.pdf_to_img import chemical_structure_segmentation

def pdfimg2smiles_conversion(pdfile_path, start_page, last_page):
    pdfile_path = Path(pdfile_path)
    patent_name = pdfile_path.stem
    pdf2smiles_folder = create_folder_in_working_directory("pdf_to_smiles")
    pdf_extraction(pdfile_path, start_page, last_page, pdf2smiles_folder)

    for pdf_file in os.listdir(pdf2smiles_folder):
        if pdf_file.endswith('.pdf'):
            structure_images = chemical_structure_segmentation(os.path.join(pdf2smiles_folder, pdf_file))
            os.remove(os.path.join(pdf2smiles_folder, pdf_file))

    working_directory = os.getcwd()

    for folder in os.listdir(pdf2smiles_folder):
        folder_path = os.path.join(pdf2smiles_folder, folder)
        if os.path.isdir(folder_path):
            base_name = os.path.basename(folder)
            segments_path = os.path.join(folder_path, 'segments')
            if os.path.exists(segments_path):
                output_file_path = os.path.join(pdf2smiles_folder, f"{base_name}_prediction.csv")
                SMILES_prediction(segments_path, output_file_path)
            folder_cleaner(folder_path)
            os.rmdir(folder_path)

    output_csv = f"{patent_name}_pages_{start_page}_{last_page}_prediction.csv"

    all_rows = []

    for csv_file in os.listdir(pdf2smiles_folder):
        if csv_file.endswith('_prediction.csv'):
            csv_file_path = os.path.join(pdf2smiles_folder, csv_file)
            with open(csv_file_path, 'r', newline='') as input_file:
                reader = csv.reader(input_file)
                for row in reader:
                    all_rows.append(row)
            os.remove(csv_file_path)

    all_rows.sort(key=lambda x: x[0])

    with open(output_csv, 'w', newline='') as concat_file:
        writer = csv.writer(concat_file)
        for row in all_rows:
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="Convert PDF pages to SMILES.")
    parser.add_argument("-p", "--pdf_path", required=True, help="Path to the PDF file")
    parser.add_argument("-s", "--start_page", type=int, required=True, help="First page to extract (1-based index)")
    parser.add_argument("-e", "--end_page", type=int, required=True, help="Last page to extract (1-based index)")
    args = parser.parse_args()

    pdfimg2smiles_conversion(args.pdf_path, args.start_page, args.end_page)

if __name__ == "__main__":
    main()