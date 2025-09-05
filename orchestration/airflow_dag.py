"""
Customer Activation Analytics - Production Airflow DAG

This DAG orchestrates the complete customer activation workflow:
1. Data transformation and quality checks
2. AI-powered customer analysis
3. Activation campaigns to multiple destinations
4. Success monitoring and alerting
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.sensors.filesystem import FileSensor

# DAG Configuration
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'catchup': False
}

def validate_activation_results():
    """Validate activation results and send metrics"""
    import pandas as pd
    import os
    
    if os.path.exists('outbox/all_payload.csv'):
        df = pd.read_csv('outbox/all_payload.csv')
        print(f"Activated {len(df)} customers")
        
        # Check for LLM enhancement
        if 'llm_risk_score' in df.columns:
            avg_risk = df['llm_risk_score'].mean()
            print(f"Average LLM risk score: {avg_risk:.3f}")
        
        return len(df)
    return 0

with DAG(
    'customer_activation_analytics',
    default_args=default_args,
    description='End-to-end customer activation analytics pipeline',
    schedule_interval='@daily',
    max_active_runs=1,
    tags=['customer', 'activation', 'ai']
) as dag:

    # 1. Data Pipeline
    build_warehouse = BashOperator(
        task_id='build_data_warehouse',
        bash_command='cd warehouse/dbt && dbt build --target prod',
        doc_md="""
        ## Data Warehouse Build
        
        Transforms raw customer data into analytics-ready tables:
        - Customer 360 views
        - Behavioral segmentation
        - Revenue attribution
        - Data quality validation
        """
    )
    
    # 2. Data Quality Checks
    data_quality_check = BashOperator(
        task_id='data_quality_validation',
        bash_command='cd warehouse/dbt && dbt test --target prod',
        doc_md="""
        ## Data Quality Validation
        
        Ensures data integrity before activation:
        - Completeness checks
        - Uniqueness constraints
        - Business rule validation
        """
    )
    
    # 3. Customer Activation (All Segments)
    activate_all_segments = BashOperator(
        task_id='activate_all_segments',
        bash_command='python -m activation.simulate_reverse_etl --segment all --dry-run 0',
        doc_md="""
        ## Customer Activation Engine
        
        AI-powered customer activation:
        - GPT-4 risk scoring
        - Personalized messaging
        - Multi-channel activation
        """
    )
    
    # 4. High-Value Customer Focus
    activate_high_value = BashOperator(
        task_id='activate_high_value_customers',
        bash_command='python -m activation.simulate_reverse_etl --segment high_value_lapse_risk --dry-run 0',
        doc_md="""
        ## High-Value Customer Activation
        
        Special focus on high-value at-risk customers:
        - Priority processing
        - Enhanced personalization
        - Account manager notification
        """
    )
    
    # 5. Validation and Metrics
    validate_results = PythonOperator(
        task_id='validate_activation_results',
        python_callable=validate_activation_results,
        doc_md="""
        ## Activation Validation
        
        Validates activation success and collects metrics:
        - Customer count validation
        - LLM performance metrics
        - Success rate tracking
        """
    )
    
    # 6. Success Notification
    success_notification = EmailOperator(
        task_id='send_success_notification',
        to=['data-team@company.com'],
        subject='Customer Activation Pipeline - Success',
        html_content="""
        <h3>Customer Activation Pipeline Completed Successfully</h3>
        <p>The daily customer activation workflow has completed.</p>
        <p><strong>Results:</strong></p>
        <ul>
            <li>Data warehouse updated</li>
            <li>Customer segments activated</li>
            <li>AI insights generated</li>
            <li>Destination systems updated</li>
        </ul>
        <p>Check the dashboard for detailed metrics and insights.</p>
        """,
        trigger_rule='all_success'
    )

    # Task Dependencies
    build_warehouse >> data_quality_check
    data_quality_check >> activate_all_segments
    data_quality_check >> activate_high_value
    [activate_all_segments, activate_high_value] >> validate_results
    validate_results >> success_notification
