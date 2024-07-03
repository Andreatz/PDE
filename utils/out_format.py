import os
import pandas as pd

from rdkit.Chem import PandasTools

def sdf_output_format(input_file: str):
    """
    Convert a CSV file to an SDF file format using RDKit.

    Args:
        input_file (str): Path to the input CSV file.
    """
    # Extract base name from input file path
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Read CSV file into a pandas DataFrame
    df = pd.read_csv(input_file, delimiter=";")
    
    # Add molecule column to DataFrame using RDKit's PandasTools
    PandasTools.AddMoleculeColumnToFrame(df, 'Smiles', 'Molecule Name', 'Activity Value', 'Activity Type', 'Activity Unit')
    
    # Write DataFrame to an SDF file
    PandasTools.WriteSDF(df, f'{base_name}.sdf', molColName='Molecule Name', properties=list(df.columns))

def smi_output_format():
    pass