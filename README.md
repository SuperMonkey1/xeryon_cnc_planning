# Xeryon CNC Operation Planning Tool

A Python application for planning and scheduling CNC manufacturing operations based on sales forecasts and operation catalogs.

## Setup and Installation

### Prerequisites
- Python 3.6+ installed on your system
- Git (optional, for cloning the repository)

### Installation Steps

1. **Clone or download the repository:**
   ```bash
   git clone https://github.com/yourusername/xeryon_cnc_planning.git
   ```
   Alternatively, download and extract the ZIP file from GitHub.

2. **Create and activate a virtual environment (recommended):**
   ```bash
   # Navigate to the project directory
   cd xeryon_cnc_planning
   
   # Create a virtual environment
   python -m venv env
   
   # Activate the virtual environment
   # On Windows
   .\env\Scripts\activate
   # On macOS/Linux
   source env/bin/activate
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```
   
   The requirements.txt file includes the following dependencies:
   - pandas - For data manipulation and analysis
   - openpyxl - For Excel file handling
   - streamlit - For the web application interface
   - numpy - For numerical operations

4. **Prepare the resource files:**
   - Create a `resources` directory in the `xeryon_cnc_planning` subdirectory if it doesn't exist
   - Place your forecast Excel file (named `Salesforecast Januari 2025.xlsx`) in the resources directory
   - Place your operations catalog file (named `planning.xlsx`) in the resources directory
   
   Both Excel files should have the correct sheet names:
   - `Salesforecast Januari 2025.xlsx` should have a sheet named "forecast 2025"
   - `planning.xlsx` should have a sheet named "operations_catalog"

5. **Create a build directory:**
   ```bash
   mkdir -p xeryon_cnc_planning/build
   ```
   This is where the generated operation schedules and pallet tables will be stored.

### Running the Application

1. **Make sure your virtual environment is activated** (if you're using one)

2. **Navigate to the project's application directory:**
   ```bash
   cd xeryon_cnc_planning
   ```

3. **Start the Streamlit application:**
   ```bash
   streamlit run xeryon_cnc_planning/app.py
   ```

4. **Access the web interface:**
   - The application will automatically open in your default web browser
   - If it doesn't open automatically, you can access it at http://localhost:8501

## Overview

This tool helps optimize the CNC machining process at Xeryon by:

1. Importing product forecasts from Excel files
2. Scheduling operations for different shifts (day/night)
3. Tracking operation status (planned, done, unlocked, failed)
4. Assigning operations to specific pallets and quadrants
5. Generating operation schedules as Excel files

## Features

- **Shift-specific planning**: Different scheduling strategies for day and night shifts
  - Night shift: Prioritizes longer machining operations
  - Day shift: Prioritizes shorter machining operations
- **Operation tracking**: Monitors the status of operations through their lifecycle
- **Dependency management**: Automatically unlocks follow-up operations when prerequisite operations are completed
- **Resource allocation**: Assigns operations to specific pallets and quadrants
- **Historical tracking**: Saves dated operation files for record-keeping

## Project Structure

- `main.py`: Entry point for the application
- `excel_handler.py`: Handles Excel file reading and writing
- `operations_scheduler.py`: Core scheduling logic for operations
- `forecast_handler.py`: Manages sales forecast data
- `resources/`: Directory for input Excel files
  - `Salesforecast Januari 2025.xlsx`: Contains product demand forecasts
  - `planning.xlsx`: Contains operation catalog with timing information
- `build/`: Output directory for generated operation schedules

## How to Use

1. Ensure the required Excel files are in the `resources/` directory:
   - `Salesforecast Januari 2025.xlsx` with a "forecast 2025" sheet
   - `planning.xlsx` with an "operations_catalog" sheet

2. Run the Streamlit app:
   ```bash
   # From the project root directory
   streamlit run xeryon_cnc_planning/app.py
   ```

3. A web browser will open with the XERYON CNC Scheduler interface.

## Using the Streamlit Interface

The Streamlit interface provides a step-by-step workflow for CNC planning:

### Step 1: Configure Shift Parameters
1. Select the shift type (Night Shift or Day Shift)
2. For Day Shift, specify the maximum pallet table time (default: 240 minutes)

### Step 2: Generate Operations Schedule
1. Click the "Generate Operations Schedule" button
2. The system will run the scheduling algorithm based on your shift parameters
3. A success message will appear when the schedule is created

### Step 3: Generate Pallet Table
1. After generating the operations schedule, click "Generate Pallet Table"
2. The system will create a pallet table file (.P extension) in the build directory
3. A preview of the pallet table will be displayed

### Step 4: Review the Operations
1. Review the generated operations in the data table
2. Use the "Show only planned operations" checkbox to filter the view
3. Update operation statuses (e.g., change from "planned" to "done" or "failed")
4. Click "Save Changes to Operations Schedule" to save your updates
5. Use "Mark All as Done" to quickly update all planned operations

### Step 5: Finish Current Session
1. After saving changes, click "Done - Start New Session" to reset the application state
2. This preserves your generated files but clears the current session variables

### File Downloads
On the sidebar, you can:
- View the status of operations and pallet table files
- Download the operations Excel file
- Download any of the generated pallet table files (sorted by creation time)

## Configuration

The main scheduling parameters can be adjusted in the code:
- Night shift duration: 840 minutes (14 hours)
- Day shift max pallet table time: 240 minutes (4 hours) 
- Maximum quadrants per run: 20

## Detailed Night and Day Shift Planning Logic

### Night Shift Planning

The night shift planning strategy (`fill_night` method) is designed to maximize machine utilization during overnight hours when operator intervention is minimal:

1. **Duration**: Night shift has a longer duration (840 minutes/14 hours) compared to day shift
2. **Operation Prioritization**: 
   - Operations are sorted by machine time in **descending order** (longest first)
   - This prioritizes longer-running jobs that can run unsupervised overnight
3. **Scheduling Algorithm**:
   - The scheduler first attempts to add operations with different IDs (product types)
   - It allows up to 2 operations of the same ID if needed, considering fixture limitations
   - Operations are added until either the total machining time reaches the night shift duration (840 min) or the maximum number of quadrants (20) is reached
4. **Implementation**: When the night shift boolean flag is set to `True` in the main function, the `fill_night` method is called

### Day Shift Planning

The day shift planning strategy (`fill_day` method) is optimized for operator efficiency and flexibility:

1. **Duration**: Day shift has a shorter pallet table time (240 minutes/4 hours)
2. **Operation Prioritization**: 
   - Operations are sorted by machine time in **ascending order** (shortest first)
   - This allows the operator to complete more operations during their shift
   - Shorter operations also allow for more frequent quality checks and adjustments
3. **Scheduling Algorithm**:
   - Similar to night shift, it first adds operations with unique IDs
   - It allows up to 2 operations of the same ID if needed
   - Operations are added until either the total machining time reaches the day shift limit (240 min) or the maximum quadrants (20) is reached
4. **Implementation**: When the night shift boolean flag is set to `False` in the main function, the `fill_day` method is called

### Common Elements in Both Strategies

1. **Failed Operation Handling**: Both strategies reset the status of failed operations so they can be rescheduled
2. **Follow-up Operation Unlocking**: Both strategies check completed operations and unlock their dependent follow-up operations
3. **Quadrant Assignment**: After scheduling, both strategies assign specific pallets (1-5) and quadrants (A-D) to planned operations
4. **Status Tracking**: Both keep track of operation statuses (done, planned, unlocked, etc.) and preserve timestamps

The key difference between night and day scheduling is the operation prioritization strategy (longest-first vs. shortest-first) and the duration constraints.

## Operation Workflow

1. First-order operations (bewerkings_orde = 1) are initially available
2. Operations are scheduled based on machine time and product variety
3. When an operation is completed (status = "done"), follow-up operations become unlocked
4. Failed operations can be reset and rescheduled

## Development TODO List

As noted in the code comments, there are several planned improvements:
- Improve Excel reading to handle the format as provided (dates, merged cells)
- Split product field into product_type, product_size, product_force components
- Better quadrant selection logic
- Reset all previous operations when an operation fails
- Improved handling for follow-up operations
- Planning for the next month when the current month is complete

## Requirements

- Python 3.6+
- pandas
- openpyxl
- math
- sys
- os
- datetime
