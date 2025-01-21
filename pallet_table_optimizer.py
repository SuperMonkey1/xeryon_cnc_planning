import pandas as pd
from openpyxl import load_workbook
from quadrant import Quadrant
import openpyxl


class PalletTableOptimizer:
    def __init__(self, pallet_table_df):
        self.pallet_table_df = pallet_table_df
    
    def fill_nights(self):

        # we werken met 3 df's : overblijvende_paletten_df, geordende_paletten_df, stock_bewerkingen_df
        # # overblijvende_paletten_df =  pallet_table_df
        # # geordende_paletten_df = empty
        # # stock_bewerkingen_df = empty

        # START NACHT
        # orden de pallet table van lange freestijd vanboven
        # neem uit overblijvende_paletten_df eerste x paletten die samen minder dan 10u machinetijd kosten
        # # max 5 paletten (verwijder uit oude, steek in nieuwe)
        # # neem enkel uit bewerkings_orde = 1

        # START OCHTEND UNLOADING
        # bereken total unload time van vorige nacht
        # maak lijn unload time: unload eerst de pallet die het minst lang duurt om te unloaden
        # maak lijn load time: load een pallet (zoek een pallet die ...)

        #... TODO


        return self.pallet_table_df
