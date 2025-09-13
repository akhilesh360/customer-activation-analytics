# Predictive Heat Pump Adoption

---

## Demo

**Live Demo:** _[Add your demo link here if available]_  

---

## System Workflow

**Ingest → Analyze → Segment → Automate → Retain**

This project predicts household adoption of heat pumps using machine learning, supporting policy makers and consultants in targeting outreach and incentives. The workflow includes data ingestion, analysis, segmentation, automation, and retention strategies.

---

## Dashboard Preview

**Main Analytics Dashboard:** _[Add dashboard screenshot or link if available]_  
Monitor household segments, adoption likelihood, and campaign impact.

---

## Key Features
- Predictive modeling for heat pump adoption
- Multiple models: Logistic Regression, Random Forest, XGBoost
- Fairness analysis across demographic and regional groups
- SHAP-based feature importance and explainability
- Modular, production-ready codebase
- Jupyter notebooks for exploration and demonstration
- Docker and Makefile for reproducible environment

---

## Technologies & Libraries
- **Python 3.10+**
- **scikit-learn**
- **XGBoost**
- **SHAP**
- **pandas, numpy**
- **matplotlib**
- **Docker**
- **Jupyter Notebooks**
- **joblib**

---

## Project Structure
```
predictive-heatpump-adoption/
├── src/                # Source code (models, preprocessing, evaluation, utils)
├── notebooks/          # Jupyter notebooks (EDA, model demo, comparison)
├── data/               # Synthetic and scored datasets
├── outputs/            # Model artifacts, metrics, plots (excluded from git)
├── config/             # Configuration files
├── docs/               # Policy brief and documentation
├── Dockerfile          # Containerization setup
├── Makefile            # Automation commands
├── requirements.txt    # Python dependencies
├── README.md           # Project overview and instructions
├── run_compare.py      # Script for model comparison
├── run_pipeline.py     # Main pipeline script
```

---

## About the Dataset

Synthetic dataset with household, housing, and utility features. Key columns: income, region, DAC status, housing attributes, utility data, adoption flag. Explored in `notebooks/01_exploration.ipynb`.

---

## Model Development Journey

Started with interpretable Logistic Regression as the baseline. Advanced to Random Forest and XGBoost for improved accuracy and feature analysis. All models trained and evaluated on the same split for fair comparison.

---

## Train-Test Split Ratio

80/20 split, stratified by target variable, for reliable generalization.

---

## Model Performance Evaluation

Metrics: AUC, confusion matrix, classification report, ROC curves. Results in `outputs/metrics_compare.json` and `outputs/roc_compare.png`. SHAP analysis for feature importance.

---

## Step-by-Step Usage
1. Clone the Repository
   ```bash
   git clone <repo-url>
   cd predictive-heatpump-adoption
   ```
2. Set Up the Environment
   **Option A: Python Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
   **Option B: Docker**
   ```bash
   docker build -t heatpump .
   docker run --rm heatpump python run_pipeline.py
   ```
3. Explore the Data
   Open `notebooks/01_exploration.ipynb` in Jupyter to review the synthetic dataset, visualize distributions, and understand key features.
4. Train and Evaluate Models
   - Run `run_pipeline.py` to train the baseline logistic regression model and generate outputs.
   - Run `run_compare.py` to compare Logistic Regression, Random Forest, and XGBoost models on the same data split.
   - Outputs include:
     - `outputs/metrics_compare.json`: AUC scores for all models
     - `outputs/roc_compare.png`: ROC curve comparison
     - `outputs/feature_importance.png`: Top features by importance
5. Fairness and Explainability
   - Fairness metrics are saved in `outputs/fairness_report.json`, showing model performance across DAC (Disadvantaged Community) and non-DAC groups, and by region.
   - SHAP analysis and feature importances are visualized in `outputs/shap_summary_xgb.png` and `outputs/feature_importance.png`.
6. Inspect Results and Artifacts
   - All key metrics, plots, and model artifacts are in the `outputs/` folder.
   - Notebooks provide step-by-step analysis, visualizations, and interpretation.

---

## How to Contribute
Pull requests welcome! For major changes, please open an issue first or contact the maintainer for enterprise deployment/customization.

---

## License
MIT License - see LICENSE for details.

---

## Author
Sai Akhilesh Veldi  
GitHub • LinkedIn • Portfolio

Built with ❤️ to help communities adopt clean energy solutions
