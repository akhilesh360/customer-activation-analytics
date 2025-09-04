with src as (select * from {{ ref('customers') }})
select
  cast(customer_id as integer) as customer_id,
  lower(email) as email,
  first_name, last_name,
  cast(created_at as date) as created_at,
  country,
  coalesce(cast(marketing_opt_in as integer),0) as marketing_opt_in,
  cast(nps_score as integer) as nps_score
from src
