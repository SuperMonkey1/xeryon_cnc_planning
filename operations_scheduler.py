import pandas as pd
from openpyxl import load_workbook
import math


class OperationScheduler:
    def __init__(self, quadrants_df, forecast_df):
        self.quadrants_df = quadrants_df
        self.forecast_df = forecast_df

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
                return int(product_count)
            else:
                print(" no matching data found")
                return None

    def get_operations_df_per_product(self,product_type, product_size, product_force):
        
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
            
            quadrants_per_product_df = self.get_operations_df_per_product(
                product_type, product_size, product_force
            )
            product_count = self.get_product_count(
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
                                    "components_per_quadrant"]]

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

    def fill_night(self, operations_df, operations_catalog_df):
        
        ### DETERMINE MACHINABLE OPERATIONS (either first bewerkingen or follow up operations from done operations)
        machinable_operations_df = operations_df[(operations_df['bewerkings_orde'] == 1) & (operations_df['status'] != "done")]
        additional_machinable_operations_df = operations_df[operations_df['status'] == "unlocked"]
        machinable_operations_df = pd.concat([machinable_operations_df, additional_machinable_operations_df]).reset_index(drop=True)

        ##  prioritize operations with the longest machine time
        machinable_operations_df["machine_time"] = pd.to_numeric(machinable_operations_df["machine_time"], errors="coerce")
        machinable_operations_df = machinable_operations_df.sort_values(by="machine_time", ascending=False)

        ### DETERMINE TO BE MACHINED OPERATIONS
        total_machining_time = 0
        machined_operations_df = pd.DataFrame()
        max_quadrants = 20  # Maximum number of quadrants to machine

        while total_machining_time < 840 and len(machined_operations_df) < max_quadrants:

            # Identify IDs already in machined_operations_df
            existing_ids = set(machined_operations_df["id"]) if not machined_operations_df.empty else set()

            # Filter machinable_operations_df for operations with a unique ID
            unique_id_operations = machinable_operations_df[~machinable_operations_df["id"].isin(existing_ids)]

            # If unique ID operations are available, pick the first one; otherwise, pick the first operation overall
            if not unique_id_operations.empty:
                first_operation = unique_id_operations.head(1)
            else:
                # If all IDs are already in machined_operations_df, allow duplicates but not more than 2 of the same ID
                id_counts = machined_operations_df["id"].value_counts()
                allowable_operations = machinable_operations_df[
                    machinable_operations_df["id"].apply(lambda x: id_counts.get(x, 0) < 2)
                ]
                first_operation = allowable_operations.head(1)

            # If no operations can be picked, break the loop
            if first_operation.empty:
                print("No suitable quadrant available.")
                break

            # Calculate the potential new total machining time
            potential_machining_time = total_machining_time + first_operation["machine_time"].iloc[0]
            
            if potential_machining_time > 840:
                break  # Exit the loop if adding this operation exceeds the limit

            machinable_operations_df = machinable_operations_df.drop(first_operation.index).reset_index(drop=True)
            machined_operations_df = pd.concat([machined_operations_df, first_operation]).reset_index(drop=True)

            total_machining_time = machined_operations_df["machine_time"].sum()
            total_unloading_time =  machined_operations_df["unloading_time"].sum()
            total_loading_time =  machined_operations_df["loading_time"].sum()

        ### MARK MACHIEND OPERATIONS AS "DONE"
        for _, row in machined_operations_df.iterrows():
            # Find the indices in operations_df where "id" matches and "status" is not already "done"
            indices_to_update = operations_df[
                (operations_df["id"] == row["id"]) & (operations_df["status"] != "done")
            ].index
            
            # Only update one row in operations_df per row in machined_operations
            if not indices_to_update.empty:
                index_to_update = indices_to_update[0]  # Take the first matching index
                operations_df.at[index_to_update, "status"] = "done"

        ### MARK FOLLOW UP OPERATIONS AS "UNLOCKED"
        for _, row in machined_operations_df.iterrows():
            # find the id of the machined operation
            machined_operation_id = row["id"]
            # look up the product and component of the machined operation in planning.xlsx
            machined_operation_product = operations_catalog_df[operations_catalog_df["id"] == machined_operation_id]["product"].values[0]
            machined_operation_component = operations_catalog_df[operations_catalog_df["id"] == machined_operation_id]["component"].values[0]

            #get the follow up_id if exists
            row_number = operations_catalog_df[operations_catalog_df["id"] == machined_operation_id].index[0]
            # get the id of the next row in operations_catalog_df
            follow_up_operation_id = operations_catalog_df.iloc[row_number + 1]["id"]
            follow_up_operation_product = operations_catalog_df[operations_catalog_df["id"] == follow_up_operation_id]["product"].values[0]
            follow_up_operation_component = operations_catalog_df[operations_catalog_df["id"] == follow_up_operation_id]["component"].values[0]
            if follow_up_operation_product == machined_operation_product and follow_up_operation_component == machined_operation_component:
                pass
            else:
                follow_up_operation_id = None
            
            # find the amount of components_per_operation of the machined operation
            components_per_operation = int(row["components_per_quadrant"])

            #look for an operation in  operations_df with the same id as follow_up_operation_id and status "unlocked" if not status "done" and if not status "unlocked", give it status "unlocked"
            
            for _ in range(components_per_operation):  # Loop N times
                if follow_up_operation_id:
                    follow_up_operation_index = operations_df[
                        (operations_df["id"] == follow_up_operation_id) & 
                        (operations_df["status"] != "done") & 
                        (operations_df["status"] != "unlocked")
                        ].index
                    
                    if not follow_up_operation_index.empty:
                        operations_df.at[follow_up_operation_index[0], "status"] = "unlocked"
    
        ### SAVE THE UPDATED operations_df TO EXCEL
        # orden operations_df on top "done" and then "unlocked"
        status_order = ["done","first order","unlocked"]  # "done" comes first, followed by "unlocked"
        operations_df["status"] = pd.Categorical(operations_df["status"], categories=status_order, ordered=True)
        operations_df = operations_df.sort_values(by=["status"], ascending=True)

        ### ASSIGN QUADRANTS TO OPERATIONS
        assigned_operations_df = self.assign_quadrants_to_operations(operations_df)

        #order first on "timestamp" and then on "pallet" and then on "quadrant"
        assigned_operations_df = assigned_operations_df.sort_values(by=["timestamp", "pallet", "quadrant"], ascending=True)

        print("machined_quadrants_df: ", machined_operations_df)
        print("total_machining_time: ", total_machining_time)
        print("total_loading_time: ", total_loading_time)
        print("total_unloading_time: ", total_unloading_time)
        print("Number of done operations: ", assigned_operations_df[assigned_operations_df["status"] == "done"].shape[0])
        print("Number of unlocked operations: ", assigned_operations_df[assigned_operations_df["status"] == "unlocked"].shape[0])

        return assigned_operations_df

    def assign_quadrants_to_operations(self, operations_df):
        pallets = [1, 2, 3, 4, 5]
        quadrants = ['A', 'B', 'C', 'D']

        # add column with time stamp in rows where 
        if 'timestamp' not in operations_df.columns:
            operations_df['timestamp'] = pd.NaT
        timestamp = pd.Timestamp.now()
        operations_df.loc[(operations_df['status'] == "done") & (pd.isna(operations_df['timestamp'])), 'timestamp'] = timestamp

        # timestamp  = pd.Timestamp.now()
        # for index, row in operations_df.iterrows():
        #     if row['status'] == "done" and pd.isna(row['quadrant']):
        #         operations_df['timestamp'] = timestamp

        # Initialize counters to keep track of the current pallet and quadrant
        current_pallet_index = 0
        current_quadrant_index = 0

        # Iterate through each row in the DataFrame
        for index, row in operations_df.iterrows():
            # Check if the status is "done"
            if row['status'] == "done" and pd.isna(row['quadrant']):
                # Assign the current pallet and quadrant to the operation
                operations_df.at[index, 'pallet'] = pallets[current_pallet_index]
                operations_df.at[index, 'quadrant'] = quadrants[current_quadrant_index]

                # Move to the next quadrant
                current_quadrant_index += 1

                # If all quadrants for the current pallet are used, move to the next pallet
                if current_quadrant_index == len(quadrants):
                    current_quadrant_index = 0
                    current_pallet_index += 1

                    # If all pallets are used, wrap back to the first pallet
                    if current_pallet_index == len(pallets):
                        current_pallet_index = 0
        
        return operations_df
    
    def unload_morning(self, pallet_table_df):
        pass
        # START OCHTEND UNLOADING
        # bereken total unload time van vorige nacht
        # maak lijn unload time: unload eerst de pallet die het minst lang duurt om te unloaden
        # maak lijn load time: load een pallet (zoek een pallet die ...)