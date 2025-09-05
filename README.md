# Customer Activation Analytics Platform

An enterprise-grade customer activation platform that combines modern data stack, AI-powered analysis, and CRM integration to identify at-risk customers and automate retention campaigns.

[![CI](https://github.com/akhilesh360/customer-activation-analytics/workflows/Customer%20Activation%20Platform%20CI/badge.svg)](https://github.com/akhilesh360/customer-activation-analytics/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🏗️ Architecture

**Modern Data Stack**: dbt + DuckDB + Python  
**AI Integration**: OpenAI GPT-4 for customer risk scoring  
**CRM Integration**: Live Salesforce API  
**Orchestration**: Apache Airflow  
**Analytics**: Streamlit dashboard  

## 🚀 Quick Start

### Option 1: GitHub Codespaces (Recommended for Demos)
1. Click "Code" → "Codespaces" → "Create codespace on main"
2. Wait for environment setup (automatic)
3. Run: `streamlit run dashboard.py`
4. Access the dashboard at the forwarded port

### Option 2: Local Development
```bash
git clone https://github.com/akhilesh360/customer-activation-analytics.git
cd customer-activation-analytics
pip install -r requirements.txt
make build
streamlit run dashboard.py
```

## 📊 Platform Components

### Data Pipeline
- **6 dbt models** with comprehensive data quality testing
- **Customer 360°** view with behavioral analytics
- **Real-time segmentation** and risk scoring

### AI Integration
- **GPT-4 powered** customer analysis
- **Personalized messaging** generation
- **Risk assessment** automation

### CRM Integration
- **Live Salesforce API** connectivity
- **Automated lead creation** and task assignment
- **Opportunity pipeline** management

## 🎯 Use Cases

1. **Customer Retention**: Identify high-value customers at risk of churn
2. **Sales Automation**: Auto-create leads and tasks in Salesforce
3. **Personalized Campaigns**: AI-generated messaging for customer outreach
4. **Revenue Recovery**: Targeted activation of lapsed customers

## 🔧 Key Scripts

| Script | Purpose |
|--------|---------|
| `architecture_overview.py` | Platform architecture and component overview |
| `run_activation_pipeline.py` | Execute end-to-end customer activation workflow |
| `validate_integrations.py` | Test CRM and AI API connectivity |
| `dashboard.py` | Analytics dashboard and real-time monitoring |

## 📈 Business Impact

- **Automated** customer risk identification
- **50% faster** sales follow-up through CRM automation  
- **Personalized** retention campaigns at scale
- **Measurable** revenue activation and recovery

## 🛠️ Technical Stack

| Component | Technology |
|-----------|------------|
| **Data Warehouse** | DuckDB |
| **Data Transformation** | dbt 1.9.4 |
| **AI/ML** | OpenAI GPT-4 |
| **CRM** | Salesforce API |
| **Orchestration** | Apache Airflow |
| **Frontend** | Streamlit |
| **Language** | Python 3.10+ |

## 🏃‍♂️ Production Deployment

The platform includes production-ready features:
- **Airflow DAG** for daily orchestration
- **Data quality testing** with automated validation
- **Error handling** and retry logic
- **Environment-based configuration**
- **API rate limiting** and authentication

## 🔐 Configuration

Create a `.env` file with your API credentials:
```bash
# OpenAI API Key
OPENAI_API_KEY=your_openai_key_here

# Salesforce Credentials
SALESFORCE_USERNAME=your_username@company.com
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_security_token

# Optional Settings
USE_LLM_SCORING=true
DEBUG=false
```

## 📋 Demo Workflow

1. **Architecture Overview**: `python architecture_overview.py`
2. **Validate Integrations**: `python validate_integrations.py`
3. **Launch Dashboard**: `streamlit run dashboard.py`
4. **Execute Pipeline**: `python run_activation_pipeline.py`

## 🤝 Contributing

This is a production demonstration platform. For enterprise deployment or customization inquiries, please contact the maintainer.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
