# Screenshot Guide for README

This guide helps you capture professional screenshots for each step of your customer activation platform workflow.

## 📸 Required Screenshots

### 1. DuckDB + dbt (Data Warehouse & Transforms)

**Screenshot 1: dbt Model Lineage**
```bash
cd warehouse/dbt
dbt docs generate
dbt docs serve
```
- Open browser to `http://localhost:8080`
- Click on "Lineage Graph" or the graph icon
- Take screenshot showing the model dependencies
- **Caption**: "Modern data stack with 6 production dbt models and automated lineage tracking"

**Screenshot 2: dbt Test Results**
```bash
cd warehouse/dbt
dbt test --select marts
```
- Take screenshot of terminal output showing all tests passing
- **Caption**: "Data quality assurance with comprehensive testing (6/6 tests passing)"

**Screenshot 3: dbt Model Details**
```bash
cd warehouse/dbt
dbt docs serve
```
- Navigate to `mart_marketing__customer_360` model
- Take screenshot showing model documentation and schema
- **Caption**: "Customer 360° view with behavioral analytics and ML features"

### 2. Customer 360 + ML Scoring (Analytics Dashboard)

**Screenshot 4: Customer Analytics Dashboard**
```bash
streamlit run dashboard.py
```
- Open the "Customer Analytics" tab
- Take screenshot of the customer segmentation charts
- **Caption**: "Real-time customer analytics with behavioral segmentation"

**Screenshot 5: Customer Risk Scoring**
```bash
streamlit run dashboard.py
```
- Go to "Customer Activation" tab
- Show the customer list with risk scores
- **Caption**: "AI-powered customer risk scoring with GPT-4 integration"

### 3. AI Decisioning Engine (LLM Integration)

**Screenshot 6: AI Analysis in Action**
```bash
python run_activation_pipeline.py
```
- Take screenshot of terminal output showing:
  - "Using OpenAI LLM for enhanced customer analysis"
  - "LLM risk score: X.XXX for customer..."
  - "Generated personalized message"
- **Caption**: "GPT-4 powered customer analysis with personalized messaging"

### 4. Reverse ETL (Salesforce Integration)

**Screenshot 7: Salesforce Lead Creation**
1. First, run the pipeline:
```bash
python run_activation_pipeline.py
```

2. Then login to your Salesforce org and navigate to:
   - Go to **App Launcher** → **Leads**
   - Take screenshot showing newly created leads
   - **Caption**: "Automated lead creation in Salesforce CRM"

**Screenshot 8: Salesforce Tasks**
- In Salesforce, go to **App Launcher** → **Tasks**
- Show the follow-up tasks created by the pipeline
- **Caption**: "Automated task assignment for sales team follow-up"

### 5. Orchestration (Airflow DAGs)

**Screenshot 9: Airflow DAG Code**
```bash
code orchestration/airflow_dag.py
```
- Take screenshot of the DAG code showing:
  - Task definitions
  - Dependencies
  - Schedule configuration
- **Caption**: "Production-ready Airflow orchestration with 153 lines of code"

**Screenshot 10: Pipeline Architecture**
```bash
python architecture_overview.py
```
- Take screenshot of terminal output showing complete platform overview
- **Caption**: "End-to-end customer activation platform architecture"

### 6. Analytics (BI-ready marts)

**Screenshot 11: Customer 360 Data**
```bash
cd warehouse/dbt
dbt run --select mart_marketing__customer_360
```
- After running, show sample data:
```bash
python -c "
import duckdb
conn = duckdb.connect('duckdb/hightouch.duckdb')
print(conn.execute('SELECT * FROM mart_marketing__customer_360 LIMIT 5').df())
"
```
- **Caption**: "Customer 360° mart with ML features and behavioral metrics"

## 📋 Screenshot Checklist

### High-Impact Screenshots (Must Have):
- [ ] dbt Lineage Graph
- [ ] Streamlit Dashboard 
- [ ] Salesforce Leads
- [ ] AI Analysis Terminal Output
- [ ] dbt Test Results

### Supporting Screenshots (Nice to Have):
- [ ] Airflow DAG Code
- [ ] Salesforce Tasks
- [ ] Customer 360 Data Sample
- [ ] Architecture Overview Output

## 🎯 Pro Tips for Screenshots

1. **Clean Terminal**: Clear terminal before commands (`clear`)
2. **Consistent Window Size**: Use same browser/terminal size
3. **Good Lighting**: Ensure readable text
4. **Crop Appropriately**: Remove unnecessary borders
5. **Professional Filenames**: 
   - `01-dbt-lineage.png`
   - `02-customer-dashboard.png`
   - `03-salesforce-leads.png`
   - etc.

## 📝 README Structure with Screenshots

```markdown
## 🏗️ Architecture Overview

![Platform Architecture](screenshots/architecture-diagram.png)

### Data Pipeline
![dbt Lineage](screenshots/01-dbt-lineage.png)
*Modern data stack with 6 production dbt models and automated lineage tracking*

### Customer Analytics
![Customer Dashboard](screenshots/02-customer-dashboard.png)
*Real-time customer analytics with behavioral segmentation*

### AI Integration
![AI Analysis](screenshots/03-ai-analysis.png)
*GPT-4 powered customer analysis with personalized messaging*

### CRM Integration
![Salesforce Leads](screenshots/04-salesforce-leads.png)
*Automated lead creation in Salesforce CRM*
```

Ready to start taking screenshots? Let me know which step you'd like to begin with!
