import csv
import os
import re
import tempfile

def preprocess_csv_text(csv_file):
    """
    Preprocesses a CSV file to filter and format specific columns and saves the result as a text file.

    Args:
        csv_file (str): Path to the input CSV file.

    Returns:
        str: Path to the preprocessed text file.
    """
    # Create a temporary file to store the preprocessed text
    preprocessed_csv_txt_file = tempfile.mktemp(suffix='.txt')

    # Open the CSV file for reading and the temporary text file for writing
    with open(csv_file, 'r', encoding='utf-8') as csvfile, open(preprocessed_csv_txt_file, 'w', encoding='utf-8') as txtfile:
        reader = csv.reader(csvfile, delimiter=',')
        header_row = next(reader, None)

        if header_row is not None:
            # Determine the indices of the columns to keep
            keep_indices = []
            example_index = None
            name_index = None

            for i, column_name in enumerate(header_row):
                # Identify columns containing 'Example' or similar substrings
                if any(substring in column_name for substring in ["Example", "Exam~le", "Examole", "Examnle"]):
                    example_index = i
                # Identify columns containing 'Name' or similar substrings
                if any(substring in column_name for substring in ["Name", "Compound", "Cpd"]):
                    name_index = i
                # Add index to keep_indices if either example_index or name_index is found
                if example_index is not None or name_index is not None:
                    keep_indices.append(i)

            # Filter and write the header row with filtered columns
            filtered_header_row = [header_row[i] for i in keep_indices]
            txtfile.write(' '.join(filtered_header_row) + '\n')

        # Process each row in the CSV file
        for row in reader:
            filtered_row = [row[i] for i in keep_indices]

            # Remove spaces in the name column if name_index is found
            if name_index is not None:
                filtered_row[name_index] = filtered_row[name_index].replace(' ', '')

            # Write example or name to the text file if example_index and name_index are found
            if example_index is not None and name_index is not None:
                if "Example" in filtered_row[example_index]:
                    txtfile.write(filtered_row[example_index] + '\n')
                if filtered_row[name_index]:
                    txtfile.write(filtered_row[name_index] + '\n')

    return preprocessed_csv_txt_file

def preprocess_text(text_or_path, output_path):
    """
    Preprocesses text to merge paragraphs ending with '-' or '- ', replaces 'l' with '1' in specific cases,
    replaces number 1 with letter 'l' in specific cases where the text combination "y1" is present,
    removes isolated numbers at the beginning of lines, deletes paragraphs containing fewer than 4 characters,
    and wraps the paragraph if it starts with an isolated number. Also, removes non-standard IUPAC names.

    Args:
        text_or_path (str): Text content or path to the input text file.
        output_path (str): Path to save the preprocessed text.

    Returns:
        str: Path to the preprocessed text file.
    """
    # Load text from file if input is a file path
    if os.path.exists(text_or_path):
        with open(text_or_path, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = text_or_path

    # Remove isolated numbers at the beginning of lines and wrap paragraph if it starts with an isolated number
    text = re.sub(r'(?<=\n)(\d+)\s+(?=[^-,a-zA-Z])', r'\n', text)
    text = re.sub(r'(?<=\n)-\s*(\d+)\s*-(?=\n)', r'\n', text)
    text = re.sub(r'(?<=\n)-\s*(\d+)\s*-(?=\s*\n)', r'\n', text)

    # Remove trailing spaces at the end of each paragraph
    text = re.sub(r'\s+$', '', text, flags=re.MULTILINE)

    # Merge paragraphs ending or starting with the '-' symbol
    text = re.sub(r'(\S)-\n\s*', r'\1-', text)
    text = re.sub(r'\n-([\\s\S]*)', r'\1-', text)

    # Replace 'l' with '1' in specific cases
    l_replacements = ['lH', '(l(', ')l)', '-l-', '-l)', '(l-', 'yl)', 'l,', ',l',]
    v_replacements = ['cvc', 'nvl', 'xvc', 'pvr', 'zvl', 'hvl', ]
    for rep_l in l_replacements:
        text = text.replace(rep_l, rep_l.replace('l', '1'))
    for rep_v in v_replacements:
        text = text.replace(rep_v, rep_v.replace('v', 'y'))

    # Remove unwanted spaces
    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s+\)', ')', text)
    text = re.sub(r'\[\s+', '[', text)
    text = re.sub(r'\s+\]', ']', text)
    text = re.sub(r'\{\s+', '{', text)
    text = re.sub(r'\s+\}', '}', text)
    text = re.sub(r'\s*-\s*', '-', text)
    text = re.sub(r'\-l\s+', '-1', text)
    text = re.sub(r'(\d)\s*,\s*(\d)', r'\1,\2', text)

    # Replace number 1 with letter 'l' in specific cases where 'y1' is present
    text = text.replace('y1', 'yl')
    text = text.replace('-IH', '-1H')

    # Find and replace words starting with 'l-'
    text = re.sub(r'\bl-', '1-', text)

    # Remove ':' from strings "Example + number:" and "Preparation of:"
    text = re.sub(r':', '', text)
    text = re.sub(r'(Preparation of):', r'Preparation of ', text)
    text = re.sub(r'(Preparation ofN)', r'Preparation of N', text)

    # Remove empty lines
    text = re.sub(r'^\s*\n', '', text, flags=re.MULTILINE)

    # Remove paragraphs containing invalid characters for IUPAC names
    valid_iupac_pattern = re.compile(r'^[a-zA-Z0-9,\-\(\)\[\]\{\}\.\s]+$')
    text = '\n'.join(line for line in text.split('\n') if valid_iupac_pattern.match(line.strip()))

    # Delete paragraphs containing fewer than 5 characters
    text = re.sub(r'^.{1,4}$[\s\S]*?\n', '', text, flags=re.MULTILINE)

    # Save preprocessed text to the specified output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    return output_path

def merge_text_files(txt_file1, txt_file2, output_file):
    """
    Merges two text files into one.

    Args:
        txt_file1 (str): Path to the first text file.
        txt_file2 (str): Path to the second text file.
        output_file (str): Path to save the merged text file.

    """
    # Open both input files for reading and the output file for writing
    with open(txt_file1, 'r', encoding='utf-8') as file1, open(txt_file2, 'r', encoding='utf-8') as file2, open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(file1.read())
        outfile.write('\n')
        outfile.write(file2.read())
    print(f"Preprocessed combined text has been created in {output_file}.")