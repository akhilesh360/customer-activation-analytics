with src as (select * from {{ ref('orders') }})
select
  cast(order_id as integer) as order_id,
  cast(customer_id as integer) as customer_id,
  cast(order_ts as timestamp) as order_ts,
  status,
  cast(amount as double) as amount
from src
