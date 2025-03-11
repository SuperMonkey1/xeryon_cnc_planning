import streamlit as st
from pathlib import Path
import pandas as pd
import subprocess
import os
import sys
import time
import importlib.util
import traceback
import glob

def run_python_script(script_path, capture_output=True):
    """
    Run a Python script using subprocess.
    Returns True if successful, False otherwise.
    """
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=capture_output,
            text=True,
            check=True
        )
        return True, result.stdout if capture_output else ""
    except subprocess.CalledProcessError as e:
        error_message = f"Error running {script_path}: {e}\n"
        if capture_output:
            error_message += f"STDOUT: {e.stdout}\nSTDERR: {e.stderr}"
        return False, error_message
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def import_and_run_script(script_path):
    """
    Import and run a Python script directly.
    Returns True if successful, False otherwise.
    """
    try:
        script_name = Path(script_path).stem
        spec = importlib.util.spec_from_file_location(script_name, script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Execute main function if it exists
        if hasattr(module, 'main'):
            output_path = module.main()
            return True, f"Script executed successfully. Output: {output_path}"
        
        return True, "Script executed successfully"
    except Exception as e:
        error_details = traceback.format_exc()
        return False, f"Error running {script_path}: {str(e)}\n\n{error_details}"

def main():
    st.set_page_config(page_title="XERYON CNC Scheduler", layout="wide")
    
    # Initialize session state variables if needed
    if 'operations_generated' not in st.session_state:
        st.session_state.operations_generated = False
    if 'pallet_table_generated' not in st.session_state:
        st.session_state.pallet_table_generated = False
    if 'operations_data' not in st.session_state:
        st.session_state.operations_data = None
    if 'edited_statuses' not in st.session_state:
        st.session_state.edited_statuses = {}
    if 'session_active' not in st.session_state:
        st.session_state.session_active = True
    # To store modified data after Mark All as Done
    if 'modified_data' not in st.session_state:
        st.session_state.modified_data = None
    # To store the most recently generated pallet table path
    if 'latest_pallet_table_path' not in st.session_state:
        st.session_state.latest_pallet_table_path = None
    # Track if changes have been saved
    if 'changes_saved' not in st.session_state:
        st.session_state.changes_saved = False
    
    st.title("XERYON CNC Scheduler 🏭")
    
    # Define paths
    project_root = Path(__file__).parent.absolute()
    build_dir = project_root / 'build'
    build_dir.mkdir(exist_ok=True)
    
    operations_path = build_dir / 'operations.xlsx'
    standard_pallet_table_path = build_dir / 'PALLET_TABLE.P'
    
    # Step 1: Select shift type and parameters
    st.header("Step 1: Configure Shift Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        shift_type = st.radio("Select Shift Type:", ["Night Shift", "Day Shift"])
        is_night_shift = shift_type == "Night Shift"
    
    with col2:
        max_pallet_time = 240  # Default value
        if not is_night_shift:
            max_pallet_time = st.number_input(
                "Maximum Pallet Table Time (minutes):",
                min_value=60,
                max_value=480,
                value=240,
                step=10
            )
    
    # Step 2: Generate Operations Schedule
    st.header("Step 2: Generate Operations Schedule")
    
    if st.button("Generate Operations Schedule"):
        with st.spinner("Running main.py to generate operations schedule..."):
            try:
                # Import the main module directly
                sys.path.insert(0, str(project_root))
                import main
                
                # Call the main function directly with user parameters
                main.main(is_type_of_shift_night=is_night_shift, max_pallet_table_time_during_day=max_pallet_time)
                
                # Check if operations file was created
                if os.path.exists(operations_path):
                    st.success("✅ Operations schedule generated successfully!")
                    st.session_state.operations_generated = True
                    # Load the newly generated data
                    st.session_state.operations_data = pd.read_excel(operations_path)
                    # Reset modified data
                    st.session_state.modified_data = None
                    # Reset changes_saved flag
                    st.session_state.changes_saved = False
                else:
                    st.error("❌ operations.xlsx file was not created.")
                    st.session_state.operations_generated = False
                    
            except Exception as e:
                error_details = traceback.format_exc()
                st.error(f"❌ Error running main.py: {str(e)}\n\n{error_details}")
                st.session_state.operations_generated = False
    
    # Step 3: Generate Pallet Table
    st.header("Step 3: Generate Pallet Table")
    
    operations_exist = os.path.exists(operations_path)
    pallet_table_button_enabled = operations_exist
    
    if not operations_exist:
        st.info("⚠️ Please generate operations schedule first before creating the pallet table")
    
    if st.button("Generate Pallet Table", disabled=not pallet_table_button_enabled):
        with st.spinner("Generating pallet table..."):
            # Run main_generate_pallet_table.py
            success, output = import_and_run_script(str(project_root / 'main_generate_pallet_table.py'))
            
            if success:
                # Find all pallet table files in the build directory
                pallet_files = list(build_dir.glob("*.P"))
                
                if pallet_files:
                    # Get the most recent pallet table file by creation time
                    latest_pallet_file = max(pallet_files, key=os.path.getctime)
                    st.session_state.latest_pallet_table_path = latest_pallet_file
                    
                    st.success(f"✅ Pallet table generated successfully: {latest_pallet_file.name}")
                    st.session_state.pallet_table_generated = True
                    
                    # Read and display the first three columns of the pallet table
                    try:
                        with open(latest_pallet_file, 'r') as file:
                            pallet_data = file.readlines()
                        
                        # Process the first few lines to extract column data
                        st.subheader("Pallet Table Preview")
                        
                        # P files are typically text-based, so we'll parse them accordingly
                        # Assuming tab or space-delimited format
                        preview_data = []
                        headers = []
                        data_started = False
                        
                        for line in pallet_data[:20]:  # Look at first 20 lines to find structure
                            line = line.strip()
                            if not line or line.startswith(';') or line.startswith('#'):
                                continue  # Skip comments and empty lines
                                
                            if not data_started:
                                # This might be a header line
                                parts = line.split()
                                if len(parts) >= 3:
                                    headers = parts[:3]  # Take first three columns as headers
                                    data_started = True
                            else:
                                # This is a data line
                                parts = line.split()
                                if len(parts) >= 3:
                                    preview_data.append(parts[:3])  # Take first three columns
                                    
                        # Create a DataFrame for display
                        if preview_data:
                            if not headers:
                                headers = [f"Column {i+1}" for i in range(3)]
                                
                            preview_df = pd.DataFrame(preview_data, columns=headers)
                            st.dataframe(preview_df)
                        else:
                            st.info("No data could be extracted from the pallet table file or the format is not as expected.")
                            
                    except Exception as e:
                        st.warning(f"Could not parse pallet table for preview: {str(e)}")
                        
                else:
                    st.error("❌ No pallet table files were found.")
            else:
                st.error(f"❌ Failed to generate pallet table:\n{output}")
                st.session_state.pallet_table_generated = False
    
    # Step 4: Review the Operations
    st.header("Step 4: Review the Operations")
    
    if operations_exist:
        try:
            # Only load operations data if it's not already in session state
            if st.session_state.operations_data is None:
                st.session_state.operations_data = pd.read_excel(operations_path)
            
            st.subheader("Operations Schedule")
            
            # Get full data (either from session state or from modified_data if it exists)
            full_df = st.session_state.modified_data.copy() if st.session_state.modified_data is not None else st.session_state.operations_data.copy()
            
            # Add a filter option
            show_only_planned = st.checkbox("Show only planned operations", value=True)
            
            # Make a deep copy of the full DataFrame to avoid SettingWithCopyWarning
            if show_only_planned and 'status' in full_df.columns:
                # Use boolean indexing to filter the data
                mask = full_df['status'] == 'planned'
                if mask.any():
                    # Any rows with 'planned' status?
                    filtered_df = full_df[mask].copy()
                else:
                    # No 'planned' rows, show all data
                    filtered_df = full_df.copy()
                    st.info("No operations with 'planned' status found.")
            else:
                filtered_df = full_df.copy()
            
            # Select only the specified columns if they exist
            columns_to_show = ['pallet', 'quadrant', 'status', 'id', 'components_per_quadrant']
            existing_columns = [col for col in columns_to_show if col in filtered_df.columns]
            
            if len(existing_columns) < len(columns_to_show):
                missing_columns = set(columns_to_show) - set(existing_columns)
                st.warning(f"Some requested columns are not available in the data: {', '.join(missing_columns)}")
            
            # Create a new DataFrame with just the columns we want
            if existing_columns:
                display_df = pd.DataFrame()
                for col in existing_columns:
                    display_df[col] = filtered_df[col].copy()
            else:
                display_df = filtered_df.copy()
                st.warning("None of the requested columns were found in the data.")
            
            # Add original index as a separate column for reference
            display_df['original_index'] = filtered_df.index.copy()
            
            # Determine which columns should be disabled in the editor
            disabled_cols = []
            if 'status' in display_df.columns:
                disabled_cols = [col for col in display_df.columns if col != 'status']
            else:
                disabled_cols = display_df.columns.tolist()
            
            # Use st.data_editor to display and edit the data
            edited_df = st.data_editor(
                display_df,
                num_rows="dynamic",
                use_container_width=True,
                disabled=disabled_cols,
                hide_index=True,
                key="operations_editor",
                column_config={
                    "original_index": st.column_config.Column(
                        "original_index",
                        disabled=True,
                        required=True,
                        help="Internal index - do not modify",
                        width="small"
                    )
                }
            )
            
            # Create two columns for the buttons
            col1, col2 = st.columns(2)
            
            # Add a button to save changes from the data editor
            if col1.button("Save Changes to Operations Schedule"):
                # Check if we have original_index to map changes back
                if 'original_index' in edited_df.columns and 'status' in edited_df.columns:
                    # Create a new full DataFrame that will contain all original rows
                    updated_full_df = full_df.copy()
                    
                    # Update only the status column for the edited rows
                    for _, row in edited_df.iterrows():
                        if pd.notna(row['original_index']):  # Make sure index is valid
                            idx = int(row['original_index'])  # Convert to int if needed
                            updated_full_df.loc[idx, 'status'] = row['status']
                    
                    # Save the updated full DataFrame
                    updated_full_df.to_excel(operations_path, index=False)
                    st.success("✅ Changes saved to operations.xlsx")
                    
                    # Update session state with the full updated data
                    st.session_state.operations_data = updated_full_df.copy()
                    st.session_state.modified_data = None  # Clear modified data
                    
                    # Set flag that changes have been saved
                    st.session_state.changes_saved = True
                else:
                    # If we don't have original_index, just save what we have (old behavior)
                    if 'original_index' in edited_df.columns:
                        edited_df = edited_df.drop(columns=['original_index'])
                    edited_df.to_excel(operations_path, index=False)
                    st.success("✅ Changes saved to operations.xlsx")
                    st.session_state.operations_data = edited_df.copy()
                    st.session_state.modified_data = None  # Clear modified data
                    
                    # Set flag that changes have been saved
                    st.session_state.changes_saved = True
                
                # Force refresh by clearing the cache
                st.rerun()
                
            # Add "Mark All as Done" button
            if col2.button("Mark All as Done"):
                if 'status' in display_df.columns:
                    # Create a copy of the full data
                    updated_full_df = full_df.copy()
                    
                    # Update the status in the full DataFrame
                    # We need to find which rows in the full dataframe match the ones in our display
                    for _, row in display_df.iterrows():
                        if pd.notna(row['original_index']) and row['status'] == 'planned':
                            idx = int(row['original_index'])
                            updated_full_df.loc[idx, 'status'] = 'done'
                    
                    # Store in session state for next render
                    st.session_state.modified_data = updated_full_df
                    
                    st.info("✅ All planned operations marked as done. Click 'Save Changes to Operations Schedule' to save to file.")
                    st.rerun()  # Rerun to update the display
                else:
                    st.error("❌ No 'status' column found in operations data")
            
        except Exception as e:
            st.error(f"❌ Error loading or processing operations file: {str(e)}")
            st.write(traceback.format_exc())
    else:
        st.info("⚠️ Operations schedule not generated yet. Please complete Step 2 first.")
    
    # Display file status
    st.sidebar.header("File Status")
    
    operations_status = "✅ Available" if operations_exist else "❌ Not Generated"
    
    # Find all pallet table files
    pallet_files = list(build_dir.glob("*.P"))
    if pallet_files:
        pallet_table_status = f"✅ Available ({len(pallet_files)} files)"
    else:
        pallet_table_status = "❌ Not Generated"
    
    st.sidebar.markdown(f"**Operations Schedule:** {operations_status}")
    st.sidebar.markdown(f"**Pallet Tables:** {pallet_table_status}")
    
    # Display file download options if available
    if operations_exist:
        with open(operations_path, "rb") as file:
            st.sidebar.download_button(
                label="Download Operations Excel",
                data=file,
                file_name="operations.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    # List all available pallet tables for download
    if pallet_files:
        st.sidebar.subheader("Available Pallet Tables")
        
        # Sort files by creation time (newest first)
        pallet_files.sort(key=os.path.getctime, reverse=True)
        
        for pallet_file in pallet_files:
            # Get file creation time
            creation_time = os.path.getctime(pallet_file)
            creation_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(creation_time))
            
            with open(pallet_file, "rb") as file:
                st.sidebar.download_button(
                    label=f"Download {pallet_file.name} ({creation_time_str})",
                    data=file,
                    file_name=pallet_file.name,
                    mime="application/octet-stream",
                    key=f"download_{pallet_file.name}"  # Unique key for each button
                )
    
    # Step 5: Reset Application State
    st.header("Step 5: Finish Current Session")
    
    st.markdown("""
    Click the button below to reset the application and start a new scheduling session.
    This will clear the current session state but will **not** delete any files in the build directory.
    """)
    
    # Show the button but disable it if changes haven't been saved
    if st.button("Done - Start New Session", type="primary", disabled=not st.session_state.changes_saved):
        # Reset session state variables but keep the files
        st.session_state.operations_generated = False
        st.session_state.pallet_table_generated = False
        st.session_state.operations_data = None
        st.session_state.edited_statuses = {}
        st.session_state.modified_data = None
        st.session_state.latest_pallet_table_path = None
        st.session_state.changes_saved = False
        
        st.success("✅ Session reset successfully! You can start a new scheduling session.")
        st.balloons()  # Add a visual celebration effect
        
        # Force a rerun to refresh the UI
        time.sleep(1)  # Brief pause for the success message to be visible
        st.rerun()

if __name__ == "__main__":
    main()