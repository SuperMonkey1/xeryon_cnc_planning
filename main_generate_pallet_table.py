# This script generates a pallet table (.P file) based on the planned operations in operations.xlsx. 

import pandas as pd
from pathlib import Path
from pallet_table_generator import PalletTableGenerator
import sys
import datetime


def get_new_filename(base_path, date_str):
    index = 1
    while True:
        new_filename = f"{date_str}_{index}_pallet_table.P"
        if not (base_path / new_filename).exists():
            return new_filename
        index += 1


def main():
    # Example usage
    project_root = Path(__file__).parent.absolute()
    operations_path = project_root / 'build' / 'operations.xlsx'
    build_path = project_root / 'build'
    
     # Get current date in YYYY_MM_DD format
    today = datetime.datetime.now().strftime("%Y_%m_%d")
    
    # Generate new filename with date and sequence number
    new_filename = get_new_filename(build_path, today)
    output_path = build_path / new_filename
    print(f"PALLET_TABLE.P already exists. Creating {new_filename} instead.")
    


    # Read operations Excel file
    operations_df = pd.read_excel(operations_path)
    
    # Generate pallet table
    generator = PalletTableGenerator()
    generator.generate_pallet_table(operations_df, output_path, new_filename)

    return output_path

if __name__ == "__main__":
    output_file = main()
    print(f"Pallet table generated at: {output_file}")
    