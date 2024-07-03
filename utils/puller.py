import csv
import os
import fitz
import PyPDF2
import pytesseract
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chemdataextractor.doc import Document
from pdf2image import convert_from_path
from utils.preprocessor import preprocess_text

def extract_text_from_pdf(pdf_file, output_folder):
    """
    Extracts text from a PDF file using PyMuPDF. Uses Tesseract OCR if PyMuPDF fails.
    
    Args:
        pdf_file (str): Path to the input PDF file.

    Returns:
        str: Path to the extracted text file.
    """
    # Generate the output text file path
    base_name = os.path.splitext(os.path.basename(pdf_file))[0]
    txt_file = output_folder / f'{base_name}.txt'

    try:
        # Attempt to open the PDF file using PyMuPDF (fitz)
        doc = fitz.open(pdf_file)
        text = ""

        # Iterate through each page in the PDF and extract text
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()

        # Check if extracted text is empty
        if not text.strip():
            raise ValueError("Empty text extracted")

        # Write the extracted text to a text file
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(text)

    except Exception as e:
        # If PyMuPDF fails, attempt OCR using Tesseract
        print(f"PyMuPDF failed with error: {e}. Trying OCR...")
        ocr_text = ""
        images = convert_from_path(pdf_file)

        # Process each page image using Tesseract OCR and concatenate results
        for image in images:
            ocr_text += pytesseract.image_to_string(image, lang='eng')

        # Write the OCR extracted text to a text file
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(ocr_text)

    return txt_file

def extract_molecules_from_text(txt_file):
    """
    Extracts molecules from preprocessed text using ChemDataExtractor, focusing on 'Example' strings.
    
    Args:
        txt_file (str): Path to the preprocessed text file.

    Returns:
        list: List of dictionaries containing extracted molecules and their corresponding examples.
    """
    # Read the preprocessed text from the input file
    with open(txt_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Generate the path for the preprocessed text file
    preprocessed_txt_path = os.path.splitext(txt_file)[0] + '_preprocessed.txt'

    # Preprocess the text to handle specific formatting issues
    preprocess_text(text, preprocessed_txt_path)

    # Read the preprocessed text after preprocessing
    with open(preprocessed_txt_path, 'r', encoding='utf-8') as f:
        preprocessed_text = f.read()

    # Split the preprocessed text into paragraphs
    paragraphs = preprocessed_text.split('\n')
    molecules = []
    current_example = None

    # Iterate through each paragraph to extract molecules
    for i, paragraph in enumerate(paragraphs):
        # Check if the paragraph contains 'Example'
        if 'Example' in paragraph:
            current_example = paragraph.split(' ')[-1]
            continue

        # Check if current_example is not None and process the next paragraph
        if current_example is not None:
            if i < len(paragraphs) - 1:
                next_paragraph = paragraphs[i + 1]
                if 'Example' not in next_paragraph:
                    paragraph += ' ' + next_paragraph

            # Use ChemDataExtractor to parse compounds from the paragraph
            compounds = Document(paragraph).records.serialize()

            # Extract molecule names and add to molecules list
            for compound in compounds:
                if compound.get('names'):
                    molecule_name = compound['names'][0]
                    if ' ' in molecule_name:
                        molecule_name = molecule_name.split(' ')[0]
                    molecules.append({'Example': 'Example ' + current_example, 'Molecule': molecule_name})
            current_example = None

    # Write the preprocessed text back to the original txt_file
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(preprocessed_text)

    return molecules

def extract_activity_from_csv(csv_file):
    """
    Extracts activity data from a csv file.
    Args:
        txt_file (str): Path to the csv file.

    Returns:
        dict: Dictionary containing molecule IDs as keys and activity data as values.
    """
    activity_data = {}  # Dictionary to store activity data

    try:
        with open(csv_file, 'r') as file:
            lines = file.readlines()

            for line in lines:
                match = re.match(r'^(Example\s+)?([0-9A-Z]+),(\d{1,3}(?:,\d{3})*|\d+|([\d.,]+))$', line.strip())
                if match:
                    molecule_id = match.group(1) + match.group(2) if match.group(1) else match.group(2)
                    activity = match.group(3).replace(',', '')  # Remove commas from activity
                    activity_data[molecule_id] = activity
    except Exception as e:
        print(f"Error processing {csv_file}: {e}")
        return {}

    return activity_data

def extract_activity_from_pdf(pdf_file):
    """
    Extracts activity data from a PDF file. Handles both text-based and image-based PDFs.

    Args:
        pdf_file (Path): Path to the PDF file.

    Returns:
        dict: Dictionary containing molecule IDs as keys and activity data as values.
    """
    activity_data = {}  # Dictionary to store activity data
    text_extracted = False

    try:
        # Attempt to read the PDF with PyPDF2
        with open(pdf_file, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:  # If text is extracted, save to a temporary .txt file and process it
                        text_extracted = True
                        temp_txt_file = pdf_file.with_stem(pdf_file.stem + f"_page_{page_num + 1}").with_suffix('.txt')
                        with open(temp_txt_file, 'w') as txt_file:
                            txt_file.write(text)
                        
                        lines = text.split('\n')
                        for line in lines:
                            match = re.match(r'^(Example\s+)?([0-9A-Z]+)\s+(\d{1,3}(?:,\d{3})*|\d+|([\d.,]+))$', line.strip())
                            if match:
                                molecule_id = match.group(1) + match.group(2) if match.group(1) else match.group(2)
                                activity = match.group(3).replace(',', '')  # Remove commas from activity
                                activity_data[molecule_id] = activity
                except Exception as page_error:
                    print(f"Error processing page {page_num + 1} of {pdf_file}: {page_error}")

    except Exception as e:
        print(f"Error processing {pdf_file}: {e}")
        return {}

    if not text_extracted:
        # If no text is extracted, use OCR
        try:
            images = convert_from_path(pdf_file)
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image)
                temp_txt_file = pdf_file.with_stem(pdf_file.stem + f"_page_{i + 1}_ocr").with_suffix('.txt')
                with open(temp_txt_file, 'w') as txt_file:
                    txt_file.write(text)

                lines = text.split('\n')
                for line in lines:
                    line = line.replace(',', '')
                    match = re.match(r'^(Example\s+)?([0-9A-Z]+)\s+(\d+(\.\d+)?)$', line.strip())
                    if match:
                        molecule_id = match.group(2)
                        activity = match.group(3)
                        activity_data[molecule_id] = activity
        except Exception as e:
            print(f"Error processing {pdf_file} with OCR: {e}")
            return {}

    return activity_data

def save_activity_to_csv(activity_data, output_file):
    """
    Saves the extracted activity data to a CSV file.

    Args:
        activity_data (dict): Dictionary containing molecule IDs and activities.
        output_file (str): Path to the output CSV file.
    """
    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Molecule ID', 'Activity'])
            for molecule_id, activity in activity_data.items():
                writer.writerow([molecule_id, activity])
    except Exception as e:
        print(f"Error saving activity data to {output_file}: {e}")