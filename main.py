from pathlib import Path #For routing files
from excel_handler import ExcelHandler
from pallet_table_creator import PalletTableCreator
from operations_scheduler import OperationScheduler
import pandas as pd
import sys 
import os


############################
# Setup
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
operations_excel_path = build_directory + "operations.xlsx"

# LOAD RESOURCES
excel_handler = ExcelHandler(forecast_excel_file_path, planning_excel_file_path)
forecast_df = excel_handler.create_df_from_excel(path = forecast_excel_file_path, sheet_name = "forecast 2025")
operations_catalog_df = excel_handler.create_df_from_excel(path = planning_excel_file_path, sheet_name = "operations_catalog")

############################
# INITIATE OPERATIONS TABLE
############################
# Which products need to be made and which forecast in months
product_types = ["XLS","XLS","XLS","XLS" ]
product_forces = ["3", "3","3", "3"]
product_sizes = ["40", "60", "80", "120"]
months = ["januari", "januari", "januari", "januari"]

operations_scheduler = OperationScheduler(operations_catalog_df, forecast_df)

if not os.path.exists(operations_excel_path):
    # gent all required operations
    all_required_operations_df = operations_scheduler.get_all_required_operations_df(product_types, product_sizes, product_forces, months)
    operations_df = all_required_operations_df
else:
    # Load the operations schedule from operations.xlsx
    operations_df = pd.read_excel(operations_excel_path)

############################
# SCEDULE OPERATIONS
############################

if os.path.exists(operations_excel_path):
    # Load the DataFrame from the Excel file
    operations_df = pd.read_excel(operations_excel_path)

operations_df = operations_scheduler.fill_night(operations_df, operations_catalog_df)
operations_df.to_excel(operations_excel_path, index=False)


# TODO: excel readen zoals hij effectief gegeven wordt (nu bepaalde aanpassingen gedaan: datum)
# TODO: excel manueel moeten unmergen... doe dit  met code
# TODO: tab quadranten: product opsplitsen in product_type, product_size, product_force to align with forecast
# TODO: data type for excel_reader.get_quadrants should be one big dictionary and not lists or even better: list of products ["XLS_3_040", "XLS_3_060"]