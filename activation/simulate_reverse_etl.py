import argparse, os, csv, duckdb, pathlib as pl
from decisioning.nbs_rules import next_best_action
from decisioning.nbs_llm import llm_score, generate_personalized_message
from activation.destinations.salesforce_stub import send_to_salesforce

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use system environment variables

DB_PATH = "warehouse/dbt/duckdb/hightouch.duckdb"
OUTBOX = pl.Path("outbox")
OUTBOX.mkdir(exist_ok=True)

SEGMENTS = ["high_value_lapse_risk", "new_users_first_week_intent", "churn_rescue_nps"]

def find_customer_in_csv(csv_path, customer_identifier):
    """
    Find a customer in the CSV file by either customer_id or email.
    Returns a pandas DataFrame with the matching customer(s).
    """
    import pandas as pd
    
    if not pl.Path(csv_path).exists():
        print(f"[activation] Error: CSV file not found at {csv_path}")
        return None
        
    df = pd.read_csv(csv_path)
    
    # First try direct match on customer_id
    matches = df[df['customer_id'] == customer_identifier]
    
    # If no matches, try case-insensitive match on email
    if len(matches) == 0:
        email_matches = df[df['email'].str.lower() == customer_identifier.lower()]
        if len(email_matches) > 0:
            print(f"[activation] Found customer by email match: {customer_identifier}")
            return email_matches
            
    # If we have matches on customer_id, return those
    if len(matches) > 0:
        return matches
        
    # No matches found
    print(f"[activation] No matches found for {customer_identifier} in {csv_path}")
    return None

def fetch_segment_with_context(seg: str):
    """Fetch customer segment data with additional context for LLM analysis"""
    con = duckdb.connect(DB_PATH, read_only=False)
    
    if seg == "all":
        q = """
        SELECT 
            s.customer_id, 
            s.email, 
            s.segment, 
            s.score,
            c.first_name,
            c.nps_score,
            c.events_30d,
            c.orders_cnt,
            c.lifetime_revenue,
            c.created_at,
            c.last_event_ts,
            c.country
        FROM main_marts.mart_marketing__segment_scores s
        LEFT JOIN main_marts.mart_marketing__customer_360 c ON s.customer_id = c.customer_id
        WHERE s.segment <> 'unclassified'
        """
        rows = con.execute(q).fetchall()
    else:
        q = """
        SELECT 
            s.customer_id, 
            s.email, 
            s.segment, 
            s.score,
            c.first_name,
            c.nps_score,
            c.events_30d,
            c.orders_cnt,
            c.lifetime_revenue,
            c.created_at,
            c.last_event_ts,
            c.country
        FROM main_marts.mart_marketing__segment_scores s
        LEFT JOIN main_marts.mart_marketing__customer_360 c ON s.customer_id = c.customer_id
        WHERE s.segment = ?
        """
        rows = con.execute(q, [seg]).fetchall()
    
    con.close()
    
    # Convert to dict with context for LLM
    records = []
    for r in rows:
        record = {
            "customer_id": r[0], 
            "email": r[1], 
            "segment": r[2], 
            "score": float(r[3]),
            "first_name": r[4] or "valued customer",
            "nps_score": r[5],
            "events_30d": r[6] or 0,
            "orders_cnt": r[7] or 0,
            "lifetime_revenue": float(r[8] or 0),
            "created_at": str(r[9]) if r[9] else "N/A",
            "last_event_ts": str(r[10]) if r[10] else "N/A",
            "country": r[11] or "Unknown"
        }
        records.append(record)
    
    return records

def fetch_segment(seg: str):
    """Legacy function for backwards compatibility"""
    return fetch_segment_with_context(seg)

def sync_to_salesforce(customer_id=None, customer_email=None):
    """
    Automatically sync a customer to Salesforce by either ID or email.
    This is a public utility function that can be called from other modules.
    
    Args:
        customer_id: The customer ID to sync
        customer_email: The customer email to sync (used if customer_id is None)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Default to looking in the manual entries CSV
        csv_path = OUTBOX / "manual_entries.csv"
        
        if not csv_path.exists():
            print(f"[activation] Error: Manual entries file not found at {csv_path}")
            return False
        
        # Determine which identifier to use
        identifier = customer_id if customer_id is not None else customer_email
        if identifier is None:
            print("[activation] Error: Must provide either customer_id or customer_email")
            return False
            
        # Find the customer
        matches = find_customer_in_csv(csv_path, identifier)
        
        if matches is None or len(matches) == 0:
            print(f"[activation] Error: Customer '{identifier}' not found in {csv_path}")
            return False
            
        # Convert to records format
        customer_records = matches.to_dict('records')
        
        # Parse JSON fields if they are strings
        for record in customer_records:
            # Handle NBA action if it's a JSON string
            if 'nba_action' in record and isinstance(record['nba_action'], str):
                try:
                    import json
                    record['nba_action'] = json.loads(record['nba_action'])
                except (json.JSONDecodeError, TypeError):
                    # If it can't be parsed as JSON, leave it as is
                    print(f"[activation] Warning: Could not parse nba_action as JSON")
        
        # Create a unique segment name for this sync
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        segment_name = f"manual_sync_{timestamp}"
        
        # Process and send to Salesforce
        export_and_send(customer_records, segment_name, dry_run=False)
        return True
        
    except Exception as e:
        print(f"[activation] Error in sync_to_salesforce: {e}")
        return False

def export_and_send(records, seg, dry_run=True):
    if not records:
        print(f"[activation] No records for segment={seg}")
        return

    use_llm = os.getenv('USE_LLM_SCORING', 'true').lower() == 'true'
    # Get API key from environment variables
    openai_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY')
    
    # Make sure it's not a placeholder
    if openai_key and (openai_key.startswith('PASTE_') or openai_key == 'your-openai-api-key-here'):
        print("[activation] API key appears to be a placeholder, not using LLM features")
        openai_key = None
    
    if use_llm and openai_key:
        print(f"[activation] Using OpenAI LLM for enhanced customer analysis")
    elif use_llm and not openai_key:
        print(f"[activation] LLM enabled but OPENAI_API_KEY not set, using rule-based fallback")
    else:
        print(f"[activation] Using rule-based decision engine")

    for r in records:
        # Get NBA action with business rules
        r["nba_action"] = next_best_action(
            r["segment"],
            goal=os.getenv("GOAL", "90d_clv"),
            discount_cap=float(os.getenv("DISCOUNT_CAP", "10")),
            suppress_hours=int(os.getenv("SUPPRESS_HOURS", "48")),
        )
        
        # Enhance with LLM scoring if available
        if use_llm and openai_key:
            try:
                # Get LLM risk score
                llm_risk_score = llm_score(r)
                r["llm_risk_score"] = llm_risk_score
                
                # Generate personalized message
                personalized_message = generate_personalized_message(r, r["nba_action"])
                r["personalized_message"] = personalized_message
                
                print(f"[activation] LLM analysis for {r['email']}: risk={llm_risk_score:.3f}")
                
            except Exception as e:
                print(f"[activation] LLM analysis failed for {r['email']}: {e}")
                r["llm_risk_score"] = None
                r["personalized_message"] = None

    out = OUTBOX / f"{seg}_payload.csv"
    with out.open("w", newline="") as f:
        if records:
            fieldnames = list(records[0].keys())
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(records)

    print(f"[activation] Wrote {len(records)} rows -> {out}")

    if str(dry_run).lower() in ("1", "true", "yes"):
        print("[activation] DRY RUN: skipping destination push.")
        return

    # Send to Salesforce - Live API Integration
    send_to_salesforce(records)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--segment", default="all")
    parser.add_argument("--dry-run", default="1")
    parser.add_argument("--manual", help="Path to manual entries CSV file")
    parser.add_argument("--customer-id", help="Specific customer ID to activate from manual entries")
    args = parser.parse_args()
    
    # Handle manual entries if provided
    if args.manual:
        try:
            import pandas as pd
            manual_path = pl.Path(args.manual)
            
            if not manual_path.exists():
                print(f"[activation] Error: Manual entries file not found at {args.manual}")
                exit(1)
                
            # Load manual entries
            manual_entries = pd.read_csv(manual_path)
            
            # Fix the column display
            print("[activation] Available entries in CSV:")
            for _, row in manual_entries.iterrows():
                # The correct order: first_name is the name, email is the email, customer_id is the ID
                print(f"  - {row['first_name']} ({row['email']}) - ID: {row['customer_id']}, Segment: {row['segment']}")
            
            # Filter by customer ID if specified
            if args.customer_id:
                print(f"[activation] Looking for customer: {args.customer_id}")
                
                # Use our helper function to find customer by ID or email
                matches = find_customer_in_csv(args.manual, args.customer_id)
                
                if matches is None or len(matches) == 0:
                    print(f"[activation] Error: Customer '{args.customer_id}' not found in {args.manual}")
                    exit(1)
                
                manual_entries = matches
                print(f"[activation] Found customer in manual entries: {manual_entries['email'].iloc[0]}")
            
            # Convert to records format
            manual_records = manual_entries.to_dict('records')
            
            # Parse JSON fields if they are strings
            for record in manual_records:
                # Handle NBA action if it's a JSON string
                if 'nba_action' in record and isinstance(record['nba_action'], str):
                    try:
                        import json
                        record['nba_action'] = json.loads(record['nba_action'])
                    except (json.JSONDecodeError, TypeError):
                        # If it can't be parsed as JSON, leave it as is
                        print(f"[activation] Warning: Could not parse nba_action as JSON for {record.get('customer_id', 'unknown')}")
            
            if len(manual_records) == 0:
                print(f"[activation] No records found in {args.manual}")
                exit(0)
                
            print(f"[activation] Processing {len(manual_records)} manual entries from {args.manual}")
            
            # Use the segment name from the first record for the output file
            segment_name = "manual"
            if args.customer_id:
                segment_name = f"manual_{args.customer_id}"
            
            # Process manual entries
            export_and_send(manual_records, segment_name, dry_run=args.dry_run)
            
        except Exception as e:
            print(f"[activation] Error processing manual entries: {e}")
            exit(1)
    else:
        # Regular segment activation
        recs = fetch_segment(args.segment)
        export_and_send(recs, args.segment, dry_run=args.dry_run)
