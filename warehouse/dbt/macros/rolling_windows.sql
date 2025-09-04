{% macro rolling_sum(expr, window_days=30) -%}
sum(case when {{ expr }} >= current_timestamp - interval {{ window_days }} day then 1 else 0 end)
{%- endmacro %}
