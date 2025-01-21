from pathlib import Path #For routing files


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
resource_a_file = resources_directory + "resource_a.txt"
build_a_file = build_directory + "build_a.txt"

############################
# 0 Approach
############################

# INLEZEN FORECAST
# INLEZEN QUADRANTS EXCEL TAB
# GENEREER UNSORTED PALLET TABLE
# ANALYSE 
# - TOTAL MACHINE TIME
# - TOTAL MANUAL TIME
