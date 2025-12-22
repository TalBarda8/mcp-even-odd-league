"""
Match Test Script

Tests one complete Even/Odd match between P01 and P02 using REF01.
This demonstrates the full match flow for Phase 3.
"""

import sys
from pathlib import Path

# Get project root (parent of tests directory)
project_root = Path(__file__).parent.parent

# Add SHARED to path
sys.path.insert(0, str(project_root / "SHARED"))

# Add src to path to enable package imports
sys.path.insert(0, str(project_root / "src"))

# Import from the installed package
from mcp_even_odd_league.agents.referee_REF01.main import Referee


def main():
    """Run a complete match between P01 and P02."""

    print("=" * 80)
    print("MCP Even/Odd League - Phase 3 Match Test")
    print("=" * 80)

    print("\n📋 Test Setup:")
    print("  - League Manager: running on port 8000")
    print("  - Player P01: running on port 8101 (chooses EVEN)")
    print("  - Player P02: running on port 8102 (chooses ODD)")
    print("  - Referee REF01: will orchestrate the match")

    print("\n⚠️  IMPORTANT: Make sure the following agents are running:")
    print("     1. League Manager: python3 agents/league_manager/main.py")
    print("     2. Player P01: python3 agents/player_P01/main.py P01")
    print("     3. Player P02: python3 agents/player_P02/main.py P02")

    input("\nPress Enter when all agents are ready...")

    # Initialize Referee
    print("\nInitializing Referee REF01...")
    referee = Referee("REF01")

    # Match parameters
    match_id = "TEST_MATCH_001"
    player_A_id = "P01"
    player_B_id = "P02"
    player_A_endpoint = "http://localhost:8101/mcp"
    player_B_endpoint = "http://localhost:8102/mcp"
    league_id = "league_2025_even_odd"
    round_id = 1

    print(f"\n🎮 Starting Match: {match_id}")
    print(f"   Player A: {player_A_id} (will choose EVEN)")
    print(f"   Player B: {player_B_id} (will choose ODD)")
    print(f"   League: {league_id}, Round: {round_id}")

    try:
        # Run the match
        result = referee.run_match(
            match_id=match_id,
            player_A_id=player_A_id,
            player_B_id=player_B_id,
            player_A_endpoint=player_A_endpoint,
            player_B_endpoint=player_B_endpoint,
            league_id=league_id,
            round_id=round_id,
            report_to_league_manager=True  # This test expects League Manager to be running
        )

        # Display final result
        print("\n" + "=" * 80)
        print("🏆 MATCH RESULT")
        print("=" * 80)
        print(f"Drawn Number: {result['drawn_number']} ({result['number_parity']})")
        print(f"P01 Choice: {result['player_A_choice']}")
        print(f"P02 Choice: {result['player_B_choice']}")

        if result['is_draw']:
            print(f"\nResult: DRAW ⚖️")
        else:
            print(f"\nWinner: {result['winner_id']} 🏆")
            print(f"Loser: {result['loser_id']}")

        print("\n✅ Match completed successfully!")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"\n❌ Match failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
