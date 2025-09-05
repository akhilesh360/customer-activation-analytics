#!/usr/bin/env python3
"""
Salesforce Record Lookup Utility

This script provides a simple dashboard to view all customer records that have been sent to Salesforce.
It reads from the manual entries CSV and displays the status of each record.
"""

import os
import sys
import pandas as pd
import streamlit as st
import datetime
from glob import glob

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def load_customer_entries():
    """Load all customer entries from the manual entries CSV and payload files"""
    customers = []
    
    # Main manual entries file
    manual_entries_path = "outbox/manual_entries.csv"
    if os.path.exists(manual_entries_path):
        try:
            df = pd.read_csv(manual_entries_path)
            main_entries = df.to_dict('records')
            for entry in main_entries:
                entry['source'] = 'manual_entries.csv'
                customers.append(entry)
        except Exception as e:
            st.error(f"Error loading manual entries: {e}")
    
    # Find all payload files which represent entries sent to Salesforce
    payload_files = glob("outbox/*_payload.csv")
    for file_path in payload_files:
        try:
            df = pd.read_csv(file_path)
            payload_entries = df.to_dict('records')
            for entry in payload_entries:
                entry['source'] = os.path.basename(file_path)
                entry['salesforce_status'] = 'Sent to Salesforce'
                customers.append(entry)
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")
    
    return customers

def main():
    st.title("Salesforce Records Lookup")
    st.write("View all customer records that have been sent to Salesforce")
    
    # Check Salesforce credentials status
    sf_username = os.environ.get('SALESFORCE_USERNAME')
    sf_password = os.environ.get('SALESFORCE_PASSWORD')
    sf_token = os.environ.get('SALESFORCE_SECURITY_TOKEN')
    sf_demo_mode = os.environ.get('SALESFORCE_DEMO_MODE', 'false').lower() == 'true'
    
    if sf_demo_mode:
        st.info("🔹 Salesforce is in DEMO MODE - All operations are simulated")
    elif sf_username and sf_password and sf_token:
        st.success("✅ Salesforce API credentials are configured")
    else:
        st.warning("⚠️ Salesforce API credentials not fully configured")
    
    # Load customer data
    customers = load_customer_entries()
    
    if not customers:
        st.warning("No customer records found. Add customers through the dashboard first.")
        return
        
    # Create a DataFrame for display
    display_df = pd.DataFrame(customers)
    
    # Handle common column name variations
    display_columns = ['customer_id', 'email', 'first_name', 'segment', 'score', 
                      'source', 'salesforce_status']
    
    # Only show columns that exist
    display_columns = [col for col in display_columns if col in display_df.columns]
    
    # Search functionality
    search_term = st.text_input("Search by name or email", "")
    
    if search_term:
        # Case-insensitive search in both name and email
        mask = display_df['email'].str.contains(search_term, case=False, na=False)
        if 'first_name' in display_df.columns:
            mask |= display_df['first_name'].astype(str).str.contains(search_term, case=False, na=False)
        display_df = display_df[mask]
    
    # Show the records
    st.write(f"Found {len(display_df)} customer records")
    st.dataframe(display_df[display_columns])
    
    # Add ability to view full record details
    st.subheader("View Record Details")
    selected_id = st.selectbox("Select a customer ID to view details", 
                              options=display_df['customer_id'].tolist())
    
    if selected_id:
        record = display_df[display_df['customer_id'] == selected_id].iloc[0].to_dict()
        
        st.write("### Customer Record Details")
        for key, value in record.items():
            st.write(f"**{key}:** {value}")
        
        # Add option to resend to Salesforce
        if st.button("Resend to Salesforce", key="resend_btn"):
            try:
                from activation.destinations.salesforce_stub import send_to_salesforce
                send_to_salesforce([record])
                st.success(f"✅ Record for {record.get('first_name', 'Unknown')} ({record.get('email', 'no-email')}) resent to Salesforce!")
            except Exception as e:
                st.error(f"Error resending to Salesforce: {e}")

if __name__ == "__main__":
    main()
