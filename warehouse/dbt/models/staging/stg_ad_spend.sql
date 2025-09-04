with src as (select * from {{ ref('ad_spend') }})
select
  cast(date as date) as date,
  channel,
  campaign,
  cast(spend as double) as spend
from src
