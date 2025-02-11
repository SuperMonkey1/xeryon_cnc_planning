from simulation_operations_scheduler import SimulationOperationsScheduler


class CNCOperator:
    def __init__(self, name, start_time, end_time, simulation_operation_scheduler: SimulationOperationsScheduler):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.simulation_operation_scheduler = simulation_operation_scheduler

    def determine_next_action(self, minute, needs_to_start_loading_for_night_shift, big_daddy_status_df):
        # is operator working?
        isOperatorWorking = self.start_time <= minute < self.end_time

        # NOT WORKING
        if not isOperatorWorking:
            return "Not working", 1
        
        # LOADING NIGHT BATCH
        elif(needs_to_start_loading_for_night_shift):
            return "loading pallets for the night", 120
        
        # DURING DAY
        else:
            # if pallet is empty, load pallet
            if (big_daddy_status_df["status"] == "empty").any():
                #choose which operation to load, determine time it takes
                operation = self.simulation_operation_scheduler.get_next_operation_to_be_loaded()
                action = "loading operation X"
                duration = operation["loading_time"]
                

                return action, duration

            # unload pallet and evaluate
            return "figuring out what to do", 1



