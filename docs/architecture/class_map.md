# Class Map - Chapter 10 Analysis

**Document Purpose:** Maps all classes defined in Chapter 10 to the high-level block architecture, documenting their responsibilities, relationships, and boundaries.

**Source:** Chapter 10 - MCP Tools Architecture (ערכת כלים בפייתון)

**Last Updated:** 2025-01-19

---

## 1. Overview

Chapter 10 introduces the `league_sdk` Python library, which provides a bridge between JSON configuration/data files and Python objects used by agents. The library implements two core design patterns:

1. **Typed Models (Dataclasses):** Type-safe models that reflect JSON structure
2. **Repository Pattern:** Simplified layer for data access

### Library Structure

```
league_sdk/
├── __init__.py           # Package entry point
├── config_models.py      # Data class definitions
├── config_loader.py      # Configuration loading
├── repositories.py       # Runtime data management
└── logger.py             # Logging implementation
```

---

## 2. Configuration Model Classes

**Module:** `config_models.py`

**Architectural Block:** Data Persistence Layer (with cross-cutting usage by all blocks)

**Purpose:** Provide type-safe, structured representations of all configuration files. These dataclasses directly mirror the JSON schema defined in Chapter 9.

### 2.1 NetworkConfig

**Purpose:** Represents network configuration settings for the system.

**Belongs To:** Data Persistence Layer (used by all blocks)

**Inputs:**
- Read from `config/system.json` → `network` field

**Outputs:**
- Provides network settings to all agents

**Fields:**
- `base_host` (str): Base hostname (typically "localhost")
- `default_league_manager_port` (int): Default port for league manager
- `default_referee_port_range` (List[int]): Port range for referees
- `default_player_port_range` (List[int]): Port range for players

**Dependencies:**
- None (pure data model)

**Responsibilities:**
- Store network configuration values
- Provide type-safe access to network settings

**Explicit Non-Responsibilities:**
- Does NOT establish network connections
- Does NOT validate port availability
- Does NOT manage network communication
- Does NOT modify configuration files

**Maps to Protocol:** Supports endpoint construction for MCP messages

**Maps to Game Flow:** Enables agent discovery and communication setup

---

### 2.2 SecurityConfig

**Purpose:** Represents security and authentication settings.

**Belongs To:** Data Persistence Layer (used by all blocks)

**Inputs:**
- Read from `config/system.json` → `security` field

**Outputs:**
- Provides security settings to all agents

**Fields:**
- `enable_auth_tokens` (bool): Whether authentication is enabled
- `token_length` (int): Length of generated tokens
- `token_ttl_hours` (int): Token time-to-live in hours

**Dependencies:**
- None (pure data model)

**Responsibilities:**
- Store security configuration values
- Provide type-safe access to security settings

**Explicit Non-Responsibilities:**
- Does NOT generate tokens
- Does NOT validate tokens
- Does NOT enforce authentication
- Does NOT manage token lifecycle

**Maps to Protocol:** Defines auth_token structure and requirements

**Maps to Game Flow:** Supports registration and authentication flow

---

### 2.3 TimeoutsConfig

**Purpose:** Represents all timeout values used throughout the system.

**Belongs To:** Data Persistence Layer (used by all blocks)

**Inputs:**
- Read from `config/system.json` → `timeouts` field

**Outputs:**
- Provides timeout settings to all agents

**Fields:**
- `register_referee_timeout_sec` (int): Timeout for referee registration
- `register_player_timeout_sec` (int): Timeout for player registration
- `game_join_ack_timeout_sec` (int): Timeout for GAME_JOIN_ACK (5 seconds)
- `move_timeout_sec` (int): Timeout for player moves (30 seconds)
- `generic_response_timeout_sec` (int): Generic response timeout (10 seconds)

**Dependencies:**
- None (pure data model)

**Responsibilities:**
- Store all timeout configuration values
- Provide type-safe access to timeout settings
- Centralize timeout definitions

**Explicit Non-Responsibilities:**
- Does NOT enforce timeouts
- Does NOT measure elapsed time
- Does NOT trigger timeout events
- Does NOT retry on timeout

**Maps to Protocol:** Directly maps to timeout requirements in Chapter 6 and 8

**Maps to Game Flow:** Defines timing constraints for all game phases

---

### 2.4 SystemConfig

**Purpose:** Top-level system configuration aggregating all global settings.

**Belongs To:** Data Persistence Layer (used by all blocks)

**Inputs:**
- Read from `config/system.json`

**Outputs:**
- Provides complete system configuration to all agents

**Fields:**
- `schema_version` (str): Configuration schema version
- `system_id` (str): System identifier
- `protocol_version` (str): Protocol version (e.g., "league.v2")
- `default_league_id` (str): Default league identifier
- `network` (NetworkConfig): Network configuration object
- `security` (SecurityConfig): Security configuration object
- `timeouts` (TimeoutsConfig): Timeout configuration object

**Dependencies:**
- NetworkConfig
- SecurityConfig
- TimeoutsConfig

**Responsibilities:**
- Aggregate all system-level configuration
- Provide single entry point to global settings
- Maintain schema version for migrations

**Explicit Non-Responsibilities:**
- Does NOT validate configuration consistency
- Does NOT enforce protocol version compatibility
- Does NOT manage configuration updates
- Does NOT persist changes

**Maps to Protocol:** Provides protocol_version field for all messages

**Maps to Game Flow:** Provides global settings for league initialization

---

### 2.5 RefereeConfig

**Purpose:** Represents configuration for a single referee agent.

**Belongs To:** Data Persistence Layer (used by League Manager and Referee blocks)

**Inputs:**
- Read from `config/agents/agents_config.json` → `referees` array

**Outputs:**
- Provides referee metadata for registration and communication

**Fields:**
- `referee_id` (str): Unique referee identifier
- `display_name` (str): Human-readable referee name
- `endpoint` (str): HTTP endpoint URL
- `version` (str): Referee version
- `game_types` (List[str]): Supported game types (e.g., ["even_odd"])
- `max_concurrent_matches` (int): Maximum parallel matches
- `active` (bool): Whether referee is active (default: True)

**Dependencies:**
- None (pure data model)

**Responsibilities:**
- Store referee configuration and metadata
- Provide referee identity information
- Track referee capabilities (game types, concurrency)

**Explicit Non-Responsibilities:**
- Does NOT manage referee lifecycle
- Does NOT assign matches to referee
- Does NOT track referee availability
- Does NOT enforce concurrency limits

**Maps to Protocol:** Provides referee_meta for REFEREE_REGISTER_REQUEST

**Maps to Game Flow:** Enables referee registration and match assignment

---

### 2.6 PlayerConfig

**Purpose:** Represents configuration for a single player agent.

**Belongs To:** Data Persistence Layer (used by League Manager and Player blocks)

**Inputs:**
- Read from `config/agents/agents_config.json` → `players` array

**Outputs:**
- Provides player metadata for registration and communication

**Fields:**
- `player_id` (str): Unique player identifier
- `display_name` (str): Human-readable player name
- `version` (str): Player version
- `preferred_leagues` (List[str]): Preferred league IDs
- `game_types` (List[str]): Supported game types
- `default_endpoint` (str): HTTP endpoint URL
- `active` (bool): Whether player is active (default: True)

**Dependencies:**
- None (pure data model)

**Responsibilities:**
- Store player configuration and metadata
- Provide player identity information
- Track player capabilities and preferences

**Explicit Non-Responsibilities:**
- Does NOT manage player lifecycle
- Does NOT assign players to matches
- Does NOT track player availability
- Does NOT store player history

**Maps to Protocol:** Provides player_meta for LEAGUE_REGISTER_REQUEST

**Maps to Game Flow:** Enables player registration and match participation

---

### 2.7 ScoringConfig

**Purpose:** Represents scoring rules for a league.

**Belongs To:** Data Persistence Layer (used by League Manager block)

**Inputs:**
- Read from `config/leagues/<league_id>.json` → `scoring` field

**Outputs:**
- Provides scoring rules for standings calculation

**Fields:**
- `win_points` (int): Points awarded for a win (typically 3)
- `draw_points` (int): Points awarded for a draw (typically 1)
- `loss_points` (int): Points awarded for a loss (typically 0)
- `technical_loss_points` (int): Points for technical loss
- `tiebreakers` (List[str]): Tiebreaker rules (ordered)

**Dependencies:**
- None (pure data model)

**Responsibilities:**
- Store league-specific scoring rules
- Define point allocation for match outcomes
- Define tiebreaker precedence

**Explicit Non-Responsibilities:**
- Does NOT calculate points
- Does NOT apply tiebreakers
- Does NOT update standings
- Does NOT enforce scoring rules

**Maps to Protocol:** Defines scoring system in league configuration

**Maps to Game Flow:** Enables League Manager to calculate standings after matches

---

### 2.8 LeagueConfig

**Purpose:** Represents complete configuration for a single league.

**Belongs To:** Data Persistence Layer (used by League Manager block)

**Inputs:**
- Read from `config/leagues/<league_id>.json`

**Outputs:**
- Provides league settings to League Manager

**Fields:**
- `schema_version` (str): Configuration schema version
- `league_id` (str): Unique league identifier
- `display_name` (str): Human-readable league name
- `game_type` (str): Type of game (e.g., "even_odd")
- `status` (str): League status (e.g., "ACTIVE", "COMPLETED")
- `scoring` (ScoringConfig): Scoring rules object

**Dependencies:**
- ScoringConfig

**Responsibilities:**
- Store league-specific configuration
- Provide league identity and status
- Define league game type

**Explicit Non-Responsibilities:**
- Does NOT manage league lifecycle
- Does NOT track league progress
- Does NOT manage participants
- Does NOT create schedules

**Maps to Protocol:** Provides league context for all league-level messages

**Maps to Game Flow:** Defines league parameters for competition

---

## 3. Configuration Loader Class

**Module:** `config_loader.py`

**Architectural Block:** Data Persistence Layer

### 3.1 ConfigLoader

**Purpose:** Centralized configuration file loader with lazy loading and caching.

**Belongs To:** Data Persistence Layer

**Inputs:**
- Configuration files from `SHARED/config/` directory
- Root path (default: CONFIG_ROOT)

**Outputs:**
- Typed configuration objects (all *Config classes)
- Cached configuration data
- Lookup/search results

**Internal State:**
- `root` (Path): Root directory for configuration files
- `_system` (SystemConfig | None): Cached system configuration
- `_agents` (AgentsConfig | None): Cached agents configuration
- `_leagues` (Dict[str, LeagueConfig]): Cached league configurations by ID

**Dependencies:**
- All configuration model classes (NetworkConfig, SystemConfig, etc.)
- File system (reads JSON files)
- JSON parser

**Responsibilities:**

**Loading:**
- Load and parse `config/system.json`
- Load and parse `config/agents/agents_config.json`
- Load and parse `config/leagues/<league_id>.json`
- Load and parse `config/games/games_registry.json`

**Caching:**
- Implement lazy loading (load only when requested)
- Cache loaded configurations in memory
- Return cached data on subsequent requests
- Avoid redundant file reads

**Lookup/Search:**
- Find referee by ID from agents list
- Find player by ID from agents list
- Raise ValueError if not found

**Type Conversion:**
- Parse JSON into typed dataclass objects
- Validate field types match dataclass definitions

**Explicit Non-Responsibilities:**
- Does NOT write or modify configuration files
- Does NOT validate business logic (only structure)
- Does NOT manage file permissions
- Does NOT handle concurrent modifications
- Does NOT enforce configuration constraints
- Does NOT send network messages
- Does NOT manage agent lifecycle
- Does NOT track configuration changes over time

**Key Methods:**
- `load_system()` → SystemConfig
- `load_agents()` → AgentsConfig
- `load_league(id)` → LeagueConfig
- `load_games_registry()` → GamesRegistry
- `get_referee_by_id(id)` → RefereeConfig (helper)
- `get_player_by_id(id)` → PlayerConfig (helper)

**Maps to Protocol:** Loads all configuration defined in Chapter 9

**Maps to Game Flow:** Provides configuration needed for all lifecycle stages

**Usage Pattern:**

```python
loader = ConfigLoader()
system_cfg = loader.load_system()  # First call: loads from file
system_cfg2 = loader.load_system() # Second call: returns cached
timeout = system_cfg.timeouts.move_timeout_sec
```

---

## 4. Repository Classes

**Module:** `repositories.py`

**Architectural Block:** Data Persistence Layer

**Purpose:** Implement the Repository Pattern for runtime data management. Each repository handles a specific data file type, providing consistent read/write/update operations.

### 4.1 StandingsRepository

**Purpose:** Manages the league standings table file.

**Belongs To:** Data Persistence Layer (used by League Manager block)

**Inputs:**
- League ID
- Data root path (default: DATA_ROOT)
- Standings data to save

**Outputs:**
- Current standings data (read from file)
- Updated standings file (write to file)

**Internal State:**
- `league_id` (str): League identifier
- `path` (Path): Path to standings.json file

**Dependencies:**
- File system (reads/writes `data/leagues/<league_id>/standings.json`)
- JSON parser
- datetime (for timestamps)

**Responsibilities:**

**File Management:**
- Construct path to `data/leagues/<league_id>/standings.json`
- Create parent directories if needed
- Ensure proper file permissions

**Read Operations:**
- Load standings from JSON file
- Return default empty standings if file doesn't exist
- Parse JSON into dictionary

**Write Operations:**
- Save standings dictionary to JSON file
- Add `last_updated` timestamp automatically
- Format JSON with indentation for readability
- Overwrite existing file atomically

**Update Operations:**
- Update individual player standings after match
- Load current standings, modify, and save back
- Maintain data integrity during updates

**Explicit Non-Responsibilities:**
- Does NOT calculate points (receives calculated values)
- Does NOT determine rankings (works with provided data)
- Does NOT validate standings logic
- Does NOT manage concurrent access (no locking)
- Does NOT send standings updates to agents
- Does NOT track standings history (only current state)
- Does NOT implement tiebreaker rules

**Key Methods:**
- `load()` → Dict: Load standings from file
- `save(standings: Dict)` → None: Save standings to file
- `update_player(player_id, result, points)`: Update player entry

**Maps to Protocol:** Manages `data/leagues/<league_id>/standings.json` from Chapter 9

**Maps to Game Flow:** Updated after MATCH_RESULT_REPORT, read for LEAGUE_STANDINGS_UPDATE

---

### 4.2 RoundsRepository

**Purpose:** Manages the rounds history file for a league.

**Belongs To:** Data Persistence Layer (used by League Manager block)

**Inputs:**
- League ID
- Round data to save

**Outputs:**
- Rounds history data

**Internal State:**
- Similar to StandingsRepository

**Dependencies:**
- File system (`data/leagues/<league_id>/rounds.json`)
- JSON parser

**Responsibilities:**
- Load rounds history from file
- Save rounds history to file
- Append new round information
- Track which rounds completed

**Explicit Non-Responsibilities:**
- Does NOT create round schedules
- Does NOT assign matches to rounds
- Does NOT determine round completion
- Does NOT send round announcements
- Does NOT manage match execution

**Maps to Protocol:** Manages `data/leagues/<league_id>/rounds.json` from Chapter 9

**Maps to Game Flow:** Updated after ROUND_COMPLETED

---

### 4.3 MatchRepository

**Purpose:** Manages individual match data files.

**Belongs To:** Data Persistence Layer (used by Referee block)

**Inputs:**
- League ID
- Match ID
- Match data to save

**Outputs:**
- Complete match data including lifecycle, transcript, result

**Internal State:**
- League ID and Match ID
- Path to match file

**Dependencies:**
- File system (`data/matches/<league_id>/<match_id>.json`)
- JSON parser

**Responsibilities:**
- Load match data from file
- Save complete match data
- Store match lifecycle (state transitions, timestamps)
- Store message transcript (all exchanged messages)
- Store final result

**Explicit Non-Responsibilities:**
- Does NOT execute match logic
- Does NOT send messages to players
- Does NOT determine winners
- Does NOT enforce game rules
- Does NOT manage timeouts
- Does NOT validate match state transitions

**Maps to Protocol:** Manages `data/matches/<league_id>/<match_id>.json` from Chapter 9

**Maps to Game Flow:** Written by Referee throughout match execution

---

### 4.4 PlayerHistoryRepository

**Purpose:** Manages personal match history for a single player.

**Belongs To:** Data Persistence Layer (used by Player block)

**Inputs:**
- Player ID
- Match history data

**Outputs:**
- Player's match history and statistics

**Internal State:**
- Player ID
- Path to history file

**Dependencies:**
- File system (`data/players/<player_id>/history.json`)
- JSON parser

**Responsibilities:**
- Load player history from file
- Save player history to file
- Track total matches, wins, losses, draws
- Store individual match records (opponent, choices, result)
- Provide data for strategy decisions

**Explicit Non-Responsibilities:**
- Does NOT implement strategy
- Does NOT make decisions
- Does NOT analyze history (only stores it)
- Does NOT share history with other players
- Does NOT modify match results

**Maps to Protocol:** Manages `data/players/<player_id>/history.json` from Chapter 9

**Maps to Game Flow:** Updated by Player after receiving GAME_OVER

---

## 5. Logger Class

**Module:** `logger.py`

**Architectural Block:** Cross-cutting (used by all blocks)

### 5.1 JsonLogger

**Purpose:** Structured logging in JSON Lines (JSONL) format for debugging and tracing.

**Belongs To:** Cross-cutting concern (used by all blocks)

**Inputs:**
- Component name (e.g., "league_manager", "referee:REF01", "player:P01")
- Optional league ID
- Event type
- Log level (DEBUG, INFO, WARNING, ERROR)
- Additional details (arbitrary key-value pairs)

**Outputs:**
- Log entries appended to JSONL file
- One JSON object per line

**Internal State:**
- `component` (str): Component identifier
- `log_file` (Path): Path to log file

**Dependencies:**
- File system (`logs/league/<league_id>/` or `logs/system/`)
- JSON serializer
- datetime (for timestamps)

**Responsibilities:**

**Log Directory Management:**
- Determine log directory based on league_id
- Create log directories if needed
- Organize logs by league and component

**Log Entry Creation:**
- Generate timestamp in UTC ISO format
- Create structured log entry with required fields
- Include event type and level
- Add arbitrary details as key-value pairs

**File Writing:**
- Append log entry to JSONL file (one JSON per line)
- Ensure UTF-8 encoding
- Support non-ASCII characters
- Append-only (never overwrites)

**Convenience Methods:**
- `debug()`: Log at DEBUG level
- `info()`: Log at INFO level
- `warning()`: Log at WARNING level
- `error()`: Log at ERROR level
- `log_message_sent()`: Log outgoing messages

**JSON Lines Format Benefits:**
- Efficient append-only writes
- Easy to parse with standard tools
- Supports real-time streaming
- One event per line (no multiline parsing needed)

**Explicit Non-Responsibilities:**
- Does NOT rotate logs
- Does NOT compress logs
- Does NOT filter log levels (writes all)
- Does NOT send logs to external systems
- Does NOT aggregate logs across components
- Does NOT provide log queries or search
- Does NOT enforce log retention policies

**Key Methods:**
- `log(event_type, level, **details)`: Core logging method
- `debug/info/warning/error(event_type, **details)`: Level-specific wrappers
- `log_message_sent(message_type, recipient, **details)`: Message logging helper

**Maps to Protocol:** Creates log files defined in Chapter 9

**Maps to Game Flow:** Logs all events throughout game lifecycle for debugging

**Usage Pattern:**

```python
logger = JsonLogger("referee:REF01", "league_2025_even_odd")
logger.info("GAME_STARTED", match_id="R1M1", players=["P01", "P02"])
logger.error("TIMEOUT", match_id="R1M1", player_id="P02", timeout_sec=30)
```

---

## 6. Cross-Cutting Relationships

### 6.1 Class Usage Matrix

| Class | Used By Blocks | Purpose |
|-------|---------------|---------|
| **Configuration Models** | All blocks | Type-safe configuration access |
| NetworkConfig | All blocks | Network settings |
| SecurityConfig | All blocks | Security settings |
| TimeoutsConfig | All blocks | Timeout values |
| SystemConfig | All blocks | Global configuration |
| RefereeConfig | League Manager, Referee | Referee metadata |
| PlayerConfig | League Manager, Player | Player metadata |
| ScoringConfig | League Manager | Scoring rules |
| LeagueConfig | League Manager | League settings |
| **ConfigLoader** | All blocks | Configuration loading |
| **Repositories** | Specific blocks | Data persistence |
| StandingsRepository | League Manager | Standings management |
| RoundsRepository | League Manager | Rounds history |
| MatchRepository | Referee | Match data |
| PlayerHistoryRepository | Player | Player history |
| **JsonLogger** | All blocks | Structured logging |

### 6.2 Dependency Graph

```
┌─────────────────────────────────────────────────────┐
│                  All Agent Blocks                   │
│  (League Manager, Referee, Player, MCP Layer)       │
└───────────────┬─────────────────────────────────────┘
                │
                ├──> ConfigLoader
                │    └──> Configuration Models (dataclasses)
                │
                ├──> JsonLogger
                │
                └──> Repositories (block-specific)
                     ├──> StandingsRepository (League Manager)
                     ├──> RoundsRepository (League Manager)
                     ├──> MatchRepository (Referee)
                     └──> PlayerHistoryRepository (Player)
```

### 6.3 How Classes Support MCP Protocol

**Configuration Models:**
- Provide type-safe access to protocol version ("league.v2")
- Define timeout values for protocol messages
- Store agent metadata for registration messages
- Define scoring rules referenced in protocol

**ConfigLoader:**
- Loads protocol version for all messages
- Provides endpoint URLs for message routing
- Supplies timeout values for MCP layer
- Retrieves agent metadata for protocol messages

**Repositories:**
- Persist state changes triggered by protocol messages
- Store data referenced in protocol messages (standings, match results)
- Enable queries that support protocol responses

**JsonLogger:**
- Logs all protocol message exchanges
- Enables end-to-end tracing via conversation_id
- Provides debugging for protocol compliance

### 6.4 How Classes Support Game Flow (Chapter 8)

**Registration (Stage 1 & 2):**
- ConfigLoader provides referee/player metadata
- Configuration models define registration parameters
- JsonLogger logs registration events

**Schedule Creation (Stage 3):**
- LeagueConfig provides game type and settings
- ConfigLoader provides player list
- RoundsRepository will store schedule

**Round Announcement (Stage 4):**
- ConfigLoader provides player endpoints
- LeagueConfig provides round structure
- JsonLogger logs announcements

**Match Execution (Stage 5):**
- TimeoutsConfig provides timeout values
- MatchRepository stores match lifecycle
- JsonLogger logs match events
- RefereeConfig provides referee capabilities

**Standings Update (Stage 6):**
- StandingsRepository manages standings table
- ScoringConfig defines point allocation
- RoundsRepository tracks round completion
- JsonLogger logs standings changes

**League Completion (Stage 7):**
- StandingsRepository provides final standings
- LeagueConfig tracks league status
- JsonLogger logs completion event

---

## 7. Important Design Boundaries

### 7.1 What These Classes Are

**Data Transfer Objects:**
- Configuration models are pure data containers
- No business logic or validation
- Map directly to JSON structure

**Infrastructure Services:**
- ConfigLoader provides file loading service
- Repositories provide data access service
- JsonLogger provides logging service

**Type Safety:**
- All classes provide compile-time type checking
- Catch errors during development
- Document expected data structure

### 7.2 What These Classes Are NOT

**Not Business Logic:**
- Classes do NOT implement game rules
- Classes do NOT make strategic decisions
- Classes do NOT enforce protocol semantics
- Classes do NOT manage agent lifecycle

**Not Network Communication:**
- Classes do NOT send HTTP requests
- Classes do NOT receive messages
- Classes do NOT manage connections
- Classes do NOT implement MCP protocol

**Not Orchestration:**
- Classes do NOT coordinate agents
- Classes do NOT manage rounds or matches
- Classes do NOT create schedules
- Classes do NOT determine winners

**Not Computation:**
- Classes do NOT calculate standings
- Classes do NOT compute scores
- Classes do NOT apply game rules
- Classes do NOT implement strategies

### 7.3 Clear Separation of Concerns

**These SDK classes provide the "how" (infrastructure):**
- How to load configuration
- How to persist data
- How to log events
- How to represent data in memory

**Agent blocks provide the "what" (business logic):**
- What to do with configuration
- What data to persist
- What events to log
- What decisions to make

**Example:**
```python
# SDK provides infrastructure:
loader = ConfigLoader()
timeout = loader.load_system().timeouts.move_timeout_sec

# Agent block provides business logic:
if time_elapsed > timeout:
    self.award_technical_loss(player_id)
```

---

## 8. Usage Patterns

### 8.1 Typical Agent Initialization

**League Manager:**

```python
loader = ConfigLoader()
system_cfg = loader.load_system()
agents_cfg = loader.load_agents()
league_cfg = loader.load_league(league_id)
logger = JsonLogger("league_manager", league_id)
standings_repo = StandingsRepository(league_id)
```

**Referee:**

```python
loader = ConfigLoader()
system_cfg = loader.load_system()
league_cfg = loader.load_league(league_id)
self_cfg = loader.get_referee_by_id(referee_id)
logger = JsonLogger(f"referee:{referee_id}", league_id)
match_repo = MatchRepository(league_id, match_id)
```

**Player:**

```python
loader = ConfigLoader()
system_cfg = loader.load_system()
self_cfg = loader.get_player_by_id(player_id)
logger = JsonLogger(f"player:{player_id}", league_id)
history_repo = PlayerHistoryRepository(player_id)
```

### 8.2 Configuration Access Pattern

```python
# Load once, use many times (cached):
loader = ConfigLoader()
system = loader.load_system()

# Access nested configuration:
timeout = system.timeouts.move_timeout_sec
port = system.network.default_league_manager_port
protocol = system.protocol_version
```

### 8.3 Repository Pattern

```python
# Read-modify-write pattern:
repo = StandingsRepository(league_id)
standings = repo.load()
# ... modify standings ...
repo.save(standings)

# Or use helper methods:
repo.update_player(player_id, result="WIN", points=3)
```

### 8.4 Logging Pattern

```python
logger = JsonLogger("component_name", league_id)
logger.info("EVENT_TYPE", key1="value1", key2="value2")
logger.error("ERROR_TYPE", error_code="E001", player_id="P01")
```

---

## 9. What is NOT in This Chapter

**Classes Not Defined Here:**

1. **MCP Communication Classes:**
   - No HTTP client/server classes
   - No JSON-RPC message builder classes
   - No protocol message classes
   - These belong in a separate MCP communication module

2. **Business Logic Classes:**
   - No LeagueManager class (implied but not defined)
   - No RefereeAgent class (implied but not defined)
   - No PlayerAgent class (not shown)
   - No ScheduleCreator class
   - No GameRulesEngine class
   - These belong in agent implementation modules

3. **Strategy Classes:**
   - No StrategyEngine classes
   - No OpponentModeling classes
   - No DecisionMaker classes
   - These belong in player strategy modules

**This chapter focuses exclusively on:**
- Data models (configuration representation)
- Data access (loading and persisting)
- Logging (event recording)

---

## 10. Summary

### Classes Defined in Chapter 10

**Total: 14 classes**

**Configuration Models (8 dataclasses):**
1. NetworkConfig - network settings
2. SecurityConfig - security settings
3. TimeoutsConfig - timeout values
4. SystemConfig - global configuration
5. RefereeConfig - referee metadata
6. PlayerConfig - player metadata
7. ScoringConfig - scoring rules
8. LeagueConfig - league settings

**Infrastructure Services (4 classes):**
9. ConfigLoader - configuration file loader
10. StandingsRepository - standings persistence
11. RoundsRepository - rounds persistence
12. MatchRepository - match data persistence
13. PlayerHistoryRepository - player history persistence

**Logging (1 class):**
14. JsonLogger - structured JSON logging

### Key Characteristics

✅ **Pure Infrastructure:** All classes are infrastructure/utility, not business logic
✅ **Type-Safe:** Dataclasses provide compile-time type checking
✅ **Separation of Concerns:** Clear boundaries between data and logic
✅ **Reusable:** All agents use the same SDK classes
✅ **Protocol-Aligned:** Maps directly to JSON structures in Chapter 9

### Architecture Integration

**These classes enable the architectural blocks to:**
- Access configuration without parsing JSON manually
- Persist state changes without file management complexity
- Log events without formatting complexity
- Maintain type safety throughout the codebase

**But these classes do NOT:**
- Implement game logic
- Send network messages
- Make strategic decisions
- Orchestrate agent interactions
- Enforce business rules

---

**Document Status:** Class extraction and mapping complete
**Next Steps:** Implementation of agent blocks using this SDK

**Available at:** `L07/SHARED/league_sdk/`
