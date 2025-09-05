DBT_DIR=warehouse/dbt

# Setup commands
setup:
	@echo "🚀 Setting up Customer Activation Analytics..."
	@echo "1. Installing dependencies..."
	pip install -r requirements.txt
	@echo "2. Setting up environment file..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "✅ Created .env file - please add your OPENAI_API_KEY"; else echo "✅ .env file already exists"; fi
	@echo "3. Testing database connection..."
	cd $(DBT_DIR) && dbt debug
	@echo "🎉 Setup complete! Run 'make demo' to see everything in action"

install-deps:
	pip install -r requirements.txt

check-api-key:
	@python -c "import os; print('✅ API Key loaded' if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your-openai-api-key-here' else '❌ No valid API key found - check your .env file')"

# Data pipeline commands
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

# Activation commands
activate:
	python -m activation.simulate_reverse_etl --segment $(SEGMENT) --dry-run $(DRY_RUN)

# Dashboard commands
dashboard:
	streamlit run dashboard.py

# Demo workflow
demo:
	@echo "🎬 Running complete demo workflow..."
	make build && make activate SEGMENT=all DRY_RUN=1 && make dashboard

# Help
help:
	@echo "Available commands:"
	@echo "  setup          - Initial project setup"
	@echo "  check-api-key  - Verify OpenAI API key is configured"
	@echo "  build          - Build dbt models"
	@echo "  test           - Run data quality tests"
	@echo "  activate       - Run customer activation (use SEGMENT=<name> DRY_RUN=1)"
	@echo "  dashboard      - Launch Streamlit dashboard"
	@echo "  demo           - Full demo workflow"
