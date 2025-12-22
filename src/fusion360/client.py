"""
Fusion 360 API Client
Handles communication with Autodesk Platform Services Fusion 360 API
"""

import os
from typing import List, Dict, Optional, Any
import requests
from dotenv import load_dotenv
import re

from src.auth.oauth_client import OAuthClient
from src.fusion360.model import ParametricModel

load_dotenv()


class Fusion360Client:
    """Client for interacting with Fusion 360 API"""
    
    def __init__(self, oauth_client: Optional[OAuthClient] = None):
        """
        Initialize Fusion 360 API client
        
        Args:
            oauth_client: OAuth client instance (creates new if not provided)
        """
        self.oauth_client = oauth_client or OAuthClient()
        self.base_url = os.getenv(
            "FUSION_API_BASE_URL", 
            "https://developer.api.autodesk.com"
        )
        self.api_version = os.getenv("FUSION_API_VERSION", "v1")
    
    @staticmethod
    def parse_autodesk360_url(url: str) -> Dict[str, Optional[str]]:
        """
        Parse Autodesk 360 URL to extract project and design IDs
        
        Args:
            url: Autodesk 360 URL (e.g., https://cctech82.autodesk360.com/g/projects/...)
            
        Returns:
            Dictionary with project_id, design_id, and hub_id if found
        """
        result = {
            'project_id': None,
            'design_id': None,
            'hub_id': None
        }
        
        # Extract project ID from URL pattern
        project_match = re.search(r'/projects/([^/]+)', url)
        if project_match:
            result['project_id'] = project_match.group(1)
        
        # Extract design/item ID from URL (base64 encoded URN)
        # Pattern: /data/dXJu:.../dXJu:.../ where the last dXJu is the item ID
        item_match = re.search(r'/data/([^/]+)/([^/]+)/', url)
        if item_match:
            # The last part before /overview or end is often the design ID
            design_match = re.search(r'/([^/]+)/(?:overview|$)', url)
            if design_match:
                result['design_id'] = design_match.group(1)
        
        return result
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make authenticated API request
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self.oauth_client.get_headers()
        
        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))
        
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response
    
    def list_projects(self) -> List[Dict]:
        """
        List all projects accessible to the user
        
        Returns:
            List of project dictionaries
        """
        response = self._make_request('GET', '/project/v1/hubs')
        return response.json().get('data', [])
    
    def get_project(self, project_id: str) -> Dict:
        """
        Get project details
        
        Args:
            project_id: Project ID
            
        Returns:
            Project dictionary
        """
        response = self._make_request('GET', f'/project/v1/projects/{project_id}')
        return response.json()
    
    def list_designs(self, project_id: str) -> List[Dict]:
        """
        List designs in a project
        
        Args:
            project_id: Project ID
            
        Returns:
            List of design dictionaries
        """
        response = self._make_request('GET', f'/project/v1/projects/{project_id}/items')
        return response.json().get('data', [])
    
    def load_model(self, project_id: str, design_id: str, hub_id: Optional[str] = None) -> ParametricModel:
        """
        Load a parametric model from Fusion 360
        
        Args:
            project_id: Project ID
            design_id: Design/Item ID
            hub_id: Optional hub ID (will try to discover if not provided)
            
        Returns:
            ParametricModel instance
        """
        # Try multiple endpoint structures
        endpoints_to_try = [
            f'/project/v1/projects/{project_id}/items/{design_id}',
            f'/data/v1/projects/{project_id}/items/{design_id}',
        ]
        
        # If hub_id is provided, try hub-based endpoints
        if hub_id:
            endpoints_to_try.insert(0, f'/project/v1/hubs/{hub_id}/projects/{project_id}/items/{design_id}')
            endpoints_to_try.insert(1, f'/data/v1/hubs/{hub_id}/projects/{project_id}/items/{design_id}')
        
        design_data = None
        last_error = None
        
        for endpoint in endpoints_to_try:
            try:
                response = self._make_request('GET', endpoint)
                design_data = response.json()
                break
            except requests.exceptions.HTTPError as e:
                last_error = e
                if e.response.status_code == 404:
                    continue  # Try next endpoint
                else:
                    raise  # Re-raise non-404 errors
            except Exception as e:
                last_error = e
                continue
        
        if design_data is None:
            error_msg = f"Could not load model. Tried endpoints: {endpoints_to_try}"
            if last_error:
                error_msg += f"\nLast error: {last_error}"
            raise ValueError(error_msg)
        
        return ParametricModel(
            client=self,
            project_id=project_id,
            design_id=design_id,
            data=design_data
        )
    
    def get_parameters(self, project_id: str, design_id: str) -> Dict[str, Any]:
        """
        Get all parameters from a parametric model
        
        Args:
            project_id: Project ID
            design_id: Design ID
            
        Returns:
            Dictionary of parameter names to values
        """
        # Note: Actual endpoint may vary based on Fusion 360 API version
        # This is a placeholder for the actual API structure
        response = self._make_request(
            'GET',
            f'/fusion/v1/projects/{project_id}/designs/{design_id}/parameters'
        )
        return response.json().get('parameters', {})
    
    def update_parameters(self, project_id: str, design_id: str, 
                         parameters: Dict[str, Any]) -> Dict:
        """
        Update parameters in a parametric model
        
        Args:
            project_id: Project ID
            design_id: Design ID
            parameters: Dictionary of parameter names to new values
            
        Returns:
            Update response dictionary
        """
        payload = {
            'parameters': [
                {'name': name, 'value': value}
                for name, value in parameters.items()
            ]
        }
        
        response = self._make_request(
            'PUT',
            f'/fusion/v1/projects/{project_id}/designs/{design_id}/parameters',
            json=payload
        )
        return response.json()
    
    def regenerate_model(self, project_id: str, design_id: str) -> Dict:
        """
        Trigger model regeneration after parameter updates
        
        Args:
            project_id: Project ID
            design_id: Design ID
            
        Returns:
            Regeneration response dictionary
        """
        response = self._make_request(
            'POST',
            f'/fusion/v1/projects/{project_id}/designs/{design_id}/regenerate'
        )
        return response.json()
    
    def get_model_geometry(self, project_id: str, design_id: str) -> bytes:
        """
        Download model geometry/stl
        
        Args:
            project_id: Project ID
            design_id: Design ID
            
        Returns:
            Binary geometry data
        """
        response = self._make_request(
            'GET',
            f'/fusion/v1/projects/{project_id}/designs/{design_id}/geometry',
            headers={'Accept': 'application/octet-stream'}
        )
        return response.content

