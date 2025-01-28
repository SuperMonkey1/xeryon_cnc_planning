import pandas as pd
from openpyxl import load_workbook
from quadrant import Quadrant
import openpyxl
import sys


class PalletTableOptimizer:
    def __init__(self):
        pass
    def unload_morning(self, pallet_table_df):
        pass
        # START OCHTEND UNLOADING
        # bereken total unload time van vorige nacht
        # maak lijn unload time: unload eerst de pallet die het minst lang duurt om te unloaden
        # maak lijn load time: load een pallet (zoek een pallet die ...)

    def fill_night(self, operations_df, quadrant_types_df):
        
        ### DETERMINE MACHINABLE QUADRANTS (either first bewerkingen or follow up quadrants from done quadrants)
        machinable_quadrants_df = operations_df[(operations_df['bewerkings_orde'] == 1) & (operations_df['status'] != "done")]
        additional_machinable_df = operations_df[operations_df['status'] == "unlocked"]
        print("Amount of machinable quadrants of order 1: ", machinable_quadrants_df.shape[0])
        print("additional_machinable_df: ", additional_machinable_df.shape[0])
        machinable_quadrants_df = pd.concat([machinable_quadrants_df, additional_machinable_df]).reset_index(drop=True)

        ##  prioritize quadrants with the longest machine time
        machinable_quadrants_df["machine_time"] = pd.to_numeric(machinable_quadrants_df["machine_time"], errors="coerce")
        machinable_quadrants_df = machinable_quadrants_df.sort_values(by="machine_time", ascending=False)
        print("machinable_quadrants_df: ", machinable_quadrants_df)
        print("Amount of machinable quadrants: ", machinable_quadrants_df.shape[0])


        ### DETERMINE TO BE MACHINED QUADRANTS
        total_machining_time = 0
        machined_quadrants_df = pd.DataFrame()
        max_quadrants = 20  # Maximum number of quadrants to machine

        while total_machining_time < 840 and len(machined_quadrants_df) < max_quadrants:

            # Identify IDs already in machined_quadrants_df
            existing_ids = set(machined_quadrants_df["id"]) if not machined_quadrants_df.empty else set()

            # Filter machinable_quadrants_df for quadrants with a unique ID
            unique_id_quadrants = machinable_quadrants_df[~machinable_quadrants_df["id"].isin(existing_ids)]

            # If unique ID quadrants are available, pick the first one; otherwise, pick the first quadrant overall
            if not unique_id_quadrants.empty:
                first_quadrant = unique_id_quadrants.head(1)
            else:
                # If all IDs are already in machined_quadrants_df, allow duplicates but not more than 2 of the same ID
                id_counts = machined_quadrants_df["id"].value_counts()
                allowable_quadrants = machinable_quadrants_df[
                    machinable_quadrants_df["id"].apply(lambda x: id_counts.get(x, 0) < 2)
                ]
                first_quadrant = allowable_quadrants.head(1)

            # If no quadrant can be picked, break the loop
            if first_quadrant.empty:
                print("No suitable quadrant available.")
                break

            # Calculate the potential new total machining time
            potential_machining_time = total_machining_time + first_quadrant["machine_time"].iloc[0]
            
            if potential_machining_time > 840:
                break  # Exit the loop if adding this quadrant exceeds the limit

            machinable_quadrants_df = machinable_quadrants_df.drop(first_quadrant.index).reset_index(drop=True)
            machined_quadrants_df = pd.concat([machined_quadrants_df, first_quadrant]).reset_index(drop=True)

            total_machining_time = machined_quadrants_df["machine_time"].sum()
            # print("firs_quadrant", first_quadrant)
            # print("total_machining_time: ", total_machining_time)
            total_unloading_time =  machined_quadrants_df["unloading_time"].sum()
            total_loading_time =  machined_quadrants_df["loading_time"].sum()


        ### MARK MACHIEND QUADRANTS AS "DONE"
        for _, row in machined_quadrants_df.iterrows():
            # Find the indices in operations_df where "id" matches and "status" is not already "done"
            indices_to_update = operations_df[
                (operations_df["id"] == row["id"]) & (operations_df["status"] != "done")
            ].index
            
            # Only update one row in operations_df per row in machined_quadrants
            if not indices_to_update.empty:
                index_to_update = indices_to_update[0]  # Take the first matching index
                operations_df.at[index_to_update, "status"] = "done"


        ### MARK FOLLOW UP QUADRANTS AS "UNLOCKED"
        for _, row in machined_quadrants_df.iterrows():
            # find the id of the machined quadrant
            machined_quadrant_id = row["id"]
            # look up the product and component of the machined quadrant in planning.xlsx
            machined_quadrant_product = quadrant_types_df[quadrant_types_df["id"] == machined_quadrant_id]["product"].values[0]
            machined_quadrant_component = quadrant_types_df[quadrant_types_df["id"] == machined_quadrant_id]["component"].values[0]

            #get the follow up_id if exists
            row_number = quadrant_types_df[quadrant_types_df["id"] == machined_quadrant_id].index[0]
            # get the id of the next row in quadrant_types_df
            follow_up_quadrant_id = quadrant_types_df.iloc[row_number + 1]["id"]
            follow_up_quadrant_product = quadrant_types_df[quadrant_types_df["id"] == follow_up_quadrant_id]["product"].values[0]
            follow_up_quadrant_component = quadrant_types_df[quadrant_types_df["id"] == follow_up_quadrant_id]["component"].values[0]
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

        assigned_operations_df.to_excel("quadrants.xlsx", index=False)

        print("machined_quadrants_df: ", machined_quadrants_df)
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