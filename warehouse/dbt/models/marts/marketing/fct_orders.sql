select
  order_id, customer_id, order_ts, status, amount,
  date_trunc('week', order_ts) as order_week
from {{ ref('stg_orders') }}
