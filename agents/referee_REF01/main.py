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

    def run_match(self, match_id: str, player_A_id: str, player_B_id: str,
                  player_A_endpoint: str, player_B_endpoint: str,
                  league_id: str, round_id: int) -> dict:
        """
        Run a complete match between two players (happy path).

        Args:
            match_id: Match identifier
            player_A_id: Player A's ID
            player_B_id: Player B's ID
            player_A_endpoint: Player A's MCP endpoint
            player_B_endpoint: Player B's MCP endpoint
            league_id: League identifier
            round_id: Round number

        Returns:
            Match result dictionary

        NOTE: This is a simplified happy-path implementation for Phase 3.
        No timeouts, retries, or error handling.
        """
        from datetime import datetime
        import game_logic

        print(f"\n=== Starting Match {match_id} ===")
        print(f"Player A: {player_A_id} ({player_A_endpoint})")
        print(f"Player B: {player_B_id} ({player_B_endpoint})")

        # Step 1: Send GAME_INVITATION to both players
        print("\nStep 1: Sending GAME_INVITATION to both players...")

        invitation_A = self.mcp_client.format_message(
            message_type="GAME_INVITATION",
            sender=f"referee:{self.referee_id}",
            payload={
                "auth_token": "tok-ref-placeholder",  # Placeholder for Phase 3
                "league_id": league_id,
                "round_id": round_id,
                "match_id": match_id,
                "game_type": "even_odd",
                "role_in_match": "PLAYER_A",
                "opponent_id": player_B_id
            }
        )

        invitation_B = self.mcp_client.format_message(
            message_type="GAME_INVITATION",
            sender=f"referee:{self.referee_id}",
            payload={
                "auth_token": "tok-ref-placeholder",
                "league_id": league_id,
                "round_id": round_id,
                "match_id": match_id,
                "game_type": "even_odd",
                "role_in_match": "PLAYER_B",
                "opponent_id": player_A_id
            }
        )

        ack_A = self.mcp_client.send_request("handle_game_invitation", invitation_A, player_A_endpoint)
        ack_B = self.mcp_client.send_request("handle_game_invitation", invitation_B, player_B_endpoint)

        print(f"  Player A accepted: {ack_A.get('accept')}")
        print(f"  Player B accepted: {ack_B.get('accept')}")

        # Step 2: Send CHOOSE_PARITY_CALL to both players
        print("\nStep 2: Sending CHOOSE_PARITY_CALL to both players...")

        parity_call_A = self.mcp_client.format_message(
            message_type="CHOOSE_PARITY_CALL",
            sender=f"referee:{self.referee_id}",
            payload={
                "auth_token": "tok-ref-placeholder",
                "match_id": match_id,
                "player_id": player_A_id,
                "game_type": "even_odd",
                "context": {
                    "opponent_id": player_B_id,
                    "round_id": round_id,
                    "your_standings": {"wins": 0, "losses": 0, "draws": 0, "points": 0}
                },
                "deadline": (datetime.utcnow().isoformat() + "Z")
            }
        )

        parity_call_B = self.mcp_client.format_message(
            message_type="CHOOSE_PARITY_CALL",
            sender=f"referee:{self.referee_id}",
            payload={
                "auth_token": "tok-ref-placeholder",
                "match_id": match_id,
                "player_id": player_B_id,
                "game_type": "even_odd",
                "context": {
                    "opponent_id": player_A_id,
                    "round_id": round_id,
                    "your_standings": {"wins": 0, "losses": 0, "draws": 0, "points": 0}
                },
                "deadline": (datetime.utcnow().isoformat() + "Z")
            }
        )

        choice_A = self.mcp_client.send_request("parity_choose", parity_call_A, player_A_endpoint)
        choice_B = self.mcp_client.send_request("parity_choose", parity_call_B, player_B_endpoint)

        player_A_choice = choice_A.get("parity_choice")
        player_B_choice = choice_B.get("parity_choice")

        print(f"  Player A chose: {player_A_choice}")
        print(f"  Player B chose: {player_B_choice}")

        # Step 3: Draw number and determine winner
        print("\nStep 3: Drawing number and determining winner...")

        drawn_number = game_logic.draw_random_number()
        result = game_logic.determine_winner(
            drawn_number, player_A_choice, player_B_choice,
            player_A_id, player_B_id
        )

        print(f"  Drawn number: {drawn_number} ({result['number_parity']})")
        if result['is_draw']:
            print(f"  Result: DRAW")
        else:
            print(f"  Winner: {result['winner_id']}")

        # Step 4: Send GAME_OVER to both players
        print("\nStep 4: Sending GAME_OVER to both players...")

        game_over_msg = self.mcp_client.format_message(
            message_type="GAME_OVER",
            sender=f"referee:{self.referee_id}",
            payload={
                "auth_token": "tok-ref-placeholder",
                "match_id": match_id,
                "game_type": "even_odd",
                "game_result": {
                    "status": "DRAW" if result['is_draw'] else "WIN",
                    "winner_player_id": result['winner_id'],
                    "drawn_number": drawn_number,
                    "number_parity": result['number_parity'],
                    "choices": {
                        player_A_id: player_A_choice,
                        player_B_id: player_B_choice
                    },
                    "reason": f"Number {drawn_number} is {result['number_parity']}. " +
                             (f"{result['winner_id']} wins." if not result['is_draw'] else "Both chose correctly. DRAW.")
                }
            }
        )

        ack_A = self.mcp_client.send_request("notify_match_result", game_over_msg, player_A_endpoint)
        ack_B = self.mcp_client.send_request("notify_match_result", game_over_msg, player_B_endpoint)

        print(f"  Player A acknowledged: {ack_A.get('status')}")
        print(f"  Player B acknowledged: {ack_B.get('status')}")

        # Step 5: Report result to League Manager
        print("\nStep 5: Reporting result to League Manager...")

        # Calculate scores (3 for win, 1 for draw, 0 for loss)
        if result['is_draw']:
            score = {player_A_id: 1, player_B_id: 1}
        elif result['winner_id'] == player_A_id:
            score = {player_A_id: 3, player_B_id: 0}
        else:
            score = {player_A_id: 0, player_B_id: 3}

        match_report = self.mcp_client.format_message(
            message_type="MATCH_RESULT_REPORT",
            sender=f"referee:{self.referee_id}",
            payload={
                "auth_token": "tok-ref-placeholder",
                "league_id": league_id,
                "round_id": round_id,
                "match_id": match_id,
                "game_type": "even_odd",
                "result": {
                    "winner": result['winner_id'],
                    "score": score,
                    "details": {
                        "drawn_number": drawn_number,
                        "choices": {
                            player_A_id: player_A_choice,
                            player_B_id: player_B_choice
                        },
                        "status": "DRAW" if result['is_draw'] else "WIN"
                    }
                }
            }
        )

        league_manager_endpoint = f"http://localhost:{self.system_config.network.league_manager_port}/mcp"
        report_ack = self.mcp_client.send_request("report_match_result", match_report, league_manager_endpoint)

        print(f"  League Manager acknowledged: {report_ack.get('status')}")
        print(f"\n=== Match {match_id} Complete ===\n")

        return result


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
