#!/usr/bin/env python3
"""
Salesforce Sync Utility

This script ensures all manual customer entries are properly sent to Salesforce.
It will:
1. Fix any data format issues in the CSV
2. Send any new/unsent entries to Salesforce
3. Generate a report of all records and their Salesforce status
"""

import os
import sys
import pandas as pd
import datetime
from glob import glob
import json

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def fix_csv_format():
    """Run the CSV format fixing utility"""
    try:
        import subprocess
        print("Fixing CSV format issues...")
        result = subprocess.run([sys.executable, "fix_csv_format.py"], 
                               capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        return True
    except Exception as e:
        print(f"Error fixing CSV format: {e}")
        return False

def sync_with_salesforce():
    """Send all unsent records to Salesforce"""
    csv_file = "outbox/manual_entries.csv"
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return False
    
    try:
        print("Syncing records with Salesforce...")
        
        # Get all records from the CSV
        df = pd.read_csv(csv_file)
        records = df.to_dict('records')
        
        # Find all payload files which indicate records already sent
        sent_files = glob("outbox/*_payload.csv")
        
        # Track which customer IDs have already been sent
        sent_ids = set()
        for file_path in sent_files:
            try:
                sent_df = pd.read_csv(file_path)
                if 'customer_id' in sent_df.columns:
                    sent_ids.update(sent_df['customer_id'].tolist())
            except:
                pass  # Skip files that can't be read
        
        # Find records that haven't been sent yet
        new_records = [r for r in records if r.get('customer_id') not in sent_ids]
        
        if new_records:
            print(f"Found {len(new_records)} records to send to Salesforce:")
            for r in new_records:
                print(f"  - {r.get('first_name', 'Unknown')} ({r.get('email', 'no-email')})")
            
            # Import Salesforce integration
            try:
                from activation.destinations.salesforce_stub import send_to_salesforce
                
                # Process JSON fields
                for record in new_records:
                    if 'nba_action' in record and isinstance(record['nba_action'], str):
                        try:
                            record['nba_action'] = json.loads(record['nba_action'])
                        except:
                            pass
                
                # Send to Salesforce
                send_to_salesforce(new_records)
                print(f"Successfully sent {len(new_records)} records to Salesforce")
                
                # Save the sent records to a payload file for reference
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                out_file = f"outbox/manual_sync_{timestamp}_payload.csv"
                pd.DataFrame(new_records).to_csv(out_file, index=False)
                print(f"Saved sent records to {out_file}")
                
                return True
            except Exception as e:
                print(f"Error sending to Salesforce: {e}")
                return False
        else:
            print("No new records to send to Salesforce")
            return True
    except Exception as e:
        print(f"Error syncing with Salesforce: {e}")
        return False

def verify_salesforce_records():
    """Check which records have been sent to Salesforce"""
    csv_file = "outbox/manual_entries.csv"
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return
    
    try:
        # Get all records from the main CSV
        df = pd.read_csv(csv_file)
        
        # Find all payload files
        payload_files = glob("outbox/*_payload.csv")
        
        # Track which customer IDs have been sent
        sent_ids = set()
        for file_path in payload_files:
            try:
                sent_df = pd.read_csv(file_path)
                if 'customer_id' in sent_df.columns:
                    sent_ids.update(sent_df['customer_id'].tolist())
            except:
                pass  # Skip files that can't be read
        
        # Add status to each record
        df['salesforce_status'] = df['customer_id'].apply(
            lambda x: "Sent to Salesforce" if x in sent_ids else "Not sent")
        
        print("\nSalesforce Status Report:")
        print("========================")
        print(f"Total records: {len(df)}")
        print(f"Records sent to Salesforce: {len(sent_ids)}")
        print(f"Records not sent to Salesforce: {len(df) - len(sent_ids)}")
        print("\nDetailed Status:")
        
        for _, row in df.iterrows():
            status = "✓" if row['customer_id'] in sent_ids else "✗"
            print(f"{status} {row.get('first_name', 'Unknown')} ({row.get('email', 'no-email')}) - ID: {row.get('customer_id', 'unknown')}")
        
    except Exception as e:
        print(f"Error verifying Salesforce records: {e}")

def main():
    print("Salesforce Sync Utility")
    print("======================")
    
    # 1. Fix CSV format issues
    fix_csv_format()
    
    # 2. Sync with Salesforce
    sync_with_salesforce()
    
    # 3. Verify which records have been sent
    verify_salesforce_records()

if __name__ == "__main__":
    main()
