with first_order as (
  select customer_id, min(order_ts) as first_order_ts
  from {{ ref('fct_orders') }}
  where status='paid'
  group by 1
),
cohorts as (
  select customer_id, date_trunc('week', first_order_ts) as cohort_week
  from first_order
),
retention as (
  select c.cohort_week, date_trunc('week', f.order_ts) as order_week,
         count(distinct f.customer_id) as active_customers
  from cohorts c
  join {{ ref('fct_orders') }} f on c.customer_id=f.customer_id and f.status='paid'
  group by 1,2
)
select * from retention
