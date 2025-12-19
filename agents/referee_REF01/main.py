"""
Referee - Main Entry Point

Match-level orchestrator. Manages complete lifecycle of a single match.
Based on interfaces.md - RefereeInterface.
"""

import sys
from pathlib import Path

# Add SHARED to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

from flask import Flask, request, jsonify
from league_sdk.config_loader import ConfigLoader
from league_sdk.repositories import MatchRepository
from league_sdk.logger import JsonLogger
from league_sdk.mcp_client import MCPClient
from league_sdk.config_models import SystemConfig


app = Flask(__name__)


class Referee:
    """
    Referee Implementation

    Implements RefereeInterface from interfaces.md
    """

    def __init__(self, referee_id: str):
        """
        Initialize Referee.

        Args:
            referee_id: Referee identifier (e.g., "REF01")
        """
        self.referee_id = referee_id
        self.config_loader = ConfigLoader()
        self.system_config = self.config_loader.load_system()
        self.logger = JsonLogger(f"referee:{referee_id}")
        self.mcp_client = MCPClient()
        self.state = "IDLE"
        self.current_match = None

        print(f"Referee initialized: {referee_id}")

    def start_referee(self) -> None:
        """
        Start Referee HTTP server and register with League Manager.

        TODO: Implement server initialization and registration
        """
        print(f"Starting Referee {self.referee_id}")
        # Server started by Flask app.run() below

    def handle_match_assignment(self, match_id: str, player_A_id: str, player_B_id: str,
                                 league_id: str, round_id: int) -> None:
        """
        Handle match assignment and invite players.

        Args:
            match_id: Match identifier
            player_A_id: First player ID
            player_B_id: Second player ID
            league_id: League identifier
            round_id: Round number

        TODO: Implement match initialization and player invitations
        """
        pass

    def handle_game_join_ack(self, player_id: str, match_id: str, accept: bool, arrival_timestamp: str) -> None:
        """
        Handle GAME_JOIN_ACK from player.

        Args:
            player_id: Player ID
            match_id: Match ID
            accept: Whether player accepts
            arrival_timestamp: Arrival timestamp

        TODO: Implement arrival handling and state transition logic
        """
        pass

    def handle_game_join_timeout(self, player_id: str, retry_count: int) -> None:
        """
        Handle timeout for GAME_JOIN_ACK.

        Args:
            player_id: Player who timed out
            retry_count: Current retry count

        TODO: Implement timeout handling with retry logic
        """
        pass

    def handle_choose_parity_response(self, player_id: str, match_id: str, parity_choice: str) -> None:
        """
        Handle CHOOSE_PARITY_RESPONSE from player.

        Args:
            player_id: Player ID
            match_id: Match ID
            parity_choice: "even" or "odd"

        TODO: Implement choice collection logic
        """
        pass

    def handle_choose_parity_timeout(self, player_id: str, retry_count: int) -> None:
        """
        Handle timeout for CHOOSE_PARITY_RESPONSE.

        Args:
            player_id: Player who timed out
            retry_count: Current retry count

        TODO: Implement timeout handling with retry logic
        """
        pass

    def draw_number_and_determine_winner(self, player_A_choice: str, player_B_choice: str) -> dict:
        """
        Draw random number and determine winner.

        Args:
            player_A_choice: Player A's choice
            player_B_choice: Player B's choice

        Returns:
            Match result object

        TODO: Implement game rules and winner determination
        """
        pass

    def notify_players_and_report(self, match_result: dict) -> None:
        """
        Send GAME_OVER to players and MATCH_RESULT_REPORT to League Manager.

        Args:
            match_result: Complete match result

        TODO: Implement result notification and reporting
        """
        pass

    def reset_for_next_match(self) -> None:
        """
        Clean up and prepare for next match.

        TODO: Implement cleanup logic
        """
        pass


# Global referee instance
referee = None


@app.route('/mcp', methods=['POST'])
def handle_mcp_request():
    """
    Handle incoming MCP requests.

    This endpoint receives JSON-RPC 2.0 requests.
    """
    from datetime import datetime

    try:
        # Parse JSON request
        data = request.get_json()

        if not data:
            return jsonify({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error: Invalid JSON"
                },
                "id": None
            }), 400

        # Validate JSON-RPC structure
        if "jsonrpc" not in data or data["jsonrpc"] != "2.0":
            return jsonify({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: jsonrpc must be '2.0'"
                },
                "id": data.get("id")
            }), 400

        if "method" not in data:
            return jsonify({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid Request: missing 'method' field"
                },
                "id": data.get("id")
            }), 400

        method = data["method"]
        params = data.get("params", {})
        request_id = data.get("id")

        # Route based on method
        # For Phase 2, we only implement basic routing - handlers are stubs
        if method in ["match_assignment", "game_join_ack", "choose_parity_response"]:
            # All referee methods return a simple acknowledgment for now
            return jsonify({
                "jsonrpc": "2.0",
                "result": {
                    "protocol": "league.v2",
                    "message_type": "ACK",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "status": "OK",
                    "message": f"Referee {referee.referee_id if referee else 'unknown'} received {method}"
                },
                "id": request_id
            })
        else:
            return jsonify({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                },
                "id": request_id
            }), 404

    except Exception as e:
        return jsonify({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            },
            "id": data.get("id") if 'data' in locals() else None
        }), 500


def main():
    """Main entry point"""
    global referee

    # Referee ID from command line or default
    referee_id = sys.argv[1] if len(sys.argv) > 1 else "REF01"

    # Initialize Referee
    referee = Referee(referee_id)
    referee.start_referee()

    # Determine port based on referee_id
    # REF01 -> 8001, REF02 -> 8002
    port = 8001 if referee_id == "REF01" else 8002

    print(f"\n=== Referee Starting ===")
    print(f"Referee ID: {referee_id}")
    print(f"Port: {port}")
    print(f"Endpoint: http://localhost:{port}/mcp")
    print("========================\n")

    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == "__main__":
    main()
