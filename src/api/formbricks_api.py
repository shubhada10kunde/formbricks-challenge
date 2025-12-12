import requests
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from tenacity import retry, stop_after_attempt, wait_exponential
from rich.console import Console
import logging

console = Console()
logger = logging.getLogger(__name__)

class FormbricksAPI:
    """Formbricks API client for Management and Client APIs"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.management_headers = {
            "Content-Type": "application/json"
        }
        self.client_headers = {
            "Content-Type": "application/json"
        }
        self.api_key = None
        
    def setup_api_key(self, api_key: str):
        """Setup API key for authentication"""
        self.api_key = api_key
        self.management_headers["x-api-key"] = api_key
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_management_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make request to Management API"""
        url = f"{self.base_url}/api/v1/management{endpoint}"
        
        logger.debug(f"Management API: {method} {url}")
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=self.management_headers, timeout=30)
            elif method == "POST":
                response = self.session.post(url, json=data, headers=self.management_headers, timeout=30)
            elif method == "PUT":
                response = self.session.put(url, json=data, headers=self.management_headers, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, headers=self.management_headers, timeout=30)
            else:
                return None
            
            logger.debug(f"Response Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 401:
                logger.error("Authentication failed. Check API key.")
                return None
            elif response.status_code == 429:
                logger.warning("Rate limited. Waiting before retry...")
                time.sleep(5)
                raise Exception("Rate limited")
            else:
                logger.error(f"API Error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            return None
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=5))
    def _make_client_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make request to Client API"""
        url = f"{self.base_url}/api/v1/client{endpoint}"
        
        logger.debug(f"Client API: {method} {url}")
        
        try:
            response = self.session.post(url, json=data, headers=self.client_headers, timeout=30)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.warning(f"Client API Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Client request failed: {e}")
            return None
    
    # Management API Methods
    def create_survey(self, survey_data: Dict) -> Optional[Dict]:
        """Create a survey using Management API"""
        return self._make_management_request("POST", "/surveys", survey_data)
    
    def create_user(self, user_data: Dict) -> Optional[Dict]:
        """Create a user using Management API"""

        console.print("[yellow]Note: User creation via API might require invitation flow[/yellow]")
        return self._make_management_request("POST", "/users/invite", user_data)
    
    def get_surveys(self) -> Optional[List[Dict]]:
        """Get all surveys"""
        response = self._make_management_request("GET", "/surveys")
        return response.get("data", []) if response else []
    
    def get_survey(self, survey_id: str) -> Optional[Dict]:
        """Get specific survey"""
        return self._make_management_request("GET", f"/surveys/{survey_id}")
    
    # Client API Methods
    def submit_response(self, survey_id: str, response_data: Dict) -> Optional[Dict]:
        """Submit a response using Client API"""
        endpoint = f"/surveys/{survey_id}/responses"
        return self._make_client_request("POST", endpoint, response_data)
    
    def get_survey_for_response(self, survey_id: str) -> Optional[Dict]:
        """Get survey for response submission"""
        return self._make_client_request("GET", f"/surveys/{survey_id}")
    
    # Helper Methods
    def health_check(self) -> bool:
        """Check if Formbricks is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/management/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def create_api_key(self, name: str = "Seeder API Key") -> Optional[str]:
        """Create an API key programmatically (if supported)"""
        data = {
            "name": name,
            "type": "management"
        }
        response = self._make_management_request("POST", "/api-keys", data)
        return response.get("key") if response else None