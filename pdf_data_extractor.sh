bash from_pdf_to_iupac.sh #Step 1
bash from_pdf_to_img_to_smiles.sh #Step 2
bash from_pdf_to_activity.sh #Step 3
python compare_smiles.py step1_smiles.csv step2_smiles.csv matched_smiles.csv #Step 4
python associate_activity.py matched_smiles.csv activity.csv final_output.csv #Step 5