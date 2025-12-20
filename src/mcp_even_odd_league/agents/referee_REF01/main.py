"""
Referee - Main Entry Point

Match-level orchestrator. Manages complete lifecycle of a single match.
Based on interfaces.md - RefereeInterface.
"""
import sys

from flask import Flask, request, jsonify
from mcp_even_odd_league.league_sdk.config_loader import ConfigLoader
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
        Run a complete match between two players with timeout and retry handling.

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

        Phase 4: Now includes timeout handling and retry logic.
        - 5 second timeout for GAME_JOIN_ACK with 1 retry
        - 30 second timeout for CHOOSE_PARITY_RESPONSE with 1 retry
        - Technical loss handling after retry failure
        """
        from datetime import datetime
        import game_logic

        print(f"\n=== Starting Match {match_id} ===")
        print(f"Player A: {player_A_id} ({player_A_endpoint})")
        print(f"Player B: {player_B_id} ({player_B_endpoint})")

        # Load timeout and retry configurations from config
        JOIN_ACK_TIMEOUT = self.system_config.timeouts.game_join_ack_timeout_sec
        PARITY_RESPONSE_TIMEOUT = self.system_config.timeouts.move_timeout_sec
        MAX_RETRIES = ConfigLoader.get_max_retries()

        # Track timeouts for technical loss
        player_A_timeout = False
        player_B_timeout = False
        technical_loss_player = None

        # Step 1: Send GAME_INVITATION to both players with timeout and retry
        print("\nStep 1: Sending GAME_INVITATION to both players...")

        invitation_A = self.mcp_client.format_message(
            message_type="GAME_INVITATION",
            sender=f"referee:{self.referee_id}",
            payload={
                "auth_token": "tok-ref-placeholder",
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

        # Send invitation to Player A with retry
        ack_A = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                print(f"  Sending invitation to Player A (attempt {attempt + 1}/{MAX_RETRIES + 1})...")
                ack_A = self.mcp_client.send_request(
                    "handle_game_invitation",
                    invitation_A,
                    player_A_endpoint,
                    timeout=JOIN_ACK_TIMEOUT
                )
                print(f"  Player A accepted: {ack_A.get('accept')}")
                break
            except Exception as e:
                if "timeout" in str(e).lower() and attempt < MAX_RETRIES:
                    print(f"  ⚠️ TIMEOUT: Player A did not respond within {JOIN_ACK_TIMEOUT}s. Retrying...")
                    self.logger.log_event("TIMEOUT_GAME_JOIN_ACK", {
                        "player_id": player_A_id,
                        "match_id": match_id,
                        "attempt": attempt + 1,
                        "will_retry": True
                    })
                elif "timeout" in str(e).lower():
                    print(f"  ❌ TECHNICAL LOSS: Player A failed to respond after {MAX_RETRIES} retries")
                    self.logger.log_event("TECHNICAL_LOSS_GAME_JOIN_ACK", {
                        "player_id": player_A_id,
                        "match_id": match_id,
                        "total_attempts": MAX_RETRIES + 1
                    })
                    player_A_timeout = True
                    technical_loss_player = player_A_id
                    break
                else:
                    raise

        # Send invitation to Player B with retry
        ack_B = None
        if not player_A_timeout:  # Only if Player A didn't timeout
            for attempt in range(MAX_RETRIES + 1):
                try:
                    print(f"  Sending invitation to Player B (attempt {attempt + 1}/{MAX_RETRIES + 1})...")
                    ack_B = self.mcp_client.send_request(
                        "handle_game_invitation",
                        invitation_B,
                        player_B_endpoint,
                        timeout=JOIN_ACK_TIMEOUT
                    )
                    print(f"  Player B accepted: {ack_B.get('accept')}")
                    break
                except Exception as e:
                    if "timeout" in str(e).lower() and attempt < MAX_RETRIES:
                        print(f"  ⚠️ TIMEOUT: Player B did not respond within {JOIN_ACK_TIMEOUT}s. Retrying...")
                        self.logger.log_event("TIMEOUT_GAME_JOIN_ACK", {
                            "player_id": player_B_id,
                            "match_id": match_id,
                            "attempt": attempt + 1,
                            "will_retry": True
                        })
                    elif "timeout" in str(e).lower():
                        print(f"  ❌ TECHNICAL LOSS: Player B failed to respond after {MAX_RETRIES} retries")
                        self.logger.log_event("TECHNICAL_LOSS_GAME_JOIN_ACK", {
                            "player_id": player_B_id,
                            "match_id": match_id,
                            "total_attempts": MAX_RETRIES + 1
                        })
                        player_B_timeout = True
                        technical_loss_player = player_B_id
                        break
                    else:
                        raise

        # Handle technical loss at invitation stage
        if player_A_timeout or player_B_timeout:
            print(f"\n⚠️ Match ending due to technical loss at invitation stage")
            winner_id = player_B_id if player_A_timeout else player_A_id
            loser_id = technical_loss_player

            result = {
                "winner_id": winner_id,
                "loser_id": loser_id,
                "is_draw": False,
                "drawn_number": None,
                "number_parity": None,
                "player_A_choice": None,
                "player_B_choice": None,
                "technical_loss": True,
                "technical_loss_reason": f"{technical_loss_player} failed to respond to GAME_INVITATION"
            }

            # Skip to reporting
            self._report_technical_loss(match_id, league_id, round_id, result, player_A_id, player_B_id)
            return result

        # Step 2: Send CHOOSE_PARITY_CALL to both players with timeout and retry
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

        # Send parity call to Player A with retry
        choice_A = None
        player_A_choice = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                print(f"  Sending parity call to Player A (attempt {attempt + 1}/{MAX_RETRIES + 1})...")
                choice_A = self.mcp_client.send_request(
                    "parity_choose",
                    parity_call_A,
                    player_A_endpoint,
                    timeout=PARITY_RESPONSE_TIMEOUT
                )
                player_A_choice = choice_A.get("parity_choice")
                print(f"  Player A chose: {player_A_choice}")
                break
            except Exception as e:
                if "timeout" in str(e).lower() and attempt < MAX_RETRIES:
                    print(f"  ⚠️ TIMEOUT: Player A did not respond within {PARITY_RESPONSE_TIMEOUT}s. Retrying...")
                    self.logger.log_event("TIMEOUT_CHOOSE_PARITY", {
                        "player_id": player_A_id,
                        "match_id": match_id,
                        "attempt": attempt + 1,
                        "will_retry": True
                    })
                elif "timeout" in str(e).lower():
                    print(f"  ❌ TECHNICAL LOSS: Player A failed to respond after {MAX_RETRIES} retries")
                    self.logger.log_event("TECHNICAL_LOSS_CHOOSE_PARITY", {
                        "player_id": player_A_id,
                        "match_id": match_id,
                        "total_attempts": MAX_RETRIES + 1
                    })
                    player_A_timeout = True
                    technical_loss_player = player_A_id
                    break
                else:
                    raise

        # Send parity call to Player B with retry
        choice_B = None
        player_B_choice = None
        if not player_A_timeout:  # Only if Player A didn't timeout
            for attempt in range(MAX_RETRIES + 1):
                try:
                    print(f"  Sending parity call to Player B (attempt {attempt + 1}/{MAX_RETRIES + 1})...")
                    choice_B = self.mcp_client.send_request(
                        "parity_choose",
                        parity_call_B,
                        player_B_endpoint,
                        timeout=PARITY_RESPONSE_TIMEOUT
                    )
                    player_B_choice = choice_B.get("parity_choice")
                    print(f"  Player B chose: {player_B_choice}")
                    break
                except Exception as e:
                    if "timeout" in str(e).lower() and attempt < MAX_RETRIES:
                        print(f"  ⚠️ TIMEOUT: Player B did not respond within {PARITY_RESPONSE_TIMEOUT}s. Retrying...")
                        self.logger.log_event("TIMEOUT_CHOOSE_PARITY", {
                            "player_id": player_B_id,
                            "match_id": match_id,
                            "attempt": attempt + 1,
                            "will_retry": True
                        })
                    elif "timeout" in str(e).lower():
                        print(f"  ❌ TECHNICAL LOSS: Player B failed to respond after {MAX_RETRIES} retries")
                        self.logger.log_event("TECHNICAL_LOSS_CHOOSE_PARITY", {
                            "player_id": player_B_id,
                            "match_id": match_id,
                            "total_attempts": MAX_RETRIES + 1
                        })
                        player_B_timeout = True
                        technical_loss_player = player_B_id
                        break
                    else:
                        raise

        # Handle technical loss at parity choice stage
        if player_A_timeout or player_B_timeout:
            print(f"\n⚠️ Match ending due to technical loss at parity choice stage")
            winner_id = player_B_id if player_A_timeout else player_A_id
            loser_id = technical_loss_player

            result = {
                "winner_id": winner_id,
                "loser_id": loser_id,
                "is_draw": False,
                "drawn_number": None,
                "number_parity": None,
                "player_A_choice": player_A_choice,
                "player_B_choice": player_B_choice,
                "technical_loss": True,
                "technical_loss_reason": f"{technical_loss_player} failed to respond to CHOOSE_PARITY_CALL"
            }

            # Skip to reporting
            self._report_technical_loss(match_id, league_id, round_id, result, player_A_id, player_B_id)
            return result

        # Step 3: Draw number and determine winner (normal path)
        print("\nStep 3: Drawing number and determining winner...")

        drawn_number = game_logic.draw_random_number()
        result = game_logic.determine_winner(
            drawn_number, player_A_choice, player_B_choice,
            player_A_id, player_B_id
        )
        result["technical_loss"] = False

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

    def _report_technical_loss(self, match_id: str, league_id: str, round_id: int,
                                result: dict, player_A_id: str, player_B_id: str) -> None:
        """
        Report technical loss result to League Manager.

        Args:
            match_id: Match identifier
            league_id: League identifier
            round_id: Round number
            result: Match result with technical loss info
            player_A_id: Player A's ID
            player_B_id: Player B's ID
        """
        print("\nReporting technical loss to League Manager...")

        # Calculate scores (winner gets 3, loser gets 0)
        score = {
            result['winner_id']: 3,
            result['loser_id']: 0
        }

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
                        "technical_loss": True,
                        "technical_loss_reason": result['technical_loss_reason'],
                        "status": "TECHNICAL_LOSS"
                    }
                }
            }
        )

        league_manager_endpoint = f"http://localhost:{self.system_config.network.league_manager_port}/mcp"
        report_ack = self.mcp_client.send_request("report_match_result", match_report, league_manager_endpoint)

        print(f"  League Manager acknowledged: {report_ack.get('status')}")
        print(f"\n=== Match {match_id} Complete (Technical Loss) ===\n")


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
