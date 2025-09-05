
# Customer Activation Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B.svg)](https://customer-activation-analytics-doswappppyzzduxxhwrd8gux.streamlit.app/)

## DEMO - **[https://customer-activation-analytics-doswappppyzzduxxhwrd8gux.streamlit.app/](https://customer-activation-analytics-doswappppyzzduxxhwrd8gux.streamlit.app/)**

## System Workflow

![Architecture Flowchart](https://github.com/user-attachments/assets/826c12e6-19df-43ce-a087-6034a62f4184)
*Complete system architecture: data pipeline, AI risk scoring, CRM integration, and analytics dashboard.*

> **Ingest → Analyze → Segment → Automate → Retain**


(https://github.com/user-attachments/assets/2103f324-c4ab-44d2-85f5-a410f6dcec74)
Activate and retain customers by combining AI-powered analytics, modern data stack, and live CRM workflows. Identify at-risk customers, automate personalized outreach, and recover revenue with actionable insights.

## Dashboard Preview

### Main Analytics Dashboard
![Dashboard Screenshot](https://github.com/user-attachments/assets/1059414a-4d24-4eec-abde-026ff2703840)
*Monitor customer segments, risk scores, and campaign impact.*

### Customer 360° Analytics  
![Customer 360 Screenshot](https://github.com/user-attachments/assets/12c492e1-c2ea-49b9-911b-a5c56b18a335)
*Deep behavioral analysis for individual customers.*

### AI Risk Scoring & Messaging
![AI Analysis Screenshot](https://github.com/user-attachments/assets/3f43f08a-b163-4940-9722-2bc73bc8c34a)
*GPT-4 powered risk assessment and outreach recommendations.*

## Key Features

- **Customer Risk Scoring** - AI-powered analysis (OpenAI GPT-4) to identify churn risk
- **Real-time Segmentation** - Dynamic customer segmentation and campaign targeting
- **Automated CRM Workflows** - Salesforce API integration for lead/task creation
- **Personalized Messaging** - AI-generated outreach content for every segment
- **Data Quality Testing** - Automated validation with dbt models
- **Interactive Dashboard** - Streamlit analytics with executive-ready charts
- **Pipeline Orchestration** - Daily scheduling and error handling with Airflow
- **Comprehensive Logging** - Data pipeline and CRM event tracking

## Quick Start

```bash
# Clone and setup
git clone https://github.com/akhilesh360/customer-activation-analytics.git
cd customer-activation-analytics

# Install dependencies
pip install -r requirements.txt

# Build and run dashboard
make build
streamlit run dashboard.py
```

Open `http://localhost:8501` to explore the dashboard.

## How It Works

The platform combines:
- **dbt models** for data transformation and quality checks
- **DuckDB** for fast, local data warehousing
- **OpenAI GPT-4** for risk scoring and automated messaging
- **Salesforce API** for live CRM automation (leads, tasks, pipeline)
- **Apache Airflow** for daily pipeline orchestration
- **Streamlit** for interactive analytics dashboards

## Tech Stack

### Core Technologies
- **Python 3.10+** - Backend language
- **dbt 1.9.4** - Data modeling & testing
- **DuckDB** - Analytical database engine
- **OpenAI GPT-4** - AI/ML risk scoring and messaging
- **Salesforce API** - CRM integration
- **Apache Airflow** - Orchestration and error handling
- **Streamlit** - Dashboard frontend

### Key Libraries
- **requests** - API connectivity
- **pandas** - Data manipulation
- **dbt-core** - Data transformation
- **openai** - AI integration

### Architecture
- **Modular Pipeline** - Separate scripts for architecture, validation, pipeline, and dashboard
- **Environment Configuration** - `.env` file for API keys and settings
- **Automated Testing** - dbt data quality checks and pipeline validation

## Project Structure

```
customer-activation-analytics/
├── dashboard.py                 # Streamlit dashboard application
├── architecture_overview.py     # System architecture script
├── run_activation_pipeline.py   # End-to-end activation workflow
├── validate_integrations.py     # CRM & AI API connectivity tests
├── models/                      # dbt models for analytics pipeline
├── airflow/                     # Airflow DAGs for orchestration
└── screenshots/                 # Dashboard previews
```

## Contributing

Pull requests welcome! For major changes, please open an issue first or contact the maintainer for enterprise deployment/customization.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Sai Akhilesh Veldi**  
[GitHub](https://github.com/akhilesh360) • [LinkedIn](https://www.linkedin.com/in/saiakhileshveldi/) • [Portfolio](https://akhilesh360.github.io/SAIPORTFOLIO/)

---

**Built with ❤️ to help enterprises activate, retain, and grow their customer base**


