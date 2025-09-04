with src as (select * from {{ ref('web_events') }})
select
  cast(event_id as integer) as event_id,
  cast(customer_id as integer) as customer_id,
  event_type,
  cast(event_ts as timestamp) as event_ts,
  session_id
from src
