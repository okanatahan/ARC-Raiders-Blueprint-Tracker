import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from typing import Optional, Dict

# --- Configuration for Data Source ---
# Ensure this matches the exact name of your spreadsheet tab (e.g., 'Sheet1')
SHEET_WORKSHEET_NAME = 'Sheet1' 

# Function to load and cache the data from the Google Sheet.
# Caching (for 10 minutes) ensures the app is fast and minimizes Sheets API calls.
@st.cache_data(ttl="10m")
def load_data():
    """Connects to the Google Sheet and retrieves the data as a Pandas DataFrame."""
    
    # Establish connection using the credentials securely stored in Streamlit Cloud Secrets.
    # The connection name 'gsheets' is a convention used by the Streamlit GSheets Connector.
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Read the data from the designated worksheet
    df = conn.read(worksheet=SHEET_WORKSHEET_NAME)
    
    # Standardize column headers for reliable access (e.g., convert all to uppercase).
    df.columns = [col.upper() for col in df.columns]
    
    # IMPORTANT: Ensure the blueprint name column is correctly labeled 'BLUEPRINT'.
    # This block renames the first column (which had no header in the sample)
    # If your first column already has a header, you may need to adjust this.
    if df.columns[0] == df.columns[0]:
        df.rename(columns={df.columns[0]: 'BLUEPRINT'}, inplace=True)
        
    return df

def get_blueprint_details(blueprint_name: str, df: pd.DataFrame) -> dict:
    """Performs a case-insensitive lookup of the blueprint against the DataFrame."""
    
    # Safety check: ensure the search column exists
    if 'BLUEPRINT' not in df.columns:
        return {"error": "The required 'BLUEPRINT' column is missing from the data. Check your sheet headers."}
        
    # Search logic: find the row where the blueprint name matches (case-insensitive)
    matching_rows = df[df['BLUEPRINT'].str.lower() == blueprint_name.lower()]
    
    if not matching_rows.empty:
        # Return the data from the first matching row as a standard Python dictionary
        return matching_rows.iloc[0].to_dict()
    else:
        # Return an empty dictionary if no match is found
        return {}

# --- Streamlit Application Layout ---
def blueprint_app():
    st.title("Arc Raiders Blueprint Finder")
    st.markdown("Enter a blueprint name to instantly view all its details.")

    # 1. Load data from the sheet
    df = load_data()

    # Handle data loading errors from the sheet connection
    if isinstance(df, dict) and "error" in df:
        st.error(df["error"])
        return

    # 2. User input field
    blueprint_input = st.text_input(
        "Blueprint Name:", 
        placeholder="e.g., IL TORO or WOLFPACK"
    ).strip()

    # 3. Lookup Button: Trigger action when button is pressed
    if st.button('Show Details'):
        if not blueprint_input:
            st.warning("Please enter a blueprint name to search.")
            return

        # Perform the search using the input value
        details = get_blueprint_details(blueprint_input, df)
        
        if details and "error" not in details:
            st.success(f"Details for: **{details['BLUEPRINT']}**")
            
            # Display results to the user
            for key, value in details.items():
                # Format header for cleaner display
                st.write(f"**{key.replace('_', ' ').title()}**: {value}")
        elif "error" in details:
            st.error(details["error"])
        else:
            st.error(f"Blueprint **'{blueprint_input}'** not found in the data.")

if __name__ == "__main__":
    blueprint_app()