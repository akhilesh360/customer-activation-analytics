#!/usr/bin/env python3
"""
Utility script to fix column misalignment and format issues in CSV files
Enhanced to ensure data consistency and proper JSON handling
"""

import pandas as pd
import os
import sys
import json
import re
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('csv_fixer')

def fix_json_fields(value):
    """Fix JSON fields that might be improperly formatted"""
    if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
        try:
            # First try to parse it as is
            return json.loads(value)
        except json.JSONDecodeError:
            # Try to fix common issues with quotes
            try:
                # Replace single quotes with double quotes for JSON standard
                fixed_value = re.sub(r"'([^']*)':", r'"\1":', value)
                fixed_value = re.sub(r": '([^']*)'", r': "\1"', fixed_value)
                return json.loads(fixed_value)
            except:
                # If all else fails, return as is
                logger.warning(f"Could not fix JSON field: {value[:50]}...")
                return value
    return value

def fix_csv_file(csv_file):
    """Fix column alignment and format issues in CSV files"""
    logger.info(f"Analyzing {csv_file}...")
    
    if not os.path.exists(csv_file):
        logger.warning(f"File does not exist: {csv_file}")
        return False
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return False
    
    # Check for common issues
    issues_found = False
    
    # 1. Check if first_name column contains segment values
    segment_values = ['high_value_lapse_risk', 'new_users_first_week_intent', 'churn_rescue_nps']
    
    if 'first_name' in df.columns and 'segment' in df.columns:
        segment_in_name = df['first_name'].isin(segment_values).any()
        # 2. Check if segment column contains numeric values
        numeric_segments = pd.to_numeric(df['segment'], errors='coerce').notna().any()
        
        if segment_in_name or numeric_segments:
            logger.info("Detected column misalignment in the CSV file.")
            issues_found = True
            
            # Make backup of original file
            backup_file = f"{csv_file}.bak"
            if not os.path.exists(backup_file):
                logger.info(f"Creating backup at {backup_file}")
                df.to_csv(backup_file, index=False)
            
            # Fix the data
            logger.info("Fixing column alignment...")
            
            # Create fixed dataframe with correct columns
            fixed_df = pd.DataFrame()
            
            # Copy customer_id and email which should be correct
            fixed_df['customer_id'] = df['customer_id']
            fixed_df['email'] = df['email']
            
            # Fix first_name, segment, score columns
            for idx, row in df.iterrows():
                # Determine the correct values
                first_name = row['first_name']
                segment = row['segment']
                score = row['score']
                
                # If first_name is a segment value, fix the column assignments
                if isinstance(first_name, str) and first_name in segment_values:
                    fixed_df.at[idx, 'first_name'] = segment  # segment value is in first_name
                    fixed_df.at[idx, 'segment'] = first_name  # segment name is in the first_name column
                    fixed_df.at[idx, 'score'] = score  # score is correct
                else:
                    # No fix needed for this row
                    fixed_df.at[idx, 'first_name'] = first_name
                    fixed_df.at[idx, 'segment'] = segment
                    fixed_df.at[idx, 'score'] = score
            
            # Copy remaining columns
            for col in df.columns:
                if col not in ['customer_id', 'email', 'first_name', 'segment', 'score']:
                    fixed_df[col] = df[col]
            
            # Save the fixed file
            df = fixed_df  # Use the fixed dataframe for additional fixes below
            issues_found = True
    
    # Fix JSON fields and other format issues
    if 'nba_action' in df.columns:
        logger.info("Fixing JSON fields in nba_action column...")
        df['nba_action'] = df['nba_action'].apply(fix_json_fields)
        # Re-serialize to ensure consistent JSON format
        df['nba_action'] = df['nba_action'].apply(
            lambda x: json.dumps(x) if not isinstance(x, str) else x
        )
        issues_found = True
        
    # Ensure all score values are between 0 and 1
    if 'score' in df.columns:
        logger.info("Normalizing score values...")
        df['score'] = df['score'].apply(
            lambda x: float(x) if 0 <= float(x) <= 1 else float(x)/100 if float(x) > 1 else 0.5
        )
        issues_found = True
        
    # Ensure proper date formats
    date_columns = ['created_at', 'last_event_ts']
    for col in date_columns:
        if col in df.columns:
            logger.info(f"Fixing date format in {col} column...")
            # Try to convert to datetime and back to string in consistent format
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
                issues_found = True
            except Exception:
                pass
                
    # Ensure customer_id is always a string
    if 'customer_id' in df.columns:
        df['customer_id'] = df['customer_id'].astype(str)
    
    if issues_found:
        # Save the fixed file
        df.to_csv(csv_file, index=False)
        logger.info(f"Fixed data saved to {csv_file}")
        return True
    else:
        logger.info("No issues detected that need fixing.")
        return False

def sync_records_with_salesforce(csv_file):
    """Send all records in the CSV file to Salesforce if they haven't been sent yet"""
    try:
        logger.info("Checking for records to send to Salesforce...")
        
        # Get all records from the CSV
        df = pd.read_csv(csv_file)
        records = df.to_dict('records')
        
        # Find all payload files which indicate records already sent
        import glob
        sent_files = glob.glob("outbox/*_payload.csv")
        
        # Track which customer IDs and emails have already been sent
        sent_ids = set()
        sent_emails = set()
        for file_path in sent_files:
            try:
                sent_df = pd.read_csv(file_path)
                if 'customer_id' in sent_df.columns:
                    sent_ids.update(sent_df['customer_id'].astype(str).tolist())
                if 'email' in sent_df.columns:
                    sent_emails.update(sent_df['email'].astype(str).tolist())
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
                pass  # Skip files that can't be read
        
        # Find records that haven't been sent yet - check by both ID and email
        new_records = [r for r in records if (
            r.get('customer_id') not in sent_ids and 
            r.get('email') not in sent_emails
        )]
        
        # Try our enhanced lookup method
        try:
            from activation.simulate_reverse_etl import sync_to_salesforce
            
            # First try individual sync of each record for better error handling
            successful = 0
            for record in new_records:
                try:
                    if 'email' in record:
                        result = sync_to_salesforce(customer_email=record['email'])
                        if result:
                            successful += 1
                            logger.info(f"Successfully synced {record['email']} using enhanced lookup")
                except Exception as e:
                    logger.warning(f"Error in enhanced sync for {record.get('email', 'unknown')}: {e}")
            
            if successful > 0:
                logger.info(f"Successfully sent {successful} records using enhanced sync")
                return True
        except ImportError:
            logger.warning("Enhanced sync_to_salesforce not available, using fallback method")
        except Exception as e:
            logger.warning(f"Error in enhanced sync: {e}")
        
        # If no successful syncs with enhanced method, fall back to traditional method
        if new_records:
            logger.info(f"Found {len(new_records)} records to send to Salesforce using traditional method")
            
            # Import Salesforce integration
            try:
                from activation.destinations.salesforce_stub import send_to_salesforce
                
                # Process JSON fields
                for record in new_records:
                    if 'nba_action' in record and isinstance(record['nba_action'], str):
                        try:
                            record['nba_action'] = fix_json_fields(record['nba_action'])
                        except Exception as e:
                            logger.warning(f"Error processing JSON field: {e}")
                
                # Send to Salesforce
                send_to_salesforce(new_records)
                logger.info(f"Successfully sent {len(new_records)} records to Salesforce")
                return True
            except Exception as e:
                logger.error(f"Error sending to Salesforce: {e}")
                return False
        else:
            logger.info("No new records to send to Salesforce")
            return False
    except Exception as e:
        logger.error(f"Error syncing with Salesforce: {e}")
        return False

def fix_all_csv_files():
    """Fix all CSV files in the outbox directory"""
    # Get the base directory (project root)
    base_dir = Path(__file__).parent
    
    # List of files to fix
    files_to_fix = [
        base_dir / "outbox" / "manual_entries.csv",
        base_dir / "outbox" / "all_payload.csv",
        base_dir / "outbox" / "high_value_lapse_risk_payload.csv"
    ]
    
    fixed_count = 0
    for file_path in files_to_fix:
        if file_path.exists():
            logger.info(f"Fixing {file_path}...")
            if fix_csv_file(str(file_path)):
                fixed_count += 1
                
    logger.info(f"Fixed {fixed_count} files")
    return fixed_count > 0

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Fix CSV format and sync with Salesforce")
    parser.add_argument("file", nargs="?", default="outbox/manual_entries.csv", 
                        help="CSV file to process (default: outbox/manual_entries.csv)")
    parser.add_argument("--sync", action="store_true", help="Sync with Salesforce after fixing")
    parser.add_argument("--all", action="store_true", help="Fix all CSV files in outbox directory")
    parser.add_argument("--email", help="Specific email to sync with Salesforce")
    args = parser.parse_args()
    
    # Fix the CSV file(s)
    if args.all:
        logger.info("Fixing all CSV files...")
        fixed = fix_all_csv_files()
    else:
        if not os.path.exists(args.file):
            logger.error(f"Error: File not found: {args.file}")
            sys.exit(1)
            
        fixed = fix_csv_file(args.file)
        
    if fixed:
        logger.info("CSV files fixed successfully.")
    else:
        logger.info("No changes made to the CSV file(s).")
    
    # Sync with Salesforce if requested
    if args.sync:
        logger.info("Syncing with Salesforce...")
        if args.email:
            try:
                from activation.simulate_reverse_etl import sync_to_salesforce
                result = sync_to_salesforce(customer_email=args.email)
                if result:
                    logger.info(f"Successfully synced customer {args.email} to Salesforce")
                else:
                    logger.warning(f"No customer found with email {args.email}")
            except Exception as e:
                logger.error(f"Error syncing customer {args.email} to Salesforce: {e}")
        else:
            sync_records_with_salesforce(args.file)
