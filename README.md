# MCP Even/Odd League

**Multi-Agent Game System with Model Context Protocol**

**Course:** AI Agents with Model Context Protocol
**Institution:** [Your Institution]
**Academic Year:** 2024-2025
**Protocol Version:** league.v2
**Author:** [Your Name]

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [System Components](#system-components)
6. [Game Rules](#game-rules)
7. [MCP Protocol](#mcp-protocol)
8. [Running the League](#running-the-league)
9. [Testing](#testing)
10. [Configuration](#configuration)
11. [Troubleshooting](#troubleshooting)
12. [Project Structure](#project-structure)
13. [Documentation](#documentation)
14. [Contributing](#contributing)
15. [License](#license)

---

## Overview

### Project Description

The MCP Even/Odd League is a **multi-agent autonomous game system** where player agents compete in an Even/Odd guessing game within a structured league format. The system demonstrates practical implementation of:

- **Model Context Protocol (MCP)** for agent-to-agent communication
- **Multi-agent coordination** with autonomous decision-making
- **League management** with round-robin tournament orchestration
- **State machine design** for robust agent behavior
- **RESTful JSON-RPC 2.0** messaging over HTTP

### What is the Even/Odd Game?

In each match:
1. Referee draws a random number (1-10)
2. Both players simultaneously choose "even" or "odd"
3. Player who correctly guesses the parity wins
4. If both guess the same (both correct or both wrong), it's a draw

### System Goals

**Academic Objectives:**
- Implement autonomous agents following formal protocol specifications
- Design extensible multi-agent systems
- Practice software engineering best practices for distributed systems
- Demonstrate competency in asynchronous communication protocols

**Technical Achievements:**
- Full MCP protocol compliance with JSON-RPC 2.0
- Autonomous player agents with state management
- Centralized league orchestration with standings tracking
- Referee arbitration with fairness guarantees
- Comprehensive error handling and timeouts

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     League Manager                           │
│  - Orchestrates rounds                                       │
│  - Tracks standings                                          │
│  - Publishes results                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐           ┌────────▼───────┐
│   Referee      │           │   Referee      │
│   (REF01)      │           │   (REF02)      │
│  - Runs match  │           │  - Runs match  │
│  - Draws num   │           │  - Draws num   │
│  - Declares    │           │  - Declares    │
│    winner      │           │    winner      │
└───┬───────┬────┘           └───┬───────┬────┘
    │       │                    │       │
┌───▼──┐ ┌──▼──┐            ┌───▼──┐ ┌──▼──┐
│ P01  │ │ P02 │            │ P03  │ │ P04 │
│Even  │ │Odd  │            │Even  │ │Odd  │
│Agent │ │Agent│            │Agent │ │Agent│
└──────┘ └─────┘            └──────┘ └─────┘
```

### Communication Protocol

All components communicate via **HTTP POST** requests to `/mcp` endpoints using **JSON-RPC 2.0** format. See [docs/architecture/mcp_message_contracts.md](docs/architecture/mcp_message_contracts.md) for complete message specifications.

### Design Principles

1. **Protocol-First Design:** All interactions defined by formal message contracts
2. **State Machines:** Each agent maintains explicit state with validated transitions
3. **Separation of Concerns:** League orchestration, match arbitration, and player strategy are independent
4. **Fail-Safe Defaults:** Timeouts, retries, and graceful degradation built-in
5. **Extensibility:** Plugin architecture for future game types

**Reference:** See [docs/architecture/block_architecture.md](docs/architecture/block_architecture.md) for detailed component breakdown.

---

## Installation

### System Requirements

- **Python:** 3.9 or higher
- **Operating System:** macOS, Linux, or Windows
- **RAM:** Minimum 2GB
- **Network:** Localhost connectivity (no external network required)

### Step 1: Clone the Repository

```bash
git clone https://github.com/TalBarda8/mcp-even-odd-league.git
cd mcp-even-odd-league
```

### Step 2: Install Package

The project is structured as a proper Python package. Install in development mode:

```bash
pip3 install -e ".[dev]"
```

This installs:
- **Core dependencies:** `flask`, `requests`
- **Development tools:** `pytest`, `pytest-cov`, `python-dotenv`
- **Package:** `mcp-even-odd-league` in editable mode

**Alternative (production install without dev tools):**
```bash
pip3 install -e .
```

### Step 3: Verify Installation

```bash
python3 -c "import mcp_even_odd_league; print(f'Package installed: v{mcp_even_odd_league.__version__}')"
```

**Expected output:**
```
Package installed: v0.1.0
```

---

## Quick Start

### Running a Full League (4 Players)

**Terminal 1 - League Manager:**
```bash
python3 agents/league_manager/main.py
```

**Terminal 2 - Player P01:**
```bash
python3 agents/player_P01/main.py P01
```

**Terminal 3 - Player P02:**
```bash
python3 agents/player_P02/main.py P02
```

**Terminal 4 - Player P03:**
```bash
python3 agents/player_P03/main.py P03
```

**Terminal 5 - Player P04:**
```bash
python3 agents/player_P04/main.py P04
```

**Terminal 6 - Run League:**
```bash
python3 test_full_league.py
```

### Expected Output

```
================================================================================
MCP Even/Odd League - Phase 6 Full League Test
================================================================================

📋 Test Setup:
  - League Manager: Tracking standings
  - Referee REF01: Orchestrating matches
  - 4 Players:
    • P01: port 8101 (prefers EVEN)
    • P02: port 8102 (prefers ODD)
    • P03: port 8103 (prefers EVEN)
    • P04: port 8104 (prefers ODD)
  - Format: Round-Robin (6 matches total)

🏆 Starting League: league_2025_even_odd
   Format: Round-Robin
   Players: P01, P02, P03, P04
   Total matches: 6

🎮 ============================================================================
Match 1/6: P01 vs P02 (LEAGUE_MATCH_001)
==============================================================================
...
```

The test orchestrates **6 matches** (every player plays every other player once) and displays:
- Real-time match results
- Standings after each match
- Final league champion

---

## System Components

### 1. League Manager

**Purpose:** Orchestrates the league, tracks standings, and coordinates referees.

**Responsibilities:**
- Register players
- Schedule round-robin matches
- Maintain standings (wins, losses, draws, points)
- Publish standings updates to players
- Declare league winner

**Endpoint:** `http://localhost:8000/mcp`

**State Machine:** IDLE → REGISTERING → ROUND_IN_PROGRESS → ROUND_COMPLETE → LEAGUE_COMPLETE

**Reference:** [docs/architecture/interfaces.md#leaguemanagerinterface](docs/architecture/interfaces.md#leaguemanagerinterface)

---

### 2. Referee

**Purpose:** Arbitrates individual matches with complete impartiality.

**Responsibilities:**
- Invite players to matches
- Collect parity choices from both players
- Draw random number (1-10)
- Determine winner based on parity
- Handle timeouts and technical losses
- Report results to League Manager

**Endpoint:** Instantiated per-match (no persistent HTTP server)

**Match Flow:**
1. Send `GAME_INVITATION` to both players
2. Wait for `GAME_JOIN_ACK` (5-second timeout)
3. Send `CHOOSE_PARITY_CALL` to both players
4. Wait for `CHOOSE_PARITY_RESPONSE` (30-second timeout)
5. Draw random number, determine winner
6. Send `GAME_OVER` notification to both players
7. Send `MATCH_RESULT_REPORT` to League Manager

**Reference:** [docs/assignment/chapter_08_game_flow.md](docs/assignment/chapter_08_game_flow.md)

---

### 3. Player Agent

**Purpose:** Autonomous participant in matches with strategic decision-making.

**Responsibilities:**
- Accept/reject game invitations
- Choose "even" or "odd" when requested
- Maintain internal state across matches
- Handle match results and update strategy
- Respond within protocol timeouts

**Endpoints:**
- Player P01: `http://localhost:8101/mcp`
- Player P02: `http://localhost:8102/mcp`
- Player P03: `http://localhost:8103/mcp`
- Player P04: `http://localhost:8104/mcp`

**State Machine:** IDLE → INVITED → CHOOSING → WAITING_RESULT → IDLE

**Current Strategy:**
- P01, P03: Always choose "even"
- P02, P04: Always choose "odd"

**Note:** Strategy is intentionally simplistic for protocol demonstration. Advanced strategies can be implemented in `agents/player_*/strategy.py` (future extension point).

**Reference:** [docs/architecture/state_machines.md#player-state-machine](docs/architecture/state_machines.md)

---

### 4. SHARED Library

**Purpose:** Common utilities shared across all agents.

**Components:**

**`league_sdk/`:**
- `config_loader.py` - Load JSON configuration files
- `config_models.py` - Pydantic models for typed configuration
- `logger.py` - JSON structured logging
- `mcp_client.py` - HTTP client for sending MCP messages
- `repositories.py` - Data persistence layer

**`data/config/`:**
- `system_config.json` - System-wide settings (ports, timeouts)
- `league_config.json` - League parameters (rounds, scoring)

**Shared Data:**
- `/SHARED/data/` - Shared database files
- `/SHARED/logs/` - Centralized JSON logs

---

## Game Rules

### Match Mechanics

1. **Initialization:**
   - Referee invites two players
   - Players must accept within 5 seconds

2. **Parity Selection:**
   - Both players choose "even" or "odd"
   - Choices made simultaneously (no information leakage)
   - 30-second timeout per player

3. **Number Drawing:**
   - Referee draws random integer from 1-10 (inclusive)
   - Number parity determines correctness

4. **Winner Determination:**

| Player A Choice | Player B Choice | Drawn Number | Result |
|----------------|----------------|--------------|---------|
| even | odd | 4 (even) | A wins |
| even | odd | 7 (odd) | B wins |
| even | even | 4 (even) | Draw (both correct) |
| even | even | 7 (odd) | Draw (both wrong) |
| odd | odd | 4 (even) | Draw (both wrong) |
| odd | odd | 7 (odd) | Draw (both correct) |

### Scoring System

- **Win:** 3 points
- **Draw:** 1 point each
- **Loss:** 0 points
- **Technical Loss:** 0 points (opponent gets 3)

### Technical Losses

A player receives a technical loss if they:
- Fail to respond to invitation within 5 seconds
- Fail to submit parity choice within 30 seconds
- Send malformed JSON
- Send invalid parity choice (not "even" or "odd")
- Crash during the match

### League Format

**Round-Robin Tournament:**
- Each player plays every other player exactly once
- With N players: N(N-1)/2 total matches
- Example: 4 players = 6 matches

**Standings Tiebreakers (in order):**
1. Total points
2. Head-to-head record
3. Win count
4. Alphabetical player ID

---

## MCP Protocol

### Protocol Overview

The system uses **JSON-RPC 2.0** over **HTTP POST** for all inter-agent communication.

**Standard Request Format:**
```json
{
  "jsonrpc": "2.0",
  "method": "handle_game_invitation",
  "params": {
    "protocol": "league.v2",
    "message_type": "GAME_INVITATION",
    "sender": "referee:REF01",
    "timestamp": "2025-01-19T10:30:00Z",
    "match_id": "MATCH_001",
    "player_id": "P01",
    "opponent_id": "P02",
    "referee_endpoint": "http://localhost:9000/mcp",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "role_in_match": "player_A"
  },
  "id": "req-123"
}
```

**Standard Response Format:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "GAME_JOIN_ACK",
    "sender": "player:P01",
    "timestamp": "2025-01-19T10:30:01Z",
    "match_id": "MATCH_001",
    "player_id": "P01",
    "arrival_timestamp": "2025-01-19T10:30:00.5Z",
    "accept": true
  },
  "id": "req-123"
}
```

### Message Types

**Referee → Player:**
1. `GAME_INVITATION` - Invite to match
2. `CHOOSE_PARITY_CALL` - Request parity choice
3. `GAME_OVER` - Match result notification

**Player → Referee:**
1. `GAME_JOIN_ACK` - Accept/reject invitation
2. `CHOOSE_PARITY_RESPONSE` - Submit parity choice
3. `GAME_OVER_ACK` - Acknowledge match result

**Referee → League Manager:**
1. `MATCH_RESULT_REPORT` - Report match outcome

**League Manager → Player:**
1. `ROUND_ANNOUNCEMENT` - Upcoming matches
2. `LEAGUE_STANDINGS_UPDATE` - Current standings
3. `ROUND_COMPLETED` - Round finished
4. `LEAGUE_COMPLETED` - League finished

**Complete Specification:** [docs/architecture/mcp_message_contracts.md](docs/architecture/mcp_message_contracts.md)

### Timeouts

| Message Type | Maximum Response Time |
|-------------|----------------------|
| GAME_JOIN_ACK | 5 seconds |
| CHOOSE_PARITY_RESPONSE | 30 seconds |
| All others | 10 seconds |

**Timeout Behavior:**
- Referee retries once on timeout
- Second timeout → Technical loss
- Opponent wins by default

---

## Running the League

### Step-by-Step Execution

#### 1. Start League Manager

```bash
python3 agents/league_manager/main.py
```

**Expected Output:**
```
League Manager initialized for league: league_2025_even_odd
Starting League Manager on port 8000

=== League Manager Starting ===
League ID: league_2025_even_odd
Port: 8000
Endpoint: http://localhost:8000/mcp
================================

 * Serving Flask app 'main'
 * Running on http://127.0.0.1:8000
```

#### 2. Start Player Agents

**In separate terminals:**

```bash
# Terminal 2
python3 agents/player_P01/main.py P01

# Terminal 3
python3 agents/player_P02/main.py P02

# Terminal 4
python3 agents/player_P03/main.py P03

# Terminal 5
python3 agents/player_P04/main.py P04
```

**Expected Output (per player):**
```
Player initialized: P01
Starting Player P01

=== Player Starting ===
Player ID: P01
Port: 8101
Endpoint: http://localhost:8101/mcp
=======================

 * Serving Flask app 'main'
 * Running on http://127.0.0.1:8101
```

#### 3. Run the League

```bash
python3 test_full_league.py
```

This orchestrates the full round-robin tournament with real-time output.

### Alternative: Run Individual Match

For quick testing of a single match:

```bash
# Ensure League Manager and 2 players are running
python3 test_match.py
```

---

## Testing

### Test Suite Overview

The project includes comprehensive testing at two levels:

#### Unit Tests
Tests for core business logic (no Flask servers required):

| Test File | Purpose | Modules Tested | Coverage |
|----------|---------|----------------|----------|
| `tests/unit/test_game_logic.py` | Even/Odd game mechanics | `game_logic.py` | 100% |
| `tests/unit/test_config_loader.py` | Configuration loading | `config_loader.py`, `config_models.py` | 84.78%, 94.59% |

#### Integration/System Tests
End-to-end tests with running agents:

| Test File | Purpose | Components Tested |
|----------|---------|-------------------|
| `tests/test_skeleton.py` | Basic component instantiation | All agents |
| `tests/test_mcp_layer.py` | MCP message formatting | MCPClient, JSON-RPC |
| `tests/test_match.py` | Single match execution | Referee, 2 Players |
| `tests/test_league.py` | Multi-match league | League Manager, Referee, 2 Players |
| `tests/test_full_league.py` | Complete round-robin | All components, 4 Players |
| `tests/test_timeout.py` | Timeout and error handling | Referee timeout logic |

### Running Tests

#### Install Test Dependencies

```bash
pip3 install -e ".[dev]"
```

This installs the package in development mode with pytest, pytest-cov, and other dev dependencies.

#### Run Unit Tests Only

```bash
pytest tests/unit/ -v
```

#### Run Integration Tests

```bash
# Run all integration tests
pytest tests/ --ignore=tests/unit/ -v

# Run specific integration test
pytest tests/test_match.py -v
```

#### Run All Tests

```bash
pytest tests/ -v
```

#### Run with Timeout Protection

```bash
pytest tests/ --timeout=60
```

### Test Coverage

The project achieves **>70% coverage on core logic modules** as required by submission guidelines.

#### Generate Coverage Report

**Terminal output:**
```bash
pytest tests/unit/ --cov=src/mcp_even_odd_league --cov-report=term-missing
```

**HTML report (recommended):**
```bash
pytest tests/unit/ --cov=src/mcp_even_odd_league --cov-report=html
open htmlcov/index.html
```

#### Coverage Results

**Core Logic Modules (Business Logic):**
- `game_logic.py`: **100%** ✓
- `config_loader.py`: **84.78%** ✓
- `config_models.py`: **94.59%** ✓

**Note:** Overall coverage appears lower (~11%) because Flask endpoints and main.py files are tested via integration tests, not unit tests. The core business logic (game mechanics, configuration) exceeds the 70% requirement.

#### Interpreting Coverage Reports

The HTML coverage report (`htmlcov/index.html`) provides:
- Line-by-line coverage visualization
- Missing lines highlighted in red
- Per-module coverage percentages
- Branch coverage analysis

**What's NOT included in unit test coverage (by design):**
- Flask route handlers (`@app.route` functions)
- Main entry points (`main()` functions)
- MCP client HTTP calls (integration layer)

These components are tested via integration/system tests in `tests/test_*.py`.

**For comprehensive testing documentation, see [TESTING.md](TESTING.md)**.

---

## Configuration

### System Configuration

**File:** `SHARED/data/config/system_config.json`

```json
{
  "league_manager": {
    "port": 8000,
    "host": "localhost"
  },
  "players": [
    {"id": "P01", "port": 8101},
    {"id": "P02", "port": 8102},
    {"id": "P03", "port": 8103},
    {"id": "P04", "port": 8104}
  ],
  "timeouts": {
    "game_join_ack": 5,
    "parity_choice": 30,
    "default": 10
  },
  "retry_policy": {
    "max_attempts": 2,
    "backoff_seconds": 1
  }
}
```

### League Configuration

**File:** `SHARED/data/config/league_config.json`

```json
{
  "league_id": "league_2025_even_odd",
  "format": "round_robin",
  "scoring": {
    "win": 3,
    "draw": 1,
    "loss": 0,
    "technical_loss": 0
  },
  "match_settings": {
    "number_range": [1, 10],
    "random_seed": null
  }
}
```

### Environment Variables

**Create `.env` file** (optional, for production deployment):

```bash
# Server Configuration
LEAGUE_MANAGER_HOST=localhost
LEAGUE_MANAGER_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/league.log

# Database
DB_PATH=SHARED/data/league.db

# Timeouts (seconds)
TIMEOUT_GAME_JOIN=5
TIMEOUT_PARITY_CHOICE=30
TIMEOUT_DEFAULT=10
```

**Note:** `.env` file is gitignored. Use `example.env` as template (to be created).

---

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find and kill process on port 8101
lsof -ti:8101 | xargs kill -9

# Verify port is free
lsof -ti:8101
```

#### 2. Players Not Responding

**Symptoms:**
- Referee reports "timeout waiting for response"
- Match results in technical loss

**Debug Steps:**
1. Verify player process is running: `lsof -ti:8101`
2. Check player logs: `tail -f logs/player_P01.log`
3. Test player endpoint:
   ```bash
   curl -X POST http://localhost:8101/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"ping","params":{},"id":"test"}'
   ```

#### 3. JSON Parsing Errors

**Error:**
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Causes:**
- Malformed JSON in request/response
- Empty response body
- Incorrect Content-Type header

**Solution:**
- Validate JSON with: `python3 -m json.tool < message.json`
- Ensure all MCP messages include `"jsonrpc": "2.0"`
- Set header: `Content-Type: application/json`

#### 4. State Machine Violations

**Error:**
```
Invalid state for GAME_INVITATION: current state is CHOOSING, expected IDLE
```

**Cause:** Player received message in wrong state (likely due to previous match not completing).

**Solution:**
1. Restart player agent
2. Verify match completion logic in `handlers.py`
3. Check state transition logs: `grep "State transition" logs/player_*.log`

### Debug Mode

Enable verbose logging:

**In player main.py:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Run with debug output:**
```bash
python3 agents/player_P01/main.py P01 --debug
```

---

## Project Structure

```
mcp-even-odd-league/
├── src/                             # Python package source (src layout)
│   └── mcp_even_odd_league/         # Main package
│       ├── __init__.py              # Package root
│       ├── agents/                  # Autonomous agent implementations
│       │   ├── league_manager/      # League orchestration
│       │   │   ├── main.py          # Entry point, Flask server
│       │   │   ├── handlers.py      # MCP message handlers
│       │   │   └── scheduler.py     # Round-robin scheduling
│       │   ├── referee_REF01/       # Match arbitration
│       │   │   ├── main.py          # Referee logic
│       │   │   ├── game_logic.py    # Even/Odd game mechanics
│       │   │   └── handlers.py      # MCP message handlers
│       │   ├── player_P01/          # Player agent (EVEN strategy)
│       │   │   ├── main.py          # Entry point, Flask server
│       │   │   ├── handlers.py      # MCP message handlers
│       │   │   └── strategy.py      # Parity choice strategy
│       │   ├── player_P02/          # Player agent (ODD strategy)
│       │   ├── player_P03/          # Player agent (EVEN strategy)
│       │   └── player_P04/          # Player agent (ODD strategy)
│       └── league_sdk/              # Common SDK for all agents
│           ├── config_loader.py     # Configuration management
│           ├── config_models.py     # Pydantic data models
│           ├── logger.py            # JSON structured logging
│           ├── mcp_client.py        # MCP HTTP client
│           └── repositories.py      # Data persistence
│
├── tests/                           # Test suite
│   ├── unit/                        # Unit tests (core logic)
│   │   ├── test_game_logic.py       # Game mechanics tests (100% coverage)
│   │   └── test_config_loader.py    # Configuration tests (84.78% coverage)
│   ├── test_skeleton.py             # Component instantiation tests
│   ├── test_mcp_layer.py            # MCP protocol tests
│   ├── test_match.py                # Single match integration test
│   ├── test_league.py               # Multi-match league test
│   ├── test_full_league.py          # Full round-robin test
│   └── test_timeout.py              # Timeout handling tests
│
├── SHARED/                          # Shared data and configuration
│   ├── data/                        # Shared data directory
│   │   └── config/                  # Configuration files
│   │       ├── system_config.json   # System-wide settings
│   │       └── league_config.json   # League parameters
│   └── logs/                        # Centralized log directory
│
├── docs/                            # Comprehensive documentation
│   ├── assignment/                  # Assignment specifications
│   │   ├── chapter_06_requirements.md  # Assignment requirements
│   │   ├── chapter_08_game_flow.md     # Game flow and rules
│   │   └── chapter_09_protocol.md      # MCP protocol details
│   └── architecture/                # Architecture documentation
│       ├── interfaces.md            # Formal interface contracts
│       ├── state_machines.md        # State machine diagrams
│       ├── mcp_message_contracts.md # Complete message specs
│       ├── block_architecture.md    # Component breakdown
│       ├── class_map.md             # Class relationships
│       └── project_tree_mapping.md  # Directory structure guide
│
├── pyproject.toml                   # Package metadata and build config
├── .gitignore                       # Git exclusions
└── README.md                        # This file
```

**Key Structure Features:**
- **src/ layout**: Modern Python packaging best practice (PEP 518/PEP 517)
- **Proper package**: Installable via `pip install -e .`
- **Separated tests**: Unit tests in `tests/unit/`, integration tests in `tests/`
- **Configuration**: Centralized in `SHARED/data/config/`
- **Editable install**: Changes to source immediately reflected without reinstall

**Detailed Mapping:** See [docs/architecture/project_tree_mapping.md](docs/architecture/project_tree_mapping.md)

---

## Documentation

### Academic Documentation

All documentation is structured per the assignment specifications:

#### Assignment Requirements
- [chapter_06_requirements.md](docs/assignment/chapter_06_requirements.md) - Mandatory tasks and deliverables
- [chapter_08_game_flow.md](docs/assignment/chapter_08_game_flow.md) - Game mechanics and match flow
- [chapter_09_protocol.md](docs/assignment/chapter_09_protocol.md) - MCP protocol specification

#### Architecture Design
- [interfaces.md](docs/architecture/interfaces.md) - Formal interface contracts for all components
- [state_machines.md](docs/architecture/state_machines.md) - State machine diagrams and transitions
- [mcp_message_contracts.md](docs/architecture/mcp_message_contracts.md) - Complete MCP message catalog
- [block_architecture.md](docs/architecture/block_architecture.md) - Component responsibilities
- [class_map.md](docs/architecture/class_map.md) - Class relationships and dependencies
- [project_tree_mapping.md](docs/architecture/project_tree_mapping.md) - Directory structure explained

### Additional Resources

**Original Assignment PDFs:**
- `chapter_06_assignment.pdf` - Assignment overview
- `chapter_08_game_flow.pdf` - Game rules and flow
- `chapter_09_protocol.pdf` - Protocol specification
- `chapter_10_classes.pdf` - Class design
- `chapter_11_project_structure.pdf` - Project organization
- `software_submission_guidelines (1).pdf` - Submission requirements

---

## Contributing

This is an academic project for course credit. External contributions are not accepted. However, students in the same course are encouraged to:

1. **Protocol Compliance Testing:** Exchange player agents to verify interoperability
2. **Bug Reports:** Report protocol violations or crashes
3. **Strategy Discussion:** Share insights on decision-making approaches (without sharing code)

### Code Style

- **Language:** Python 3.9+
- **Style Guide:** PEP 8
- **Line Length:** 100 characters maximum
- **Docstrings:** Google-style docstrings for all public methods
- **Type Hints:** Use type annotations where beneficial

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/player-advanced-strategy

# Make changes and commit
git add agents/player_P01/strategy.py
git commit -m "Implement adaptive parity selection strategy"

# Push to remote
git push origin feature/player-advanced-strategy
```

**Commit Message Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:** feat, fix, docs, test, refactor, chore

---

## License

**Academic Use Only**

This project is submitted as part of academic coursework for **AI Agents with Model Context Protocol** course. All rights reserved by the author.

**Permitted:**
- View source code for educational purposes
- Run locally for testing and learning
- Reference in academic citations

**Prohibited:**
- Commercial use
- Redistribution without attribution
- Plagiarism or submission as own work

**Citation:**
```
[Your Name]. (2025). MCP Even/Odd League: Multi-Agent Game System
with Model Context Protocol. [Course Name], [Institution].
https://github.com/TalBarda8/mcp-even-odd-league
```

---

## Credits

**Course:** AI Agents with Model Context Protocol
**Instructor:** Dr. Yoram Segal
**Institution:** [Your Institution]
**Academic Year:** 2024-2025

**Technologies:**
- [Flask](https://flask.palletsprojects.com/) - Web framework for MCP endpoints
- [Requests](https://requests.readthedocs.io/) - HTTP client library
- [Pytest](https://pytest.org/) - Testing framework
- [JSON-RPC 2.0](https://www.jsonrpc.org/specification) - RPC protocol

**Special Thanks:**
- Course instructor for assignment design and protocol specification
- Fellow students for interoperability testing
- Python community for excellent libraries

---

## Contact

**Author:** [Your Name]
**Email:** [Your Email]
**GitHub:** https://github.com/TalBarda8/mcp-even-odd-league

**Project Issues:** https://github.com/TalBarda8/mcp-even-odd-league/issues

---

**Document Version:** 1.0
**Last Updated:** 2025-01-20
**Status:** Active Development
