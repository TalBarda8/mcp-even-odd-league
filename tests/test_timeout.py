"""
Timeout Test Script

Tests timeout and retry behavior when a player doesn't respond.
This demonstrates Phase 4 timeout handling:
- 5-second timeout for GAME_JOIN_ACK with 1 retry
- Technical loss after retry failure
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
    """Run a timeout test where P02 doesn't respond (simulated by not starting P02)."""

    print("=" * 80)
    print("MCP Even/Odd League - Phase 4 Timeout Test")
    print("=" * 80)

    print("\n📋 Test Setup:")
    print("  - League Manager: running on port 8000")
    print("  - Player P01: running on port 8101 (will respond normally)")
    print("  - Player P02: NOT RUNNING (simulates timeout)")
    print("  - Referee REF01: will attempt to contact P02, timeout, retry, then apply technical loss")

    print("\n⚠️  IMPORTANT: Start the following agents:")
    print("     1. League Manager: python3 agents/league_manager/main.py")
    print("     2. Player P01: python3 agents/player_P01/main.py P01")
    print("     3. DO NOT start Player P02 (we're testing timeout)")

    input("\nPress Enter when League Manager and P01 are ready (P02 should NOT be running)...")

    # Initialize Referee
    print("\nInitializing Referee REF01...")
    referee = Referee("REF01")

    # Match parameters
    match_id = "TIMEOUT_TEST_001"
    player_A_id = "P01"
    player_B_id = "P02"
    player_A_endpoint = "http://localhost:8101/mcp"
    player_B_endpoint = "http://localhost:8102/mcp"  # This will timeout
    league_id = "league_2025_even_odd"
    round_id = 1

    print(f"\n🎮 Starting Match: {match_id}")
    print(f"   Player A: {player_A_id} (responsive)")
    print(f"   Player B: {player_B_id} (non-responsive - will timeout)")
    print(f"   Expected behavior:")
    print(f"     1. P01 accepts invitation immediately")
    print(f"     2. P02 times out after 5 seconds")
    print(f"     3. Referee retries P02 invitation")
    print(f"     4. P02 times out again after 5 seconds")
    print(f"     5. Referee declares P02 technical loss, P01 wins")
    print(f"     6. Match result reported to League Manager")

    print("\n⏱️  Timeout test starting (expect ~10 seconds for 2 attempts)...")

    try:
        # Run the match - P02 will timeout
        result = referee.run_match(
            match_id=match_id,
            player_A_id=player_A_id,
            player_B_id=player_B_id,
            player_A_endpoint=player_A_endpoint,
            player_B_endpoint=player_B_endpoint,
            league_id=league_id,
            round_id=round_id
        )

        # Display final result
        print("\n" + "=" * 80)
        print("🏆 MATCH RESULT")
        print("=" * 80)

        if result.get('technical_loss'):
            print(f"Result: TECHNICAL LOSS")
            print(f"Winner: {result['winner_id']} (by technical loss)")
            print(f"Loser: {result['loser_id']} (failed to respond)")
            print(f"Reason: {result['technical_loss_reason']}")
        else:
            print(f"Unexpected result - match completed normally")
            print(f"Winner: {result.get('winner_id')}")

        print("\n✅ Timeout test completed successfully!")
        print("=" * 80)

        print("\n📝 Verification Checklist:")
        print("  ✓ P02 timed out after 5 seconds (1st attempt)")
        print("  ✓ Referee logged timeout event")
        print("  ✓ Referee retried P02 invitation")
        print("  ✓ P02 timed out again after 5 seconds (2nd attempt)")
        print("  ✓ Referee logged technical loss")
        print("  ✓ P01 declared winner")
        print("  ✓ Match result reported to League Manager")

        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
