from pathlib import Path #For routing files
from excel_handler import ExcelHandler
from operations_scheduler import OperationScheduler
from forecast_handler import ForecastHandler
import pandas as pd
import sys 
import os
import time

############################
# Setup
############################

# Define the main directory paths
project_root_path = Path(__file__).parent.absolute()  # Use __file__ instead of __name__
project_root_str = str(project_root_path)  # Convert the Path object to string

# Resources
resources_directory = project_root_str + '/resources/'
forecast_excel_file_path = resources_directory + "Salesforecast Januari 2025.xlsx"
planning_excel_file_path = resources_directory + "planning.xlsx"

# Builds
build_directory = project_root_str + '/build/'
operations_excel_path = build_directory + "operations.xlsx"

# LOAD RESOURCES
excel_handler = ExcelHandler(forecast_excel_file_path, planning_excel_file_path)
forecast_df = excel_handler.create_df_from_excel(path = forecast_excel_file_path, sheet_name = "forecast 2025")
operations_catalog_df = excel_handler.create_df_from_excel(path = planning_excel_file_path, sheet_name = "operations_catalog")

############################
# INITIATE OPERATIONS TABLE
############################
forecast_handler = ForecastHandler()
forecast_handler.add_forecast_element('XLS', '3', '40', 'januari')
forecast_handler.add_forecast_element('XLS', '3', '60', 'januari')
forecast_handler.add_forecast_element('XLS', '3', '80', 'januari')
forecast_handler.add_forecast_element('XLS', '3', '120', 'januari')
forecast_elements_df = forecast_handler.get_forecast_elements_df() # TODO: get forecats count per product

operations_scheduler = OperationScheduler(operations_catalog_df, forecast_df) #TODO: should get forecast_elements_df instead of forecast_df

if not os.path.exists(operations_excel_path):
    # gent all required operations
    all_required_operations_df = operations_scheduler.get_all_required_operations_df(forecast_elements_df)    
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

# NIGHT SHIFT
operations_df = operations_scheduler.fill_night(operations_df, operations_catalog_df)
operations_df.to_excel(operations_excel_path, index=False)
print("Operations scheduled. Please evaluate the planned operations and afterwards Press enter to continue.")
input()

#MORNING SHIFT
operations_df = pd.read_excel(operations_excel_path)
operations_df = operations_scheduler.fill_day(operations_df, operations_catalog_df)
operations_df.to_excel(operations_excel_path, index=False)



# TODO: excel readen zoals hij effectief gegeven wordt (nu bepaalde aanpassingen gedaan: datum)
# TODO: excel manueel moeten unmergen... doe dit  met code
# TODO: tab quadranten: product opsplitsen in product_type, product_size, product_force to align with forecast
# TODO: data type for excel_reader.get_quadrants should be one big dictionary and not lists or even better: list of products ["XLS_3_040", "XLS_3_060"]
# TODO: implement multiple possible follow up operations (? is dit nodig?)
# TODO: keuze quadranten verbeteren (of aan operator laten?)
# TODO: als een operatie failes, dan moeten ook alle voorgaande operaties op de component gereset worden
# TODO: volgende maand starten als eerste niet meer effcient machine en operator vult