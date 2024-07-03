import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0 (default) to print all logs, 1 to print only INFO logs, 3 to print only ERROR logs

from DECIMER import predict_SMILES
from pathlib import Path

def SMILES_prediction(image_path: Path, output_file: str):
    """
    Predict SMILES representations from PNG images in a directory and write results to a file.

    Args:
        image_path (Path): Path to the directory containing PNG images.
        output_file (str): Name of the output file to store results.

    """
    with open(output_file, "w") as f:
        # Find all PNG files in the specified directory
        png_files = [f for f in os.listdir(image_path) if f.endswith(".png")]     
        print(f"Number of PNG files found: {len(png_files)}")
        
        # Process each PNG file
        for png_file in png_files:
            png_file_path = os.path.join(image_path, png_file)
            print(f"Processing file: {png_file_path}")
            
            # Predict SMILES for the current PNG file using DECIMER
            SMILES = predict_SMILES(png_file_path)         
            print(f"File: {png_file}, SMILES: {SMILES}")
            
            # Write the results to the output file
            if SMILES:
                f.write(f"{png_file},{SMILES}\n")                
            else:
                print(f"Warning: No SMILES found for the file {png_file}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Brief description of the tool")
    parser.add_argument("-p", "--path", required=True, help="Path to the directory containing PNG images.")
    parser.add_argument("-o", "--output", required=True, help= "Output file name.")
    args = parser.parse_args()

    SMILES_prediction(Path(args.path), args.output)