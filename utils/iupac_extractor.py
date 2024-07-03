import csv
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from utils.converter import pdf_to_excel, excel_to_csv, csv_to_txt
from utils.preprocessor import preprocess_csv_text, preprocess_text, merge_text_files
from utils.puller import extract_text_from_pdf, extract_molecules_from_text

def pdf_molecules_extractor(pdf_file: Path, output_folder: Path):
    """
    Extract molecules from a PDF and save them in a CSV file.

    Args:
        pdf_file (Path): Path to the input PDF file.
        output_folder (Path): Path to the output folder.

    Returns:
        str: Path to the output CSV file containing extracted molecules.

    """
    # Ensure pdf_file and output_folder are Path objects
    pdf_file = Path(pdf_file)
    output_folder = Path(output_folder)

    # Generate filenames based on the PDF file name
    base_name = pdf_file.stem  # Use .stem to get the filename without extension
    txt_file = output_folder / f'{base_name}.txt'
    excel_file = output_folder / f'{base_name}_tables.xlsx'
    csv_file = output_folder / f'{base_name}_tables.csv'
    csv_txt_file = output_folder / f'{base_name}_csv.txt'
    combined_txt_file = output_folder / f'{base_name}_combined.txt'

    # Extract tables from PDF and convert to CSV
    tables_extracted = pdf_to_excel(pdf_file, excel_file)
    
    if tables_extracted:
        # Extract text from PDF and preprocess CSV and text files
        txt_file = extract_text_from_pdf(pdf_file, output_folder)
        excel_to_csv(excel_file, csv_file)
        csv_txt = preprocess_csv_text(csv_file)
        csv_to_txt(csv_txt, csv_txt_file)
        
        # Preprocess and merge text files, then extract molecules
        preprocessed_txt_path = output_folder / f'{base_name}_preprocessed.txt'
        preprocess_text(txt_file, preprocessed_txt_path)
        merge_text_files(csv_txt_file, preprocessed_txt_path, combined_txt_file)
        molecules = extract_molecules_from_text(combined_txt_file)
    else:        
        # If no tables extracted, directly preprocess text and extract molecules
        txt_file = extract_text_from_pdf(pdf_file, output_folder)
        preprocessed_txt_path = output_folder / f'{base_name}_preprocessed.txt'
        preprocess_text(txt_file, preprocessed_txt_path)
        molecules = extract_molecules_from_text(preprocessed_txt_path)
        
    # If no molecules found, print a message and return
    if not molecules:
        print("No molecule found.")
        return
    
    # Save extracted molecules to a CSV file
    output_file = output_folder / f'{base_name}_iupac.csv'
    save_to_csv(molecules, output_file)
    print(f"The results have been saved in {output_file}")

    return output_file

def save_to_csv(molecules, output_file):
    """
    Save molecules with names of at least 3 characters in a CSV file, including the 'Example' column.

    Args:
        molecules (list): List of dictionaries containing molecule information.
        output_file (str): Path to the output CSV file.

    """
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        # Define the field names for the CSV header
        fieldnames = ['Example', 'Molecule']
        
        # Create a CSV DictWriter object with specified delimiter
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        
        # Write the header row in the CSV file
        writer.writeheader()
        
        # Iterate through each molecule dictionary in the list
        for molecule in molecules:
            # Extract molecule name and example from the dictionary
            molecule_name = molecule.get('Molecule', '')
            example = molecule.get('Example', '')
            
            # Check if molecule name has at least 4 characters
            if len(molecule_name) >= 4:
                # Write a row to the CSV file with 'Molecule' and 'Example' columns
                writer.writerow({'Molecule': molecule_name, 'Example': example})

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pdf_to_iupac.py <pdf_file>")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    if not os.path.exists(pdf_file):
        print(f"The following file does not exist: {pdf_file}.")
        sys.exit(1)

    pdf_molecules_extractor(Path(pdf_file))