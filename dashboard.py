#!/usr/bin/env python3
"""
Customer Activation Analytics Dashboard
Interactive Streamlit dashboard for customer intelligence and activation insights
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import duckdb
from datetime import datetime, timedelta
import os

# Load environment variables from multiple sources
try:
    # First try to load from Streamlit secrets if available
    # This is used in production/cloud deployment
    if hasattr(st, 'secrets'):
        # Copy secrets to environment variables for subprocess
        if 'openai' in st.secrets:
            os.environ['OPENAI_API_KEY'] = st.secrets.openai.api_key
        
        if 'salesforce' in st.secrets:
            os.environ['SALESFORCE_USERNAME'] = st.secrets.salesforce.username
            os.environ['SALESFORCE_PASSWORD'] = st.secrets.salesforce.password
            os.environ['SALESFORCE_SECURITY_TOKEN'] = st.secrets.salesforce.security_token
            os.environ['SALESFORCE_INSTANCE_URL'] = st.secrets.salesforce.instance_url
    
    # Then try .env file (mainly for local development)
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, will use system environment variables

# Page configuration
st.set_page_config(
    page_title="Customer Activation Analytics",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .highlight {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load data from DuckDB warehouse"""
    try:
        db_path = "warehouse/dbt/duckdb/hightouch.duckdb"
        if not os.path.exists(db_path):
            st.error(f"Database not found at {db_path}. Please run 'make build' first.")
            return None, None, None, None
            
        conn = duckdb.connect(db_path)
        
        # Load customer 360 data
        customer_360 = conn.execute("""
            SELECT * FROM main_marts.mart_marketing__customer_360
        """).df()
        
        # Load segment scores
        segments = conn.execute("""
            SELECT * FROM main_marts.mart_marketing__segment_scores
        """).df()
        
        # Load orders data
        orders = conn.execute("""
            SELECT * FROM main_marts.fct_orders
        """).df()
        
        # Load activation results
        activation_results = None
        if os.path.exists("outbox/all_payload.csv"):
            activation_results = pd.read_csv("outbox/all_payload.csv")
            
        conn.close()
        return customer_360, segments, orders, activation_results
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None

def main():
    # Header
    st.title("Customer Activation Analytics Dashboard")
    st.markdown("### AI-Powered Customer Intelligence & Activation Platform")
    
    # Show LLM status
    openai_available = os.getenv('OPENAI_API_KEY') is not None
    if openai_available:
        st.success("OpenAI LLM Integration: **ACTIVE** - Enhanced customer analysis enabled (GPT-4)")
    else:
        st.warning("OpenAI LLM Integration: **DISABLED** - Add OPENAI_API_KEY for enhanced analysis")
    
    # Create tabs
    tab1, tab2 = st.tabs(["Analytics Dashboard", "Customer Activation"])
    
    with tab1:
        # Load data
        customer_360, segments, orders, activation_results = load_data()
        
        if customer_360 is None:
            st.stop()
        
        # Sidebar filters
        st.sidebar.header("Dashboard Filters")
        
        # Country filter
        countries = ['All'] + list(customer_360['country'].unique())
        selected_country = st.sidebar.selectbox("Select Country", countries)
        
        # Segment filter
        if segments is not None:
            segment_options = ['All'] + list(segments['segment'].unique())
            selected_segment = st.sidebar.selectbox("Select Customer Segment", segment_options)
        else:
            selected_segment = 'All'
        
        # Filter data
        filtered_data = customer_360.copy()
        if selected_country != 'All':
            filtered_data = filtered_data[filtered_data['country'] == selected_country]
        
        # Main metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_customers = len(filtered_data)
            st.metric("Total Customers", f"{total_customers:,}")
        
        with col2:
            total_revenue = filtered_data['lifetime_revenue'].sum()
            st.metric("Total Revenue", f"${total_revenue:,.0f}")
        
        with col3:
            avg_nps = filtered_data['nps_score'].mean()
            st.metric("Average NPS", f"{avg_nps:.1f}")
        
        with col4:
            active_customers = len(filtered_data[filtered_data['events_30d'] > 0])
            st.metric("Active Customers (30d)", f"{active_customers:,}")
        
        # Two column layout for charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Revenue Distribution")
            fig_revenue = px.histogram(
                filtered_data, 
                x='lifetime_revenue', 
                nbins=20,
                title="Customer Lifetime Value Distribution",
                color_discrete_sequence=['#1f77b4']
            )
            fig_revenue.update_layout(
                xaxis_title="Lifetime Revenue ($)",
                yaxis_title="Number of Customers"
            )
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        with col2:
            st.subheader("Revenue by Country")
            country_revenue = filtered_data.groupby('country')['lifetime_revenue'].sum().reset_index()
            fig_country = px.pie(
                country_revenue, 
                values='lifetime_revenue', 
                names='country',
                title="Revenue Distribution by Country"
            )
            st.plotly_chart(fig_country, use_container_width=True)
        
        # Customer Segmentation Analysis
        if segments is not None:
            st.subheader("Customer Segmentation Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                segment_counts = segments['segment'].value_counts().reset_index()
                segment_counts.columns = ['segment', 'count']
                
                fig_segments = px.bar(
                    segment_counts,
                    x='segment',
                    y='count',
                    title="Customer Distribution by Segment",
                    color='segment',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_segments.update_layout(xaxis_title="Segment", yaxis_title="Number of Customers")
                st.plotly_chart(fig_segments, use_container_width=True)
            
            with col2:
                # Segment performance metrics
                segment_performance = segments.merge(customer_360, on='customer_id', how='left')
                seg_metrics = segment_performance.groupby('segment').agg({
                    'lifetime_revenue': 'mean',
                    'nps_score': 'mean',
                    'score': 'mean'
                }).round(2).reset_index()
                
                fig_performance = px.scatter(
                    seg_metrics,
                    x='nps_score',
                    y='lifetime_revenue',
                    size='score',
                    color='segment',
                    title="Segment Performance: NPS vs Revenue",
                    hover_data=['segment']
                )
                st.plotly_chart(fig_performance, use_container_width=True)
        
        # Activation Results
        if activation_results is not None:
            st.subheader("AI Activation Results")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("""
                <div class="highlight">
                <h4>Latest AI Recommendations</h4>
                <p>The AI decision engine has analyzed customer behavior and generated personalized activation recommendations:</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display activation results
                display_results = activation_results.copy()
                if 'nba_action' in display_results.columns:
                    # Parse the NBA action for better display
                    display_results['Action'] = display_results['nba_action'].apply(
                        lambda x: eval(x) if isinstance(x, str) else x
                    )
                    display_results['Channel'] = display_results['Action'].apply(lambda x: x.get('channel', 'N/A'))
                    display_results['Template'] = display_results['Action'].apply(lambda x: x.get('template', 'N/A'))
                    display_results['Discount'] = display_results['Action'].apply(lambda x: f"{x.get('discount_pct', 0)}%")
                
                # Check for LLM enhancements
                has_llm_data = 'llm_risk_score' in activation_results.columns
                columns_to_show = ['customer_id', 'email', 'segment', 'score', 'Channel', 'Template', 'Discount']
                
                if has_llm_data:
                    st.info("Enhanced with OpenAI LLM Analysis")
                    display_results['LLM_Risk'] = activation_results['llm_risk_score'].apply(
                        lambda x: f"{float(x):.3f}" if x is not None else "N/A"
                    )
                    columns_to_show.append('LLM_Risk')
                
                st.dataframe(
                    display_results[columns_to_show],
                    use_container_width=True
                )
                
                # Show personalized messages if available
                if has_llm_data and 'personalized_message' in activation_results.columns:
                    st.subheader("AI-Generated Personalized Messages")
                    for _, row in activation_results.iterrows():
                        if row.get('personalized_message'):
                            with st.expander(f"Message for {row['email']}"):
                                st.write(f"**Segment**: {row['segment']}")
                                st.write(f"**LLM Risk Score**: {row.get('llm_risk_score', 'N/A')}")
                                st.write("**Personalized Message**:")
                                st.info(row['personalized_message'])
            
            with col2:
                st.markdown("### Activation Summary")
                total_activated = len(activation_results)
                st.metric("Customers Activated", total_activated)
                
                if 'segment' in activation_results.columns:
                    segment_breakdown = activation_results['segment'].value_counts()
                    for segment, count in segment_breakdown.items():
                        st.write(f"**{segment}**: {count} customers")
        
        # NPS Analysis
        st.subheader("Customer Satisfaction (NPS) Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # NPS distribution
            fig_nps = px.histogram(
                filtered_data,
                x='nps_score',
                nbins=10,
                title="NPS Score Distribution",
                color_discrete_sequence=['#ff7f0e']
            )
            fig_nps.update_layout(
                xaxis_title="NPS Score",
                yaxis_title="Number of Customers"
            )
            st.plotly_chart(fig_nps, use_container_width=True)
        
        with col2:
            # NPS categories
            def categorize_nps(score):
                if score >= 9:
                    return "Promoters"
                elif score >= 7:
                    return "Passives"
                else:
                    return "Detractors"
            
            filtered_data['nps_category'] = filtered_data['nps_score'].apply(categorize_nps)
            nps_categories = filtered_data['nps_category'].value_counts().reset_index()
            nps_categories.columns = ['category', 'count']
            
            fig_nps_cat = px.pie(
                nps_categories,
                values='count',
                names='category',
                title="NPS Categories",
                color_discrete_map={
                    'Promoters': '#2ecc71',
                    'Passives': '#f39c12',
                    'Detractors': '#e74c3c'
                }
            )
            st.plotly_chart(fig_nps_cat, use_container_width=True)
        
        # Recent Activity
        st.subheader("Recent Customer Activity")
        
        # Filter customers with recent activity
        recent_activity = filtered_data[filtered_data['events_30d'] > 0].sort_values('events_30d', ascending=False)
        
        if len(recent_activity) > 0:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig_activity = px.scatter(
                    recent_activity,
                    x='events_30d',
                    y='lifetime_revenue',
                    size='nps_score',
                    color='country',
                    hover_data=['email', 'orders_cnt'],
                    title="Customer Activity vs Revenue (Last 30 Days)"
                )
                st.plotly_chart(fig_activity, use_container_width=True)
            
            with col2:
                st.markdown("### Most Active Customers")
                top_active = recent_activity.head(5)[['email', 'events_30d', 'lifetime_revenue']]
                for _, row in top_active.iterrows():
                    st.write(f"**{row['email']}**")
                    st.write(f"Events: {row['events_30d']} | Revenue: ${row['lifetime_revenue']:.0f}")
                    st.write("---")
        else:
            st.info("No recent customer activity found in the selected filters.")
    
    with tab2:
        st.header("Customer Activation Engine")
        st.markdown("### AI-Powered Customer Engagement & Activation")
        
        # Check API keys and environment configuration
        api_status_col1, api_status_col2 = st.columns([1, 1])
        
        with api_status_col1:
            if openai_available:
                st.success("✅ OpenAI: Connected and ready (GPT-4)")
            else:
                st.error("❌ OpenAI: Not configured (add OPENAI_API_KEY in Streamlit secrets or .env)")
        
        with api_status_col2:
            # Check if Salesforce credentials are available
            sf_username = os.environ.get('SALESFORCE_USERNAME')
            sf_password = os.environ.get('SALESFORCE_PASSWORD')
            sf_token = os.environ.get('SALESFORCE_SECURITY_TOKEN')
            
            if sf_username and sf_password and sf_token:
                st.success("✅ Salesforce: Credentials found")
            else:
                st.error("❌ Salesforce: Missing credentials (add in Streamlit secrets)")
                
        # Mode information
        if openai_available:
            st.info("LLM Enhanced Mode: AI risk scoring and personalized messaging enabled (GPT-4)")
        else:
            st.warning("Standard Mode: Rule-based activation only (AI features disabled)")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Select Activation Parameters")
            
            # Segment selection
            segment_options = ['all', 'high_value_lapse_risk', 'new_users_first_week_intent', 'churn_rescue_nps']
            selected_segment = st.selectbox(
                "Customer Segment to Activate",
                segment_options,
                help="Choose which customer segment to target for activation"
            )
            
            # Run activation button
            if st.button("Run Customer Activation", type="primary"):
                with st.spinner("Running activation pipeline..."):
                    import subprocess
                    import sys
                    
                    # Create a placeholder for logs
                    log_placeholder = st.empty()
                    
                    try:
                        # Run the activation pipeline with safeguards
                        log_placeholder.info("Starting activation pipeline...")
                        
                        # Set environment variables from .env for subprocess
                        env = os.environ.copy()
                        
                        # Run with subprocess but ensure it doesn't crash the app
                        result = subprocess.run([
                            sys.executable, "-m", "activation.simulate_reverse_etl",
                            "--segment", selected_segment,
                            "--dry-run", "0"  # Actually send to Salesforce
                        ], capture_output=True, text=True, cwd=os.getcwd(), env=env, timeout=60)
                        
                        if result.returncode == 0:
                            log_placeholder.success("✅ Activation completed successfully!")
                            
                            # Display the output
                            if result.stdout:
                                st.text_area("Activation Log", result.stdout, height=200)
                            
                            # Show success message that persists
                            st.success(f"Successfully activated {selected_segment} segment!")
                        else:
                            error_msg = result.stderr or "Unknown error occurred"
                            log_placeholder.error(f"⚠️ Activation encountered issues: {error_msg}")
                            st.error(f"Activation process had errors - check the log below")
                            st.text_area("Error Log", error_msg, height=200)
                            
                    except subprocess.TimeoutExpired:
                        log_placeholder.warning("⏱️ Activation process took too long and was stopped")
                        st.warning("The process was taking too long and was stopped. This could be due to API rate limits or network issues.")
                    except Exception as e:
                        log_placeholder.error(f"❌ Error: {str(e)}")
                        st.error(f"Error running activation: {str(e)}")
                        
                    # Always show something useful regardless of errors
                    st.info("You can also run activations from the command line with: `python -m activation.simulate_reverse_etl --segment high_value_lapse_risk`")
        
        with col2:
            st.subheader("Activation Insights")
            st.markdown("""
            **What happens during activation:**
            
            **Customer Analysis**
            - Analyzes customer behavior patterns
            - Calculates risk and engagement scores
            - Identifies optimal activation moments
            
            **AI Enhancement** (if enabled)
            - OpenAI GPT-4 risk assessment
            - Personalized message generation
            - Context-aware recommendations
            
            **Action Generation**
            - Creates targeted campaigns
            - Determines optimal channels
            - Sets personalized discounts
            
            **Activation Delivery**
            - Sends to Salesforce (Live API Integration)
            - Creates leads and tasks automatically
            - Tracks campaign performance
            - Monitors customer response
            """)
        
        # Show recent activation results if available
        if os.path.exists("outbox/all_payload.csv"):
            st.subheader("Latest Activation Results")
            
            try:
                latest_results = pd.read_csv("outbox/all_payload.csv")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Customers Activated", len(latest_results))
                with col2:
                    if 'segment' in latest_results.columns:
                        unique_segments = latest_results['segment'].nunique()
                        st.metric("Segments Targeted", unique_segments)
                with col3:
                    if 'llm_risk_score' in latest_results.columns:
                        avg_risk = latest_results['llm_risk_score'].mean()
                        st.metric("Avg LLM Risk Score", f"{avg_risk:.3f}")
                
                # Show detailed results
                st.dataframe(latest_results, use_container_width=True)
                
                # Show AI messages if available
                if openai_available and 'personalized_message' in latest_results.columns:
                    st.subheader("AI-Generated Messages")
                    for _, row in latest_results.iterrows():
                        if row.get('personalized_message'):
                            with st.expander(f"AI Message for {row['email']}"):
                                st.write(f"**Segment**: {row['segment']}")
                                if 'llm_risk_score' in row:
                                    st.write(f"**AI Risk Score**: {row['llm_risk_score']:.3f}")
                                st.write("**Personalized Message**:")
                                st.info(row['personalized_message'])
                
            except Exception as e:
                st.error(f"Error loading activation results: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
    <p>Customer Activation Analytics Platform | Built with dbt, DuckDB, Python & Streamlit</p>
    <p>Real-time customer intelligence powered by AI decisioning and automated activation</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
