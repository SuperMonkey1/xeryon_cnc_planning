from pathlib import Path #For routing files
from excel_handler import ExcelHandler
from pallet_table_creator import PalletTableCreator
from pallet_table_optimizer import PalletTableOptimizer
import pandas as pd
import sys 
import os


############################
# 0 Setup
############################

# Define the main directory paths
project_root_path = Path(__file__).parent.absolute()  # Use __file__ instead of __name__
project_root_str = str(project_root_path)  # Convert the Path object to string

# Define subdirectory paths
resources_directory = project_root_str + '/resources/'
build_directory = project_root_str + '/build/'

# Define specific file paths
forecast_excel_file_path = resources_directory + "Salesforecast Januari 2025.xlsx"
planning_excel_file_path = resources_directory + "planning.xlsx"
excel_file_path_unmerged = resources_directory + "Salesforecast Januari 2025 unmerged.xlsx"
pallet_table_excel_file_path = build_directory + "unordered_pallet_table.xlsx"

#define classes used in main
excel_handler = ExcelHandler(forecast_excel_file_path, planning_excel_file_path)
forecast_df = excel_handler.create_df_from_excel(path = forecast_excel_file_path, sheet_name = "forecast 2025")
quadrant_types_df = excel_handler.create_df_from_excel(path = planning_excel_file_path, sheet_name = "quadrants")


############################
# 0 Approach
############################

# GENEREER UNSORTED PALLET TABLE

# Which products need to be made and which forecast in months
product_types = ["XLS","XLS","XLS","XLS" ]
product_forces = ["3", "3","3", "3"]
product_sizes = ["40", "60", "80", "120"]
months = ["januari", "januari", "januari", "januari"]

pallet_table_creator = PalletTableCreator(quadrant_types_df, forecast_df)
unordered_pallet_table_df = pallet_table_creator.create_unordered_pallet_table_df_from_quadrants(product_types, product_sizes, product_forces, months)
excel_handler.create_excel_tab_from_df(excel_path= pallet_table_excel_file_path, sheet = "unordered_pallet_table", df = unordered_pallet_table_df)
operations_df = unordered_pallet_table_df

# ANALYSE (pallet_table_df)
# - implement night shift
pallet_table_optimizer = PalletTableOptimizer()

quadrants_excel_path = "quadrants.xlsx"

if os.path.exists(quadrants_excel_path):
    # Load the DataFrame from the Excel file
    operations_df = pd.read_excel(quadrants_excel_path)

assigned_opperations_df= pallet_table_optimizer.fill_night(operations_df = operations_df, quadrant_types_df = quadrant_types_df)

# - TOTAL MACHINE TIME

# - TOTAL MANUAL TIME

# Paletten tabel opsplitsen: eentje voor de nacht en eentje (?) voor de dag



# TODO: excel readen zoals hij effectief gegeven wordt (nu bepaalde aanpassingen gedaan: datum)
# TODO: excel manueel moeten unmergen... doe dit  met code
# TODO: tab quadranten: product opsplitsen in product_type, product_size, product_force to align with forecast
# TODO: data type for excel_reader.get_quadrants should be one big dictionary and not lists or even better: list of products ["XLS_3_040", "XLS_3_060"]

#print(f"unique_ids: ${unique_ids}")
