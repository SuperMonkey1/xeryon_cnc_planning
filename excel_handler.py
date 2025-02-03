import pandas as pd

class ExcelHandler:
    def __init__(self, forecast_excel_file_path,planning_excel_file_path,  sheet_names_list = []):
        self.forecast_excel_file_path = forecast_excel_file_path
        self.planning_excel_file_path = planning_excel_file_path
        self.sheet_names_list = sheet_names_list

        # project specific
        self.forecast_df = self.create_df_from_excel(path = self.forecast_excel_file_path, sheet_name = "forecast 2025")
        self.quadrants_df = self.create_df_from_excel(path = self.planning_excel_file_path, sheet_name = "operations_catalog")

    # GENERAL METHODS 
    def create_df_from_excel(self, path,sheet_name):     #returns a dictionary with all the info from the info sheet
        excel_df = pd.read_excel(path, sheet_name=sheet_name, header=0, dtype=str)
        return excel_df
    
    def create_excel_tab_from_df(self, excel_path, sheet, df):
        print(type(df))
        if not isinstance(df, pd.DataFrame):
            raise ValueError("The provided df is not a pandas DataFrame")

        # Ensure specified columns are numerical
        numerical_columns = ['loading_time', 'machine_time', 'unloading_time']
        for col in numerical_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    raise ValueError(f"Error converting column {col} to numeric: {e}")

        # Save DataFrame to Excel
        df.to_excel(excel_path, sheet_name=sheet)
