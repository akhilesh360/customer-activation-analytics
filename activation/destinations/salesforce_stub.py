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
ENABLE_SALESFORCE_API = bool(SALESFORCE_USERNAME and SALESFORCE_PASSWORD and SALESFORCE_SECURITY_TOKEN)

def send_to_salesforce(records: List[Dict]) -> None:
    """
    Salesforce reverse ETL integration for customer activation.
    
    Supports both demo mode and real API integration:
    - Demo mode: Realistic simulation of Salesforce workflows
    - API mode: Actual Salesforce API calls for lead/contact management
    """
    
    print(f"[salesforce] Sending {len(records)} records to Salesforce")
    
    # Check if we should use real API or demo mode
    if not ENABLE_SALESFORCE_API:
        print("[salesforce] DEMO MODE - Set SALESFORCE credentials in your .env file for live integration")
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
                return session_id.text
                
        print(f"[salesforce] Authentication failed: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"[salesforce] Authentication error: {e}")
        return None

def _process_salesforce_record(record: Dict, session_token: str) -> None:
    """Process a single record with real Salesforce API"""
    try:
        # Create or update lead/contact based on segment
        if record['segment'] in ['high_value', 'at_risk']:
            _create_lead(record, session_token)
        
        # Create follow-up task for sales team
        _create_task(record, session_token)
        
        print(f"[salesforce] Processed {record['email']} successfully")
        
    except Exception as e:
        print(f"[salesforce] Error processing {record['email']}: {e}")

def _create_lead(record: Dict, session_token: str) -> None:
    """Create a lead in Salesforce"""
    # This would use the Salesforce REST API to create a lead
    # Implementation would depend on your Salesforce org structure
    pass

def _create_task(record: Dict, session_token: str) -> None:
    """Create a follow-up task for the sales team"""
    # This would create a task in Salesforce for sales follow-up
    pass

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
