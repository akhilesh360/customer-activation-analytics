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
	python -m activation.simulate_reverse_etl --segment $(SEGMENT) --dry-run $(DRY_RUN)
	make build && make docs && make activate SEGMENT=all DRY_RUN=1
