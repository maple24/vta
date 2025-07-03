# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

"""
Enhanced Network Client for HTTP operations.

This module provides a comprehensive HTTP client with enhanced error handling,
retry logic, and user-friendly APIs for REST operations.
"""

from typing import Optional, Dict, Any, Union
import json
import time
from loguru import logger

try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
except ImportError:
    logger.warning("requests library not installed. Network client may not work properly.")
    requests = None

from .base import (
    BaseClient, ClientConfig, VTAError, ConnectionError,
    OperationError, ValidationError, 
    log_operation
)


class NetworkClient(BaseClient):
    """
    Enhanced HTTP client for network operations.
    
    Features:
    - RESTful API operations (GET, POST, PUT, DELETE)
    - Automatic retry with exponential backoff
    - Session management with connection pooling
    - Request/response logging and monitoring
    - Authentication support
    - Custom headers and timeout handling
    
    Example:
        ```python
        # Basic usage
        client = NetworkClient(ClientConfig(extra_config={"base_url": "https://api.example.com"}))
        response = client.get("/users")
        
        # With authentication
        client.set_auth_token("your-api-token")
        response = client.post("/data", {"key": "value"})
        ```
    """
    
    def __init__(self, config: Optional[ClientConfig] = None):
        """
        Initialize Network client.
        
        Args:
            config: Client configuration including base_url
        """
        if requests is None:
            raise VTAError("requests library is required but not installed. Install with: pip install requests")
        
        super().__init__(config)
        
        self.base_url = self.config.extra_config.get("base_url", "")
        if not self.base_url:
            raise ValidationError("base_url is required in extra_config")
        
        self._session = None
        self._auth_headers = {}
        
        if self.config.auto_connect:
            self.connect()
    
    def connect(self) -> bool:
        """
        Initialize HTTP session with retry strategy.
        
        Returns:
            bool: True if session created successfully
        """
        try:
            self._session = requests.Session()
            
            # Configure retry strategy
            retry_strategy = Retry(
                total=self.config.retry_count,
                backoff_factor=self.config.retry_delay,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
            )
            
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=self.config.connection_pool_size,
                pool_maxsize=self.config.connection_pool_size
            )
            
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)
            
            # Set default timeout
            self._session.timeout = self.config.timeout
            
            # Test connection with a simple request
            try:
                response = self._session.head(self.base_url, timeout=5)
                self._connected = True
                logger.info(f"Successfully connected to {self.base_url}")
                return True
            except Exception as e:
                logger.warning(f"Could not verify connection to {self.base_url}: {e}")
                # Still consider it connected if session was created
                self._connected = True
                return True
                
        except Exception as e:
            raise ConnectionError(f"Failed to create HTTP session: {e}")
    
    def disconnect(self) -> bool:
        """
        Close HTTP session.
        
        Returns:
            bool: True if disconnection successful
        """
        if self._session:
            self._session.close()
            self._session = None
        
        self._connected = False
        logger.info("HTTP session closed")
        return True
    
    def is_connected(self) -> bool:
        """
        Check if HTTP session is active.
        
        Returns:
            bool: True if session is active
        """
        return self._connected and self._session is not None
    
    def set_auth_token(self, token: str, token_type: str = "Bearer"):
        """
        Set authentication token for requests.
        
        Args:
            token: Authentication token
            token_type: Type of token (Bearer, API-Key, etc.)
        """
        self._auth_headers["Authorization"] = f"{token_type} {token}"
        logger.info(f"Authentication token set with type: {token_type}")
    
    def set_custom_headers(self, headers: Dict[str, str]):
        """
        Set custom headers for all requests.
        
        Args:
            headers: Dictionary of header key-value pairs
        """
        self._auth_headers.update(headers)
        logger.info(f"Custom headers set: {list(headers.keys())}")
    
    @log_operation
    def get(self, endpoint: str, params: Optional[Dict] = None, 
            headers: Optional[Dict] = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Perform HTTP GET request.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout
            
        Returns:
            Response data as dictionary
        """
        return self._make_request("GET", endpoint, params=params, headers=headers, timeout=timeout)
    
    @log_operation
    def post(self, endpoint: str, data: Optional[Union[Dict, str]] = None, 
             json_data: Optional[Dict] = None, headers: Optional[Dict] = None, 
             timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Perform HTTP POST request.
        
        Args:
            endpoint: API endpoint path
            data: Form data or raw data
            json_data: JSON data (will be serialized)
            headers: Additional headers
            timeout: Request timeout
            
        Returns:
            Response data as dictionary
        """
        return self._make_request("POST", endpoint, data=data, json=json_data, 
                                headers=headers, timeout=timeout)
    
    @log_operation
    def put(self, endpoint: str, data: Optional[Union[Dict, str]] = None,
            json_data: Optional[Dict] = None, headers: Optional[Dict] = None,
            timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Perform HTTP PUT request.
        
        Args:
            endpoint: API endpoint path
            data: Form data or raw data
            json_data: JSON data (will be serialized)
            headers: Additional headers
            timeout: Request timeout
            
        Returns:
            Response data as dictionary
        """
        return self._make_request("PUT", endpoint, data=data, json=json_data,
                                headers=headers, timeout=timeout)
    
    @log_operation
    def delete(self, endpoint: str, headers: Optional[Dict] = None,
               timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Perform HTTP DELETE request.
        
        Args:
            endpoint: API endpoint path
            headers: Additional headers
            timeout: Request timeout
            
        Returns:
            Response data as dictionary
        """
        return self._make_request("DELETE", endpoint, headers=headers, timeout=timeout)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with error handling.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            ConnectionError: If not connected
            OperationError: If request fails
        """
        if not self.is_connected():
            raise ConnectionError("HTTP session not active")
        
        # Build full URL
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Merge headers
        request_headers = {**self._auth_headers}
        if kwargs.get('headers'):
            request_headers.update(kwargs.pop('headers'))
        
        # Set timeout
        timeout = kwargs.pop('timeout', None) or self.config.timeout
        
        try:
            logger.debug(f"Making {method} request to: {url}")
            
            response = self._session.request(
                method=method,
                url=url,
                headers=request_headers,
                timeout=timeout,
                **kwargs
            )
            
            # Log response details
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Raise for HTTP errors
            response.raise_for_status()
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                # If not JSON, return text content
                response_data = {
                    "content": response.text,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }
            
            logger.info(f"Request {method} {endpoint} completed successfully")
            return response_data
            
        except requests.exceptions.Timeout:
            raise OperationError(f"Request to {endpoint} timed out after {timeout}s")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Connection error for {endpoint}: {e}")
        except requests.exceptions.HTTPError as e:
            raise OperationError(f"HTTP error for {endpoint}: {e}")
        except Exception as e:
            raise OperationError(f"Unexpected error for {endpoint}: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the service.
        
        Returns:
            Dictionary with health status information
        """
        try:
            start_time = time.time()
            response = self._session.head(self.base_url, timeout=5)
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "status_code": response.status_code,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
