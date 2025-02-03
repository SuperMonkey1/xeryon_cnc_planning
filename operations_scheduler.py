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

    def get_all_required_operations_df_old(self, product_types, product_sizes, product_forces, months): #quadrants is a df with  quadrants
        
        quadrants_df = self.get_quadrants_df(product_types, product_sizes, product_forces, months)

        num_pallets = 5  # Number of unique pallet numbers
        quadrant_count = 4  # Number of times each pallet number is repeated
        quadrant_pattern = ["A", "B", "C", "D"]
        
        #get_info_from_quadrants
        pallet_table_df = quadrants_df[["id", "loading_time", "machine_time", "unloading_time", "bewerkings_orde", "components_per_quadrant"]]
        # Ensure the specified columns are integers
        pallet_table_df.loc[:, "loading_time"] = pd.to_numeric(pallet_table_df["loading_time"], errors="coerce").fillna(0).astype(int)
        pallet_table_df.loc[:, "machine_time"] = pd.to_numeric(pallet_table_df["machine_time"], errors="coerce").fillna(0).astype(int)
        pallet_table_df.loc[:, "unloading_time"] = pd.to_numeric(pallet_table_df["unloading_time"], errors="coerce").fillna(0).astype(int)
        pallet_table_df.loc[:, "bewerkings_orde"] = pd.to_numeric(pallet_table_df["bewerkings_orde"], errors="coerce").fillna(0).astype(int)
        pallet_table_df.loc[:, "components_per_quadrant"] = pd.to_numeric(pallet_table_df["components_per_quadrant"], errors="coerce").fillna(0).astype(int)

        # PALLET COLUMN
        pallet_column = [pallet for pallet in range(1, num_pallets + 1) for _ in range(quadrant_count)]
        pallet_column = (pallet_column * (len(pallet_table_df) // len(pallet_column) + 1))[:len(pallet_table_df)]
        pallet_table_df.insert(0, 'pallet', pallet_column)

        # QUADRANT COLUMN
        quadrant_column = (quadrant_pattern * (len(pallet_table_df) // len(quadrant_pattern) + 1))[:len(pallet_table_df)]
        pallet_table_df.insert(1, 'quadrant', quadrant_column)

        # Empty all cells in "pallet" and "quadrant": yeah this is weird: above we assigned pallets and quadrants, here we empty them because above was done orginially but no w the assignmenet of quadrants and pallets happens later
        pallet_table_df['pallet'] = None
        pallet_table_df['quadrant'] = None

        # ADD STATUS COLUMN
        pallet_table_df.insert(2, 'status', "")
        # Update rows where "bewerkings_orde" == 1 to have "first order" in "status"
        pallet_table_df.loc[pallet_table_df["bewerkings_orde"] == 1, "status"] = "first order"
        print(pallet_table_df)


        return  pallet_table_df

        # save this df to excel tab (use general method)

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
        
        ### DETERMINE MACHINABLE QUADRANTS (either first bewerkingen or follow up quadrants from done quadrants)
        machinable_operations_df = operations_df[(operations_df['bewerkings_orde'] == 1) & (operations_df['status'] != "done")]
        additional_machinable_operations_df = operations_df[operations_df['status'] == "unlocked"]
        print("Amount of machinable quadrants of order 1: ", machinable_operations_df.shape[0])
        print("additional_machinable_df: ", additional_machinable_operations_df.shape[0])
        machinable_operations_df = pd.concat([machinable_operations_df, additional_machinable_operations_df]).reset_index(drop=True)

        ##  prioritize quadrants with the longest machine time
        machinable_operations_df["machine_time"] = pd.to_numeric(machinable_operations_df["machine_time"], errors="coerce")
        machinable_operations_df = machinable_operations_df.sort_values(by="machine_time", ascending=False)

        ### DETERMINE TO BE MACHINED QUADRANTS
        total_machining_time = 0
        machined_operations_df = pd.DataFrame()
        max_quadrants = 20  # Maximum number of quadrants to machine

        while total_machining_time < 840 and len(machined_operations_df) < max_quadrants:

            # Identify IDs already in machined_quadrants_df
            existing_ids = set(machined_operations_df["id"]) if not machined_operations_df.empty else set()

            # Filter machinable_quadrants_df for quadrants with a unique ID
            unique_id_quadrants = machinable_operations_df[~machinable_operations_df["id"].isin(existing_ids)]

            # If unique ID quadrants are available, pick the first one; otherwise, pick the first quadrant overall
            if not unique_id_quadrants.empty:
                first_quadrant = unique_id_quadrants.head(1)
            else:
                # If all IDs are already in machined_quadrants_df, allow duplicates but not more than 2 of the same ID
                id_counts = machined_operations_df["id"].value_counts()
                allowable_operations = machinable_operations_df[
                    machinable_operations_df["id"].apply(lambda x: id_counts.get(x, 0) < 2)
                ]
                first_quadrant = allowable_operations.head(1)

            # If no quadrant can be picked, break the loop
            if first_quadrant.empty:
                print("No suitable quadrant available.")
                break

            # Calculate the potential new total machining time
            potential_machining_time = total_machining_time + first_quadrant["machine_time"].iloc[0]
            
            if potential_machining_time > 840:
                break  # Exit the loop if adding this quadrant exceeds the limit

            machinable_operations_df = machinable_operations_df.drop(first_quadrant.index).reset_index(drop=True)
            machined_operations_df = pd.concat([machined_operations_df, first_quadrant]).reset_index(drop=True)

            total_machining_time = machined_operations_df["machine_time"].sum()
            # print("firs_quadrant", first_quadrant)
            # print("total_machining_time: ", total_machining_time)
            total_unloading_time =  machined_operations_df["unloading_time"].sum()
            total_loading_time =  machined_operations_df["loading_time"].sum()

        ### MARK MACHIEND QUADRANTS AS "DONE"
        for _, row in machined_operations_df.iterrows():
            # Find the indices in operations_df where "id" matches and "status" is not already "done"
            indices_to_update = operations_df[
                (operations_df["id"] == row["id"]) & (operations_df["status"] != "done")
            ].index
            
            # Only update one row in operations_df per row in machined_quadrants
            if not indices_to_update.empty:
                index_to_update = indices_to_update[0]  # Take the first matching index
                operations_df.at[index_to_update, "status"] = "done"

        ### MARK FOLLOW UP QUADRANTS AS "UNLOCKED"
        for _, row in machined_operations_df.iterrows():
            # find the id of the machined quadrant
            machined_quadrant_id = row["id"]
            # look up the product and component of the machined quadrant in planning.xlsx
            machined_quadrant_product = operations_catalog_df[operations_catalog_df["id"] == machined_quadrant_id]["product"].values[0]
            machined_quadrant_component = operations_catalog_df[operations_catalog_df["id"] == machined_quadrant_id]["component"].values[0]

            #get the follow up_id if exists
            row_number = operations_catalog_df[operations_catalog_df["id"] == machined_quadrant_id].index[0]
            # get the id of the next row in quadrant_types_df
            follow_up_quadrant_id = operations_catalog_df.iloc[row_number + 1]["id"]
            follow_up_quadrant_product = operations_catalog_df[operations_catalog_df["id"] == follow_up_quadrant_id]["product"].values[0]
            follow_up_quadrant_component = operations_catalog_df[operations_catalog_df["id"] == follow_up_quadrant_id]["component"].values[0]
            if follow_up_quadrant_product == machined_quadrant_product and follow_up_quadrant_component == machined_quadrant_component:
                pass
            else:
                follow_up_quadrant_id = None
            
            # find the amount of components_per_quadrant of the machined quadrant
            components_per_quadrant = int(row["components_per_quadrant"])

            #look for a quadrant in  operations_df with the same id as follow_up_quadrant_id and status "unlocked" if not status "done" and if not status "unlocked", give it status "unlocked"
            
            for _ in range(components_per_quadrant):  # Loop N times
                if follow_up_quadrant_id:
                    follow_up_quadrant_index = operations_df[
                        (operations_df["id"] == follow_up_quadrant_id) & 
                        (operations_df["status"] != "done") & 
                        (operations_df["status"] != "unlocked")
                        ].index
                    
                    if not follow_up_quadrant_index.empty:
                        operations_df.at[follow_up_quadrant_index[0], "status"] = "unlocked"
    
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
        print("Number of done quadrants: ", assigned_operations_df[assigned_operations_df["status"] == "done"].shape[0])
        print("Number of unlocked quadrants: ", assigned_operations_df[assigned_operations_df["status"] == "unlocked"].shape[0])

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
