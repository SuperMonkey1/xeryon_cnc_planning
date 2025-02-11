import pandas as pd

class CNCMachine:
    def __init__(self, amount_of_pallets, amount_of_quadrants_per_pallet):
        self.amount_of_pallets = amount_of_pallets
        self.amount_quadrants_per_pallet = amount_of_quadrants_per_pallet
        self.initiate_status_df()

    def initiate_status_df(self):
        self.status_df = pd.DataFrame(columns = ['pallet', 'quadrant', 'status'])
        for pallet in range(self.amount_of_pallets):
            for quadrant in range(self.amount_quadrants_per_pallet):
                new_row = pd.DataFrame([{'pallet': pallet, 'quadrant': quadrant, 'status': 'empty'}])
                self.status_df = pd.concat([self.status_df, new_row], ignore_index=True)
    
    def get_status_df(self):
        return self.status_df


