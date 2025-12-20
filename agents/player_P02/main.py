"""
Player - Main Entry Point

Autonomous game participant. Handles match invitations, makes strategic decisions.
Based on interfaces.md - PlayerInterface.
"""

import sys
from pathlib import Path

# Add SHARED to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

from flask import Flask, request, jsonify
from league_sdk.config_loader import ConfigLoader
from league_sdk.repositories import PlayerHistoryRepository
from league_sdk.logger import JsonLogger
from league_sdk.mcp_client import MCPClient
from league_sdk.config_models import SystemConfig


app = Flask(__name__)


class Player:
    """
    Player Implementation

    Implements PlayerInterface from interfaces.md
    """

    def __init__(self, player_id: str):
        """
        Initialize Player.

        Args:
            player_id: Player identifier (e.g., "P01")
        """
        self.player_id = player_id
        self.config_loader = ConfigLoader()
        self.system_config = self.config_loader.load_system()
        self.history_repo = PlayerHistoryRepository(player_id)
        self.logger = JsonLogger(f"player:{player_id}")
        self.mcp_client = MCPClient()
        self.state = "IDLE"
        self.current_match = None
        self.assigned_parity = None

        print(f"Player initialized: {player_id}")

    def start_player(self) -> None:
        """
        Start Player HTTP server and register with League Manager.

        TODO: Implement server initialization and registration
        """
        print(f"Starting Player {self.player_id}")
        # Server started by Flask app.run() below

    def handle_round_announcement(self, round_id: int, matches: list) -> None:
        """
        Handle ROUND_ANNOUNCEMENT from League Manager.

        Args:
            round_id: Round number
            matches: List of matches in this round

        TODO: Implement round announcement processing
        """
        pass

    def handle_game_join_invite(self, match_id: str, referee_endpoint: str,
                                 opponent_id: str, league_id: str, round_id: int) -> None:
        """
        Handle GAME_JOIN_INVITE from Referee.

        Args:
            match_id: Match identifier
            referee_endpoint: Referee's endpoint
            opponent_id: Opponent player ID
            league_id: League identifier
            round_id: Round number

        TODO: Implement invitation handling and decision logic
        """
        pass

    def handle_choose_parity_request(self, match_id: str) -> None:
        """
        Handle CHOOSE_PARITY_REQUEST from Referee.

        Args:
            match_id: Match identifier

        TODO: Implement parity choice request handling
        """
        pass

    def handle_game_over(self, match_result: dict) -> None:
        """
        Handle GAME_OVER from Referee.

        Args:
            match_result: Complete match result

        TODO: Implement match result processing
        """
        pass

    def handle_league_standings_update(self, standings: list, round_id: int) -> None:
        """
        Handle LEAGUE_STANDINGS_UPDATE from League Manager.

        Args:
            standings: Current standings
            round_id: Completed round number

        TODO: Implement standings update processing
        """
        pass

    def handle_round_completed(self, round_id: int, next_round_id: int = None) -> None:
        """
        Handle ROUND_COMPLETED from League Manager.

        Args:
            round_id: Completed round number
            next_round_id: Next round number or None

        TODO: Implement round completion handling
        """
        pass

    def handle_league_completed(self, final_standings: list, total_rounds: int,
                                 total_matches: int) -> None:
        """
        Handle LEAGUE_COMPLETED from League Manager.

        Args:
            final_standings: Final standings
            total_rounds: Total rounds played
            total_matches: Total matches played

        TODO: Implement league completion handling
        """
        pass

    def query_standings(self) -> dict:
        """
        Query current standings from League Manager.

        Returns:
            Standings data

        TODO: Implement standings query
        """
        pass

    def make_parity_choice(self, match_context: dict) -> str:
        """
        Make strategic parity choice for a match.

        Args:
            match_context: Context including opponent, history, etc.

        Returns:
            Parity choice ("even" or "odd")

        TODO: Implement decision-making logic (delegates to strategy module)
        """
        pass

    def validate_state_transition(self, current_state: str, message_type: str) -> bool:
        """
        Validate if a message can be processed in the current state.

        Args:
            current_state: Current player state
            message_type: Incoming message type

        Returns:
            True if transition is valid, False otherwise

        Phase 4: Simple state validation
        State flow: IDLE → INVITED → CHOOSING → WAITING_RESULT → IDLE
        """
        valid_transitions = {
            "IDLE": ["GAME_INVITATION"],
            "INVITED": ["CHOOSE_PARITY_CALL"],
            "CHOOSING": ["GAME_OVER"],  # After sending response, we're effectively waiting
            "WAITING_RESULT": ["GAME_OVER"]
        }

        return message_type in valid_transitions.get(current_state, [])

    def transition_state(self, new_state: str, reason: str = "") -> None:
        """
        Transition to a new state.

        Args:
            new_state: Target state
            reason: Reason for transition

        Phase 4: Basic state tracking with logging
        """
        old_state = self.state
        self.state = new_state

        log_msg = f"[{self.player_id}] State transition: {old_state} → {new_state}"
        if reason:
            log_msg += f" (Reason: {reason})"
        print(log_msg)

        self.logger.log_event("STATE_TRANSITION", {
            "player_id": self.player_id,
            "old_state": old_state,
            "new_state": new_state,
            "reason": reason
        })


# Global player instance
player = None


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
        if method == "handle_game_invitation":
            from handlers import handle_game_invitation
            result = handle_game_invitation(player, params)
            return jsonify({
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            })

        elif method == "parity_choose":
            from handlers import handle_parity_choose
            result = handle_parity_choose(player, params)
            return jsonify({
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            })

        elif method == "notify_match_result":
            from handlers import handle_notify_match_result
            result = handle_notify_match_result(player, params)
            return jsonify({
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            })

        elif method in ["round_announcement", "standings_update", "round_completed", "league_completed"]:
            # Other player methods return a simple acknowledgment for now
            return jsonify({
                "jsonrpc": "2.0",
                "result": {
                    "protocol": "league.v2",
                    "message_type": "ACK",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "status": "OK",
                    "message": f"Player {player.player_id if player else 'unknown'} received {method}"
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
    global player

    # Player ID from command line or default
    player_id = sys.argv[1] if len(sys.argv) > 1 else "P01"

    # Initialize Player
    player = Player(player_id)
    player.start_player()

    # Determine port from configuration based on player_id
    player_index = {"P01": 0, "P02": 1, "P03": 2, "P04": 3}.get(player_id, 0)
    port = player.system_config.network.player_ports[player_index]

    print(f"\n=== Player Starting ===")
    print(f"Player ID: {player_id}")
    print(f"Port: {port}")
    print(f"Endpoint: http://localhost:{port}/mcp")
    print("=======================\n")

    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == "__main__":
    main()
