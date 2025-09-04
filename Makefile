DBT_DIR=warehouse/dbt

seed:
	cd $(DBT_DIR) && dbt seed

build:
	cd $(DBT_DIR) && dbt build

test:
	cd $(DBT_DIR) && dbt test

docs:
	cd $(DBT_DIR) && dbt docs generate

serve-docs:
	cd $(DBT_DIR) && dbt docs serve

activate:
	python activation/simulate_reverse_etl.py --segment $(SEGMENT) --dry-run $(DRY_RUN)

demo:
	make build && make docs && make activate SEGMENT=all DRY_RUN=1
