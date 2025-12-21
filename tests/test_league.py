"""
League Test Script

Tests league orchestration with multiple sequential matches.
This demonstrates Phase 5 functionality:
- Multiple matches run sequentially
- Standings updated after each match
- Final standings declared at end
"""

import sys
import importlib.util
from pathlib import Path

# Get project root (parent of tests directory)
project_root = Path(__file__).parent.parent

# Add SHARED to path
sys.path.insert(0, str(project_root / "SHARED"))

# Add src to path to enable package imports
sys.path.insert(0, str(project_root / "src"))

# Import from the installed package
from mcp_even_odd_league.agents.referee_REF01.main import Referee
from mcp_even_odd_league.agents.league_manager.main import LeagueManager


def main():
    """Run a mini-league with multiple matches."""

    print("=" * 80)
    print("MCP Even/Odd League - Phase 5 League Test")
    print("=" * 80)

    print("\n📋 Test Setup:")
    print("  - League Manager: Will track standings")
    print("  - Player P01: running on port 8101 (chooses EVEN)")
    print("  - Player P02: running on port 8102 (chooses ODD)")
    print("  - Referee REF01: will orchestrate matches")
    print("  - 3 matches will be played")

    print("\n⚠️  IMPORTANT: Make sure the following agents are running:")
    print("     1. League Manager: python3 agents/league_manager/main.py")
    print("     2. Player P01: python3 agents/player_P01/main.py P01")
    print("     3. Player P02: python3 agents/player_P02/main.py P02")

    input("\nPress Enter when all agents are ready...")

    # Initialize League Manager and Referee
    print("\nInitializing League Manager...")
    league_manager = LeagueManager("league_2025_even_odd")

    print("Initializing Referee REF01...")
    referee = Referee("REF01")

    # League parameters
    league_id = "league_2025_even_odd"
    round_id = 1
    player_A_id = "P01"
    player_B_id = "P02"
    player_A_endpoint = "http://localhost:8101/mcp"
    player_B_endpoint = "http://localhost:8102/mcp"

    # Number of matches to play
    num_matches = 3

    print(f"\n🏆 Starting League: {league_id}")
    print(f"   Players: {player_A_id} vs {player_B_id}")
    print(f"   Total matches: {num_matches}")
    print()

    # Run matches
    match_results = []

    for match_num in range(1, num_matches + 1):
        match_id = f"LEAGUE_MATCH_{match_num:03d}"

        print(f"\n{'🎮 ' + '=' * 76}")
        print(f"Match {match_num}/{num_matches}: {match_id}")
        print(f"{'=' * 78}")

        try:
            # Run the match
            result = referee.run_match(
                match_id=match_id,
                player_A_id=player_A_id,
                player_B_id=player_B_id,
                player_A_endpoint=player_A_endpoint,
                player_B_endpoint=player_B_endpoint,
                league_id=league_id,
                round_id=round_id
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
        print(f"🏆 LEAGUE CHAMPION: {champion[0]} 🏆")
        print(f"   Total Points: {champion[1]['points']}")
        print(f"   Record: {champion[1]['wins']}W - {champion[1]['losses']}L - {champion[1]['draws']}D")
        print()

    print("=" * 80)
    print("✅ League test completed successfully!")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
