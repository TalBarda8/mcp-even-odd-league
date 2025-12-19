"""
MCP Layer End-to-End Test

Tests the JSON-RPC 2.0 MCP communication layer implementation.
Tests player registration flow: Player → League Manager
"""

import sys
from pathlib import Path
import time
import subprocess
import signal

# Add SHARED to path
sys.path.insert(0, str(Path(__file__).parent / "SHARED"))

from league_sdk.mcp_client import MCPClient


def test_mcp_client_basics():
    """Test MCPClient instantiation and message formatting."""
    print("\n=== Test 1: MCPClient Basics ===")

    client = MCPClient()
    assert client.protocol_version == "league.v2"
    assert client.jsonrpc_version == "2.0"
    print("✓ MCPClient instantiated correctly")

    # Test message formatting
    msg = client.format_message(
        message_type="TEST_MESSAGE",
        sender="test_client",
        payload={"data": "test"}
    )

    assert msg["protocol"] == "league.v2"
    assert msg["message_type"] == "TEST_MESSAGE"
    assert msg["sender"] == "test_client"
    assert "timestamp" in msg
    assert "conversation_id" in msg
    assert msg["data"] == "test"
    print("✓ Message formatting works correctly")

    return True


def test_player_registration_flow():
    """
    Test end-to-end player registration flow.

    Assumes League Manager is running on port 8000.
    """
    print("\n=== Test 2: Player Registration Flow ===")

    client = MCPClient()

    # Format LEAGUE_REGISTER_REQUEST payload
    params = client.format_message(
        message_type="LEAGUE_REGISTER_REQUEST",
        sender="player:test_alpha",
        payload={
            "player_meta": {
                "display_name": "TestPlayer",
                "version": "1.0.0",
                "game_types": ["even_odd"],
                "contact_endpoint": "http://localhost:9999/mcp"
            }
        }
    )

    print("Sending LEAGUE_REGISTER_REQUEST to League Manager...")
    print(f"  Endpoint: http://localhost:8000/mcp")
    print(f"  Method: register_player")

    try:
        # Send request
        result = client.send_request(
            method="register_player",
            params=params,
            endpoint="http://localhost:8000/mcp",
            timeout=10
        )

        print("✓ Request sent successfully")
        print(f"  Response: {result}")

        # Validate response
        assert "protocol" in result, "Missing 'protocol' field"
        assert result["protocol"] == "league.v2", f"Invalid protocol: {result['protocol']}"
        print("✓ Protocol field correct")

        assert "message_type" in result, "Missing 'message_type' field"
        assert result["message_type"] == "LEAGUE_REGISTER_RESPONSE", f"Invalid message_type: {result['message_type']}"
        print("✓ Message type correct")

        assert "status" in result, "Missing 'status' field"
        assert result["status"] in ["ACCEPTED", "REJECTED"], f"Invalid status: {result['status']}"
        print(f"✓ Status: {result['status']}")

        if result["status"] == "ACCEPTED":
            assert "player_id" in result, "Missing 'player_id' for ACCEPTED response"
            assert "auth_token" in result, "Missing 'auth_token' for ACCEPTED response"
            assert "league_id" in result, "Missing 'league_id' for ACCEPTED response"
            print(f"  Player ID: {result['player_id']}")
            print(f"  Auth Token: {result['auth_token']}")
            print(f"  League ID: {result['league_id']}")
        else:
            assert "reason" in result, "Missing 'reason' for REJECTED response"
            print(f"  Rejection Reason: {result['reason']}")

        print("✓ All response fields valid")
        return True

    except Exception as e:
        print(f"✗ Request failed: {str(e)}")
        return False


def test_error_handling():
    """Test JSON-RPC error handling."""
    print("\n=== Test 3: Error Handling ===")

    client = MCPClient()

    # Test 3a: Invalid method
    print("Testing invalid method...")
    try:
        params = client.format_message(
            message_type="INVALID_MESSAGE",
            sender="test_client",
            payload={}
        )

        result = client.send_request(
            method="invalid_method",
            params=params,
            endpoint="http://localhost:8000/mcp",
            timeout=5
        )

        print("✗ Should have raised an error for invalid method")
        return False

    except Exception as e:
        if "Method not found" in str(e) or "-32601" in str(e):
            print(f"✓ Invalid method correctly rejected: {str(e)}")
        else:
            print(f"✗ Unexpected error: {str(e)}")
            return False

    # Test 3b: Missing required fields
    print("Testing missing required fields...")
    try:
        params = client.format_message(
            message_type="LEAGUE_REGISTER_REQUEST",
            sender="test_client",
            payload={
                # Missing player_meta
            }
        )

        result = client.send_request(
            method="register_player",
            params=params,
            endpoint="http://localhost:8000/mcp",
            timeout=5
        )

        # Should get REJECTED status, not an error
        if result["status"] == "REJECTED":
            print(f"✓ Missing fields correctly rejected: {result.get('reason', 'No reason')}")
        else:
            print("✗ Should have rejected request with missing fields")
            return False

    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return False

    return True


def test_timeout_handling():
    """Test timeout handling."""
    print("\n=== Test 4: Timeout Handling ===")

    client = MCPClient()

    print("Testing connection to non-existent endpoint...")
    try:
        params = client.format_message(
            message_type="TEST",
            sender="test_client",
            payload={}
        )

        # Try to connect to non-existent endpoint
        result = client.send_request(
            method="test",
            params=params,
            endpoint="http://localhost:9876/mcp",  # Non-existent
            timeout=2
        )

        print("✗ Should have raised a connection error")
        return False

    except Exception as e:
        if "timeout" in str(e).lower() or "connection" in str(e).lower():
            print(f"✓ Timeout/connection error correctly handled: {str(e)}")
            return True
        else:
            print(f"✗ Unexpected error: {str(e)}")
            return False


def main():
    """Run all MCP layer tests."""
    print("=" * 70)
    print("MCP Layer End-to-End Test Suite")
    print("=" * 70)

    print("\nNOTE: This test requires the League Manager to be running on port 8000.")
    print("      Start it with: python3 agents/league_manager/main.py")
    print("\nWaiting 3 seconds for you to start the League Manager if needed...")
    time.sleep(3)

    results = []

    # Test 1: MCPClient basics
    results.append(("MCPClient Basics", test_mcp_client_basics()))

    # Test 2: Player registration flow
    results.append(("Player Registration", test_player_registration_flow()))

    # Test 3: Error handling
    results.append(("Error Handling", test_error_handling()))

    # Test 4: Timeout handling
    results.append(("Timeout Handling", test_timeout_handling()))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {name}: {status}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n✓ All MCP layer tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
