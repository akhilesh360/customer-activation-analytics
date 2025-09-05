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

def export_and_send(records, seg, dry_run=True):
    if not records:
        print(f"[activation] No records for segment={seg}")
        return

    use_llm = os.getenv('USE_LLM_SCORING', 'true').lower() == 'true'
    openai_key = os.getenv('OPENAI_API_KEY')
    
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
    args = parser.parse_args()
    recs = fetch_segment(args.segment)
    export_and_send(recs, args.segment, dry_run=args.dry_run)
