import pandas as pd
from cnc_operator import CNCOperator
from cnc_machine import CNCMachine
from simulation_operations_scheduler import SimulationOperationsScheduler
from forecast_handler import ForecastHandler
from pathlib import Path #For routing files
import os

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
operations_excel_path = build_directory + "simulator_operations.xlsx"
planning_excel_path = build_directory + "simulator_planning.xlsx"
actions_excel_path = build_directory + "simulator_actions.xlsx"

####################
# Decides
####################
forecast_handler = ForecastHandler()
forecast_handler.add_forecast_element('XLS', '3', '40', 'januari')
forecast_handler.add_forecast_element('XLS', '3', '60', 'januari')
forecast_handler.add_forecast_element('XLS', '3', '80', 'januari')
forecast_handler.add_forecast_element('XLS', '3', '120', 'januari')
forecast_elements_df = forecast_handler.get_forecast_elements_df()

amount_of_pallets_on_big_daddy = 5
amount_of_quadrants_per_pallet_on_big_daddy = 4



####################
# get resources
####################
# get forecast_df 
# get operations_catalog_df


# get simulation planner
simulation_operation_scheduler = SimulationOperationsScheduler()

# calculate all operations (with timings and status) operations_df
if not os.path.exists(operations_excel_path):
    # gent all required operations
    all_required_operations_df = simulation_operation_scheduler.get_all_required_operations_df(forecast_elements_df)    
    operations_status_df = all_required_operations_df
else:
    # Load the operations schedule from operations.xlsx
    operations_status_df = pd.read_excel(operations_excel_path)

# calculate big daddy status
big_daddy = CNCMachine(amount_of_pallets_on_big_daddy, amount_of_quadrants_per_pallet_on_big_daddy)
big_daddy_status_df = big_daddy.get_status_df()

# get operators with working hours
roel = CNCOperator('Roel', 480, 960, simulation_operation_scheduler)
enes = CNCOperator('Enes', 480, 960)

# get machine with #pallets, quadrants
# get planner
####################
# run simulation
####################

minute = 0
alive = True
is_roel_bussy = False
actions_df = pd.DataFrame(columns = ['minute', 'roel_action', 'enes_action'])

while minute < 1440 and alive:

    # OPERATOR ACTIONS
    needs_to_start_loading_for_night_shift = simulation_operation_scheduler.does_operator_needs_to_start_loading_for_night_shift(minute)

    if not is_roel_bussy: 
        roel_action, roel_duration  = roel.determine_next_action(minute, needs_to_start_loading_for_night_shift, big_daddy_status_df)
        is_roel_bussy = True
        # TODO: UPDATE STATES: look at what roel is bussy with and  update the states: "loading"
        # operations.update()
    else:
        print("roel is bussy")
    
    # MACHINE ACTIONS
    # if not is_big_daddy_bussy: 
    # big_daddy.determine_next_action()
    
    
    
    # UPDATE TIME LINE AND ACTIONS_DF
    new_row_actions_df = pd.DataFrame([{'minute': minute, 'roel_action': roel_action}])
    actions_df = pd.concat([actions_df, new_row_actions_df], ignore_index=True)
    minute += 1
    
    roel_duration -= 1
    if roel_duration == 0:
        is_roel_bussy = False
        # TODO: UPDATE STATES: look at what roel was bussy with and now finished to update the states: "loaded"
        # operations.update()

actions_df.to_excel(actions_excel_path, sheet_name="Actions", index=False)



# TODO: implement simulation_planner.does_operator_needs_to_load_for_night_shift