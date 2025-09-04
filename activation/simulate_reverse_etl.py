import argparse, os, csv, duckdb, pathlib as pl
from decisioning.nbs_rules import next_best_action
from destinations.hubspot_stub import send_to_hubspot
from destinations.salesforce_stub import send_to_salesforce

DB_PATH = "warehouse/dbt/duckdb/hightouch.duckdb"
OUTBOX = pl.Path("outbox")
OUTBOX.mkdir(exist_ok=True)

SEGMENTS = ["high_value_lapse_risk","new_users_first_week_intent","churn_rescue_nps"]

def fetch_segment(seg: str):
    con = duckdb.connect(DB_PATH, read_only=False)
    if seg == "all":
        q = "select customer_id,email,segment,score from marts.marketing_mart_marketing__segment_scores where segment <> 'unclassified'"
        rows = con.execute(q).fetchall()
    else:
        q = "select customer_id,email,segment,score from marts.marketing_mart_marketing__segment_scores where segment = ?"
        rows = con.execute(q, [seg]).fetchall()
    con.close()
    return [{"customer_id":r[0],"email":r[1],"segment":r[2],"score":float(r[3])} for r in rows]

def export_and_send(records, seg, dry_run=True):
    if not records:
        print(f"[activation] No records for segment={seg}")
        return
    for r in records:
        r["nba_action"] = next_best_action(r["segment"],
                                           goal=os.getenv("GOAL","90d_clv"),
                                           discount_cap=float(os.getenv("DISCOUNT_CAP","10")),
                                           suppress_hours=int(os.getenv("SUPPRESS_HOURS","48")))
    out = OUTBOX / f"{seg}_payload.csv"
    import csv
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)
    print(f"[activation] Wrote {len(records)} rows -> {out}")
    if str(dry_run) in ("1","true","True"):
        print("[activation] DRY RUN: skipping destination push.")
        return
    send_to_hubspot(records)
    send_to_salesforce(records)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--segment", default="all")
    parser.add_argument("--dry-run", default="1")
    args = parser.parse_args()
    recs = fetch_segment(args.segment)
    export_and_send(recs, args.segment, dry_run=args.dry_run)
