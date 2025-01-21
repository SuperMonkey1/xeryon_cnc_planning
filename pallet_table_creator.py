import pandas as pd
from openpyxl import load_workbook
from quadrant import Quadrant
import openpyxl


class PalletTableCreator:
    def __init__(self, quadrants_df):
        self.quadrants_df = quadrants_df
    
    def create_pallet_table_df_from_quadrants(self, quadrants): #quadrants is a df with  quadrants
        num_pallets = 5  # Number of unique pallet numbers
        quadrant_count = 4  # Number of times each pallet number is repeated
        quadrant_pattern = ["A", "B", "C", "D"]
        
        #get_info_from_quadrants
        pallet_table_df = quadrants[["id", "loading_time", "machine_time", "unloading_time"]]

        # PALLET COLUMN
        pallet_column = [pallet for pallet in range(1, num_pallets + 1) for _ in range(quadrant_count)]
        pallet_column = (pallet_column * (len(pallet_table_df) // len(pallet_column) + 1))[:len(pallet_table_df)]
        pallet_table_df.insert(0, 'pallet', pallet_column)

        # QUADRANT COLUMN
        quadrant_column = (quadrant_pattern * (len(pallet_table_df) // len(quadrant_pattern) + 1))[:len(pallet_table_df)]
        pallet_table_df.insert(1, 'quadrant', quadrant_column)

        print(pallet_table_df)
        return  pallet_table_df

        # save this df to excel tab (use general method)

