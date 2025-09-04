from datetime import datetime, timedelta

def next_best_action(segment: str, goal: str = "90d_clv", discount_cap: float = 10.0, suppress_hours: int = 48):
    """
    Deterministic guardrailed policy:
    - high_value_lapse_risk -> soft winback: email + 5% coupon (cap enforced)
    - new_users_first_week_intent -> product tips sequence, no discount
    - churn_rescue_nps -> CS follow-up then targeted offer (<= cap)
    """
    if segment == "high_value_lapse_risk":
        return {"channel": "email", "template": "winback_soft", "discount_pct": min(5.0, discount_cap)}
    if segment == "new_users_first_week_intent":
        return {"channel": "email", "template": "onboarding_tips", "discount_pct": 0.0}
    if segment == "churn_rescue_nps":
        return {"channel": "cs_ticket", "template": "nps_followup_then_offer", "discount_pct": min(10.0, discount_cap)}
    return {"channel": "none", "template": "holdout", "discount_pct": 0.0}
