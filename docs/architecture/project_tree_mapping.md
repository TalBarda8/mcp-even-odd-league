# Project Tree Structure Mapping

**Even/Odd League System - Project Structure to Block Architecture Mapping**

**Document Version:** 1.0
**Last Updated:** 2025-01-19
**Based On:** Chapter 11 (Project Structure) + Block Architecture Document

---

## 1. Executive Summary

This document maps the proposed project tree structure from Chapter 11 to the high-level block architecture. It analyzes directory ownership, identifies agent filesystem boundaries, and proposes the final adjusted structure.

**Key Finding:** The project uses a **hybrid filesystem model**:
- **Shared Resources:** Configuration, data, and logs in SHARED/ directory (logical ownership with file-level access control)
- **Agent Isolation:** Each agent has its own code directory and process isolation
- **Logical Boundaries:** File-level permissions determine who reads/writes what, not directory-level isolation

---

## 2. Chapter 11 Project Tree (As Proposed)

```
L07/
├── SHARED/                          # Shared resources for all agents
│   ├── config/                      # Configuration layer
│   │   ├── system.json
│   │   ├── agents/
│   │   │   └── agents_config.json
│   │   ├── leagues/
│   │   │   └── league_2025_even_odd.json
│   │   ├── games/
│   │   │   └── games_registry.json
│   │   └── defaults/
│   │       ├── referee.json
│   │       └── player.json
│   │
│   ├── data/                        # Runtime data layer
│   │   ├── leagues/
│   │   │   └── <league_id>/
│   │   │       ├── standings.json
│   │   │       └── rounds.json
│   │   ├── matches/
│   │   │   └── <league_id>/
│   │   │       └── <match_id>.json
│   │   └── players/
│   │       └── <player_id>/
│   │           └── history.json
│   │
│   ├── logs/                        # Logging layer
│   │   ├── league/
│   │   │   └── <league_id>/
│   │   │       └── league.log.jsonl
│   │   ├── agents/
│   │   │   ├── <agent_id>.log.jsonl
│   │   │   └── ...
│   │   └── system/
│   │       └── orchestrator.log.jsonl
│   │
│   └── league_sdk/                  # Python SDK library
│       ├── __init__.py
│       ├── config_models.py
│       ├── config_loader.py
│       ├── repositories.py
│       └── logger.py
│
├── agents/                          # Agent code (each agent separate)
│   ├── league_manager/
│   │   ├── main.py
│   │   ├── handlers.py
│   │   ├── scheduler.py
│   │   └── requirements.txt
│   │
│   ├── referee_REF01/
│   │   ├── main.py
│   │   ├── game_logic.py
│   │   ├── handlers.py
│   │   └── requirements.txt
│   │
│   ├── player_P01/
│   │   ├── main.py
│   │   ├── strategy.py
│   │   ├── handlers.py
│   │   └── requirements.txt
│   │
│   └── player_P02/
│       ├── main.py
│       ├── strategy.py
│       ├── handlers.py
│       └── requirements.txt
│
└── doc/                             # Documentation
    ├── protocol-spec.md
    ├── message-examples/
    │   ├── registration/
    │   ├── game-flow/
    │   └── errors/
    └── diagrams/
        ├── architecture.png
        └── message-flow.png
```

---

## 3. Directory-by-Directory Analysis

### 3.1 SHARED/ Directory

#### Purpose
Central repository for all shared resources including configuration, runtime data, logs, and SDK library.

#### Architectural Blocks Served
- **Data Persistence Layer** (primary)
- **MCP Communication Layer** (league_sdk/)

#### Agent Ownership
**Shared by all agents** with file-level access control:

| File/Directory | Reader | Writer | Notes |
|----------------|--------|--------|-------|
| config/* | All agents | System admin only | Read-only for agents at runtime |
| data/leagues/*/standings.json | All agents | League Manager | Source of truth for standings |
| data/leagues/*/rounds.json | All agents | League Manager | Round history |
| data/matches/*/*.json | All agents | Referee (match owner) | Per-match ownership |
| data/players/*/history.json | All agents (read), Player (write own) | Player (own only) | Each player writes only their own |
| logs/league/*/*.log.jsonl | DevOps/analysis | League Manager | League-level logging |
| logs/agents/<agent_id>.log.jsonl | DevOps/analysis | Agent (own only) | Each agent writes only its own log |
| logs/system/*.log.jsonl | DevOps/analysis | System components | System-level logging |
| league_sdk/* | All agents (import) | Developers | Shared library code |

#### Alignment with Block Architecture
✅ **Perfect Alignment:** Matches Data Persistence Layer responsibilities exactly.

**From block_architecture.md Section 2.5:**
- Configuration Management: SHARED/config/
- Data File Management: SHARED/data/
- Log Management: SHARED/logs/
- Three-layer architecture: config/ data/ logs/

#### Risks and Considerations

**Risk 1: Concurrent Write Access**
- **Issue:** Multiple agents writing to same files simultaneously
- **Mitigation:** File-level ownership enforced by architecture (each agent writes different files)
- **Example:** Two referees never write to same match file (different match_ids)

**Risk 2: Read Consistency**
- **Issue:** Agent reads file while another is writing
- **Mitigation:** Atomic file writes (write to temp, then rename)
- **Status:** Not specified in Chapter 11, should be clarified

**Risk 3: Shared SDK Dependency**
- **Issue:** SDK version mismatch between agents
- **Mitigation:** Single shared installation with `pip install -e league_sdk/`
- **Status:** Specified in Chapter 11 Section 11.8.2

---

### 3.2 SHARED/config/ - Configuration Layer

#### Purpose
Static configuration files that define system behavior, agent registry, league settings, game rules, and defaults.

#### Architectural Block
**Data Persistence Layer** (Configuration Management subsystem)

#### Agent Ownership
- **Read by:** All agents
- **Written by:** System administrator (manual editing or setup scripts)
- **Access Pattern:** Read at startup, cached in memory

#### Responsibilities
1. **system.json** - Global system settings (network, timeouts, security)
2. **agents/agents_config.json** - Registry of all agents (referees and players)
3. **leagues/<league_id>.json** - League-specific configuration
4. **games/games_registry.json** - Supported game types and rules
5. **defaults/referee.json** - Default referee settings
6. **defaults/player.json** - Default player settings

#### Alignment
✅ **Perfect:** Maps directly to ConfigLoader class responsibilities from class_map.md.

#### Notes
- **Immutable at runtime:** Agents should not modify these files during execution
- **Version control friendly:** JSON files can be tracked in git
- **Human-editable:** Administrators can modify configuration without recompilation

---

### 3.3 SHARED/data/ - Runtime Data Layer

#### Purpose
Dynamic data generated during league operation. Stores current state, historical records, and match results.

#### Architectural Block
**Data Persistence Layer** (Data File Management subsystem)

#### Agent Ownership (by subdirectory)

**data/leagues/<league_id>/**
- **Owner:** League Manager Block
- **Writes:** standings.json (after each match), rounds.json (after round completion)
- **Reads:** All agents (for queries and decision-making)
- **Repositories:** StandingsRepository, RoundsRepository

**data/matches/<league_id>/<match_id>.json**
- **Owner:** Referee Block (match owner)
- **Writes:** Referee running that specific match
- **Reads:** All agents (for analytics)
- **Repository:** MatchRepository
- **Note:** Each referee writes only matches assigned to them

**data/players/<player_id>/history.json**
- **Owner:** Player Agent Block (individual player)
- **Writes:** Player agent (own history only)
- **Reads:** All agents (but typically only player reads own)
- **Repository:** PlayerHistoryRepository
- **Critical:** Player P01 writes only data/players/P01/history.json, never P02's file

#### Alignment
✅ **Perfect:** Matches repository class responsibilities from class_map.md exactly.

#### Notes
- **Directory structure scales:** New leagues/matches/players add new files, not modify existing
- **Parallel writes safe:** Different agents write different files
- **Read-while-write:** May need atomic write operations (write temp file, then rename)

---

### 3.4 SHARED/logs/ - Logging Layer

#### Purpose
Structured logging in JSONL format (one JSON object per line) for debugging, monitoring, and analytics.

#### Architectural Block
**Data Persistence Layer** (Log Management subsystem)

#### Agent Ownership (by subdirectory)

**logs/league/<league_id>/league.log.jsonl**
- **Owner:** League Manager Block
- **Writes:** League Manager only
- **Reads:** DevOps, analysis tools
- **Content:** League-level events (registrations, rounds, standings updates)

**logs/agents/<agent_id>.log.jsonl**
- **Owner:** Individual agent (REF01, P01, P02, etc.)
- **Writes:** Agent writes only its own log
- **Reads:** DevOps, analysis tools
- **Content:** Agent-specific events (messages sent/received, decisions, errors)
- **Examples:**
  - logs/agents/REF01.log.jsonl (written by Referee REF01)
  - logs/agents/P01.log.jsonl (written by Player P01)
  - logs/agents/P02.log.jsonl (written by Player P02)

**logs/system/orchestrator.log.jsonl**
- **Owner:** System orchestrator (if separate process)
- **Writes:** System-level orchestrator
- **Reads:** DevOps, analysis tools
- **Content:** System-level events (startup, shutdown, health checks)

#### Alignment
✅ **Perfect:** Matches JsonLogger class from class_map.md.

**From class_map.md:**
```python
class JsonLogger:
    def __init__(self, component: str, league_id: str | None = None)
    def log(event_type, level="INFO", **details)
```

#### Notes
- **Append-only:** Logs never modified, only appended
- **JSONL format:** One JSON object per line enables streaming analysis
- **File per agent:** Each agent logs to separate file (no write contention)
- **Tracing:** conversation_id enables cross-agent tracing

---

### 3.5 SHARED/league_sdk/ - Python SDK

#### Purpose
Shared Python library providing infrastructure classes for configuration loading, data persistence, logging, and MCP communication.

#### Architectural Blocks
- **Data Persistence Layer** (ConfigLoader, Repositories)
- **MCP Communication Layer** (if MCP client code included)

#### Agent Ownership
**Shared by all agents** - installed once, imported by all.

#### Contents (from Chapter 10)

**config_models.py** - Dataclass definitions
- NetworkConfig, SecurityConfig, TimeoutsConfig
- SystemConfig, RefereeConfig, PlayerConfig
- ScoringConfig, LeagueConfig

**config_loader.py** - ConfigLoader class
- Loads configuration files from SHARED/config/
- Lazy loading and caching
- Methods: load_system(), load_agents(), load_league(id)

**repositories.py** - Repository classes
- StandingsRepository (standings.json)
- RoundsRepository (rounds.json)
- MatchRepository (match files)
- PlayerHistoryRepository (player history)

**logger.py** - JsonLogger class
- Structured JSONL logging
- Methods: log(), info(), warning(), error()
- Automatic timestamp and component tagging

#### Installation (from Chapter 11 Section 11.8.2)
```bash
cd SHARED
pip install -e league_sdk/
```

#### Alignment
✅ **Perfect:** This is exactly the SDK layer defined in class_map.md.

#### Notes
- **Single installation:** All agents share one SDK installation
- **Editable install:** `-e` flag allows development changes without reinstall
- **Version consistency:** All agents use same SDK version (critical for protocol compliance)

---

### 3.6 agents/ Directory

#### Purpose
Contains executable code for each agent. Each agent has its own isolated directory with complete independence.

#### Architectural Blocks
Each agent directory maps to an architectural block:
- **agents/league_manager/** → League Manager Block
- **agents/referee_REF01/** → Referee Block
- **agents/player_P01/** → Player Agent Block
- **agents/player_P02/** → Player Agent Block

#### Agent Ownership
**Each directory owned by one agent exclusively.**

#### Directory Structure Pattern (consistent across all agents)

```
agents/<agent_name>/
├── main.py              # Entry point - starts HTTP server, initializes agent
├── handlers.py          # Message handlers - implements MCP tool methods
├── <business_logic>.py  # Agent-specific logic (scheduler, game_logic, strategy)
└── requirements.txt     # Python dependencies
```

#### Per-Agent Analysis

**agents/league_manager/**
- **Block:** League Manager Block
- **Purpose:** Top-level league orchestrator
- **Files:**
  - main.py - Entry point, starts HTTP server on port 8000
  - handlers.py - Handles REFEREE_REGISTER_REQUEST, LEAGUE_REGISTER_REQUEST, LEAGUE_QUERY
  - scheduler.py - Round-Robin scheduling, match assignment
  - requirements.txt - Dependencies (flask, requests, league_sdk)
- **Responsibilities:**
  - Registration management
  - Schedule creation
  - Standings calculation
  - Round coordination
- **Data Written:**
  - SHARED/data/leagues/*/standings.json
  - SHARED/data/leagues/*/rounds.json
  - SHARED/logs/league/*/league.log.jsonl

**agents/referee_REF01/**
- **Block:** Referee Block
- **Purpose:** Match-level orchestrator
- **Files:**
  - main.py - Entry point, starts HTTP server on port 8001
  - handlers.py - Handles match lifecycle (no direct tools, invokes players)
  - game_logic.py - Even/Odd rules implementation
  - requirements.txt - Dependencies
- **Responsibilities:**
  - Match initialization
  - Player invitation
  - Choice collection
  - Winner determination
  - Result reporting
- **Data Written:**
  - SHARED/data/matches/*/REF01_<match_id>.json
  - SHARED/logs/agents/REF01.log.jsonl

**agents/player_P01/**
- **Block:** Player Agent Block
- **Purpose:** Game participant
- **Files:**
  - main.py - Entry point, starts HTTP server on port 8101
  - handlers.py - Implements handle_game_invitation, parity_choose, notify_match_result
  - strategy.py - Decision-making logic (even/odd choice)
  - requirements.txt - Dependencies
- **Responsibilities:**
  - Match participation
  - Strategic decision-making
  - History management
- **Data Written:**
  - SHARED/data/players/P01/history.json
  - SHARED/logs/agents/P01.log.jsonl

**agents/player_P02/**
- **Block:** Player Agent Block
- **Purpose:** Game participant
- **Files:** Same structure as player_P01
- **Data Written:**
  - SHARED/data/players/P02/history.json
  - SHARED/logs/agents/P02.log.jsonl

#### Alignment
✅ **Perfect:** Each agent directory corresponds exactly to one architectural block.

#### Notes on "Each Agent Has Its Own Filesystem"

**What This Means:**
1. **Code Isolation:** Each agent has separate directory with own code
2. **Process Isolation:** Each agent runs as separate process with own HTTP server
3. **Log Isolation:** Each agent writes to its own log file
4. **Data Isolation:** Each agent writes to its own data files (match files, history files)

**What This Does NOT Mean:**
1. **NOT separate file systems:** All agents share SHARED/ directory
2. **NOT complete data isolation:** Agents read each other's data (e.g., standings)
3. **NOT separate SDK installations:** All agents share league_sdk/

**This is LOGICAL filesystem ownership, not physical filesystem isolation.**

---

### 3.7 doc/ Directory

#### Purpose
Project documentation including protocol specifications, message examples, and diagrams.

#### Architectural Block
**None** - This is documentation, not runtime architecture.

#### Agent Ownership
**No agent ownership** - This is for developers and documentation.

#### Contents

**protocol-spec.md**
- Protocol specification document
- Message formats and flows

**message-examples/**
- **registration/** - Example registration JSON messages
  - referee_register_request.json
  - player_register_request.json
- **game-flow/** - Example game messages
  - game_start.json
  - move_request.json
  - game_over.json
- **errors/** - Example error messages
  - timeout_error.json
  - invalid_move.json

**diagrams/**
- architecture.png - System architecture diagram
- message-flow.png - Message sequence diagrams

#### Alignment
✅ **Aligned:** Supports development and testing, not part of runtime architecture.

#### Notes
- **Version control:** These files should be in git
- **Testing aid:** Example messages useful for unit tests
- **Onboarding:** Helps new developers understand protocol

---

## 4. Comparison Against Block Architecture

### 4.1 Direct Mappings (Perfect Alignment)

| Chapter 11 Directory | Block Architecture Component | Alignment |
|---------------------|------------------------------|-----------|
| SHARED/config/ | Data Persistence Layer (Configuration Management) | ✅ Perfect |
| SHARED/data/ | Data Persistence Layer (Data File Management) | ✅ Perfect |
| SHARED/logs/ | Data Persistence Layer (Log Management) | ✅ Perfect |
| SHARED/league_sdk/ | Data Persistence Layer + MCP Communication Layer (SDK) | ✅ Perfect |
| agents/league_manager/ | League Manager Block | ✅ Perfect |
| agents/referee_REF01/ | Referee Block | ✅ Perfect |
| agents/player_P01/ | Player Agent Block | ✅ Perfect |
| agents/player_P02/ | Player Agent Block | ✅ Perfect |
| doc/ | Documentation (not part of runtime) | ✅ N/A |

### 4.2 Cross-Cutting Concerns

**MCP Communication Layer**
- **In block architecture:** Separate conceptual layer
- **In Chapter 11 tree:** Potentially part of league_sdk/, or embedded in each agent's code
- **Status:** Not explicitly visible as separate directory
- **Recommendation:** MCP client code should be in league_sdk/ as mcp_client.py

**Timeout Enforcement**
- **In block architecture:** Cross-cutting concern managed by multiple blocks
- **In Chapter 11 tree:** Enforced by individual agent code (handlers.py)
- **Status:** Implicit, not visible in tree structure
- **Recommendation:** No change needed, this is implementation detail

**Error Handling**
- **In block architecture:** Each block has error handling responsibilities
- **In Chapter 11 tree:** Implemented within each agent's handlers.py
- **Status:** Implicit, not visible in tree structure
- **Recommendation:** No change needed

---

## 5. File Access Permission Matrix

This table shows WHO can READ and WRITE each file type:

| File/Directory | Read Access | Write Access | Repository Class | Notes |
|----------------|-------------|--------------|------------------|-------|
| **Configuration Layer** | | | | |
| config/system.json | All agents | System admin | ConfigLoader | Read at startup, cached |
| config/agents/agents_config.json | All agents | League Manager (registration) | ConfigLoader | Updated when agents register |
| config/leagues/<league_id>.json | All agents | System admin | ConfigLoader | Read at startup |
| config/games/games_registry.json | All agents | System admin | ConfigLoader | Read at startup |
| config/defaults/*.json | All agents | System admin | ConfigLoader | Read at startup |
| **Data Layer - League** | | | | |
| data/leagues/*/standings.json | All agents | League Manager | StandingsRepository | Updated after each match |
| data/leagues/*/rounds.json | All agents | League Manager | RoundsRepository | Updated after each round |
| **Data Layer - Matches** | | | | |
| data/matches/*/<match_id>.json | All agents | Referee (match owner) | MatchRepository | Each referee writes own matches |
| **Data Layer - Players** | | | | |
| data/players/<player_id>/history.json | Player (own), All agents (read) | Player (own only) | PlayerHistoryRepository | Each player writes only their own |
| **Logging Layer** | | | | |
| logs/league/*/league.log.jsonl | DevOps/analysis | League Manager | JsonLogger | Append-only |
| logs/agents/<agent_id>.log.jsonl | DevOps/analysis | Agent (own only) | JsonLogger | Each agent logs to own file |
| logs/system/*.log.jsonl | DevOps/analysis | System components | JsonLogger | System-level logging |
| **SDK Layer** | | | | |
| league_sdk/*.py | All agents (import) | Developers | N/A | Shared library code |

**Key Principles:**
1. **Read access is broad:** Most data files readable by all agents
2. **Write access is narrow:** Each agent writes only its own data
3. **No write conflicts:** Architecture ensures no two agents write same file
4. **Logs are append-only:** No modification or deletion at runtime

---

## 6. Agent Filesystem Boundaries

### 6.1 The "Own Filesystem" Requirement

**From Assignment:** "Pay special attention to the requirement that EACH AI agent has its own filesystem."

**Interpretation:**

This does NOT mean each agent has a completely separate filesystem (like Docker containers). Instead, it means:

1. **Code Isolation:**
   - Each agent has separate code directory (agents/<agent_name>/)
   - Agents do not modify each other's code

2. **Process Isolation:**
   - Each agent runs as separate process
   - Each agent has own HTTP server on different port
   - Agents communicate only via MCP protocol (HTTP)

3. **Data Ownership:**
   - Each agent writes to its own log file
   - Each player writes to its own history file
   - Each referee writes to its own match files
   - League Manager writes to league-wide files

4. **Shared Resources:**
   - All agents read from SHARED/config/ (read-only)
   - All agents read from SHARED/data/ (for coordination)
   - All agents use SHARED/league_sdk/ (shared library)

**This is LOGICAL ownership within a SHARED filesystem.**

### 6.2 Filesystem Boundaries Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          SHARED/                                 │
│                    (Shared Resources)                            │
│                                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ config/    │  │ data/      │  │ logs/      │  │league_sdk/│ │
│  │ (read all) │  │(read all,  │  │(append own)│  │ (import)  │ │
│  │            │  │ write own) │  │            │  │           │ │
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
         ↑                ↑                ↑                ↑
         │                │                │                │
         └────────────────┴────────────────┴────────────────┘
                    (All agents access SHARED/)
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
    ┌────▼─────┐         ┌──────▼──────┐        ┌──────▼──────┐
    │ League   │         │  Referee    │        │   Player    │
    │ Manager  │         │   REF01     │        │     P01     │
    │          │         │             │        │             │
    │ agents/  │         │  agents/    │        │  agents/    │
    │ league_  │         │  referee_   │        │  player_    │
    │ manager/ │         │  REF01/     │        │  P01/       │
    │          │         │             │        │             │
    │ Writes:  │         │  Writes:    │        │  Writes:    │
    │ standings│         │  match files│        │  P01/history│
    │ rounds   │         │  REF01.log  │        │  P01.log    │
    │ league   │         │             │        │             │
    │ .log     │         │             │        │             │
    └──────────┘         └─────────────┘        └─────────────┘
   Process 1            Process 2              Process 3
   Port 8000            Port 8001              Port 8101
```

### 6.3 What Each Agent "Owns"

**League Manager**
- **Code:** agents/league_manager/
- **Process:** Separate process on port 8000
- **Writes to:**
  - SHARED/data/leagues/*/standings.json
  - SHARED/data/leagues/*/rounds.json
  - SHARED/logs/league/*/league.log.jsonl
- **Reads from:** All SHARED/ resources

**Referee REF01**
- **Code:** agents/referee_REF01/
- **Process:** Separate process on port 8001
- **Writes to:**
  - SHARED/data/matches/*/<match_id>.json (only matches assigned to REF01)
  - SHARED/logs/agents/REF01.log.jsonl
- **Reads from:** All SHARED/ resources

**Player P01**
- **Code:** agents/player_P01/
- **Process:** Separate process on port 8101
- **Writes to:**
  - SHARED/data/players/P01/history.json (only own history)
  - SHARED/logs/agents/P01.log.jsonl (only own log)
- **Reads from:** All SHARED/ resources (but typically only reads own history)

**Player P02**
- **Code:** agents/player_P02/
- **Process:** Separate process on port 8102
- **Writes to:**
  - SHARED/data/players/P02/history.json
  - SHARED/logs/agents/P02.log.jsonl
- **Reads from:** All SHARED/ resources

---

## 7. Identified Issues and Adaptations

### 7.1 Issue 1: MCP Communication Layer Not Explicit

**Issue:**
- Block architecture defines MCP Communication Layer as separate conceptual block
- Chapter 11 tree does not show explicit directory for MCP client code

**Impact:**
- Ambiguity about where MCP protocol implementation lives
- Risk of duplication if each agent implements own MCP client

**Resolution:**
- **Add mcp_client.py to league_sdk/**
- All agents import and use shared MCP client
- Client handles JSON-RPC formatting, HTTP transport, timeouts

**Rationale:**
- DRY principle (Don't Repeat Yourself)
- Ensures protocol consistency across all agents
- Centralizes timeout enforcement logic

**Proposed Addition:**
```
SHARED/league_sdk/
├── __init__.py
├── config_models.py
├── config_loader.py
├── repositories.py
├── logger.py
└── mcp_client.py        # NEW: MCP communication client
```

### 7.2 Issue 2: No Explicit Test Directory

**Issue:**
- Chapter 11 does not specify where tests should live
- Block architecture emphasizes testability

**Impact:**
- Unclear where to place unit tests, integration tests
- May lead to inconsistent test organization

**Resolution:**
- **Add tests/ directory at root level**
- Mirror agent structure for unit tests
- Add integration/ subdirectory for integration tests

**Proposed Addition:**
```
L07/
├── SHARED/
├── agents/
├── doc/
└── tests/               # NEW: Test directory
    ├── unit/
    │   ├── test_league_manager.py
    │   ├── test_referee.py
    │   └── test_player.py
    ├── integration/
    │   ├── test_registration_flow.py
    │   ├── test_match_flow.py
    │   └── test_full_league.py
    └── fixtures/
        └── sample_configs.json
```

### 7.3 Issue 3: Configuration Update During Registration

**Issue:**
- Table 23 (file access permissions) shows config/* as read-only for agents
- BUT: agents_config.json must be updated when agents register
- Contradiction: Who writes to agents_config.json?

**Resolution Options:**

**Option A (Recommended):** Pre-Registration Configuration
- All agents registered manually in agents_config.json before startup
- League Manager only validates registrations against existing config
- No runtime writes to config/

**Option B:** Runtime Configuration Updates
- League Manager writes to agents_config.json during registration
- Treat agents_config.json as part of data/ layer, not config/
- Move to data/agents_registry.json

**Recommended:** **Option A**
- Aligns with "config is read-only at runtime" principle
- Simpler concurrency (no writes to config/)
- More predictable behavior

**Clarification in Final Tree:**
- config/agents/agents_config.json remains read-only
- Pre-populated with all agents before league starts
- Registration validates against this config

### 7.4 Issue 4: Atomic File Writes Not Specified

**Issue:**
- Multiple agents read files that are being written (e.g., standings.json)
- Chapter 11 does not specify atomic write strategy
- Risk of reading partially-written files

**Resolution:**
- **Specify atomic write pattern in implementation:**
  1. Write to temporary file (e.g., standings.json.tmp)
  2. Flush and sync to disk
  3. Atomically rename to final name (standings.json)

**Implementation Note:**
```python
# In repositories.py
def atomic_write(file_path, data):
    temp_path = f"{file_path}.tmp"
    with open(temp_path, 'w') as f:
        json.dump(data, f, indent=4)
        f.flush()
        os.fsync(f.fileno())
    os.rename(temp_path, file_path)  # Atomic on POSIX systems
```

**Status:** Architecture decision, not directory structure change.

### 7.5 Issue 5: No .gitignore Specification

**Issue:**
- Chapter 11 does not specify what should be version controlled
- Risk of committing logs, data files, or __pycache__

**Resolution:**
- **Add .gitignore at root level**

**Proposed .gitignore:**
```
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
.venv/
venv/

# Runtime data (should NOT be in git)
SHARED/data/
SHARED/logs/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Keep structure but ignore contents (optional)
!SHARED/data/.gitkeep
!SHARED/logs/.gitkeep
```

**What SHOULD be in git:**
- SHARED/config/ (all config files)
- SHARED/league_sdk/ (SDK source code)
- agents/ (all agent code)
- doc/ (all documentation)
- tests/ (all tests)

**What should NOT be in git:**
- SHARED/data/ (runtime data)
- SHARED/logs/ (logs)
- __pycache__, *.pyc (Python artifacts)

---

## 8. Final Adjusted Project Tree

This is the RECOMMENDED final structure incorporating all adaptations:

```
L07/
├── .gitignore                       # NEW: Git ignore rules
│
├── SHARED/                          # Shared resources for all agents
│   ├── config/                      # Configuration layer (in git)
│   │   ├── system.json
│   │   ├── agents/
│   │   │   └── agents_config.json   # Pre-populated, read-only at runtime
│   │   ├── leagues/
│   │   │   └── league_2025_even_odd.json
│   │   ├── games/
│   │   │   └── games_registry.json
│   │   └── defaults/
│   │       ├── referee.json
│   │       └── player.json
│   │
│   ├── data/                        # Runtime data layer (NOT in git)
│   │   ├── .gitkeep                 # Keeps directory in git, ignores contents
│   │   ├── leagues/
│   │   │   └── <league_id>/
│   │   │       ├── standings.json
│   │   │       └── rounds.json
│   │   ├── matches/
│   │   │   └── <league_id>/
│   │   │       └── <match_id>.json
│   │   └── players/
│   │       └── <player_id>/
│   │           └── history.json
│   │
│   ├── logs/                        # Logging layer (NOT in git)
│   │   ├── .gitkeep
│   │   ├── league/
│   │   │   └── <league_id>/
│   │   │       └── league.log.jsonl
│   │   ├── agents/
│   │   │   ├── <agent_id>.log.jsonl
│   │   │   └── ...
│   │   └── system/
│   │       └── orchestrator.log.jsonl
│   │
│   └── league_sdk/                  # Python SDK library (in git)
│       ├── __init__.py
│       ├── config_models.py         # Dataclass definitions
│       ├── config_loader.py         # ConfigLoader class
│       ├── repositories.py          # Data repositories (with atomic writes)
│       ├── logger.py                # JsonLogger class
│       └── mcp_client.py            # NEW: MCP communication client
│
├── agents/                          # Agent code (in git)
│   ├── league_manager/
│   │   ├── main.py                  # Entry point, port 8000
│   │   ├── handlers.py              # Message handlers
│   │   ├── scheduler.py             # Round scheduling
│   │   └── requirements.txt
│   │
│   ├── referee_REF01/
│   │   ├── main.py                  # Entry point, port 8001
│   │   ├── game_logic.py            # Even/Odd rules
│   │   ├── handlers.py              # Message handlers
│   │   └── requirements.txt
│   │
│   ├── player_P01/
│   │   ├── main.py                  # Entry point, port 8101
│   │   ├── strategy.py              # Playing strategy
│   │   ├── handlers.py              # Message handlers (3 MCP tools)
│   │   └── requirements.txt
│   │
│   └── player_P02/
│       ├── main.py                  # Entry point, port 8102
│       ├── strategy.py              # Playing strategy
│       ├── handlers.py              # Message handlers (3 MCP tools)
│       └── requirements.txt
│
├── tests/                           # NEW: Test directory (in git)
│   ├── unit/
│   │   ├── test_config_loader.py
│   │   ├── test_repositories.py
│   │   ├── test_logger.py
│   │   ├── test_mcp_client.py
│   │   ├── test_league_manager.py
│   │   ├── test_referee.py
│   │   └── test_player.py
│   ├── integration/
│   │   ├── test_registration_flow.py
│   │   ├── test_match_flow.py
│   │   └── test_full_league.py
│   └── fixtures/
│       ├── sample_system.json
│       └── sample_agents_config.json
│
├── doc/                             # Documentation (in git)
│   ├── protocol-spec.md
│   ├── message-examples/
│   │   ├── registration/
│   │   │   ├── referee_register_request.json
│   │   │   └── player_register_request.json
│   │   ├── game-flow/
│   │   │   ├── game_start.json
│   │   │   ├── move_request.json
│   │   │   └── game_over.json
│   │   └── errors/
│   │       ├── timeout_error.json
│   │       └── invalid_move.json
│   └── diagrams/
│       ├── architecture.png
│       └── message-flow.png
│
└── README.md                        # Project README (in git)
```

---

## 9. Changes from Chapter 11 Proposal

| Change | Rationale | Impact |
|--------|-----------|--------|
| **Add mcp_client.py to league_sdk/** | Centralize MCP protocol implementation | All agents share same MCP client (DRY, consistency) |
| **Add tests/ directory** | Enable unit and integration testing | Clear test organization, supports TDD |
| **Add .gitignore** | Prevent committing runtime data and logs | Cleaner git history, smaller repo size |
| **Clarify agents_config.json is read-only** | Avoid concurrency issues with config writes | Pre-populate all agents before startup |
| **Add .gitkeep to data/ and logs/** | Keep directory structure in git | Developers don't need to manually create dirs |
| **Specify atomic writes in repositories** | Prevent reading partially-written files | Architecture decision, documented |
| **Add README.md at root** | Project onboarding and quick start | Standard practice for open source |

---

## 10. Deployment and Execution

### 10.1 Installation Steps

**Step 1: Clone Repository**
```bash
git clone <repository_url>
cd L07
```

**Step 2: Install SDK**
```bash
cd SHARED
pip install -e league_sdk/
```

**Step 3: Install Agent Dependencies**
```bash
# Install for each agent
cd ../agents/league_manager
pip install -r requirements.txt

cd ../referee_REF01
pip install -r requirements.txt

cd ../player_P01
pip install -r requirements.txt

cd ../player_P02
pip install -r requirements.txt
```

### 10.2 Startup Sequence

**Required Order:**
1. League Manager must start first (port 8000)
2. Referees start and register (ports 8001-8002)
3. Players start and register (ports 8101-8104)
4. League begins after all registrations complete

**Terminal 1: League Manager**
```bash
cd agents/league_manager
python main.py --league-id league_2025_even_odd
```

**Terminal 2: Referee REF01**
```bash
cd agents/referee_REF01
python main.py --referee-id REF01 --league-id league_2025_even_odd
```

**Terminal 3: Player P01**
```bash
cd agents/player_P01
python main.py --player-id P01 --league-id league_2025_even_odd
```

**Terminal 4: Player P02**
```bash
cd agents/player_P02
python main.py --player-id P02 --league-id league_2025_even_odd
```

### 10.3 Runtime File Access Pattern

**During Startup:**
1. Each agent loads configuration from SHARED/config/
2. Each agent caches configuration in memory
3. Each agent initializes HTTP server on assigned port
4. Each agent sends registration request to League Manager

**During League Operation:**
1. League Manager writes standings after each match
2. Referees write match files during matches
3. Players write own history after each match
4. All agents append to own log files continuously
5. All agents read (but not write) other agents' data as needed

---

## 11. Scalability and Extensibility

### 11.1 Adding New Players

**Required Changes:**
1. Create agents/player_P03/ directory with code
2. Add player to config/agents/agents_config.json
3. Start player process on port 8103

**No Changes Needed:**
- League Manager code (already supports N players)
- Referee code (already supports any player)
- Data structure (new player creates data/players/P03/)

### 11.2 Adding New Referees

**Required Changes:**
1. Create agents/referee_REF02/ directory with code
2. Add referee to config/agents/agents_config.json
3. Start referee process on port 8002

**No Changes Needed:**
- League Manager code (already assigns matches to available referees)
- Player code (receives referee endpoint in GAME_INVITATION)

### 11.3 Adding New Game Types

**Required Changes:**
1. Add game definition to config/games/games_registry.json
2. Create game_logic_<gametype>.py in referee
3. Update referee to load appropriate rules module
4. Create league config for new game type

**No Changes Needed:**
- League Manager code (game-agnostic orchestration)
- Player code (if game uses same tool interface)
- Data structure (same match file format)

### 11.4 Adding New Leagues

**Required Changes:**
1. Create config/leagues/<new_league_id>.json
2. Start league with --league-id <new_league_id>

**Automatic:**
- data/leagues/<new_league_id>/ created automatically
- data/matches/<new_league_id>/ created automatically
- logs/league/<new_league_id>/ created automatically

---

## 12. Summary and Recommendations

### 12.1 Alignment Assessment

✅ **Excellent Alignment:** Chapter 11's project tree structure aligns extremely well with the block architecture.

**Perfect Mappings:**
- SHARED/config/ → Data Persistence Layer (Configuration Management)
- SHARED/data/ → Data Persistence Layer (Data File Management)
- SHARED/logs/ → Data Persistence Layer (Log Management)
- SHARED/league_sdk/ → Infrastructure SDK
- agents/<agent_name>/ → Corresponding architectural blocks

**Minor Gaps Filled:**
- Added mcp_client.py to SDK
- Added tests/ directory
- Added .gitignore
- Clarified config read-only policy

### 12.2 "Own Filesystem" Interpretation

The requirement that "each agent has its own filesystem" means:

✅ **Code Isolation:** Each agent has separate code directory
✅ **Process Isolation:** Each agent runs as separate process
✅ **Data Ownership:** Each agent writes to its own files
✅ **Log Isolation:** Each agent writes to its own log

❌ **NOT Physical Filesystem Isolation:** All agents share SHARED/
❌ **NOT Complete Data Isolation:** Agents read each other's data

**This is LOGICAL ownership, not physical separation.**

### 12.3 Key Strengths

1. **Clear Boundaries:** Each directory has clear purpose and ownership
2. **Scalable:** Adding agents requires minimal changes
3. **Testable:** Test directory enables comprehensive testing
4. **Version Control Friendly:** Config in git, data/logs excluded
5. **Shared SDK:** Centralized infrastructure reduces duplication

### 12.4 Key Risks and Mitigations

**Risk 1: Concurrent File Access**
- **Mitigation:** File-level ownership, atomic writes

**Risk 2: Configuration Inconsistency**
- **Mitigation:** Read-only config at runtime, pre-registration

**Risk 3: SDK Version Mismatch**
- **Mitigation:** Single shared installation with -e flag

**Risk 4: Log File Growth**
- **Mitigation:** Implement log rotation (future)

### 12.5 Final Recommendation

**ADOPT the adjusted project tree structure with the following additions:**

1. ✅ Add mcp_client.py to league_sdk/
2. ✅ Add tests/ directory
3. ✅ Add .gitignore
4. ✅ Add README.md
5. ✅ Document atomic write pattern in repositories.py
6. ✅ Clarify agents_config.json is pre-populated and read-only

**This structure:**
- Fully complies with Chapter 11 requirements
- Preserves block architecture separation
- Is scalable to hundreds of agents
- Is readable and maintainable
- Supports testing and debugging
- Is production-ready

---

## 13. Appendices

### Appendix A: File Access Quick Reference

**Read-Only for Agents:**
- SHARED/config/* (all configuration)

**Read by All, Write by Owner:**
- SHARED/data/leagues/*/standings.json (owner: League Manager)
- SHARED/data/leagues/*/rounds.json (owner: League Manager)
- SHARED/data/matches/*/*.json (owner: Referee for that match)
- SHARED/data/players/*/history.json (owner: Player for that ID)

**Append by Owner Only:**
- SHARED/logs/league/*/*.log.jsonl (owner: League Manager)
- SHARED/logs/agents/<agent_id>.log.jsonl (owner: Agent with that ID)

### Appendix B: Port Allocation

| Agent Type | Port Range | Example |
|------------|------------|---------|
| League Manager | 8000 | 8000 |
| Referees | 8001-8002 | REF01: 8001, REF02: 8002 |
| Players | 8101-8104 | P01: 8101, P02: 8102, P03: 8103, P04: 8104 |

### Appendix C: Command Reference

**Install SDK:**
```bash
cd SHARED && pip install -e league_sdk/
```

**Start League Manager:**
```bash
cd agents/league_manager
python main.py --league-id league_2025_even_odd
```

**Start Referee:**
```bash
cd agents/referee_REF01
python main.py --referee-id REF01 --league-id league_2025_even_odd
```

**Start Player:**
```bash
cd agents/player_P01
python main.py --player-id P01 --league-id league_2025_even_odd
```

**Run Tests:**
```bash
cd tests
pytest unit/
pytest integration/
```

---

**Document Status:** Architecture Mapping Complete
**Approved Structure:** Ready for implementation
