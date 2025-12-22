"""
OAuth 2.0 Client for Autodesk Platform Services (APS)
Handles authentication and token management
"""

import os
import json
import time
from typing import Optional, Dict
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.tokens import OAuth2Token
import requests
from dotenv import load_dotenv

load_dotenv()


class OAuthClient:
    """Handles OAuth 2.0 authentication with Autodesk Platform Services"""
    
    # APS OAuth endpoints
    AUTHORIZATION_BASE_URL = "https://developer.api.autodesk.com/authentication/v2/authorize"
    TOKEN_URL = "https://developer.api.autodesk.com/authentication/v2/token"
    
    # Required scopes for Fusion 360 API
    SCOPES = [
        "data:read",
        "data:write",
        "data:create",
        "code:all"
    ]
    
    def __init__(self, client_id: Optional[str] = None, 
                 client_secret: Optional[str] = None,
                 callback_url: Optional[str] = None):
        """
        Initialize OAuth client
        
        Args:
            client_id: APS Client ID (from .env if not provided)
            client_secret: APS Client Secret (from .env if not provided)
            callback_url: OAuth callback URL (from .env if not provided)
        """
        self.client_id = client_id or os.getenv("APS_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("APS_CLIENT_SECRET")
        self.callback_url = callback_url or os.getenv("APS_CALLBACK_URL", 
                                                       "http://localhost:8080/callback")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("APS_CLIENT_ID and APS_CLIENT_SECRET must be set")
        
        self.token: Optional[Dict] = None
        self.oauth_session: Optional[OAuth2Session] = None
        
    def get_authorization_url(self) -> str:
        """
        Get the authorization URL for user to visit
        
        Returns:
            Authorization URL string
        """
        oauth = OAuth2Session(
            self.client_id,
            redirect_uri=self.callback_url,
            scope=self.SCOPES
        )
        
        authorization_url, state = oauth.authorization_url(self.AUTHORIZATION_BASE_URL)
        return authorization_url
    
    def get_token_from_code(self, authorization_code: str) -> Dict:
        """
        Exchange authorization code for access token
        
        Args:
            authorization_code: Authorization code from callback
            
        Returns:
            Token dictionary with access_token, refresh_token, expires_in, etc.
        """
        oauth = OAuth2Session(
            self.client_id,
            redirect_uri=self.callback_url,
            scope=self.SCOPES
        )
        
        token = oauth.fetch_token(
            self.TOKEN_URL,
            code=authorization_code,
            client_secret=self.client_secret,
            include_client_id=True
        )
        
        self.token = token
        self.oauth_session = oauth
        return token
    
    def get_token_from_client_credentials(self) -> Dict:
        """
        Get access token using client credentials flow (for server-to-server)
        
        Returns:
            Token dictionary with access_token, expires_in, etc.
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
            'scope': ' '.join(self.SCOPES)
        }
        
        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()
        
        token = response.json()
        token['expires_at'] = time.time() + token.get('expires_in', 3600)
        
        self.token = token
        return token
    
    def refresh_token(self) -> Dict:
        """
        Refresh the access token using refresh token
        
        Returns:
            New token dictionary
        """
        if not self.token or 'refresh_token' not in self.token:
            raise ValueError("No refresh token available")
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.token['refresh_token']
        }
        
        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()
        
        token = response.json()
        token['expires_at'] = time.time() + token.get('expires_in', 3600)
        
        self.token = token
        return token
    
    def get_access_token(self) -> str:
        """
        Get valid access token, refreshing if necessary
        
        Returns:
            Access token string
        """
        if not self.token:
            self.get_token_from_client_credentials()
        
        # Check if token is expired (with 60 second buffer)
        expires_at = self.token.get('expires_at', 0)
        if time.time() >= expires_at - 60:
            if 'refresh_token' in self.token:
                self.refresh_token()
            else:
                self.get_token_from_client_credentials()
        
        return self.token['access_token']
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get authorization headers for API requests
        
        Returns:
            Dictionary with Authorization header
        """
        access_token = self.get_access_token()
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

