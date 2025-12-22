"""
Full League Test Script - Phase 6

Tests complete league orchestration with 4 players in Round-Robin format.
This demonstrates Phase 6 functionality:
- 4 players compete in Round-Robin (6 matches total)
- Standings updated after each match
- Final standings and league winner declared
- Fully automated (no manual input required)
"""

import sys
import importlib.util
from pathlib import Path
from itertools import combinations

# Get project root (parent of tests directory)
project_root = Path(__file__).parent.parent

# Add SHARED to path
sys.path.insert(0, str(project_root / "SHARED"))

# Add src to path to enable package imports
sys.path.insert(0, str(project_root / "src"))

# Import from the installed package
from mcp_even_odd_league.agents.referee_REF01.main import Referee
from mcp_even_odd_league.agents.league_manager.main import LeagueManager


def generate_round_robin_matches(players):
    """
    Generate all Round-Robin match pairings.

    Args:
        players: List of player IDs

    Returns:
        List of tuples (player_A, player_B) for each match
    """
    return list(combinations(players, 2))


def main():
    """Run a full Round-Robin league with 4 players (6 matches)."""

    print("=" * 80)
    print("MCP Even/Odd League - Phase 6 Full League Test")
    print("=" * 80)

    print("\n📋 Test Setup:")
    print("  - League Manager: Tracking standings")
    print("  - Referee REF01: Orchestrating matches")
    print("  - 4 Players:")
    print("    • P01: port 8101 (prefers EVEN)")
    print("    • P02: port 8102 (prefers ODD)")
    print("    • P03: port 8103 (prefers EVEN)")
    print("    • P04: port 8104 (prefers ODD)")
    print("  - Format: Round-Robin (6 matches total)")

    print("\n⚠️  IMPORTANT: Ensure all agents are running:")
    print("     1. League Manager: python3 agents/league_manager/main.py")
    print("     2. Player P01: python3 agents/player_P01/main.py P01")
    print("     3. Player P02: python3 agents/player_P02/main.py P02")
    print("     4. Player P03: python3 agents/player_P03/main.py P03")
    print("     5. Player P04: python3 agents/player_P04/main.py P04")

    print("\n🚀 Starting automated league test in 3 seconds...")
    import time
    time.sleep(3)

    # Initialize League Manager and Referee
    print("\nInitializing League Manager...")
    league_manager = LeagueManager("league_2025_even_odd")

    print("Initializing Referee REF01...")
    referee = Referee("REF01")

    # League parameters
    league_id = "league_2025_even_odd"
    round_id = 1

    # Player configuration
    players = [
        {"id": "P01", "port": 8101},
        {"id": "P02", "port": 8102},
        {"id": "P03", "port": 8103},
        {"id": "P04", "port": 8104}
    ]

    # Generate Round-Robin match pairings
    player_ids = [p["id"] for p in players]
    match_pairings = generate_round_robin_matches(player_ids)

    print(f"\n🏆 Starting League: {league_id}")
    print(f"   Format: Round-Robin")
    print(f"   Players: {', '.join(player_ids)}")
    print(f"   Total matches: {len(match_pairings)}")
    print()

    # Create player endpoint lookup
    player_endpoints = {p["id"]: f"http://localhost:{p['port']}/mcp" for p in players}

    # Run matches
    match_results = []
    match_num = 0

    for player_A_id, player_B_id in match_pairings:
        match_num += 1
        match_id = f"LEAGUE_MATCH_{match_num:03d}"

        print(f"\n{'🎮 ' + '=' * 76}")
        print(f"Match {match_num}/{len(match_pairings)}: {player_A_id} vs {player_B_id} ({match_id})")
        print(f"{'=' * 78}")

        try:
            # Run the match (with league manager reporting disabled for integration test)
            result = referee.run_match(
                match_id=match_id,
                player_A_id=player_A_id,
                player_B_id=player_B_id,
                player_A_endpoint=player_endpoints[player_A_id],
                player_B_endpoint=player_endpoints[player_B_id],
                league_id=league_id,
                round_id=round_id,
                report_to_league_manager=False  # Integration test handles reporting locally
            )

            match_results.append(result)

            # Print match summary
            print(f"\n📊 Match {match_num} Summary:")
            if result.get('technical_loss'):
                print(f"   Result: TECHNICAL LOSS")
                print(f"   Winner: {result['winner_id']} (by technical loss)")
                print(f"   Reason: {result.get('technical_loss_reason', 'N/A')}")
            elif result.get('is_draw'):
                print(f"   Result: DRAW")
                print(f"   Drawn Number: {result.get('drawn_number')} ({result.get('number_parity')})")
                print(f"   Both players chose: {result.get('number_parity')}")
            else:
                print(f"   Result: WIN")
                print(f"   Winner: {result['winner_id']}")
                print(f"   Drawn Number: {result.get('drawn_number')} ({result.get('number_parity')})")
                print(f"   {player_A_id} chose: {result.get('player_A_choice')}")
                print(f"   {player_B_id} chose: {result.get('player_B_choice')}")

            # Update local standings by converting result to MATCH_RESULT_REPORT format
            if result.get('is_draw'):
                score = {player_A_id: 1, player_B_id: 1}
                status = "DRAW"
            elif result.get('technical_loss'):
                score = {result['winner_id']: 3, result['loser_id']: 0}
                status = "TECHNICAL_LOSS"
            else:
                score = {result['winner_id']: 3}
                # Add loser with 0 points
                loser_id = player_A_id if result['winner_id'] == player_B_id else player_B_id
                score[loser_id] = 0
                status = "WIN"

            match_report = {
                "match_id": match_id,
                "round_id": round_id,
                "result": {
                    "winner": result.get('winner_id'),
                    "score": score,
                    "details": {
                        "status": status
                    }
                }
            }
            league_manager.update_standings_from_match(match_report)

            # Print current standings after each match
            league_manager.print_standings(title=f"STANDINGS AFTER MATCH {match_num}")

        except Exception as e:
            print(f"\n❌ Match {match_num} failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1

    # Print final standings
    print("\n" + "=" * 80)
    print("🏆 LEAGUE COMPLETE 🏆".center(80))
    print("=" * 80)

    league_manager.print_standings(title="FINAL STANDINGS")

    # Determine league winner
    if league_manager.standings:
        sorted_standings = sorted(
            league_manager.standings.items(),
            key=lambda x: (x[1]["points"], x[1]["wins"]),
            reverse=True
        )

        champion = sorted_standings[0]
        print(f"\n🏆 LEAGUE CHAMPION: {champion[0]} 🏆")
        print(f"   Total Points: {champion[1]['points']}")
        print(f"   Record: {champion[1]['wins']}W - {champion[1]['losses']}L - {champion[1]['draws']}D")
        print()

    print("=" * 80)
    print("✅ Full league test completed successfully!")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
