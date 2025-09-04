with d as (select * from {{ ref('dim_customer') }}),
recent_12wk as (
  select customer_id, sum(amount) as revenue_12wk
  from {{ ref('fct_orders') }}
  where order_ts >= current_timestamp - interval 12 week and status='paid'
  group by 1
),
revenue_90d as (
  select customer_id, sum(amount) as revenue_90d
  from {{ ref('fct_orders') }}
  where order_ts >= current_timestamp - interval 90 day and status='paid'
  group by 1
),
activity as (
  select customer_id, count(*) as events_30d
  from {{ ref('fct_events') }}
  where event_ts >= current_timestamp - interval 30 day
  group by 1
)
select
  d.*,
  coalesce(r12.revenue_12wk,0) as revenue_12wk,
  coalesce(r90.revenue_90d,0) as revenue_90d,
  coalesce(a.events_30d,0) as events_30d
from d
left join recent_12wk r12 on d.customer_id=r12.customer_id
left join revenue_90d r90 on d.customer_id=r90.customer_id
left join activity a on d.customer_id=a.customer_id
