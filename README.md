# Warehouse-Native Composable CDP + AI Decisioning Lite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![dbt](https://img.shields.io/badge/dbt-1.0+-orange.svg)](https://www.getdbt.com/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A production-ready demonstration of a modern, warehouse-native Customer Data Platform (CDP) with AI-powered decisioning capabilities. This project showcases how to build composable customer activation pipelines using your data warehouse as the foundation.

## 🏗️ Architecture Overview

This system demonstrates a complete customer lifecycle management platform built on modern data stack principles:

- **🏭 Data Warehouse Foundation**: DuckDB-powered analytics with dbt transformations
- **📊 Customer Intelligence**: 360-degree customer views, retention cohorts, and ML-driven segment scoring
- **🤖 AI Decisioning Engine**: Guardrailed next-best-action recommendations with business rule enforcement
- **🚀 Reverse ETL Activation**: Automated customer journey orchestration to downstream systems
- **📈 Self-Service Analytics**: BI-ready marts for stakeholder enablement

### Key Features

- **Customer 360 Views**: Unified customer profiles with behavioral segmentation
- **Predictive Segmentation**: ML-driven customer scoring and risk identification
- **Guardrailed Automation**: AI decisioning with configurable business constraints
- **Multi-Channel Activation**: Simulated integrations with HubSpot, Salesforce, and more
- **Real-Time Orchestration**: Airflow-ready DAGs for production deployment

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Make utility
- Git

### 1. Environment Setup

```bash
# Clone and navigate to project
git clone <repository-url>
cd customer-activation-analytics

# Create and activate virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -U pip && pip install dbt-duckdb duckdb pandas pyyaml
```

### 2. Configure dbt Profile

```bash
# Create dbt profile directory
mkdir -p ~/.dbt

# Configure DuckDB connection (path relative to warehouse/dbt)
cat > ~/.dbt/profiles.yml <<'YAML'
hightouch_analytics_demo:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: duckdb/hightouch.duckdb
      schema: main
YAML
```

### 3. Build Data Models

```bash
# Seed sample data and build all models
make seed && make build && make test

# Generate and serve documentation
make docs
make serve-docs  # Available at http://localhost:8080
```

### 4. Run Customer Activation

```bash
# Dry run activation for all segments (outputs to /outbox)
make activate SEGMENT=all DRY_RUN=1

# Activation with guardrails (discount cap + suppression)
GOAL=90d_clv DISCOUNT_CAP=5 SUPPRESS_HOURS=24 make activate SEGMENT=all DRY_RUN=1

# Target specific customer segment
make activate SEGMENT=high_value_lapse_risk DRY_RUN=1
```

---

## 📁 Project Structure

```
customer-activation-analytics/
├── 📊 bi/                          # Business Intelligence exports
│   ├── dim_customer.csv
│   ├── mart_marketing__customer_360.csv
│   └── mart_marketing__segment_scores.csv
├── 🏭 warehouse/dbt/               # Data warehouse & transformations
│   ├── models/
│   │   ├── staging/                # Raw data staging models
│   │   └── marts/marketing/        # Customer analytics marts
│   ├── seeds/                      # Sample datasets
│   └── macros/                     # Reusable dbt macros
├── 🤖 decisioning/                 # AI decisioning engine
│   ├── nbs_rules.py               # Next-best-action logic
│   └── nbs_llm.py                 # LLM-powered recommendations
├── 🚀 activation/                  # Reverse ETL & activation
│   ├── simulate_reverse_etl.py    # Main activation orchestrator
│   └── destinations/              # Integration stubs
├── 🔄 orchestration/              # Workflow management
│   └── airflow_dag.py            # Production DAG definitions
└── 📤 outbox/                     # Activation outputs
```

---

## 🎯 Available Customer Segments

| Segment | Description | Activation Strategy |
|---------|-------------|-------------------|
| `high_value_lapse_risk` | High-value customers at risk of churning | Soft winback email + 5% discount |
| `new_users_first_week_intent` | New users showing engagement in first week | Onboarding tips sequence |
| `churn_rescue_nps` | Low NPS customers requiring intervention | CS follow-up + targeted offer |
| `all` | All classified segments | Mixed activation strategies |

---

## 🛠️ Available Commands

All project operations are managed through the `Makefile`. See below for available commands:

### Data Pipeline Commands

```bash
make seed          # Load sample data into warehouse
make build         # Build all dbt models and tests
make test          # Run data quality tests
make docs          # Generate dbt documentation
make serve-docs    # Serve documentation at localhost:8080
```

### Customer Activation Commands

```bash
# Basic activation (dry run)
make activate SEGMENT=<segment_name> DRY_RUN=1

# Advanced activation with guardrails
GOAL=<goal> DISCOUNT_CAP=<cap> SUPPRESS_HOURS=<hours> make activate SEGMENT=<segment> DRY_RUN=<0|1>
```

**Parameters:**
- `SEGMENT`: Target customer segment (`all`, `high_value_lapse_risk`, `new_users_first_week_intent`, `churn_rescue_nps`)
- `DRY_RUN`: Set to `1` for simulation mode, `0` for live activation
- `GOAL`: Optimization objective (e.g., `90d_clv`, `engagement`)
- `DISCOUNT_CAP`: Maximum discount percentage (0-100)
- `SUPPRESS_HOURS`: Contact suppression window in hours

---

## 🤖 AI Decisioning Engine

The decisioning engine provides guardrailed, next-best-action recommendations:

### Guardrail Features
- **Discount Capping**: Configurable maximum discount limits
- **Contact Suppression**: Time-based customer contact frequency limits
- **Goal Optimization**: Objective-driven decision making (CLV, engagement, etc.)
- **Channel Routing**: Intelligent channel selection based on customer preferences

### Example Usage

```python
from decisioning.nbs_rules import next_best_action

# Get recommendation with guardrails
action = next_best_action(
    segment="high_value_lapse_risk",
    goal="90d_clv",
    discount_cap=5.0,
    suppress_hours=24
)
# Returns: {"channel": "email", "template": "winback_soft", "discount_pct": 5.0}
```

---

## 🔌 Integration Points

### Supported Destinations
- **HubSpot**: Contact updates and email campaigns
- **Salesforce**: Lead scoring and opportunity management
- **Custom REST APIs**: Extensible integration framework

### Data Sources
- **E-commerce**: Orders, customers, product interactions
- **Marketing**: Ad spend, campaign performance
- **Web Analytics**: User behavior, conversion events

---

## 📈 Business Intelligence

The platform generates ready-to-use BI assets:

- **Customer 360 Views**: Complete customer lifecycle metrics
- **Retention Cohorts**: Time-based customer behavior analysis  
- **Segment Performance**: Campaign effectiveness by customer segment
- **Activation Metrics**: Real-time activation and engagement tracking

All BI assets are automatically exported to the `/bi` directory for consumption by your preferred BI tool.

---

## 🚀 Production Deployment

### Airflow Integration
The project includes production-ready Airflow DAGs for automated execution:

```python
# See orchestration/airflow_dag.py for complete implementation
from airflow import DAG
from datetime import datetime, timedelta

# Daily customer activation pipeline
customer_activation_dag = DAG(
    'customer_activation_pipeline',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1)
)
```

### Scaling Considerations
- Replace DuckDB with production warehouse (Snowflake, BigQuery, Databricks)
- Implement proper secret management for destination credentials
- Add monitoring and alerting for activation pipeline health
- Configure horizontal scaling for high-volume customer bases

---

## 🤝 Contributing

This project demonstrates modern CDP architecture patterns and is designed for educational and prototyping purposes. Contributions welcome!

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Run tests: `make test`
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙋 Support

For questions about implementation or extending this platform:

- Review the [dbt documentation](https://docs.getdbt.com/)
- Check the `/warehouse/dbt/target` directory for generated docs
- Examine activation outputs in `/outbox` for troubleshooting

Built to demonstrate modern Analytics Engineering practices and warehouse-native customer activation patterns.
