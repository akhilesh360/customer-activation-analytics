select
  event_id, customer_id, event_type, event_ts,
  date_trunc('week', event_ts) as event_week
from {{ ref('stg_web_events') }}
