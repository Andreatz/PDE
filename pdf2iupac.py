import argparse
import csv
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow warnings
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add parent directory to sys.path

from pathlib import Path
from utils.cleaner import csv_cleaning
from utils.folder_check import create_folder_in_working_directory
from utils.pdf_splitter import pdf_extraction
from utils.iupac_extractor import pdf_molecules_extractor
from utils.iupac_to_smiles import from_iupac_to_smiles_conversion

def csv_filtering(csv_file):
    """
    Filter lines in CSV file to keep only those containing "Example [number];".
    
    Args:
        csv_file (str): Path to the input CSV file.

    Returns:
        str: Path to the filtered CSV file.
    """
    temp_csv = "temp.csv"
    print(f"Filtering CSV: {csv_file}")

    # Define the pattern to match lines containing "Example [number];"
    pattern = re.compile(r"Example [0-9]+;")

    # Open the original file for reading and a temporary file for writing
    with open(csv_file, 'r') as infile, open(temp_csv, 'w') as outfile:
        for line in infile:
            if pattern.search(line):
                outfile.write(line)

    # Replace the original file with the temporary file
    os.replace(temp_csv, csv_file)
    
    return csv_file

def extract_key(row):
    """
    Extracts the numeric part from the "Example [number];" format in CSV rows for sorting.

    Args:
        row (list): CSV row containing the "Example [number];" format.

    Returns:
        int: The extracted number or a large number if no match is found.
    """
    match = re.match(r"Example (\d+);", row[0])
    return int(match.group(1)) if match else float('inf')  # Return a large number to sort unmatched rows last

def csv_sorting(csv_file):
    """
    Sorts rows in a CSV file based on the "Example [number];" format.

    Args:
        csv_file (str): Path to the input CSV file.

    Returns:
        str: Path to the sorted CSV file.
    """
    temp_csv = "temp.csv"
    print(f"Sorting CSV: {csv_file}")

    # Read the CSV file
    with open(csv_file, 'r') as infile:
        reader = csv.reader(infile)
        rows = list(reader)

    # Sort the rows based on the specified key
    sorted_rows = sorted(rows, key=extract_key)

    # Write the sorted rows to a temporary file
    with open(temp_csv, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(sorted_rows)

    # Replace the original file with the sorted file
    os.replace(temp_csv, csv_file)

    return csv_file

def adjust_csv(csv_file):
    """
    Adjusts CSV format by changing delimiter and adding header.

    Args:
        csv_file (str): Path to the input CSV file.

    Returns:
        str: Path to the adjusted CSV file.
    """
    temp_csv = "temp.csv"
    print(f"Adjusting CSV: {csv_file}")

    with open(csv_file, 'r') as infile, open(temp_csv, 'w', newline='') as outfile:
        reader = csv.reader(infile, delimiter=';')
        writer = csv.writer(outfile, delimiter=',')

        # Write the header
        writer.writerow(['Example No', 'IUPAC Name'])

        # Process and write each row
        for row in reader:
            writer.writerow(row)

    # Replace the original file with the modified file
    os.replace(temp_csv, csv_file)

    return csv_file

def pdf2iupac_conversion(pdfile_path, start_page, last_page, together):
    """
    Orchestrates the conversion process from PDF to IUPAC names and finally to SMILES format.

    Args:
        pdfile_path (str): Path to the PDF file.
        start_page (int): First page to extract (1-based index).
        last_page (int): Last page to extract (1-based index).
        together (bool): Flag to extract pages together into a single file.
    """
    # Create output folder
    output_folder = create_folder_in_working_directory('pdf_to_smiles')
    print(f"Created output folder: {output_folder}")

    # Extract and combine specified page range from PDF
    combined_pdf = pdf_extraction(pdfile_path, start_page, last_page, output_folder, together)
    print(f"Extracted PDF: {combined_pdf}")

    # Extract molecules from combined PDF into CSV
    csv_with_molecules = pdf_molecules_extractor(combined_pdf, output_folder)
    print(f"CSV with molecules: {csv_with_molecules}")

    # Clean up the CSV
    cleaned_csv_with_molecules = csv_cleaning(csv_with_molecules)
    print(f"Cleaned CSV with molecules: {cleaned_csv_with_molecules}")

    # Filter out lines not containing "Example [number]"
    filtered_csv_with_molecules = csv_filtering(cleaned_csv_with_molecules)
    print(f"Filtered CSV with molecules: {filtered_csv_with_molecules}")

    # Sort the CSV based on "Example [number]"
    sorted_csv_with_molecules = csv_sorting(filtered_csv_with_molecules)
    print(f"Sorted CSV with molecules: {sorted_csv_with_molecules}")

    # Adjust the CSV format
    modified_csv_with_molecules = adjust_csv(sorted_csv_with_molecules)
    print(f"Modified CSV with molecules: {modified_csv_with_molecules}")

    # Convert IUPAC names to SMILES notation
    from_iupac_to_smiles_conversion(modified_csv_with_molecules, column_name="IUPAC Name")

    # Remove all intermediate .pdf, .txt, .xlsx, and .csv files generated during the process.
    remove_intermediate_files(output_folder)

def remove_intermediate_files(output_folder):
    """
    Removes all intermediate files (.pdf, .txt, .xlsx, .csv) except the final '_iupac_smiles.csv' file.

    Args:
        output_folder (str): Path to the folder containing the files to be removed.
    """
    for filename in os.listdir(output_folder):
        file_path = os.path.join(output_folder, filename)
        if os.path.isfile(file_path) and not filename.endswith('_iupac_smiles.csv'):
            os.remove(file_path)

def main():
    parser = argparse.ArgumentParser(description="Brief description of the tool.")
    parser.add_argument("-p", "--pdfile_path", type=Path, required=True, help="Path to the file to be processed.")
    parser.add_argument("-s", "--start_page", type=int, help="First page to extract (1-based index).")
    parser.add_argument("-e", "--end_page", type=int, help="Last page to extract (1-based index).")
    parser.add_argument("-t", "--together", action="store_true", help="Extract the pages together into a single file.")
    args = parser.parse_args()

    if args.start_page is None or args.end_page is None:
        parser.error("Both --start-page (-s) and --end-page (-e) must be provided.")

    pdf2iupac_conversion(
        pdfile_path=args.pdfile_path,
        start_page=args.start_page,
        last_page=args.end_page,
        together=args.together
    )

if __name__ == '__main__':
    main()