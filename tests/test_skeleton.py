"""
Skeleton Test Script

Tests basic imports and validates project structure.
"""

import sys
from pathlib import Path

# Add SHARED to path
sys.path.insert(0, str(Path(__file__).parent / "SHARED"))

def test_imports():
    """Test that all SDK modules can be imported."""
    print("Testing SDK imports...")

    try:
        from league_sdk import __version__, __protocol__
        print(f"✓ league_sdk imported successfully (v{__version__}, {__protocol__})")
    except Exception as e:
        print(f"✗ Failed to import league_sdk: {e}")
        return False

    try:
        from league_sdk.config_models import SystemConfig, LeagueConfig, NetworkConfig
        print("✓ config_models imported successfully")
    except Exception as e:
        print(f"✗ Failed to import config_models: {e}")
        return False

    try:
        from league_sdk.config_loader import ConfigLoader
        print("✓ config_loader imported successfully")
    except Exception as e:
        print(f"✗ Failed to import config_loader: {e}")
        return False

    try:
        from league_sdk.repositories import StandingsRepository, MatchRepository
        print("✓ repositories imported successfully")
    except Exception as e:
        print(f"✗ Failed to import repositories: {e}")
        return False

    try:
        from league_sdk.logger import JsonLogger
        print("✓ logger imported successfully")
    except Exception as e:
        print(f"✗ Failed to import logger: {e}")
        return False

    try:
        from league_sdk.mcp_client import MCPClient
        print("✓ mcp_client imported successfully")
    except Exception as e:
        print(f"✗ Failed to import mcp_client: {e}")
        return False

    return True


def test_class_instantiation():
    """Test that basic classes can be instantiated."""
    print("\nTesting class instantiation...")

    try:
        from league_sdk.config_loader import ConfigLoader
        loader = ConfigLoader()
        print("✓ ConfigLoader instantiated")
    except Exception as e:
        print(f"✗ Failed to instantiate ConfigLoader: {e}")
        return False

    try:
        from league_sdk.logger import JsonLogger
        logger = JsonLogger("test")
        print("✓ JsonLogger instantiated")
    except Exception as e:
        print(f"✗ Failed to instantiate JsonLogger: {e}")
        return False

    try:
        from league_sdk.mcp_client import MCPClient
        client = MCPClient()
        print("✓ MCPClient instantiated")
    except Exception as e:
        print(f"✗ Failed to instantiate MCPClient: {e}")
        return False

    return True


def test_project_structure():
    """Verify project structure exists."""
    print("\nVerifying project structure...")

    base = Path(__file__).parent

    required_paths = [
        "SHARED/league_sdk/__init__.py",
        "SHARED/league_sdk/config_models.py",
        "SHARED/league_sdk/config_loader.py",
        "SHARED/league_sdk/repositories.py",
        "SHARED/league_sdk/logger.py",
        "SHARED/league_sdk/mcp_client.py",
        "agents/league_manager/main.py",
        "agents/referee_REF01/main.py",
        "agents/player_P01/main.py",
        "agents/player_P02/main.py",
        ".gitignore",
    ]

    all_exist = True
    for path_str in required_paths:
        path = base / path_str
        if path.exists():
            print(f"✓ {path_str}")
        else:
            print(f"✗ Missing: {path_str}")
            all_exist = False

    return all_exist


def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP Even/Odd League - Skeleton Test")
    print("=" * 60)

    results = []

    # Test imports
    results.append(("Imports", test_imports()))

    # Test instantiation
    results.append(("Instantiation", test_class_instantiation()))

    # Test structure
    results.append(("Project Structure", test_project_structure()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{name}: {status}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n✓ All tests passed! Skeleton is ready.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
