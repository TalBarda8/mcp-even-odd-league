# Testing Guide - MCP Even/Odd League

## Overview

This document provides comprehensive instructions for running tests and measuring code coverage in the MCP Even/Odd League project.

## Test Strategy

The project uses a **two-tier testing approach**:

1. **Unit Tests**: Test core business logic in isolation (no Flask servers, no HTTP calls)
2. **Integration/System Tests**: Test end-to-end functionality with running agents

This approach ensures:
- Core logic is thoroughly tested and maintainable
- System behavior is validated in realistic scenarios
- Fast feedback loop for developers (unit tests run in <1 second)

---

## Prerequisites

Install the package with development dependencies:

```bash
pip3 install -e ".[dev]"
```

This installs:
- `pytest` - Testing framework
- `pytest-cov` - Coverage measurement
- `pytest-timeout` - Timeout handling for integration tests
- `python-dotenv` - Environment variable management

---

## Unit Tests

### What is Tested

Unit tests focus on **core business logic** modules:

| Module | Location | Purpose | Coverage |
|--------|----------|---------|----------|
| `game_logic.py` | `src/mcp_even_odd_league/agents/referee_REF01/` | Even/Odd game mechanics | 100% |
| `config_loader.py` | `src/mcp_even_odd_league/league_sdk/` | Configuration loading | 84.78% |
| `config_models.py` | `src/mcp_even_odd_league/league_sdk/` | Data models | 94.59% |

### Test Files

- `tests/unit/test_game_logic.py` - 13 tests for game mechanics
- `tests/unit/test_config_loader.py` - 11 tests for configuration

### Running Unit Tests

**Run all unit tests:**
```bash
pytest tests/unit/ -v
```

**Run specific test file:**
```bash
pytest tests/unit/test_game_logic.py -v
```

**Run specific test class:**
```bash
pytest tests/unit/test_game_logic.py::TestDetermineWinner -v
```

**Run specific test:**
```bash
pytest tests/unit/test_game_logic.py::TestDetermineWinner::test_player_a_wins_with_even -v
```

### Expected Output

```
======================== test session starts =========================
collected 24 items

tests/unit/test_config_loader.py::TestConfigLoader::test_load_system_defaults PASSED [  4%]
tests/unit/test_config_loader.py::TestConfigLoader::test_load_system_network_defaults PASSED [  8%]
...
tests/unit/test_game_logic.py::TestValidateParityChoice::test_invalid_choice PASSED [100%]

======================== 24 passed in 0.36s ==========================
```

---

## Integration/System Tests

### What is Tested

Integration tests validate end-to-end system behavior with running Flask servers and MCP communication.

| Test File | Purpose | Required Processes |
|-----------|---------|-------------------|
| `tests/test_skeleton.py` | Component instantiation | None (imports only) |
| `tests/test_mcp_layer.py` | MCP message formatting | None (mocking) |
| `tests/test_match.py` | Single match flow | League Manager + 2 Players |
| `tests/test_league.py` | Multi-match league | League Manager + 2 Players |
| `tests/test_full_league.py` | Complete round-robin | League Manager + 4 Players |
| `tests/test_timeout.py` | Timeout handling | League Manager + 2 Players |

### Running Integration Tests

**Run all integration tests:**
```bash
pytest tests/ --ignore=tests/unit/ -v
```

**Run specific integration test:**
```bash
pytest tests/test_match.py -v
```

**Run with timeout protection (recommended):**
```bash
pytest tests/test_full_league.py --timeout=60 -v
```

### Notes on Integration Tests

- These tests start Flask servers on specific ports
- Tests may fail if ports are already in use
- Some tests require multiple terminal windows
- Use `lsof -ti:8000 | xargs kill -9` to clean up stuck processes

---

## Test Coverage

### Coverage Requirements

Per submission guidelines (Section 6.1):
- **Minimum**: 70% coverage of core logic modules
- **Current**: **>90% average** on core modules ✓

### Generating Coverage Reports

#### Terminal Report (Quick Check)

```bash
pytest tests/unit/ --cov=src/mcp_even_odd_league --cov-report=term-missing
```

**Output:**
```
Name                                                 Stmts   Miss  Cover   Missing
----------------------------------------------------------------------------------
src/mcp_even_odd_league/agents/referee_REF01/game_logic.py    24      0   100%
src/mcp_even_odd_league/league_sdk/config_loader.py          46      7    85%   20-21, 39, 90-96, 133
src/mcp_even_odd_league/league_sdk/config_models.py          74      4    95%   24, 55, 59, 109
----------------------------------------------------------------------------------
TOTAL                                                       1235   1099    11%
```

#### HTML Report (Detailed Analysis)

```bash
pytest tests/unit/ --cov=src/mcp_even_odd_league --cov-report=html
```

**View report:**
```bash
open htmlcov/index.html
```

The HTML report provides:
- **Line-by-line coverage**: See exactly which lines are covered
- **Branch coverage**: Identify untested conditional paths
- **File-level metrics**: Coverage percentage per module
- **Visual highlighting**: Covered lines (green), missed lines (red)

### Understanding Coverage Numbers

**Why is overall coverage only 11%?**

The overall coverage includes:
- Flask route handlers (`@app.route` decorated functions)
- Main entry points (`main()` functions)
- HTTP client code (integration layer)
- Logging and persistence utilities

These components are **intentionally not covered by unit tests** because:
1. They are integration/glue code
2. They require running servers (tested via integration tests)
3. They depend on external resources (network, filesystem)

**What matters:**

Focus on **core logic coverage**:
- `game_logic.py`: **100%** ✓
- `config_loader.py`: **84.78%** ✓
- `config_models.py`: **94.59%** ✓

All core modules exceed the 70% requirement.

---

## Coverage Configuration

Coverage settings are defined in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

**Key settings:**
- `source = ["src"]`: Only measure coverage for package code
- `omit`: Exclude test files from coverage calculation
- `exclude_lines`: Lines that don't need coverage (e.g., debug code)

---

## Running All Tests

**Run complete test suite (unit + integration):**
```bash
pytest tests/ -v
```

**Run with coverage on unit tests only:**
```bash
pytest tests/unit/ --cov=src/mcp_even_odd_league --cov-report=term-missing --cov-report=html
```

**Run with summary:**
```bash
pytest tests/ -v --tb=short
```

---

## Continuous Integration (CI) Setup

For automated testing in CI/CD pipelines:

```bash
# Install dependencies
pip3 install -e ".[dev]"

# Run unit tests with coverage
pytest tests/unit/ \
  --cov=src/mcp_even_odd_league \
  --cov-report=xml \
  --cov-report=term \
  --cov-fail-under=70

# Run integration tests with timeout
pytest tests/ --ignore=tests/unit/ --timeout=60
```

**Coverage threshold enforcement:**
- `--cov-fail-under=70`: CI fails if coverage drops below 70%
- Ensures regression prevention

---

## Troubleshooting

### Coverage Report Not Generated

**Problem:** Running `pytest --cov` but no report appears.

**Solution:**
```bash
# Verify pytest-cov is installed
pip3 list | grep pytest-cov

# Reinstall if needed
pip3 install pytest-cov
```

### "No module named mcp_even_odd_league"

**Problem:** Tests fail with import errors.

**Solution:**
```bash
# Install package in editable mode
pip3 install -e ".[dev]"

# Verify installation
python3 -c "import mcp_even_odd_league; print('OK')"
```

### HTML Coverage Report Shows Wrong Files

**Problem:** Coverage report includes virtual environment files.

**Solution:**
Edit `pyproject.toml` to ensure `source = ["src"]` is set correctly.

### Tests Hang or Timeout

**Problem:** Integration tests don't complete.

**Solution:**
```bash
# Kill stuck processes
pkill -f "python3 agents"

# Run with explicit timeout
pytest tests/test_match.py --timeout=30
```

---

## Test Development Guidelines

### Writing Unit Tests

**Good unit test characteristics:**
- Tests single function/method
- No external dependencies (network, filesystem, database)
- Fast (<10ms per test)
- Deterministic (same input = same output)
- Uses mocking for external calls

**Example:**
```python
def test_determine_winner_even_number():
    """Test that player choosing 'even' wins when number is even."""
    result = game_logic.determine_winner(
        drawn_number=4,
        player_A_choice="even",
        player_B_choice="odd",
        player_A_id="P01",
        player_B_id="P02"
    )
    assert result["winner_id"] == "P01"
    assert result["is_draw"] is False
```

### Writing Integration Tests

**Good integration test characteristics:**
- Tests realistic end-to-end scenarios
- Starts required services (League Manager, Players)
- Validates MCP message flow
- Includes cleanup (stop servers, close connections)

**Example structure:**
```python
def test_single_match():
    # Setup: Start League Manager and Players
    # Action: Trigger match via orchestrator
    # Assert: Verify match result
    # Cleanup: Stop all servers
```

---

## Coverage Goals

### Current Status

| Module | Coverage | Target | Status |
|--------|----------|--------|--------|
| game_logic.py | 100% | 70% | ✓ Exceeds |
| config_loader.py | 84.78% | 70% | ✓ Exceeds |
| config_models.py | 94.59% | 70% | ✓ Exceeds |

### Future Improvements

To further improve coverage:

1. **Add repository tests**: Test `StandingsRepository`, `RoundsRepository`
2. **Add logger tests**: Test `JsonLogger` output format
3. **Add client tests**: Mock HTTP calls in `MCPClient`

---

## Quick Reference

```bash
# Install dependencies
pip3 install -e ".[dev]"

# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/ --ignore=tests/unit/ -v

# Generate coverage report
pytest tests/unit/ --cov=src/mcp_even_odd_league --cov-report=html
open htmlcov/index.html

# Run all tests with coverage
pytest tests/ --cov=src/mcp_even_odd_league --cov-report=term-missing
```

---

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Testing Best Practices (Python)](https://docs.python-guide.org/writing/tests/)

---

**Document Version:** 1.0
**Last Updated:** 2025-01-20
**Maintainer:** Project Team
