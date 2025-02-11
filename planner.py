import pandas as pd
from openpyxl import load_workbook
import math
import sys

class Planner:
    def __init__(self):
        pass

    def update_planning_df(self, loading_time, machining_time, unloading_time, is_night_shift=False):
        """
        Updates the planning DataFrame with shift statistics and adds summary rows before datum changes.
        """
        # Initialize planning_df if it doesn't exist as class attribute
        if not hasattr(self, 'planning_df'):
            self.planning_df = pd.DataFrame(columns=[
                'datum', 'shift_type', 'operation_type', 'duration'
            ])
            self.current_datum = 0
            self.last_shift_type = None

        shift_type = 'night' if is_night_shift else 'day'
        
        # For night shifts, only add loading and machining rows
        if is_night_shift:
            new_rows = [
                {
                    'datum': self.current_datum,
                    'shift_type': 'night',
                    'operation_type': 'loading',
                    'duration': loading_time
                },
                {
                    'datum': self.current_datum,
                    'shift_type': 'night',
                    'operation_type': 'machining',
                    'duration': machining_time
                }
            ]
        else:
            # For day shift, increment datum if coming from night shift
            if self.last_shift_type == 'night':
                # Before incrementing datum, add summary row for previous datum
                if not self.planning_df.empty:
                    prev_datum_data = self.planning_df[self.planning_df['datum'] == self.current_datum]
                    operator_time = prev_datum_data[prev_datum_data['operation_type'].isin(['loading', 'unloading'])]['duration'].sum()
                    machine_time = prev_datum_data[prev_datum_data['operation_type'] == 'machining']['duration'].sum()
                    
                    summary_row = pd.DataFrame([{
                        'datum': self.current_datum,
                        'shift_type': 'summary',
                        'operation_type': 'total',
                        'operator_time': operator_time,
                        'machine_time': machine_time
                    }])
                    
                    self.planning_df = pd.concat([
                        self.planning_df, 
                        summary_row
                    ], ignore_index=True)
                
                self.current_datum += 1
                
            # For day shift, add all three operations
            new_rows = [
                {
                    'datum': self.current_datum,
                    'shift_type': 'day',
                    'operation_type': 'loading',
                    'duration': loading_time
                },
                {
                    'datum': self.current_datum,
                    'shift_type': 'day',
                    'operation_type': 'machining',
                    'duration': machining_time
                },
                {
                    'datum': self.current_datum,
                    'shift_type': 'day',
                    'operation_type': 'unloading',
                    'duration': unloading_time
                }
            ]
            
            # If this is a day shift and previous shift was night, add the night's unloading
            if self.last_shift_type == 'night':
                night_unloading = {
                    'datum': self.current_datum,
                    'shift_type': 'day',
                    'operation_type': 'unloading',
                    'duration': self.last_night_unloading_time if hasattr(self, 'last_night_unloading_time') else 0
                }
                new_rows.insert(0, night_unloading)

        # Store unloading time if this is a night shift for use in next day shift
        if is_night_shift:
            self.last_night_unloading_time = unloading_time

        # Add the new rows to the planning DataFrame
        new_rows_df = pd.DataFrame(new_rows)
        
        # Ensure all columns exist in both DataFrames
        all_columns = set(list(self.planning_df.columns) + list(new_rows_df.columns))
        for col in all_columns:
            if col not in self.planning_df.columns:
                self.planning_df[col] = None
            if col not in new_rows_df.columns:
                new_rows_df[col] = None
                
        self.planning_df = pd.concat([
            self.planning_df, 
            new_rows_df
        ], ignore_index=True)

        # Update last shift type
        self.last_shift_type = shift_type

        return self.planning_df
    
    def update_planning_df_old(self, loading_time, machining_time, unloading_time, is_night_shift=False):

        # Initialize planning_df if it doesn't exist as class attribute
        if not hasattr(self, 'planning_df'):
            self.planning_df = pd.DataFrame(columns=[
                'datum', 'shift_type', 'operation_type', 'duration'
            ])
            self.current_datum = 0
            self.last_shift_type = None

        shift_type = 'night' if is_night_shift else 'day'
        
        # For night shift, only add loading and machining rows
        if is_night_shift:
            new_rows = [
                {
                    'datum': self.current_datum,
                    'shift_type': 'night',
                    'operation_type': 'loading',
                    'duration': loading_time
                },
                {
                    'datum': self.current_datum,
                    'shift_type': 'night',
                    'operation_type': 'machining',
                    'duration': machining_time
                }
            ]
        else:
            # For day shift, increment datum if coming from night shift
            if self.last_shift_type == 'night':
                self.current_datum += 1
                
            # For day shift, add all three operations
            new_rows = [
                {
                    'datum': self.current_datum,
                    'shift_type': 'day',
                    'operation_type': 'loading',
                    'duration': loading_time
                },
                {
                    'datum': self.current_datum,
                    'shift_type': 'day',
                    'operation_type': 'machining',
                    'duration': machining_time
                },
                {
                    'datum': self.current_datum,
                    'shift_type': 'day',
                    'operation_type': 'unloading',
                    'duration': unloading_time
                }
            ]
            
            # If this is a day shift and previous shift was night, add the night's unloading
            # as part of this day shift (before the day shift operations)
            if self.last_shift_type == 'night':
                night_unloading = {
                    'datum': self.current_datum,
                    'shift_type': 'day',
                    'operation_type': 'unloading',
                    'duration': self.last_night_unloading_time if hasattr(self, 'last_night_unloading_time') else 0
                }
                new_rows.insert(0, night_unloading)

        # Store unloading time if this is a night shift for use in next day shift
        if is_night_shift:
            self.last_night_unloading_time = unloading_time

        # Add the new rows to the planning DataFrame
        self.planning_df = pd.concat([
            self.planning_df, 
            pd.DataFrame(new_rows)
        ], ignore_index=True)

        # Update last shift type
        self.last_shift_type = shift_type

        return self.planning_df

    
        # Initialize planning_df if it doesn't exist as class attribute
        if not hasattr(self, 'planning_df'):
            self.planning_df = pd.DataFrame(columns=[
                'datum', 'shift_type', 'operation_type', 'duration'
            ])
            self.current_datum = 0
            self.last_shift_type = None

        # Increment datum if transitioning from night to day shift
        if self.last_shift_type == 'night' and not is_night_shift:
            self.current_datum += 1

        shift_type = 'night' if is_night_shift else 'day'

        # Create three new rows for the planning DataFrame
        new_rows = [
            {
                'datum': self.current_datum,
                'shift_type': shift_type,
                'operation_type': 'loading',
                'duration': loading_time
            },
            {
                'datum': self.current_datum,
                'shift_type': shift_type,
                'operation_type': 'machining',
                'duration': machining_time
            },
            {
                'datum': self.current_datum,
                'shift_type': shift_type,
                'operation_type': 'unloading',
                'duration': unloading_time
            }
        ]

        # Add the new rows to the planning DataFrame
        self.planning_df = pd.concat([
            self.planning_df, 
            pd.DataFrame(new_rows)
        ], ignore_index=True)

        # Update last shift type
        self.last_shift_type = shift_type

        return self.planning_df

        # Initialize planning_df if it doesn't exist as class attribute
        if not hasattr(self, 'planning_df'):
            print("creating planning df")
            self.planning_df = pd.DataFrame(columns=[
                'datum', 'shift_type', 'loading_time', 
                'machining_time', 'unloading_time'
            ])
            self.current_datum = 0
            self.last_shift_type = None

        # Increment datum if transitioning from night to day shift
        if self.last_shift_type == 'night' and not is_night_shift:
            self.current_datum += 1

        # Create new row for the planning DataFrame 
        new_row = {
            'datum': self.current_datum,
            'shift_type': 'night' if is_night_shift else 'day',
            'loading_time': loading_time,
            'machining_time': machining_time,
            'unloading_time': unloading_time
        }

        # Add the new row to the planning DataFrame
        self.planning_df = pd.concat([
            self.planning_df, 
            pd.DataFrame([new_row])
        ], ignore_index=True)

        # Update last shift type
        self.last_shift_type = 'night' if is_night_shift else 'day'

        return self.planning_df