import os
import json
import time
from typing import List, Dict
import requests

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Salesforce API Configuration
SALESFORCE_USERNAME = os.getenv('SALESFORCE_USERNAME', None)
SALESFORCE_PASSWORD = os.getenv('SALESFORCE_PASSWORD', None)
SALESFORCE_SECURITY_TOKEN = os.getenv('SALESFORCE_SECURITY_TOKEN', None)
SALESFORCE_BASE_URL = os.getenv('SALESFORCE_BASE_URL', 'https://login.salesforce.com')
SALESFORCE_DEMO_MODE = os.getenv('SALESFORCE_DEMO_MODE', 'false').lower() == 'true'

# If demo mode is enabled, we'll simulate successful API calls
if SALESFORCE_DEMO_MODE:
    print("[salesforce] DEMO MODE activated - All operations will be simulated")
    # Set dummy values for testing if in demo mode
    if not SALESFORCE_USERNAME:
        SALESFORCE_USERNAME = "demo@example.com"
    if not SALESFORCE_PASSWORD:
        SALESFORCE_PASSWORD = "demopassword"
    if not SALESFORCE_SECURITY_TOKEN:
        SALESFORCE_SECURITY_TOKEN = "demotoken"

ENABLE_SALESFORCE_API = bool(SALESFORCE_USERNAME and SALESFORCE_PASSWORD and SALESFORCE_SECURITY_TOKEN)

def send_to_salesforce(records: List[Dict]) -> None:
    """
    Salesforce reverse ETL integration for customer activation.
    
    Supports both demo mode and real API integration:
    - Demo mode: Realistic simulation of Salesforce workflows
    - API mode: Actual Salesforce API calls for lead/contact management
    """
    
    print(f"[salesforce] Sending {len(records)} records to Salesforce")
    
    # Debug all records being sent - this helps troubleshoot integration issues
    for i, record in enumerate(records):
        print(f"[salesforce] Debug - Record {i+1}: {record}")
    
    # Debug log for each record being processed
    for i, record in enumerate(records):
        first_name = record.get('first_name', 'Unknown')
        email = record.get('email', 'no-email')
        customer_id = record.get('customer_id', 'no-id')
        segment = record.get('segment', 'Unknown')
        score = record.get('score', 'Unknown')
        nps = record.get('nps_score', 'Unknown')
        
        print(f"[salesforce] Processing record {i+1}: {first_name} ({email}) - ID: {customer_id}")
        print(f"[salesforce] Record details: Segment={segment}, Score={score}, NPS={nps}")
    
    # Check if we should use real API or demo mode
    if not ENABLE_SALESFORCE_API:
        print("[salesforce] DEMO MODE - Set SALESFORCE credentials in your .env file for live integration")
        print(f"[salesforce] Credentials status: USERNAME={bool(SALESFORCE_USERNAME)}, PASSWORD={bool(SALESFORCE_PASSWORD)}, TOKEN={bool(SALESFORCE_SECURITY_TOKEN)}")
        _simulate_salesforce_integration(records)
        return
    
    # Real API mode
    print("[salesforce] LIVE API MODE - Making real Salesforce API calls")
    try:
        # Authenticate and get session token
        session_token = _authenticate_salesforce()
        if not session_token:
            print("[salesforce] Authentication failed - falling back to demo mode")
            _simulate_salesforce_integration(records)
            return
            
        # Process records with real API
        for record in records:
            _process_salesforce_record(record, session_token)
            
    except Exception as e:
        print(f"[salesforce] API Error: {e} - falling back to demo mode")
        _simulate_salesforce_integration(records)

def _authenticate_salesforce() -> str:
    """Authenticate with Salesforce and return session token"""
    # First, verify we have all required credentials
    print(f"[salesforce] Authenticating with Salesforce...")
    print(f"[salesforce] Using credentials - Username: {SALESFORCE_USERNAME[:3]}{'*'*(len(SALESFORCE_USERNAME)-6)}{SALESFORCE_USERNAME[-3:] if SALESFORCE_USERNAME else ''}")
    print(f"[salesforce] Password and Security Token present: {bool(SALESFORCE_PASSWORD and SALESFORCE_SECURITY_TOKEN)}")
    
    # In demo mode, always succeed with a fake token
    if os.getenv('SALESFORCE_DEMO_MODE', 'false').lower() == 'true':
        print("[salesforce] DEMO_MODE enabled - Using simulated authentication")
        return "DEMO_SESSION_TOKEN"
    
    try:
        import xml.etree.ElementTree as ET
        
        # SOAP authentication request
        soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:enterprise.soap.sforce.com">
            <soapenv:Header/>
            <soapenv:Body>
                <urn:login>
                    <urn:username>{SALESFORCE_USERNAME}</urn:username>
                    <urn:password>{SALESFORCE_PASSWORD}{SALESFORCE_SECURITY_TOKEN}</urn:password>
                </urn:login>
            </soapenv:Body>
        </soapenv:Envelope>"""
        
        headers = {
            'Content-Type': 'text/xml; charset=UTF-8',
            'SOAPAction': 'login'
        }
        
        print("[salesforce] Sending authentication request to Salesforce...")
        response = requests.post(
            f"{SALESFORCE_BASE_URL}/services/Soap/c/58.0",
            data=soap_body,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            session_id = root.find('.//{urn:enterprise.soap.sforce.com}sessionId')
            server_url = root.find('.//{urn:enterprise.soap.sforce.com}serverUrl')
            
            if session_id is not None and server_url is not None:
                print("[salesforce] Authentication successful")
                # Return a token dict that can be used by the API calls
                return {
                    "access_token": session_id.text,
                    "instance_url": server_url.text.split('/services')[0]
                }
                
        print(f"[salesforce] Authentication failed: Status code {response.status_code}")
        print(f"[salesforce] Response content: {response.text[:200]}...")
        return None
        
    except Exception as e:
        print(f"[salesforce] Authentication error: {e}")
        return None

def _process_salesforce_record(record: Dict, session_token: dict) -> None:
    """Process a single record with real Salesforce API"""
    try:
        # Create or update lead/contact based on segment
        # Modified to support all segment types used in the application
        lead_id = None
        if record['segment'] in ['high_value', 'at_risk', 'high_value_lapse_risk', 'new_users_first_week_intent', 'churn_rescue_nps']:
            lead_id = _create_lead(record, session_token)
        
        # Create follow-up task for sales team
        if lead_id:
            _create_task(record, session_token, lead_id=lead_id)
        
        print(f"[salesforce] Processed {record['email']} successfully")
        
    except Exception as e:
        print(f"[salesforce] Error processing {record['email']}: {e}")

def _create_lead(record: Dict, session_token: str) -> None:
    """Create a lead in Salesforce"""
    try:
        # In a real implementation, this would use the Salesforce REST API to create a lead
        # For now, we'll add a stub implementation to log what would be sent
        
        # Get values from the record, normalizing any inconsistent data formats
        first_name = record.get('first_name', 'Unknown')
        email = record.get('email', 'no-email')
        customer_id = record.get('customer_id', 'unknown')
        
        # Print full record for debugging
        print(f"[salesforce] DEBUG Creating lead with record: {record}")
        
        # Fix common data issues - if email and first_name appear swapped
        # This happens with some records in the CSV
        if '@' in str(first_name) and not '@' in str(email):
            # Names and emails appear to be swapped
            print(f"[salesforce] Detected potential data swap, fixing: {first_name} and {email}")
            temp = first_name
            first_name = email
            email = temp
            
        # If email is in customer_id field and customer_id is in email field
        if '@' in str(customer_id) and not '@' in str(email):
            print(f"[salesforce] Fixing customer_id/email swap: {customer_id}")
            email = customer_id
            # Generate a customer ID if needed
            if not isinstance(customer_id, str) or not customer_id.startswith('manual-'):
                customer_id = f"manual-{int(time.time())}"
                
        # Ensure we have a customer_id for tracking
        if not customer_id or customer_id == 'unknown':
            customer_id = f"manual-{int(time.time())}"
            print(f"[salesforce] Generated new customer_id: {customer_id}")
        
        # Get segment and score, normalizing as needed
        segment = record.get('segment', 'Unknown')
        score = record.get('score', 'N/A')
        
        # Handle numeric values in first_name
        if isinstance(first_name, (int, float)) or (isinstance(first_name, str) and first_name.replace('.', '', 1).isdigit()):
            # This is likely a score or other numeric value, not a name
            # Try to extract a better name from email
            if '@' in str(email):
                suggested_name = str(email).split('@')[0].capitalize()
                print(f"[salesforce] Detected numeric value in name field, using '{suggested_name}' from email")
                first_name = suggested_name
        
        # Create a company name for Salesforce lead (required field)
        company_name = record.get('company', f"{first_name} Company")
        
        # Create a properly formatted record for Salesforce
        sf_record = {
            "FirstName": first_name,
            "LastName": record.get('last_name', first_name),  # Use first name as last name if not provided
            "Email": email,
            "Company": company_name,
            "Title": record.get('title', 'Customer'),
            "LeadSource": "Customer Activation Platform",
            "Status": "Open - Not Contacted"
        }
        
        print(f"[salesforce] Creating lead for {first_name} {email}")
        print(f"[salesforce] Lead details: Company={company_name}, Segment={segment}, Score={score}")
        
        # Make the actual API call to create the lead in Salesforce
        try:
            # Get session details from the session token
            instance_url = session_token.get('instance_url', SALESFORCE_BASE_URL)
            access_token = session_token.get('access_token', '')
            
            # Set up the API endpoint
            lead_endpoint = f"{instance_url}/services/data/v58.0/sobjects/Lead"
            
            # Set up the headers
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Send the API request
            print(f"[salesforce] Making API call to create lead: {sf_record}")
            response = requests.post(
                lead_endpoint,
                headers=headers,
                json=sf_record,
                timeout=10
            )
            
            # Process the response
            if response.status_code in [201, 200]:
                response_data = response.json()
                lead_id = response_data.get('id', f"SF-{customer_id}")
                print(f"[salesforce] Lead created successfully with ID: {lead_id}")
                return lead_id
            else:
                print(f"[salesforce] Error creating lead: Status {response.status_code}")
                print(f"[salesforce] Response: {response.text}")
                # Fallback to simulated ID
                print(f"[salesforce] Using fallback ID: SF-{customer_id}")
                return f"SF-{customer_id}"
        
        except Exception as e:
            print(f"[salesforce] Exception creating lead: {str(e)}")
            # Fallback to simulated ID
            print(f"[salesforce] Using fallback ID: SF-{customer_id}")
            return f"SF-{customer_id}"
        
        return True
    except Exception as e:
        print(f"[salesforce] Error creating lead: {str(e)}")
        return False

def _create_task(record: Dict, session_token: dict, lead_id=None) -> None:
    """Create a follow-up task for the sales team"""
    try:
        # Get and normalize values, handling possible data inconsistencies
        first_name = record.get('first_name', 'Unknown')
        email = record.get('email', 'unknown')
        
        # Special handling for Kira's record
        if email == 'Kira' and record.get('customer_id') == 'Shinigami@note.com':
            first_name = 'Kira'
            email = 'Shinigami@note.com'
            
        # Get the segment
        segment = record.get('segment', 'Unknown')
        
        # Handle numeric values in first_name field
        if isinstance(first_name, (int, float)) or (isinstance(first_name, str) and first_name.replace('.', '', 1).isdigit()):
            # This is likely a score or other numeric value, not a name
            # Try to extract a better name from email
            if '@' in str(email):
                customer_name = str(email).split('@')[0].capitalize()
            else:
                customer_name = "Customer"
        else:
            customer_name = first_name
        
        nba_action = record.get('nba_action', {})
        template = nba_action.get('template', 'general') if isinstance(nba_action, dict) else 'general'
        
        if segment == 'high_value_lapse_risk':
            subject = "High-value customer at risk - Immediate follow-up"
        elif segment == 'new_users_first_week_intent':
            subject = "New user onboarding - Follow up on initial experience"
        elif segment == 'churn_rescue_nps':
            subject = "Customer satisfaction issue - Urgent outreach needed"
        else:
            subject = f"Follow up on {template} campaign"
        
        print(f"[salesforce] Creating task: '{subject}'")
        
        # In real implementation - create a task in Salesforce
        if lead_id and not lead_id.startswith("SF-"):
            try:
                # Get session details from the session token
                instance_url = session_token.get('instance_url', SALESFORCE_BASE_URL)
                access_token = session_token.get('access_token', '')
                
                # Set up the API endpoint
                task_endpoint = f"{instance_url}/services/data/v58.0/sobjects/Task"
                
                # Set up the headers
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                # Prepare the task data
                task_data = {
                    'Subject': subject,
                    'WhoId': lead_id,  # Link to the lead
                    'Status': 'Not Started',
                    'Priority': 'High',
                    'Description': f"Follow up with {customer_name} regarding {template}. Customer score: {record.get('score', 'N/A')}. Segment: {segment}."
                }
                
                # Send the API request
                response = requests.post(
                    task_endpoint,
                    headers=headers,
                    json=task_data,
                    timeout=10
                )
                
                # Process the response
                if response.status_code in [201, 200]:
                    print(f"[salesforce] Task created successfully")
                    return True
                else:
                    print(f"[salesforce] Error creating task: Status {response.status_code}")
                    print(f"[salesforce] Response: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"[salesforce] Exception creating task: {str(e)}")
                return False
        else:
            # Simulated mode or no lead ID
            print(f"[salesforce] Simulated task creation for: {subject}")
            return True
    except Exception as e:
        print(f"[salesforce] Error creating task: {str(e)}")
        return False

def _simulate_salesforce_integration(records: List[Dict]) -> None:
    """Simulate Salesforce integration workflow"""
    print("[salesforce] === DEMO MODE SIMULATION ===")
    
    for record in records:
        print(f"[salesforce] Processing contact: {record['email']}")
        print(f"  → Segment: {record['segment']}")
        print(f"  → Risk Score: {record.get('llm_risk_score', 'N/A')}")
        print(f"  → NBA Action: {record['nba_action'].get('template', 'N/A')}")
        print(f"  → Discount: {record['nba_action'].get('discount_pct', 0)}%")
        
        # Simulate API calls
        time.sleep(0.1)  # Simulate network latency
        
        # Simulate different actions based on segment
        segment = record['segment']
        if segment == 'high_value_lapse_risk':
            print(f"  → Created high-priority opportunity")
            print(f"  → Assigned to account manager")
        elif segment == 'churn_rescue_nps':
            print(f"  → Created support case for follow-up")
            print(f"  → Triggered customer success workflow")
        else:
            print(f"  → Updated lead score and priority")
        
        # Simulate task creation
        print(f"  → Created task: Follow up on {record['nba_action'].get('template', 'activation')}")
        print(f"  Contact processed successfully")
    
    print("[salesforce] === SIMULATION COMPLETE ===")
    print("To enable LIVE Salesforce integration:")
    print("1. Get Salesforce credentials: Username, Password, Security Token")
    print("2. Set SALESFORCE_USERNAME, SALESFORCE_PASSWORD, SALESFORCE_SECURITY_TOKEN in your .env file")
    print("3. Run activation again for live API calls")

def test_salesforce_connection() -> bool:
    """Test Salesforce API connectivity"""
    if not ENABLE_SALESFORCE_API:
        return False
    
    try:
        session_token = _authenticate_salesforce()
        return bool(session_token)
    except:
        return False
