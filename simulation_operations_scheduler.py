import pandas as pd
import math

class SimulationOperationsScheduler:
    def __init__(self, quadrants_df, forecast_df):
        self.quadrants_df = quadrants_df
        pass
    
    def _get_product_count(self, product_type, product_size, product_force, month ):
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
                return int(product_count)
            else:
                print(" no matching data found")
                return None

    def _get_operations_df_per_product(self,product_type, product_size, product_force):
        
        if(product_size == "120"):
            product = f"{product_type}_{product_force}_{product_size}"
        else:
            product = f"{product_type}_{product_force}_0{product_size}"

        #filter in quadrants_df op product_size, product_force
        filtered_quadrants_df = self.quadrants_df[self.quadrants_df['product'] == product]
        
        return filtered_quadrants_df 

    def get_all_required_operations_df(self, forecast_elements_df):

        all_required_operations_df = pd.DataFrame()
        
        # Iterate through forecast elements
        for _, row in forecast_elements_df.iterrows():
            product_type = row['product_type']
            product_size = row['product_size']
            product_force = row['product_force']
            month = row['month']
            
            quadrants_per_product_df = self._get_operations_df_per_product(
                product_type, product_size, product_force
            )
            product_count = self._get_product_count(
                product_type, product_size, product_force, month
            )

            # Duplicate the quadrants_df based on the product count
            repeated_quadrants_df = pd.concat(
                [quadrants_per_product_df] * product_count, 
                ignore_index=True
            )

            # Append the repeated data to the combined DataFrame
            all_required_operations_df = pd.concat(
                [all_required_operations_df, repeated_quadrants_df], 
                ignore_index=True
            )

        # Create a copy of the DataFrame to avoid modifying the original
        all_required_operations_df = all_required_operations_df.copy()

        # Process components per quadrant
        unique_ids = all_required_operations_df['id'].unique()
        processed_quadrants = []

        for unique_id in unique_ids:
            id_quadrants = all_required_operations_df[all_required_operations_df['id'] == unique_id]
            components_per_quadrant = int(id_quadrants.iloc[0]['components_per_quadrant'])
            total_quadrants = len(id_quadrants)
            amount_of_quadrants = math.ceil(total_quadrants / components_per_quadrant)
            
            if total_quadrants > amount_of_quadrants:
                processed_quadrants.append(id_quadrants.head(amount_of_quadrants))
            else:
                processed_quadrants.append(id_quadrants)

        # Combine processed quadrants
        result_df = pd.concat(processed_quadrants, ignore_index=True)

        # Add required columns and convert data types
        operations_df = result_df[["id", "loading_time", "machine_time", 
                                    "unloading_time", "bewerkings_orde", 
                                    "components_per_quadrant", "hfile"]]

        # Convert numeric columns
        numeric_columns = ["loading_time", "machine_time", "unloading_time", 
                        "bewerkings_orde", "components_per_quadrant"]
        
        for col in numeric_columns:
            operations_df[col] = pd.to_numeric(
                operations_df[col], 
                errors="coerce"
            ).fillna(0).astype(int)

        # Add empty pallet and quadrant columns
        operations_df.insert(0, 'pallet', None)
        operations_df.insert(1, 'quadrant', None)

        # Add status column
        operations_df.insert(2, 'status', "")
        operations_df.loc[operations_df["bewerkings_orde"] == 1, "status"] = "first order"

        return operations_df
    
    def does_operator_needs_to_start_loading_for_night_shift(self, minute):
        if  minute == 900:
            return True
        else:
            return False
    
    def get_next_operation_to_be_loaded():
        pass