from pathlib import Path #For routing files
from excel_handler import ExcelHandler
from operations_scheduler import OperationScheduler
from forecast_handler import ForecastHandler
import pandas as pd
import sys 
import os
import time
import datetime

is_type_of_shift_night = True
max_pallet_table_time_during_day: 240

def get_new_filename(base_path, date_str, prefix="operations", extension=".xlsx"):
    """
    Generate a unique filename with a date prefix and incremental index.
    Similar to the function in main_generate_pallet_table.py
    """
    index = 1
    while True:
        new_filename = f"{date_str}_{index}_{prefix}{extension}"
        if not (base_path / new_filename).exists():
            return new_filename
        index += 1

def main(is_type_of_shift_night: True, max_pallet_table_time_during_day: 240):

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
    build_directory_path = Path(build_directory)
    
    # Get current date in YYYY_MM_DD format for filename
    today = datetime.datetime.now().strftime("%Y_%m_%d")
    
    # Standard operations path (for compatibility with other scripts that expect this filename)
    standard_operations_excel_path = build_directory + "operations.xlsx"
    
    # New operations path with date and index
    new_filename = get_new_filename(build_directory_path, today)
    operations_excel_path = build_directory + new_filename
    
    print(f"Operations will be saved to: {operations_excel_path}")

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

    # Check if standard operations file exists to use as a base
    if not os.path.exists(standard_operations_excel_path):
        # Generate all required operations
        all_required_operations_df = operations_scheduler.get_all_required_operations_df(forecast_elements_df)    
        operations_df = all_required_operations_df
    else:
        # Load the operations schedule from the standard operations.xlsx
        operations_df = pd.read_excel(standard_operations_excel_path)

    ############################
    # SCHEDULE OPERATIONS
    ############################

    # NIGHT SHIFT
    if is_type_of_shift_night:
        print("Calculated night shift")
        assigned_operations_df, total_loading_time, total_machining_time, total_unloading_time = operations_scheduler.fill_night(operations_df, operations_catalog_df)
    # MORNING SHIFT
    else:
        print("Calculated day shift")
        assigned_operations_df, total_loading_time, total_machining_time, total_unloading_time = operations_scheduler.fill_day(operations_df, operations_catalog_df, max_pallet_table_time_during_day)

    # Save to the new dated operations file
    assigned_operations_df.to_excel(operations_excel_path, index=False)
    
    # Also save to the standard operations.xlsx path for compatibility with other scripts
    # that expect the file to be at this location
    assigned_operations_df.to_excel(standard_operations_excel_path, index=False)
    
    print(f"Operations saved to {operations_excel_path} and {standard_operations_excel_path}")
    
    return operations_excel_path

if __name__ == "__main__":
    output_path = main(is_type_of_shift_night, max_pallet_table_time_during_day)
    print(f"Operations schedule generated at: {output_path}")


# TODO: excel readen zoals hij effectief gegeven wordt (nu bepaalde aanpassingen gedaan: datum)
# TODO: excel manueel moeten unmergen... doe dit  met code
# TODO: tab quadranten: product opsplitsen in product_type, product_size, product_force to align with forecast
# TODO: data type for excel_reader.get_quadrants should be one big dictionary and not lists or even better: list of products ["XLS_3_040", "XLS_3_060"]
# TODO: implement multiple possible follow up operations (? is dit nodig?)
# TODO: keuze quadranten verbeteren (of aan operator laten?)
# TODO: als een operatie failes, dan moeten ook alle voorgaande operaties op de component gereset worden
# TODO: volgende maand starten als eerste niet meer effcient machine en operator vult