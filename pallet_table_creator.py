import pandas as pd
from openpyxl import load_workbook
from quadrant import Quadrant
import openpyxl
import math


class PalletTableCreator:
    def __init__(self, quadrants_df, forecast_df):
        self.quadrants_df = quadrants_df
        self.forecast_df = forecast_df
    
        #PROJECT SPECIFIC METHODS
    def get_product_count(self, product_type, product_size, product_force, month ):
        # Filter rows by product type, size, and force
        filtered_df = self.forecast_df[
            (self.forecast_df.iloc[:, 1].str.contains(product_size, na=False)) &
            (self.forecast_df.iloc[:, 2].str.contains(product_force, na=False)) &
            (self.forecast_df.iloc[:, 3].str.contains(product_type, na=False))
        ]
        
        # Find the column that matches the given month
        matching_columns = [col for col in self.forecast_df.columns if month in col]
        if not matching_columns:
            raise ValueError(f"Month '{month}' not found in forecast data headers.")
        
        # Use the first matching column (in case of duplicates, which should ideally not happen)
        month_column = matching_columns[0]
        
        # Retrieve the product count for the specified month
        if not filtered_df.empty:
            # Convert the month column values to float and sum them
            product_count = filtered_df[month_column].astype(float).sum() if not filtered_df.empty else 0
            return product_count
        else:
            print(" no matching data found")
            return None

    def get_quadrants_df_per_product(self,product_type, product_size, product_force):
        
        if(product_size == "120"):
            product = f"{product_type}_{product_force}_{product_size}"
        else:
            product = f"{product_type}_{product_force}_0{product_size}"

        #filter in quadrants_df op product_size, product_force
        filtered_quadrants_df = self.quadrants_df[self.quadrants_df['product'] == product]
        
        return filtered_quadrants_df 
    
    def get_quadrants_df(self, product_types, product_sizes, product_forces, months):

        # Initialize an empty DataFrame to hold all the combined data
        quadrants_df = pd.DataFrame()      

        length = len(product_types)
        for i in range(length):
            product_type = product_types[i]
            product_size = product_sizes[i]
            product_force = product_forces[i]
            month = months[i]
            
            quadrants_per_product_df = self.get_quadrants_df_per_product(product_type, product_size, product_force)
            product_count = self.get_product_count(product_type, product_size, product_force, month )
            product_count = int(product_count)

            # Duplicate the quadrants_df based on the product count
            repeated_quadrants_df = pd.concat([quadrants_per_product_df] * product_count, ignore_index=True)

            # Append the repeated data to the combined DataFrame
            quadrants_df = pd.concat([quadrants_df, repeated_quadrants_df], ignore_index=True)

        
        # Create a copy of the DataFrame to avoid modifying the original
        quadrants_df = quadrants_df.copy()

        # Remove quadrants base on components_per_quadrant
        unique_ids = quadrants_df['id'].unique()

        for unique_id in unique_ids:
            # Filter rows with the current id
            id_quadrants = quadrants_df[quadrants_df['id'] == unique_id]
            # Get components_per_quadrant (assuming it's the same for all rows of the same id)
            components_per_quadrant = id_quadrants.iloc[0]['components_per_quadrant']

            # Count the total number of quadrants with this id
            total_amount_of_quadrants = len(id_quadrants)

            # Calculate the desired number of quadrants
            amount_of_quadrants = math.ceil(total_amount_of_quadrants/int(components_per_quadrant) )
            # Remove excess rows to match the desired amount_of_quadrants
            if total_amount_of_quadrants > amount_of_quadrants:
                rows_to_keep = id_quadrants.head(amount_of_quadrants)
                quadrants_df = pd.concat([
                    quadrants_df[quadrants_df['id'] != unique_id],  # Keep rows with other ids
                    rows_to_keep
                ])
        # Reset the index for cleanliness
        quadrants_df.reset_index(drop=True, inplace=True)

        return quadrants_df


    def create_unordered_pallet_table_df_from_quadrants(self, product_types, product_sizes, product_forces, months): #quadrants is a df with  quadrants
        
        quadrants = self.get_quadrants_df(product_types, product_sizes, product_forces, months)
        
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

