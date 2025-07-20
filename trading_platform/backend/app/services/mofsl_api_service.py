import requests
import json
import hashlib
import uuid
from typing import Optional, Dict, Any

from fastapi import HTTPException

# A realistic, configurable base URL for the MOFSL API
BASE_URL = "https://api.motilaloswal.com"
API_VERSION = "V.1.1.0"

class MofslApiService:
    """
    A reusable service class to interact with the MOFSL Trading API.
    """
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        client_id: str,
        password: str,
        two_fa: str,
        totp: Optional[str] = None,
        vendor_info: Optional[str] = "MyTradingApp",
        source_id: str = "WEB",
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client_id = client_id
        self.password = password
        self.two_fa = two_fa
        self.totp = totp
        self.vendor_info = vendor_info
        self.source_id = source_id
        self.base_url = BASE_URL
        self.auth_token = None
        self.user_agent = f"MOSL/{API_VERSION}"

        # Perform login to get the auth token upon initialization
        self._login()

    def _get_device_info(self) -> Dict[str, Any]:
        """Provides realistic default device and network information."""
        return {
            "macaddress": ':'.join(re.findall('..', '%012x' % uuid.getnode())),
            "clientlocalip": "192.168.1.1", # Placeholder
            "clientpublicip": "1.2.3.4", # Placeholder
            "osname": "Linux",
            "osversion": "5.15",
            "installedappid": str(uuid.uuid4()),
            "devicemodel": "Generic-PC",
            "manufacturer": "System-Builder",
            "productname": "TradingApp-Backend",
            "productversion": "1.0",
            "latitude": "19.0760",
            "longitude": "72.8777",
            "sdkversion": "Python-3.0"
        }

    def _get_url(self, api_path: str) -> str:
        """Constructs the full URL for a given API endpoint."""
        endpoints = {
            "Login": "/rest/login/v4/authdirectapi",
            "Logout": "/rest/login/v1/logout",
            "GetProfile": "/rest/login/v1/getprofile",
            "OrderBook": "/rest/book/v1/getorderbook",
            "TradeBook": "/rest/book/v1/gettradebook",
            "GetPosition": "/rest/book/v1/getposition",
            "PlaceOrder": "/rest/trans/v1/placeorder",
            "ModifyOrder": "/rest/trans/v2/modifyorder",
            "CancelOrder": "/rest/trans/v1/cancelorder",
            "GetReportMargin": "/rest/report/v1/getreportmargin",
        }
        path = endpoints.get(api_path)
        if not path:
            raise ValueError(f"Invalid API path provided: {api_path}")
        return f"{self.base_url}{path}"

    def _make_request(self, method: str, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handles making requests to the MOFSL API and processes the response."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": self.auth_token or "",
            "User-Agent": self.user_agent,
            "apikey": self.api_key,
            "apisecretkey": self.api_secret,
            "sourceid": self.source_id,
            "vendorinfo": self.vendor_info,
            **self._get_device_info(),
        }

        try:
            response = requests.request(method, url, headers=headers, data=json.dumps(data) if data else None, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            
            response_json = response.json()

            if response_json.get("status") == "ERROR":
                raise HTTPException(
                    status_code=400,
                    detail=response_json.get("message", "An unknown API error occurred."),
                )
            
            return response_json

        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=503, detail=f"Failed to connect to MOFSL API: {e}")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to decode response from MOFSL API.")

    def _login(self):
        """Logs into the MOFSL API to retrieve an authentication token."""
        url = self._get_url("Login")
        
        combined_string = self.password + self.api_key
        checksum = hashlib.sha256(combined_string.encode("utf-8")).hexdigest()
        
        payload = {
            "userid": self.client_id,
            "password": checksum,
            "2FA": self.two_fa,
            "totp": self.totp,
        }
        
        response = self._make_request("POST", url, data=payload)
        
        if response.get("status") == "SUCCESS" and response.get("AuthToken"):
            self.auth_token = response["AuthToken"]
        else:
            raise HTTPException(status_code=401, detail="MOFSL login failed.")

    def place_order(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """Places an order."""
        url = self._get_url("PlaceOrder")
        return self._make_request("POST", url, data=order_details)

    def get_positions(self) -> Dict[str, Any]:
        """Retrieves the client's current positions."""
        url = self._get_url("GetPosition")
        payload = {"clientcode": self.client_id}
        return self._make_request("POST", url, data=payload)

    def get_margin(self) -> Dict[str, Any]:
        """Retrieves the client's margin report."""
        url = self._get_url("GetReportMargin")
        payload = {"clientcode": self.client_id}
        return self._make_request("POST", url, data=payload)

    def get_order_book(self) -> Dict[str, Any]:
        """Retrieves the client's order book."""
        url = self._get_url("OrderBook")
        payload = {"clientcode": self.client_id}
        return self._make_request("POST", url, data=payload)

    def cancel_order(self, unique_order_id: str) -> Dict[str, Any]:
        """Cancels a specific order."""
        url = self._get_url("CancelOrder")
        payload = {
            "clientcode": self.client_id,
            "uniqueorderid": unique_order_id
        }
        return self._make_request("POST", url, data=payload)
