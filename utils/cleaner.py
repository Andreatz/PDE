import argparse
import os
import shutil

from pathlib import Path

def csv_cleaning(csv_file: Path):
    """
    Clean the contents of a CSV file by removing unwanted characters.
    
    Args:
    - csv_file (Path): Path object representing the CSV file to be cleaned.
    
    Returns:
    - csv_file (Path): Path object representing the cleaned CSV file.
    """
    # Read all lines from the CSV file
    with open(csv_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Process each line for cleaning
    cleaned_lines = []
    for line in lines:
        # Replace colons with empty string
        line = line.replace(':', '')
        # Replace double quotes with empty string
        line = line.replace('"', '')
        # Replace single quotes with double quotes
        line = line.replace("'", '"')
        cleaned_lines.append(line)
    
    # Write the cleaned content back to the same file
    with open(csv_file, 'w', encoding='utf-8') as file:
        file.writelines(cleaned_lines)

    return csv_file

def folder_cleaner(directory):
    """
    Remove all files and subdirectories within a directory.
    
    Args:
    - directory (str): Path to the directory to be cleaned.
    """
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            # Remove subdirectory and all its contents
            shutil.rmtree(item_path)
        else:
            # Remove file
            os.remove(item_path)

def main():
    parser = argparse.ArgumentParser(description="Clean a CSV file by removing unwanted characters.")
    parser.add_argument("-p", "--csv_path", type=Path, required=True, help="Path to the CSV file to be cleaned")
    args = parser.parse_args()

    csv_cleaning(args.csv_path)

if __name__ == "__main__":
    main()