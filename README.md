# Customer Activation Analytics Platform

An enterprise-grade customer activation platform that combines the modern data stack, AI-powered analysis, and CRM integration to identify at-risk customers and automate retention campaigns.

Live Demo - https://customer-activation-analytics-doswappppyzzduxxhwrd8gux.streamlit.app/

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Dashboard](#dashboard)
3. [Quick Start](#quick-start)
4. [Platform Components](#platform-components)
5. [Use Cases](#use-cases)
6. [Key Scripts](#key-scripts)
7. [Business Impact](#business-impact)
8. [Technical Stack](#technical-stack)
9. [Production Deployment](#production-deployment)
10. [Configuration](#configuration)
11. [Demo Workflow](#demo-workflow)
12. [Contributing](#contributing)
13. [License](#license)

---

## Architecture Overview

![Architecture Flowchart: High-level overview of the customer activation analytics platform.](https://github.com/user-attachments/assets/826c12e6-19df-43ce-a087-6034a62f4184)
*Figure: System architecture and integration flow.*

---

## Dashboard

![Dashboard Screenshot: Main analytics dashboard interface.](https://github.com/user-attachments/assets/1059414a-4d24-4eec-abde-026ff2703840)
*Figure: Dashboard view for customer analytics.*

![Dashboard Screenshot: Alternate dashboard layout.](https://github.com/user-attachments/assets/aa5b3157-3368-4c00-835f-a97c66ec7e79)
*Figure: Alternate dashboard view.*

---

**Modern Data Stack:** dbt + DuckDB + Python  
**AI Integration:** OpenAI GPT-4 for customer risk scoring  
**CRM Integration:** Live Salesforce API  
**Orchestration:** Apache Airflow  
**Analytics:** Streamlit dashboard  

---

## Demo Workflow

1. **Architecture Overview**: `python architecture_overview.py`
2. **Validate Integrations**: `python validate_integrations.py`
3. **Launch Dashboard**: `streamlit run dashboard.py`
4. **Execute Pipeline**: `python run_activation_pipeline.py`

## Quick Start

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

---

## Platform Components

### Data Pipeline

![Data Pipeline Diagram: dbt models and customer analytics flow.](https://github.com/user-attachments/assets/2103f324-c4ab-44d2-85f5-a410f6dcec74)
*Figure: Data pipeline overview.*

- **6 dbt models** with comprehensive data quality testing

![Customer 360 Screenshot: Behavioral analytics view for a customer.](https://github.com/user-attachments/assets/12c492e1-c2ea-49b9-911b-a5c56b18a335)
*Figure: Customer 360° view.*

- **Customer 360°** view with behavioral analytics
- **Real-time segmentation** and risk scoring

### AI Integration

- **GPT-4 powered** customer analysis

![AI Analysis Screenshot: Customer risk scoring and insights.](https://github.com/user-attachments/assets/3f43f08a-b163-4940-9722-2bc73bc8c34a)
*Figure: AI-powered risk scoring.*

- **Personalized messaging** generation

![Personalized Messaging Screenshot: AI-generated customer outreach messaging.](https://github.com/user-attachments/assets/e2998473-35ed-4f03-add6-3dc781e7c26b)
*Figure: Personalized AI messaging.*

- **Risk assessment** automation

### CRM Integration

- **Live Salesforce API** connectivity
- **Automated lead creation** and task assignment
- **Opportunity pipeline** management

---

## Use Cases

1. **Customer Retention**: Identify high-value customers at risk of churn
2. **Sales Automation**: Auto-create leads and tasks in Salesforce
3. **Personalized Campaigns**: AI-generated messaging for customer outreach
4. **Revenue Recovery**: Targeted activation of lapsed customers

---

## Key Scripts

| Script                   | Purpose                                        |
|--------------------------|------------------------------------------------|
| `architecture_overview.py` | Platform architecture and component overview  |
| `run_activation_pipeline.py` | Execute end-to-end customer activation workflow |
| `validate_integrations.py` | Test CRM and AI API connectivity              |
| `dashboard.py`           | Analytics dashboard and real-time monitoring   |

---

## Business Impact

- **Automated** customer risk identification
- **50% faster** sales follow-up through CRM automation  
- **Personalized** retention campaigns at scale
- **Measurable** revenue activation and recovery

---

## Technical Stack

| Component             | Technology         |
|-----------------------|-------------------|
| **Data Warehouse**    | DuckDB            |
| **Data Transformation** | dbt 1.9.4       |
| **AI/ML**             | OpenAI GPT-4      |
| **CRM**               | Salesforce API    |
| **Orchestration**     | Apache Airflow    |
| **Frontend**          | Streamlit         |
| **Language**          | Python 3.10+      |

---

## Production Deployment

The platform includes production-ready features:
- **Airflow DAG** for daily orchestration
- **Data quality testing** with automated validation
- **Error handling** and retry logic
- **Environment-based configuration**
- **API rate limiting** and authentication

---

## Configuration

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

---

## Contributing

This is a production demonstration platform. For enterprise deployment or customization inquiries, please contact the maintainer.

---

## License

MIT License - see [LICENSE](LICENSE) file for details.
