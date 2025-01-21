from pathlib import Path #For routing files
from excel_reader import ExcelReader
from pallet_table_creator import PalletTableCreator

############################
# 0 Setup
############################

# Define the main directory paths
project_root_path = Path(__file__).parent.absolute()  # Use __file__ instead of __name__
project_root_str = str(project_root_path)  # Convert the Path object to string

# Define subdirectory paths
resources_directory = project_root_str + '/resources/'
build_directory = project_root_str + '/build/'

# Define specific file paths
forecast_excel_file_path = resources_directory + "Salesforecast Januari 2025.xlsx"
planning_excel_file_path = resources_directory + "planning.xlsx"
excel_file_path_unmerged = resources_directory + "Salesforecast Januari 2025 unmerged.xlsx"

#define classes used in main
excel_reader = ExcelReader(forecast_excel_file_path, planning_excel_file_path)


############################
# 0 Approach
############################

# INLEZEN FORECAST
#forecast_excel_reader.unmerge_and_fill_values(excel_file_path, excel_file_path_unmerged, "forecast 2025")

product_type = "XLS"
product_force = "3"
product_size = "40"
month = "januari"

product_types = ["XLS","XLS","XLS","XLS" ]
product_forces = ["3", "3","3", "3"]
product_sizes = ["40", "60", "80", "120"]
months = ["januari", "januari", "januari", "januari"]

#xls_3_40_count_january = excel_reader.get_product_count(product_type, product_size, product_force, month)
#xls_3_040_quadrants = excel_reader.get_quadrants_df_per_product(product_type, product_size, product_force)

quadrants_df = excel_reader.get_quadrants_df(product_types, product_sizes, product_forces, months)

# maak pallet_table
pallet_table_creator = PalletTableCreator(quadrants_df)
pallet_table_df = pallet_table_creator.create_pallet_table_df_from_quadrants(quadrants_df)
#excel_reader.create_excel_tab_from_df(excel_path= planning_excel_file_path, tab_name = "pallet_table", df = pallet_table_df)



# - doe dit x aantal stuks nodig
# - doe dit voor een lijst van producten en bijbehorende hoeveelheden (die haal je uit forecast)

#excel_reader.get_quadrants_per_product(product)  # geeft een lijst met alle quadranten



# INLEZEN QUADRANTS EXCEL TAB
# GENEREER UNSORTED PALLET TABLE
# - first only XLS_3_040 (jan) (amount required => all bewerkingen x amount required)
# - then all XLS (jan)

# ANALYSE 
# - TOTAL MACHINE TIME
# - TOTAL MANUAL TIME



# TODO: excel readen zoals hij effectief gegeven wordt (nu bepaalde aanpassingen gedaan: datum)
# TODO: excel manueel moeten unmergen... doe dit  met code
# TODO: manier waarop excel reader is geimplementeerd is niet goed... liever niet foreacast en planning als parameter: HAAL BASIS df's uit excel en gebruik die dan veder in ANALYZER
# TODO: tab quadranten: product opsplitsen in product_type, product_size, product_force to align with forecast
# TODO: data type for excel_reader.get_quadrants should be one big dictionary and not lists or even better: list of products
