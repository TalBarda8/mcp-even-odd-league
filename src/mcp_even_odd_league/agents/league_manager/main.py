"""
League Manager - Main Entry Point

Top-level orchestrator for the entire league system.
Based on interfaces.md - LeagueManagerInterface.
"""
import sys

from flask import Flask, request, jsonify
from mcp_even_odd_league.league_sdk.config_loader import ConfigLoader
from mcp_even_odd_league.league_sdk.repositories import StandingsRepository, RoundsRepository
from mcp_even_odd_league.league_sdk.logger import JsonLogger
from mcp_even_odd_league.league_sdk.mcp_client import MCPClient
from mcp_even_odd_league.league_sdk.config_models import SystemConfig, LeagueConfig


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

        # Phase 5: In-memory standings tracking
        # Structure: {player_id: {"wins": int, "losses": int, "draws": int, "points": int, "matches_played": int}}
        self.standings = {}
        self.total_matches = 0

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

    def initialize_player_standings(self, player_id: str) -> None:
        """
        Initialize standings entry for a player.

        Args:
            player_id: Player identifier

        Phase 5: In-memory standings initialization
        """
        if player_id not in self.standings:
            self.standings[player_id] = {
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "points": 0,
                "matches_played": 0
            }

    def update_standings_from_match(self, match_result: dict) -> None:
        """
        Update standings based on match result.

        Args:
            match_result: Match result from MATCH_RESULT_REPORT

        Phase 5: Update in-memory standings
        Scoring: Win = 3 points, Draw = 1 point, Loss = 0 points
        """
        result = match_result.get("result", {})
        score_dict = result.get("score", {})
        details = result.get("details", {})
        status = details.get("status", "")

        # Get player IDs from score dict
        player_ids = list(score_dict.keys())

        if len(player_ids) != 2:
            print(f"  ⚠️ WARNING: Expected 2 players in score, got {len(player_ids)}")
            return

        player_A_id = player_ids[0]
        player_B_id = player_ids[1]

        # Initialize if needed
        self.initialize_player_standings(player_A_id)
        self.initialize_player_standings(player_B_id)

        # Update based on result
        if status == "DRAW":
            # Both players get 1 point
            self.standings[player_A_id]["draws"] += 1
            self.standings[player_A_id]["points"] += 1
            self.standings[player_A_id]["matches_played"] += 1

            self.standings[player_B_id]["draws"] += 1
            self.standings[player_B_id]["points"] += 1
            self.standings[player_B_id]["matches_played"] += 1

        elif status == "TECHNICAL_LOSS":
            # Technical loss: winner gets 3 points, loser gets 0
            winner = result.get("winner")
            if winner == player_A_id:
                loser = player_B_id
            else:
                loser = player_A_id

            self.standings[winner]["wins"] += 1
            self.standings[winner]["points"] += 3
            self.standings[winner]["matches_played"] += 1

            self.standings[loser]["losses"] += 1
            self.standings[loser]["points"] += 0
            self.standings[loser]["matches_played"] += 1

        else:  # Normal WIN
            winner = result.get("winner")
            if winner == player_A_id:
                loser = player_B_id
            else:
                loser = player_A_id

            self.standings[winner]["wins"] += 1
            self.standings[winner]["points"] += 3
            self.standings[winner]["matches_played"] += 1

            self.standings[loser]["losses"] += 1
            self.standings[loser]["points"] += 0
            self.standings[loser]["matches_played"] += 1

        self.total_matches += 1

    def print_standings(self, title: str = "CURRENT STANDINGS") -> None:
        """
        Print current standings to console.

        Args:
            title: Title to display

        Phase 5: Console output for standings
        """
        print(f"\n{'=' * 80}")
        print(f"{title:^80}")
        print(f"{'=' * 80}")

        if not self.standings:
            print("No matches played yet.")
            print(f"{'=' * 80}\n")
            return

        # Sort by points (descending), then by wins (descending)
        sorted_standings = sorted(
            self.standings.items(),
            key=lambda x: (x[1]["points"], x[1]["wins"]),
            reverse=True
        )

        # Print header
        print(f"{'Rank':<6} {'Player':<10} {'Played':<8} {'W':<4} {'D':<4} {'L':<4} {'Points':<8}")
        print(f"{'-' * 80}")

        # Print each player
        for rank, (player_id, stats) in enumerate(sorted_standings, 1):
            print(f"{rank:<6} {player_id:<10} {stats['matches_played']:<8} "
                  f"{stats['wins']:<4} {stats['draws']:<4} {stats['losses']:<4} "
                  f"{stats['points']:<8}")

        print(f"{'=' * 80}")
        print(f"Total matches played: {self.total_matches}")
        print(f"{'=' * 80}\n")

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

        elif method == "report_match_result":
            from handlers import handle_match_result_report
            result = handle_match_result_report(league_manager, params)

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
