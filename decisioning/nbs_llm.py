import os
import json
from typing import Dict, Optional
import openai
from openai import OpenAI

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, use system environment variables

# Initialize OpenAI client
def get_openai_client():
    """Get OpenAI client if API key is available"""
    # Try multiple sources for the API key, in order of preference:
    # 1. Environment variables (OPENAI_API_KEY or OPENAI_KEY)
    # 2. Direct .env file values (bypassing environment override)
    
    # Check environment variables first
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY')
    
    # Debug - Check what API key we're getting
    if api_key:
        masked_key = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
        print(f"[llm] Found API key starting with {masked_key}")
    else:
        print("[llm] No valid API key found")
        return None
        
    # Make sure it's not a placeholder
    if api_key and not (api_key.startswith('PASTE_') or api_key == 'your-openai-api-key-here'):
        try:
            client = OpenAI(api_key=api_key)
            # Test the client with a minimal call
            print(f"[llm] Testing OpenAI API connection...")
            models = client.models.list()
            print(f"[llm] Successfully connected to OpenAI API")
            return client
        except Exception as e:
            print(f"[llm] Error initializing OpenAI client: {e}")
    else:
        print("[llm] API key appears to be a placeholder or is missing")
    return None

def llm_score(context: Dict) -> float:
    """
    LLM-powered customer risk scoring using OpenAI.
    
    Analyzes customer profile and returns churn risk score (0-1).
    Falls back to rule-based scoring if OpenAI API is not available.
    """
    client = get_openai_client()
    
    if not client:
        print("[llm] OpenAI API key not found, using rule-based scoring")
        return rule_based_score(context)
    
    try:
        # Create structured prompt for the LLM
        prompt = f"""
You are a customer success expert analyzing customer data to predict churn risk.

Customer Profile:
- NPS Score: {context.get('nps_score', 'N/A')} (scale 0-10, where 10 is highly likely to recommend)
- Events in last 30 days: {context.get('events_30d', 0)}
- Total orders: {context.get('orders_cnt', 0)}
- Lifetime revenue: ${context.get('lifetime_revenue', 0)}
- Customer since: {context.get('created_at', 'N/A')}
- Last activity: {context.get('last_event_ts', 'N/A')}
- Country: {context.get('country', 'N/A')}

Based on this customer profile, predict the churn risk as a decimal between 0.0 (very low risk) and 1.0 (very high risk).

Consider:
- Low NPS scores (0-6) indicate higher churn risk
- Lack of recent activity suggests disengagement
- High-value customers may be worth more retention effort
- New customers need different treatment than long-term customers

Respond with ONLY the risk score as a decimal (e.g., 0.73), no explanation needed.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4 Omni Mini for better performance and cost efficiency
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=10,
            temperature=0.1
        )
        
        # Parse the response
        score_text = response.choices[0].message.content.strip()
        score = float(score_text)
        
        # Ensure score is within bounds
        score = max(0.0, min(1.0, score))
        
        print(f"[llm] LLM risk score: {score:.3f} for customer {context.get('email', 'unknown')}")
        return score
        
    except Exception as e:
        print(f"[llm] Error calling OpenAI API: {e}")
        print("[llm] Falling back to rule-based scoring")
        return rule_based_score(context)

def rule_based_score(context: Dict) -> float:
    """
    Fallback rule-based scoring when LLM is not available.
    """
    nps_score = context.get('nps_score', 5)
    events_30d = context.get('events_30d', 0)
    lifetime_revenue = context.get('lifetime_revenue', 0)
    
    # Basic risk calculation
    nps_risk = max(0, (7 - nps_score) / 7)  # Higher risk for low NPS
    activity_risk = 1.0 if events_30d == 0 else 0.3  # High risk if inactive
    value_weight = min(1.0, lifetime_revenue / 500)  # Weight by customer value
    
    final_score = (nps_risk * 0.4 + activity_risk * 0.6) * value_weight
    return min(1.0, max(0.0, final_score))

def generate_personalized_message(customer_context: Dict, action: Dict) -> str:
    """
    Generate personalized customer messages using OpenAI.
    
    Creates custom email content based on customer behavior and recommended action.
    """
    client = get_openai_client()
    
    if not client:
        return generate_template_message(customer_context, action)
    
    try:
        customer_name = customer_context.get('first_name', 'valued customer')
        segment = customer_context.get('segment', 'general')
        nps_score = customer_context.get('nps_score', 'unknown')
        lifetime_revenue = customer_context.get('lifetime_revenue', 0)
        template = action.get('template', 'generic')
        discount_pct = action.get('discount_pct', 0)
        
        prompt = f"""
Write a personalized customer email for the following scenario:

Customer Details:
- Name: {customer_name}
- Segment: {segment}
- NPS Score: {nps_score}/10
- Lifetime Value: ${lifetime_revenue}
- Action Template: {template}
- Discount Available: {discount_pct}%

Email Requirements:
- Warm, personal tone but professional
- 2-3 sentences maximum
- Include specific value proposition
- If discount > 0%, mention it naturally
- Address their segment-specific needs

Email Types:
- winback_soft: Re-engage inactive valuable customers
- onboarding_tips: Help new customers get started
- nps_followup_then_offer: Address low satisfaction with solution

Write only the email body, no subject line needed.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a customer success expert writing personalized retention emails. Be concise, warm, and action-oriented."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        message = response.choices[0].message.content.strip()
        print(f"[llm] Generated personalized message for {customer_context.get('email', 'unknown')}")
        return message
        
    except Exception as e:
        print(f"[llm] Error generating personalized message: {e}")
        return generate_template_message(customer_context, action)

def generate_template_message(customer_context: Dict, action: Dict) -> str:
    """
    Fallback template-based messages when LLM is not available.
    """
    template = action.get('template', 'generic')
    customer_name = customer_context.get('first_name', 'valued customer')
    discount_pct = action.get('discount_pct', 0)
    
    templates = {
        'winback_soft': f"Hi {customer_name}, we miss you! Here's {discount_pct}% off your next order to welcome you back.",
        'onboarding_tips': f"Welcome {customer_name}! Here are some tips to get the most out of your experience with us.",
        'nps_followup_then_offer': f"Hi {customer_name}, thanks for your feedback. Let's make this right with a {discount_pct}% discount on us.",
    }
    
    return templates.get(template, f"Hi {customer_name}, we have something special for you!")

def analyze_customer_sentiment(customer_context: Dict) -> Dict:
    """
    Analyze customer sentiment and provide insights using OpenAI.
    """
    client = get_openai_client()
    
    if not client:
        return {"sentiment": "neutral", "insights": "LLM analysis not available"}
    
    try:
        prompt = f"""
Analyze this customer profile and provide insights:

Customer Data:
- NPS Score: {customer_context.get('nps_score', 'N/A')}/10
- Recent Activity: {customer_context.get('events_30d', 0)} events in 30 days
- Order History: {customer_context.get('orders_cnt', 0)} total orders
- Revenue: ${customer_context.get('lifetime_revenue', 0)}
- Customer Since: {customer_context.get('created_at', 'N/A')}

Provide a JSON response with:
1. sentiment: "positive", "neutral", or "negative"
2. key_insights: array of 2-3 bullet points about this customer
3. recommended_action: one-sentence recommendation

Format as valid JSON only.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a customer analytics expert. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        analysis = json.loads(response.choices[0].message.content)
        return analysis
        
    except Exception as e:
        print(f"[llm] Error analyzing customer sentiment: {e}")
        return {"sentiment": "neutral", "insights": ["Analysis unavailable"], "recommended_action": "Standard follow-up recommended"}

# Feature flag for LLM integration
USE_LLM_SCORING = os.getenv('USE_LLM_SCORING', 'true').lower() == 'true'
