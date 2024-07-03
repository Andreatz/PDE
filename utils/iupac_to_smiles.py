import logging
import os
import pandas as pd
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_IUPAC_to_SMILES(iupac_name: str):
    """
    Convert an IUPAC name to SMILES notation using the OPSIN web service.

    Args:
        iupac_name (str): IUPAC name of the molecule to convert.

    Returns:
        str or None: SMILES notation if conversion successful, None otherwise.
    """
    try:      
        # Send a GET request to OPSIN web service
        response = requests.get(f"https://opsin.ch.cam.ac.uk/opsin/{iupac_name}.json")
        
        # Raise an exception for HTTP errors (non-2xx status codes)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Extract SMILES notation from JSON data
        smiles = data.get('smiles')
        
        if smiles:
            return smiles
        else:
            logger.warning(f"OPSIN could not convert IUPAC name '{iupac_name}' to SMILES notation.")
            return None
    except Exception as e:
        # Log error if conversion fails
        logger.error(f"Error converting IUPAC name '{iupac_name}' using OPSIN: {e}")
        return None

def from_iupac_to_smiles_conversion(file_path, column_name):
    """
    Convert IUPAC names in a CSV file to SMILES notation and save the results in a new CSV file.

    Args:
        file_path (str): Path to the input CSV file containing molecule names.
        column_name (str): Name of the column in the CSV file containing molecule names.
    """
    
    # Load CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)
    
    # Apply convert_to_smiles_with_opsin function to each IUPAC name in the specified column
    df['SMILES'] = df[column_name].apply(convert_IUPAC_to_SMILES)
    
    # Drop rows where SMILES could not be generated
    df = df.dropna(subset=['SMILES'])
    
    # Determine output file name based on input file name
    base_name = os.path.splitext(file_path)[0]
    output_file_name = base_name + '_smiles.csv'
    
    # Save results to a new CSV file
    df.to_csv(output_file_name, index=False)
    
    logger.info(f"Molecule names converted to SMILES and saved to {output_file_name}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert IUPAC names to SMILES notation.")
    parser.add_argument("-f", "--file_path", required=True, help="Path to the CSV file containing molecule names")    
    parser.add_argument("-c", "--column_name", required=True, help="Name of the column containing molecule names")
    args = parser.parse_args()

    from_iupac_to_smiles_conversion(args.file_path, args.column_name)