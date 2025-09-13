# Predictive Heat Pump Adoption

## Project Overview

This repository provides a comprehensive, production-style pipeline for predicting household adoption of electric heat pumps using machine learning. The project leverages a synthetic dataset with realistic household, housing, and utility features, and demonstrates best practices in data science, model evaluation, and interpretability. The workflow is designed to support policy makers, consultants, and researchers in understanding adoption drivers and targeting outreach efforts.

## Key Features
- **End-to-end pipeline:** Data preprocessing, model training, evaluation, and reporting
- **Multiple models:** Logistic Regression (baseline), Random Forest, and XGBoost
- **Interpretability:** Feature importance and SHAP analysis
- **Fairness analysis:** Performance across demographic and regional groups
- **Consulting-ready structure:** Modular code, clear documentation, reproducible environment

## Repository Structure

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

## Step-by-Step Usage

### 1. Clone the Repository
```bash
git clone <repo-url>
cd predictive-heatpump-adoption
```

### 2. Set Up the Environment
#### Option A: Python Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
#### Option B: Docker
```bash
docker build -t heatpump .
docker run --rm heatpump python run_pipeline.py
```

### 3. Explore the Data
Open `notebooks/01_exploration.ipynb` in Jupyter to review the synthetic dataset, visualize distributions, and understand key features.

### 4. Train and Evaluate Models
- Run `run_pipeline.py` to train the baseline logistic regression model and generate outputs.
- Run `run_compare.py` to compare Logistic Regression, Random Forest, and XGBoost models on the same data split.
- Outputs include:
  - `outputs/metrics_compare.json`: AUC scores for all models
  - `outputs/roc_compare.png`: ROC curve comparison
  - `outputs/feature_importance.png`: Top features by importance

### 5. Fairness and Explainability
- Fairness metrics are saved in `outputs/fairness_report.json`, showing model performance across DAC (Disadvantaged Community) and non-DAC groups, and by region.
- SHAP analysis and feature importances are visualized in `outputs/shap_summary_xgb.png` and `outputs/feature_importance.png`.

### 6. Inspect Results and Artifacts
- All key metrics, plots, and model artifacts are in the `outputs/` folder.
- Notebooks provide step-by-step analysis, visualizations, and interpretation.

## About the Dataset

The project uses a synthetic dataset designed to mimic real-world household, housing, and utility characteristics relevant to heat pump adoption. Key features include:
- **Household income**: Captures economic status and purchasing power.
- **Region**: Reflects geographic differences in climate, policy, and infrastructure.
- **DAC status**: Indicates whether a household is in a Disadvantaged Community, supporting fairness analysis.
- **Housing attributes**: Such as home type, age, and square footage, which influence adoption likelihood.
- **Utility data**: Includes energy usage and costs, providing context for potential savings.
- **Adoption flag**: The target variable indicating whether a household has adopted a heat pump.

The synthetic nature of the data ensures privacy and reproducibility, while still allowing for meaningful analysis and demonstration of modeling techniques. The dataset is explored in detail in the first notebook, where distributions and relationships are visualized to inform feature engineering and model selection.

## Extended Project Background

Electrification of residential heating is a key strategy for reducing carbon emissions and improving energy efficiency. Understanding which households are most likely to adopt heat pumps can help utilities, governments, and consultants design targeted programs and incentives. This repository simulates such a scenario using a synthetic dataset, providing a safe and reproducible environment for experimentation and demonstration.

## Technologies Used
- **Python 3.10+**: Main programming language
- **scikit-learn**: Machine learning models and pipelines
- **XGBoost**: Advanced gradient boosting model
- **SHAP**: Model explainability
- **pandas, numpy**: Data manipulation
- **matplotlib**: Visualization
- **Docker**: Containerization for reproducible environments
- **Jupyter Notebooks**: Interactive analysis and reporting

## Libraries Used

The project leverages several key Python libraries to build, evaluate, and explain the models:

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical operations
- **scikit-learn**: Machine learning models, pipelines, preprocessing, and metrics
- **xgboost**: Advanced gradient boosting model
- **matplotlib**: Data visualization and plotting
- **shap**: Model explainability and feature importance analysis
- **joblib**: Model serialization and saving artifacts

These libraries are listed in `requirements.txt` and are installed automatically when you set up the environment. Docker is also used for containerization and reproducibility.

## Example Outputs
- **ROC Curve Comparison**: Visualizes the trade-off between true positive and false positive rates for all models.
- **Feature Importance**: Bar chart showing which features most influence adoption predictions.
- **Fairness Report**: JSON file summarizing model performance across demographic and regional groups.
- **SHAP Summary Plot**: Beeswarm plot showing the impact of each feature on model output.

## How to Contribute
1. Fork the repository and create a new branch for your feature or fix.
2. Make your changes, following the modular structure and commenting code clearly.
3. Submit a pull request with a description of your changes and why they improve the project.

## Troubleshooting & FAQ
- **Missing packages?** Run `pip install -r requirements.txt` or use Docker for a guaranteed reproducible setup.
- **Data issues?** The synthetic dataset is included and should work out of the box. For real-world data, update the data loading and preprocessing scripts.
- **Model performance?** Results may vary with different random seeds or data splits. All metrics are reproducible using the provided scripts.

## Acknowledgements
This project structure and workflow are inspired by best practices in consulting, research, and open-source data science. Special thanks to contributors and reviewers who help improve the codebase.

## Project Story: Model Development Journey

The modeling journey in this project begins with a strong foundation: **Logistic Regression**. This base model was chosen for its interpretability and reliability, making it ideal for understanding the key drivers behind heat pump adoption. Logistic Regression provides clear insights into how each feature influences the probability of adoption, which is crucial for policy and outreach decisions.

After establishing the baseline, the project explores more advanced models:
- **Random Forest**: Introduced to capture non-linear relationships and interactions between features that Logistic Regression might miss. Random Forests are robust to overfitting and provide feature importance metrics, helping to validate and expand on the findings from the baseline model.
- **XGBoost**: Added as a state-of-the-art gradient boosting algorithm, XGBoost is known for its high performance in predictive tasks. It is used to push the limits of accuracy and to compare how much improvement can be gained over simpler models.

Each model is trained and evaluated on the same data split, ensuring a fair comparison. The results are visualized using ROC curves and summarized in metrics files, allowing for transparent assessment of strengths and weaknesses.

This stepwise approach—from interpretable baseline to complex ensemble—demonstrates best practices in model selection, benchmarking, and communication. It ensures that any improvements in predictive power are meaningful and justified, while maintaining clarity for stakeholders.

## Train-Test Split Ratio

For model training and evaluation, the dataset is split into training and test sets using an 80/20 ratio. This means 80% of the data is used to train the models, while the remaining 20% is reserved for testing and evaluating model performance. The split is stratified by the target variable to ensure balanced representation of adopters and non-adopters in both sets. This approach provides a reliable estimate of how well the models will generalize to new, unseen data.

## Model Performance Evaluation

To compare the predictive performance of different models (Logistic Regression, Random Forest, and XGBoost), a consistent evaluation methodology was used:

- **Metrics Used:**
  - **AUC (Area Under the ROC Curve):** Measures the ability of the model to distinguish between adopters and non-adopters. Higher AUC indicates better performance.
  - **Confusion Matrix & Classification Report:** Provide detailed insights into precision, recall, and F1-score for each class.
  - **ROC Curves:** Visualize the trade-off between true positive and false positive rates for each model.

- **Comparison Process:**
  - All models were trained and tested on the same data split to ensure fairness.
  - Results were saved in `outputs/metrics_compare.json` and visualized in `outputs/roc_compare.png`.
  - Feature importance and SHAP analysis were used to interpret model decisions and validate findings.

This approach ensures that improvements in predictive power are meaningful and that model selection is transparent and justified.

---

For further details, see the notebooks and documentation in the `docs/` folder. If you have questions or want to collaborate, please contact the repository owner via GitHub.
