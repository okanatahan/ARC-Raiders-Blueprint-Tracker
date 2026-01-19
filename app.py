import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection 
from typing import Optional, Dict

# 1. --- WIDE-SCREEN CONFIGURATION ---
# This line must be the VERY FIRST Streamlit command called.
st.set_page_config(layout="wide")

# --- CONFIGURATION FOR CLOUD DEPLOYMENT ---
SHEET_WORKSHEET_NAME = 'Sheet1'
# The Spreadsheet URL is loaded securely from Streamlit Secrets under [connections.gsheets]
# -----------------------------------------

@st.cache_data(ttl="10m")
def load_data():
    """Connects to the Google Sheet securely using Streamlit Secrets and retrieves the data."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=SHEET_WORKSHEET_NAME)
        
        df.columns = [col.upper() for col in df.columns]
        
        if df.columns[0] == df.columns[0]:
            df.rename(columns={df.columns[0]: 'BLUEPRINT'}, inplace=True)
            
        df.dropna(subset=['BLUEPRINT'], inplace=True)
        
        return df
        
    except Exception as e:
        # Generic error handling for deployment issues
        return pd.DataFrame() 


def get_blueprint_details(blueprint_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Performs a case-insensitive lookup and returns ALL matching rows."""
    if 'BLUEPRINT' not in df.columns:
        return pd.DataFrame()
        
    # Case-insensitive search
    matching_rows = df[df['BLUEPRINT'].str.lower() == blueprint_name.lower()].copy()
    
    # Rename columns for cleaner display
    matching_rows.columns = [col.replace('_', ' ').title() for col in matching_rows.columns]
    
    return matching_rows

# --- Streamlit Application Main Function ---
def blueprint_app():
    # Title will now span the full width
    st.title("Arc Raiders Blueprint Finder")
    st.markdown("Start typing a name to filter the blueprint selection below.")

    # 1. Load data from the sheet
    df = load_data()
    
    if df.empty:
        st.error("Error loading data from Google Sheets. Please check your secrets and sharing permissions.")
        return

    # 2. Extract unique blueprint names
    all_blueprint_options = sorted(df['BLUEPRINT'].unique().tolist())
    
    # 3. Text Input for Filtering
    search_term = st.text_input(
        "Search Blueprints:", 
        placeholder="Type a name (e.g., WOLFPACK)",
        label_visibility='collapsed'
    ).strip()

    # Filter the options based on the search term
    if search_term:
        filtered_options = [
            name for name in all_blueprint_options 
            if search_term.lower() in name.lower()
        ]
    else:
        # If no search term, show all options
        filtered_options = all_blueprint_options

    # 4. Display the Filtered Selection Box
    # The first item in the list is automatically selected on load/filter, so no placeholder is needed.
    if filtered_options:
        blueprint_selection = st.selectbox(
            "Matching Blueprints:", 
            options=filtered_options,
            index=0, # Forces the selector to the first result
            key='filtered_select', 
            label_visibility='collapsed'
        )
    else:
        st.warning(f"No blueprints found matching '{search_term}'.")
        return

    # 5. Logic to display results
    if blueprint_selection:
        
        details_df = get_blueprint_details(blueprint_selection, df)
        
        if not details_df.empty:
            st.subheader(f"All Known Locations for: {blueprint_selection}")
            
            # --- FINAL DATA DISPLAY CONFIGURATION (Using Raw HTML/CSS as requested) ---
            st.markdown(
                """
                <style>
                /* NOTE: The max-width styling for the overall container is NOT here 
                   because st.set_page_config(layout="wide") is used. */
                .centered-table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 15px;
                }

                .centered-table th,
                .centered-table td {
                    text-align: center !important;
                    padding: 10px 12px;
                    white-space: normal;
                    word-wrap: break-word;
                }

                /* Sticky header */
                .centered-table th {
                    position: sticky;
                    top: 0;
                    font-weight: 600;
                    z-index: 2;
                    background-color: rgba(30, 30, 30, 0.95);
                }

                /* Hover effect */
                .centered-table tr:hover {
                    background-color: rgba(255, 255, 255, 0.06);
                }

                /* Text colors per column - Keep this for color, but rely on dataframe size for fit */
                .centered-table th:nth-child(2),
                .centered-table td:nth-child(2) { color: purple; }

                .centered-table th:nth-child(3),
                .centered-table td:nth-child(3) { color: red; }

                .centered-table th:nth-child(4),
                .centered-table td:nth-child(4) { color: grey; }

                .centered-table th:nth-child(5),
                .centered-table td:nth-child(5) { color: green; }

                .centered-table th:nth-child(6),
                .centered-table td:nth-child(6) { color: blue; }

                .centered-table th:nth-child(7),
                .centered-table td:nth-child(7) { color: orange; }
                </style>
                """,
                unsafe_allow_html=True
            )

            # Output the DataFrame as an HTML table with the custom CSS class
            st.markdown(
                details_df.to_html(
                    index=True,
                    classes="centered-table",
                    escape=False
                ),
                unsafe_allow_html=True
            )

            # --- END FINAL DATA DISPLAY CONFIGURATION ---
            st.success(f"Found {len(details_df)} different records for this blueprint.")
        else:
            st.error(f"Blueprint **'{blueprint_selection}'** not found in the data.")

if __name__ == "__main__":
    blueprint_app()