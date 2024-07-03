import argparse
import os
import pandas as pd
import re
import shutil
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pathlib import Path
from utils.converter import pdf_to_excel, excel_to_csv
from utils.folder_check import create_folder_in_working_directory
from utils.puller import extract_activity_from_csv, extract_activity_from_pdf, save_activity_to_csv
from utils.pdf_splitter import pdf_extraction

def ensure_example_prefix(molecule_id):
    """
    Ensure that each molecule_id contains the prefix 'Example' and remove any extra spaces.
    Args:
        molecule_id (str): The molecule ID to check and possibly modify.
    Returns:
        str: The modified molecule ID with 'Example' as a prefix and no extra spaces.
    """
    molecule_id = re.sub(r'\s+', ' ', molecule_id).strip()  # Remove extra spaces
    if not molecule_id.startswith("Example"):
        return f"Example {molecule_id}"
    return molecule_id

def sort_key(molecule_id):
    """
    Key function for sorting molecule_id strings.
    Args:
        molecule_id (str): The molecule ID string to convert to a sortable tuple.
    Returns:
        tuple: A tuple containing the numerical part and any alphabetical suffix for sorting.
    """
    match = re.match(r'Example (\d+)([A-Za-z]?)', molecule_id)
    if match:
        num_part = int(match.group(1))
        suffix_part = match.group(2)
        return (num_part, suffix_part)
    else:
        # Handle cases where molecule_id does not start with "Example"
        return (0, molecule_id)  # Adjust default tuple as per your sorting needs

def pdf2activity_conversion(pdfile_path: Path, start_page: int, last_page: int, together: bool = False):
    """
    Orchestrates the conversion process from PDF pages to activity data CSV.

    Args:
        pdfile_path (Path): Path to the PDF file.
        start_page (int): First page to extract (1-based index).
        last_page (int): Last page to extract (1-based index).
        together (bool, optional): Flag to extract pages together into a single file. Defaults to False.
    """
    patent_name = pdfile_path.stem  # Extract filename without extension as patent name
    pdf2activity_folder = Path(create_folder_in_working_directory('pdf_to_activity'))  # Create output folder

    # Split PDF into pages or together based on 'together' flag
    pdf_extraction(pdfile_path, start_page, last_page, pdf2activity_folder, together)
    
    pdfs_to_process = [pdf2activity_folder / f"{patent_name}_extracted.pdf"]

    # Extract activity data from each PDF and save as CSV
    for pdf in pdfs_to_process:
        activity_data = pdf_activity_extractor(pdf, pdf2activity_folder)
        if activity_data is not None:
            output_file = pdf2activity_folder / f"{patent_name}_{start_page}_{last_page}_activity.csv"  # Change extension to CSV
            save_activity_to_csv(activity_data, output_file)

    all_data = []
    for csv_file in pdf2activity_folder.glob(f"{patent_name}_{start_page}_{last_page}_activity.csv"):
        df = pd.read_csv(csv_file, header=None, names=['molecule_id', 'activity'])
        all_data.append(df)
    
    if all_data:
        combined_df = pd.concat(all_data)  # Concatenate all dataframes
        combined_df['molecule_id'] = combined_df['molecule_id'].apply(str).apply(ensure_example_prefix)  # Ensure 'Example' prefix and convert to string
        
        # Convert molecule_id to a sortable tuple using sort_key
        combined_df['sort_key'] = combined_df['molecule_id'].apply(sort_key)
        
        # Sort by sort_key
        combined_df.sort_values(by=['sort_key'], inplace=True)
        
        # Drop the temporary sort_key column
        combined_df.drop(columns=['sort_key'], inplace=True)
        
        combined_df.to_csv(output_file, index=False, header=False)
    
    # Clean up: remove individual CSV files and PDFs
    for file in pdf2activity_folder.glob(f"{patent_name}_extracted*.csv"):
        file.unlink()
    for file in pdf2activity_folder.glob(f"{patent_name}_*.xlsx"):
        file.unlink()
    for file in pdf2activity_folder.glob("*.pdf"):
        file.unlink()
    for file in pdf2activity_folder.glob("*.txt"):
        file.unlink()

def pdf_activity_extractor(pdf_file: Path, pdf2activity_folder: Path):
    """
    Extract activity from a PDF and save them in a CSV file.

    Args:
        pdf_file (Path): Path to the input PDF file.
        pdf2activity_folder (Path): Path to the output folder for CSV files.

    Returns:
        dict: Dictionary containing molecule IDs and activities.
    """
    try:
        # Generate filenames based on the PDF file name
        base_name = pdf_file.stem
        excel_file = pdf2activity_folder / (base_name + '_tables.xlsx')
        csv_file = pdf2activity_folder / (base_name + '_tables.csv')

        # Extract tables from PDF and convert to CSV
        tables_extracted = pdf_to_excel(pdf_file, excel_file)
        
        if tables_extracted:
            # Extract text from PDF and preprocess CSV and text files
            excel_to_csv(excel_file, csv_file)
            activity_data = extract_activity_from_csv(csv_file)
            
        else:        
            # If no tables extracted, directly extract activity from pdf
            activity_data = extract_activity_from_pdf(pdf_file)

        # If no activity found, print a message and return
        if not activity_data:
            print(f"No activity found in {pdf_file}.")
            return {}

        return activity_data

    except Exception as e:
        print(f"Error processing {pdf_file}: {e}")
        return {}    

def main():
    parser = argparse.ArgumentParser(description="Extract specific pages from a PDF and process them for activity data.")
    parser.add_argument("-p", "--pdfile_path", type=Path, required=True, help="Path to the PDF file to be processed.")
    parser.add_argument("-s", "--start_page", type=int, required=True, help="First page to extract (1-based index).")
    parser.add_argument("-e", "--end_page", type=int, required=True, help="Last page to extract (1-based index).")
    parser.add_argument("-t", "--together", action="store_true", help="Extract the pages together into a single file.")
    args = parser.parse_args()

    pdf2activity_conversion(
        pdfile_path=args.pdfile_path,
        start_page=args.start_page,
        last_page=args.end_page,
        together=args.together
    )

if __name__ == '__main__':
    main()