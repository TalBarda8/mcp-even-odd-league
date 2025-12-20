"""
MCP Client

Protocol-compliant messaging infrastructure.
Based on interfaces.md - MCPClientInterface.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class MCPClient:
    """
    MCP Communication Client

    Handles JSON-RPC 2.0 formatting, HTTP transport, and timeout enforcement.
    """

    def __init__(self):
        """Initialize MCP client"""
        self.protocol_version = "league.v2"
        self.base_timeout = 10  # seconds
        self.jsonrpc_version = "2.0"

    def initialize(self, protocol_version: str, base_timeout: int) -> None:
        """
        Initialize the MCP client with protocol version and default timeout.

        Args:
            protocol_version: Protocol version (e.g., "league.v2")
            base_timeout: Default timeout in seconds

        TODO: Implement HTTP client initialization
        """
        self.protocol_version = protocol_version
        self.base_timeout = base_timeout
        # TODO: Initialize HTTP client library (requests, httpx, etc.)

    def send_request(self, method: str, params: Dict[str, Any], endpoint: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Send JSON-RPC 2.0 request to specified endpoint and wait for response.

        Args:
            method: JSON-RPC method name (e.g., "register_player")
            params: Message payload (already formatted with protocol fields)
            endpoint: Target HTTP endpoint (e.g., "http://localhost:8000/mcp")
            timeout: Optional timeout override (uses default if None)

        Returns:
            Response result object

        Raises:
            Exception: On network error, timeout, or JSON-RPC error
        """
        import requests

        # Use provided timeout or default
        actual_timeout = timeout if timeout is not None else self.base_timeout

        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Construct JSON-RPC 2.0 request envelope
        rpc_request = {
            "jsonrpc": self.jsonrpc_version,
            "method": method,
            "params": params,
            "id": request_id
        }

        try:
            # Send POST request to endpoint
            response = requests.post(
                endpoint,
                json=rpc_request,
                headers={"Content-Type": "application/json"},
                timeout=actual_timeout
            )

            # Parse JSON response (even if HTTP error, might contain JSON-RPC error)
            try:
                rpc_response = response.json()
            except ValueError:
                # Not JSON, check HTTP status
                response.raise_for_status()
                raise Exception("Invalid response: not JSON")

            # Check HTTP status only if we couldn't parse JSON-RPC error
            if response.status_code >= 400 and "error" not in rpc_response:
                response.raise_for_status()

            # Validate JSON-RPC response structure
            if "jsonrpc" not in rpc_response or rpc_response["jsonrpc"] != "2.0":
                raise Exception("Invalid JSON-RPC response: missing or invalid 'jsonrpc' field")

            if "id" not in rpc_response or rpc_response["id"] != request_id:
                raise Exception("Invalid JSON-RPC response: missing or mismatched 'id' field")

            # Check for error
            if "error" in rpc_response:
                error = rpc_response["error"]
                error_code = error.get("code", -1)
                error_message = error.get("message", "Unknown error")
                error_data = error.get("data", None)
                raise Exception(f"JSON-RPC error {error_code}: {error_message} (data: {error_data})")

            # Return result
            if "result" not in rpc_response:
                raise Exception("Invalid JSON-RPC response: missing 'result' field")

            return rpc_response["result"]

        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout after {actual_timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP error: {str(e)}")
        except ValueError as e:
            raise Exception(f"Invalid JSON response: {str(e)}")

    def send_notification(self, method: str, params: Dict[str, Any], endpoint: str) -> None:
        """
        Send JSON-RPC 2.0 notification (no response expected, no id field).

        Args:
            method: JSON-RPC method name
            params: Message payload
            endpoint: Target endpoint
        """
        import requests

        # Construct JSON-RPC 2.0 notification (without id field)
        rpc_notification = {
            "jsonrpc": self.jsonrpc_version,
            "method": method,
            "params": params
        }

        try:
            # Send POST request (fire-and-forget, short timeout)
            requests.post(
                endpoint,
                json=rpc_notification,
                headers={"Content-Type": "application/json"},
                timeout=2  # Short timeout for notifications
            )
            # Do not wait for or process response
        except Exception:
            # Notifications are fire-and-forget, ignore errors
            pass

    def format_message(self, message_type: str, sender: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format message payload with common protocol fields.

        Args:
            message_type: MCP message type (e.g., "ROUND_ANNOUNCEMENT")
            sender: Sender identifier (e.g., "league_manager")
            payload: Message-specific payload

        Returns:
            Formatted message object with all required fields
        """
        message = {
            "protocol": self.protocol_version,
            "message_type": message_type,
            "sender": sender,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_id": self.generate_conversation_id(message_type.lower())
        }
        message.update(payload)
        return message

    def validate_response(self, response: Dict[str, Any], expected_message_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate JSON-RPC response structure and protocol fields.

        Args:
            response: Raw response object
            expected_message_type: Expected message_type in result (optional)

        Returns:
            Validated result object

        Raises:
            Exception: If validation fails

        TODO: Implement response validation
        """
        # TODO: Validate JSON-RPC structure
        # TODO: Validate protocol fields
        # TODO: Check expected_message_type if specified
        # TODO: Return result or raise error
        pass

    def generate_conversation_id(self, prefix: str) -> str:
        """
        Generate unique conversation ID for message tracing.

        Args:
            prefix: Prefix for conversation ID (e.g., "conv-round-1")

        Returns:
            Unique conversation ID string
        """
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}-{unique_id}"

    def set_timeout(self, timeout_seconds: int) -> None:
        """
        Set default timeout for future requests.

        Args:
            timeout_seconds: Timeout in seconds
        """
        self.base_timeout = timeout_seconds
