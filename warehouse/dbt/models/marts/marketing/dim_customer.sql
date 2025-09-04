with c as (select * from {{ ref('stg_customers') }}),
orders as (
  select customer_id, count(*) as orders_cnt,
         sum(case when status='paid' then amount else 0 end) as revenue
  from {{ ref('stg_orders') }}
  group by 1
),
events as (
  select customer_id, max(event_ts) as last_event_ts
  from {{ ref('stg_web_events') }}
  group by 1
)
select
  c.customer_id, c.email, c.first_name, c.last_name, c.created_at, c.country,
  c.marketing_opt_in, c.nps_score,
  coalesce(o.orders_cnt,0) as orders_cnt,
  coalesce(o.revenue,0) as lifetime_revenue,
  e.last_event_ts
from c
left join orders o on c.customer_id=o.customer_id
left join events e on c.customer_id=e.customer_id
