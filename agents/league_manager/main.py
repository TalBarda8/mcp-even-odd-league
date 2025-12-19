"""
League Manager - Main Entry Point

Top-level orchestrator for the entire league system.
Based on interfaces.md - LeagueManagerInterface.
"""

import sys
from pathlib import Path

# Add SHARED to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

from flask import Flask, request, jsonify
from league_sdk.config_loader import ConfigLoader
from league_sdk.repositories import StandingsRepository, RoundsRepository
from league_sdk.logger import JsonLogger
from league_sdk.mcp_client import MCPClient
from league_sdk.config_models import SystemConfig, LeagueConfig


app = Flask(__name__)


class LeagueManager:
    """
    League Manager Implementation

    Implements LeagueManagerInterface from interfaces.md
    """

    def __init__(self, league_id: str):
        """
        Initialize League Manager.

        Args:
            league_id: League identifier
        """
        self.league_id = league_id
        self.config_loader = ConfigLoader()
        self.system_config = self.config_loader.load_system()
        self.league_config = self.config_loader.load_league(league_id)
        self.standings_repo = StandingsRepository(league_id)
        self.rounds_repo = RoundsRepository(league_id)
        self.logger = JsonLogger("league_manager", league_id)
        self.mcp_client = MCPClient()
        self.state = "WAITING_FOR_REGISTRATIONS"

        print(f"League Manager initialized for league: {league_id}")

    def start_league_manager(self) -> None:
        """
        Start League Manager HTTP server.

        TODO: Implement server initialization logic
        """
        print(f"Starting League Manager on port {self.system_config.network.league_manager_port}")
        # Server started by Flask app.run() below

    def register_referee(self, referee_meta: dict) -> dict:
        """
        Handle referee registration request.

        Args:
            referee_meta: Referee metadata

        Returns:
            Registration response

        TODO: Implement referee registration logic
        """
        # TODO: Validate referee_meta
        # TODO: Assign unique referee_id
        # TODO: Generate auth_token
        # TODO: Store in agents registry
        pass

    def register_player(self, player_meta: dict) -> dict:
        """
        Handle player registration request.

        Args:
            player_meta: Player metadata

        Returns:
            Registration response

        TODO: Implement player registration logic
        """
        # TODO: Validate player_meta
        # TODO: Assign unique player_id
        # TODO: Generate auth_token
        # TODO: Store in agents registry
        pass

    def create_schedule(self, players: list, referees: list) -> dict:
        """
        Create Round-Robin match schedule.

        Args:
            players: List of player configurations
            referees: List of referee configurations

        Returns:
            Schedule object

        TODO: Implement Round-Robin scheduling algorithm
        """
        pass

    def announce_round(self, round_id: int, matches: list) -> None:
        """
        Broadcast ROUND_ANNOUNCEMENT to all players.

        Args:
            round_id: Round number
            matches: List of matches in this round

        TODO: Implement round announcement broadcasting
        """
        pass

    def report_match_result(self, match_result: dict) -> None:
        """
        Handle MATCH_RESULT_REPORT from referee.

        Args:
            match_result: Match result data

        TODO: Implement standings update logic
        """
        pass

    def update_standings(self, round_id: int) -> None:
        """
        Broadcast LEAGUE_STANDINGS_UPDATE to all players.

        Args:
            round_id: Completed round number

        TODO: Implement standings broadcast
        """
        pass

    def announce_round_completed(self, round_id: int, next_round_id: int = None) -> None:
        """
        Broadcast ROUND_COMPLETED to all players.

        Args:
            round_id: Completed round number
            next_round_id: Next round number or None

        TODO: Implement round completion announcement
        """
        pass

    def announce_league_completed(self, total_rounds: int, total_matches: int) -> None:
        """
        Broadcast LEAGUE_COMPLETED to all players.

        Args:
            total_rounds: Total rounds played
            total_matches: Total matches played

        TODO: Implement league completion announcement
        """
        pass

    def query_standings(self, player_id: str, auth_token: str) -> dict:
        """
        Handle LEAGUE_QUERY request from player.

        Args:
            player_id: Requesting player's ID
            auth_token: Player's authentication token

        Returns:
            Standings data

        TODO: Implement standings query
        """
        pass


# Global league manager instance
league_manager = None


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
        if method == "register_player":
            from handlers import handle_league_register_request
            result = handle_league_register_request(league_manager, params)

            # Add protocol fields
            result["protocol"] = "league.v2"
            result["message_type"] = "LEAGUE_REGISTER_RESPONSE"
            result["timestamp"] = datetime.utcnow().isoformat() + "Z"

            return jsonify({
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            })

        elif method == "register_referee":
            from handlers import handle_referee_register_request
            result = handle_referee_register_request(league_manager, params)

            # Add protocol fields
            result["protocol"] = "league.v2"
            result["message_type"] = "REFEREE_REGISTER_RESPONSE"
            result["timestamp"] = datetime.utcnow().isoformat() + "Z"

            return jsonify({
                "jsonrpc": "2.0",
                "result": result,
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
    global league_manager

    # Default league ID
    league_id = "league_2025_even_odd"

    # Initialize League Manager
    league_manager = LeagueManager(league_id)
    league_manager.start_league_manager()

    # Start Flask server
    port = league_manager.system_config.network.league_manager_port
    print(f"\n=== League Manager Starting ===")
    print(f"League ID: {league_id}")
    print(f"Port: {port}")
    print(f"Endpoint: http://localhost:{port}/mcp")
    print("================================\n")

    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == "__main__":
    main()
