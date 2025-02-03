import pandas as pd

class ForecastHandler:
    def __init__(self):
        
        self.forecast_elements_df = pd.DataFrame(columns=[
            'product_type',
            'product_force',
            'product_size',
            'month'
        ])


    def add_forecast_element(self, product_type, product_force, product_size, month):
        """
        Add a single forecast element to the DataFrame
        """
        new_element = pd.DataFrame({
            'product_type': [product_type],
            'product_force': [product_force],
            'product_size': [product_size],
            'month': [month]
        })
        self.forecast_elements_df = pd.concat([self.forecast_elements_df, new_element], ignore_index=True)

    def add_multiple_elements(self, elements_df):
        """
        Add multiple forecast elements from a DataFrame
        elements_df: DataFrame containing forecast elements
        """
        self.forecast_elements_df = pd.concat([self.forecast_elements_df, elements_df], ignore_index=True)

    def get_forecast_elements_df(self):
        """
        Return the forecast elements DataFrame with standardized product identifiers
        """
        result_df = self.forecast_elements_df.copy()
        result_df['product_id'] = result_df.apply(
            lambda row: f"{row['product_type']}_{row['product_force']}_{row['product_size'].zfill(3)}",
            axis=1
        )
        return result_df