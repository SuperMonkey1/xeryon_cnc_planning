from pathlib import Path #For routing files
from excel_handler import ExcelHandler
from operations_scheduler import OperationScheduler
from forecast_handler import ForecastHandler
import pandas as pd
import sys 
import os
import time
from planner import Planner
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
planning_excel_path = build_directory + "planning.xlsx"

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
# INITIATE PLANNER
############################

planner = Planner()

############################
# SCHEDULE OPERATIONS
############################
total_time_of_day_shift = 8 * 60 
total_remaining_time_of_day_shift = total_time_of_day_shift
max_pallet_table_time_during_day = 120
has_finished = False
total_remaining_time_of_day_shift = 8 * 60 

# LONG TERM PLANNING (if all machiening goes well, but machine loading and unloading not in parallel with machineing)

#check if there are still rows in the operations_df where status is not "done"
if  operations_df[operations_df["status"] != "done"].empty:
    has_finished = True

while not has_finished:

    time.sleep(1) #make sure the operations_excel_path is refreshed
    if os.path.exists(operations_excel_path):
        # Load the DataFrame from the Excel file
        operations_df = pd.read_excel(operations_excel_path)
        
    night_copy_of_operations_df = operations_df.copy()

    operations_day_df, total_loading_time_day, total_machining_time_day ,total_unloading_time_day = operations_scheduler.fill_day(operations_df, operations_catalog_df, max_pallet_table_time_during_day)
    operations_night_df, total_loading_time_night, total_machining_time_night ,total_unloading_time_night = operations_scheduler.fill_night(night_copy_of_operations_df, operations_catalog_df)

    total_remaining_time_of_day_shift = total_remaining_time_of_day_shift - total_loading_time_day - total_machining_time_day - total_unloading_time_day - total_loading_time_night
    print("Total remaining time of day shift: ", total_remaining_time_of_day_shift)

    if total_remaining_time_of_day_shift < 0:
        
        # ADD NIGHT SHIFT
        print("Planning night shift")
        operations_df = operations_night_df
        total_remaining_time_of_day_shift = total_time_of_day_shift
        loading_time = total_loading_time_night
        machining_time = total_machining_time_night
        unloading_time = total_unloading_time_night

        planning_df = planner.update_planning_df(
            loading_time, 
            machining_time, 
            unloading_time,
            is_night_shift=True
        )

    else:
        # ADD DAY SHIFT
        operations_df = operations_day_df
        loading_time = total_loading_time_day
        machining_time = total_machining_time_day
        unloading_time = total_unloading_time_day

        planning_df = planner.update_planning_df(
            loading_time, 
            machining_time, 
            unloading_time,
            is_night_shift=False
        )
    

    # save to excel
    operations_df.to_excel(operations_excel_path, index=False)
    planning_df.to_excel(planning_excel_path, index=False)

    # print("Operations scheduled. Please evaluate the planned operations and afterwards Press enter to continue.")
    # input()

    if  operations_df[operations_df["status"] != "done"].empty:
        has_finished = True
    
    sys.exit()

print("next batch calculated")
