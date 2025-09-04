with c360 as (select * from {{ ref('mart_marketing__customer_360') }})
select
  customer_id,
  email,
  case
    when revenue_90d >= 150 and events_30d=0 then 'high_value_lapse_risk'
    when revenue_90d=0 and events_30d>=2 then 'new_users_first_week_intent'
    when coalesce(nps_score,11) < 7 then 'churn_rescue_nps'
    else 'unclassified'
  end as segment,
  (coalesce(revenue_90d,0) * 0.6)
  + (coalesce(events_30d,0) * 5)
  + case when coalesce(nps_score,11) < 7 then 20 else 0 end as score
from c360
