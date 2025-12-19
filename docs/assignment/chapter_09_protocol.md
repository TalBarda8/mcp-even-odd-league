# Chapter 9 - League Data Protocol

**Source:** Chapter 9 - League Data Protocol

This chapter describes the "genetic code" of the agents' society - the JSON file-based data protocol that enables a scalable system for thousands of agents and leagues.

---

## 1. Overview

### 1.1 Introduction

When building a society of autonomous agents (players, referees, league manager), we are creating a new digital culture. Like any human society, three critical foundations are required:

1. **Shared Rules** - The protocol defined in previous chapters
2. **Collective Memory** - The ability to store and retrieve historical information
3. **Genetic Code** - The configuration that defines each agent's DNA

This chapter describes the "data foundation" based on JSON files - a three-layer architecture that enables a scalable system for thousands of agents and leagues.

### 1.2 Three-Layer Architecture

```
┌─────────────────────────────────────┐
│  /config - Configuration Layer      │
│  Static settings                    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  /data - Runtime Data Layer         │
│  Dynamic state and history          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  /logs - Logs Layer                 │
│  Tracking and debugging             │
└─────────────────────────────────────┘
```

### 1.3 Guiding Principles

Every file in the system follows these principles:

- **Unique ID (`id`):** Every primary object receives a unique single-value identifier
- **Schema Version (`schema_version`):** Enables future version migrations
- **Timestamp (`last_updated`):** Timestamp in UTC/ISO-8601 format
- **Protocol Compliance:** All fields conform to `league.v2`

---

## 2. Configuration Layer - `/config`

This layer contains the system's "genetic code" - static settings that are read at agent startup.

### 2.1 Global System Configuration

**File:** `config/system.json`

**Purpose:** Global parameters for the entire system

**Users:** All agents, top-level orchestrator

**Location:** `SHARED/config/system.json`

**Description:** This file defines default values for:
- Network settings (network) - addresses and ports
- Security settings (security) - tokens and TTL
- Timeout settings (timeouts) - conforms to protocol settings
- Retry policy (retry_policy) - conforms to protocol settings

**Required Fields:**
- `schema_version` (string): Schema version number (e.g., "1.0.0")
- `system_id` (string): System identifier (e.g., "league_system_prod")
- `protocol_version` (string): Protocol version (e.g., "league.v2")
- `timeouts` (object):
  - `move_timeout_sec` (number): Timeout for moves in seconds (e.g., 30)
  - `generic_response_timeout_sec` (number): Generic response timeout (e.g., 10)
- `retry_policy` (object):
  - `max_retries` (number): Maximum retry attempts (e.g., 3)
  - `backoff_strategy` (string): Backoff strategy (e.g., "exponential")

**Optional Fields:** None specified

**Example Structure:**

```json
{
  "schema_version": "1.0.0",
  "system_id": "league_system_prod",
  "protocol_version": "league.v2",
  "timeouts": {
    "move_timeout_sec": 30,
    "generic_response_timeout_sec": 10
  },
  "retry_policy": {
    "max_retries": 3,
    "backoff_strategy": "exponential"
  }
}
```

---

### 2.2 Agent Registry

**File:** `config/agents/agents_config.json`

**Purpose:** Central management of thousands of agents

**Users:** League Manager, Deployment tools

**Location:** `SHARED/config/agents/agents_config.json`

**Description:** This file contains the "citizen registry" of the agent society:
- League manager details
- List of all registered referees
- List of all registered players

**Required Fields:**
- `league_manager` (object): League manager details
- `referees` (array): List of all registered referees
- `players` (array): List of all registered players

**Optional Fields:** None specified

---

### 2.3 League Configuration

**File:** `config/leagues/<league_id>.json`

**Purpose:** League-specific settings

**Users:** League Manager, Referees

**Location:** `SHARED/config/leagues/league_2025_even_odd.json`

**Description:** Each league is an independent "state" with its own rules.

**Required Fields:**
- `league_id` (string): League identifier (e.g., "league_2025_even_odd")
- `game_type` (string): Type of game (e.g., "even_odd")
- `status` (string): League status (e.g., "ACTIVE")
- `scoring` (object):
  - `win_points` (number): Points for a win (e.g., 3)
  - `draw_points` (number): Points for a draw (e.g., 1)
  - `loss_points` (number): Points for a loss (e.g., 0)
- `participants` (object):
  - `min_players` (number): Minimum players (e.g., 2)
  - `max_players` (number): Maximum players (e.g., 10000)

**Optional Fields:** None specified

**Example Structure:**

```json
{
  "league_id": "league_2025_even_odd",
  "game_type": "even_odd",
  "status": "ACTIVE",
  "scoring": {
    "win_points": 3,
    "draw_points": 1,
    "loss_points": 0
  },
  "participants": {
    "min_players": 2,
    "max_players": 10000
  }
}
```

---

### 2.4 Game Types Registry

**File:** `config/games/games_registry.json`

**Purpose:** Registry of all supported game types

**Users:** League Manager, Referees (to load rules module)

**Location:** `SHARED/config/games/games_registry.json`

**Description:** The system supports multiple game types. Each game defines:
- Unique identifier
- Rules module to load
- Maximum round time

**Required Fields:**
- `game_type` (string): Unique game identifier
- `rules_module` (string): Module to load for rules
- `max_round_time_sec` (number): Maximum time for a round in seconds

**Optional Fields:** None specified

---

### 2.5 Default Agent Settings

**Files:** `config/defaults/player.json`, `config/defaults/referee.json`

**Purpose:** Default values by agent type

**Users:** New agents

**Location:** `SHARED/config/defaults/`

**Description:** These files enable a new agent to start operating with reasonable settings without defining each parameter separately.

**Required Fields:** Not specified (varies by agent type)

**Optional Fields:** Not specified (varies by agent type)

---

## 3. Runtime Data Layer - `/data`

If the configuration layer is the "genetic code", the runtime data layer is the "historical memory" of the society. All events happening in the system are stored here.

### 3.1 Standings Table

**File:** `data/leagues/<league_id>/standings.json`

**Purpose:** Current standings state of the league

**Updated By:** League Manager (after MATCH_RESULT_REPORT)

**Location:** `SHARED/data/leagues/league_2025_even_odd/standings.json`

**Required Fields:**
- `schema_version` (string): Schema version
- `league_id` (string): League identifier
- `version` (number): Version number (increments with each update)
- `rounds_completed` (number): Number of completed rounds
- `standings` (array): Array of player standings
  - Each entry:
    - `rank` (number): Current rank
    - `player_id` (string): Player identifier
    - `display_name` (string): Player display name
    - `wins` (number): Number of wins
    - `draws` (number): Number of draws
    - `losses` (number): Number of losses
    - `points` (number): Total points

**Optional Fields:** None specified

**Example Structure:**

```json
{
  "schema_version": "1.0.0",
  "league_id": "league_2025_even_odd",
  "version": 12,
  "rounds_completed": 3,
  "standings": [
    {
      "rank": 1,
      "player_id": "P01",
      "display_name": "Agent Alpha",
      "wins": 4,
      "draws": 1,
      "losses": 1,
      "points": 13
    }
  ]
}
```

---

### 3.2 Rounds History

**File:** `data/leagues/<league_id>/rounds.json`

**Purpose:** Documentation of all rounds that took place

**Updated By:** League Manager (after ROUND_COMPLETED)

**Location:** `SHARED/data/leagues/league_2025_even_odd/rounds.json`

**Required Fields:** Not fully specified in document

**Optional Fields:** Not fully specified in document

---

### 3.3 Individual Match Data

**File:** `data/matches/<league_id>/<match_id>.json`

**Purpose:** Complete documentation of an individual match

**Updated By:** The referee managing the match

**Location:** `SHARED/data/matches/league_2025_even_odd/R1M1.json`

**Description:** This file is the "identity document" of the match and includes:
- Match lifecycle - match state and timestamps
- Transcript - all messages exchanged (process history)
- Result - final outcome (conforms to GAME_OVER)

**Required Fields:**
- `lifecycle` (object): Match state and timestamps
- `transcript` (array): All exchanged messages (process history)
- `result` (object): Final outcome (conforms to GAME_OVER)

**Optional Fields:** None specified

---

### 3.4 Player History

**File:** `data/players/<player_id>/history.json`

**Purpose:** Player's "personal memory"

**Users:** The player itself (for strategy building)

**Location:** `SHARED/data/players/P01/history.json`

**Description:** A smart player can use this file as "memory" to improve their strategy.

**Required Fields:**
- `player_id` (string): Player identifier
- `stats` (object):
  - `total_matches` (number): Total matches played
  - `wins` (number): Number of wins
  - `losses` (number): Number of losses
  - `draws` (number): Number of draws
- `matches` (array): Array of match records
  - Each entry:
    - `match_id` (string): Match identifier
    - `opponent_id` (string): Opponent identifier
    - `result` (string): Match result (e.g., "WIN", "LOSS", "DRAW")
    - `my_choice` (string): Player's choice
    - `opponent_choice` (string): Opponent's choice

**Optional Fields:** None specified

**Example Structure:**

```json
{
  "player_id": "P01",
  "stats": {
    "total_matches": 20,
    "wins": 12,
    "losses": 5,
    "draws": 3
  },
  "matches": [
    {
      "match_id": "R1M1",
      "opponent_id": "P02",
      "result": "WIN",
      "my_choice": "even",
      "opponent_choice": "odd"
    }
  ]
}
```

---

## 4. Logs Layer - `/logs`

This layer is the "nervous system" of the society - it enables us to see what is truly happening in the distributed system.

### 4.1 Central League Log

**File:** `logs/league/<league_id>/league.log.jsonl`

**Format:** JSON Lines (each line is a separate JSON object)

**Users:** DevOps, Technical support

**Location:** `SHARED/logs/league/league_2025_even_odd/league.log.jsonl`

**Description:** Each logged event provides tracking capabilities.

**Required Fields per Log Entry:**
- `timestamp` (string): ISO timestamp (e.g., "2025-01-15T10:15:00Z")
- `component` (string): Component name (e.g., "league_manager")
- `event_type` (string): Event type (e.g., "ROUND_ANNOUNCEMENT_SENT")
- `level` (string): Log level (e.g., "INFO", "ERROR", "WARNING")
- `details` (object): Event-specific details

**Optional Fields:** None specified

**Example Log Entry:**

```json
{
  "timestamp": "2025-01-15T10:15:00Z",
  "component": "league_manager",
  "event_type": "ROUND_ANNOUNCEMENT_SENT",
  "level": "INFO",
  "details": {"round_id": 1, "matches_count": 2}
}
```

---

### 4.2 Agent Log

**File:** `logs/agents/<agent_id>.log.jsonl`

**Purpose:** Per-agent tracking for debugging

**Users:** Agent developers

**Location:** `SHARED/logs/agents/P01.log.jsonl`

**Description:** Each agent documents the messages it sends and receives, which enables receiving an End-to-End Trace of every interaction in the system.

**Required Fields per Log Entry:**
- Similar to league log structure (not fully detailed in document)

**Optional Fields:** Not fully specified in document

---

## 5. File Summary Table

| Layer | Path | Purpose | Users |
|-------|------|---------|-------|
| Config | config/system.json | Global parameters | All agents |
| Config | config/agents/ | Agent registry | League Manager |
| Config | config/leagues/ | League settings | League Manager |
| Config | config/games/ | Game registry | Referees |
| Config | config/defaults/ | Default values | Agents |
| Data | data/.../standings.json | Standings table | All |
| Data | data/.../rounds.json | Round history | League Manager |
| Data | data/matches/ | Match details | Analytics |
| Data | data/players/ | Personal history | Player |
| Logs | logs/league/ | Central log | DevOps |
| Logs | logs/agents/ | Agent log | Developers |

---

## 6. Shared Files Usage

All example files described in this chapter are available in the shared directory:

```
L07/SHARED/
```

Students are invited to use these files as a basis for implementing their agents. The files include:

- Complete examples for each file type
- Data conforming to the `league.v2` protocol
- Recommended directory structure for the project

---

## 7. Protocol Conventions

### 7.1 Common Field Standards

**All files must include:**

1. **Unique ID** - Every primary object has a unique identifier
   - Examples: `player_id`, `league_id`, `match_id`, `referee_id`
   - Format: Single-value string

2. **Schema Version** - Enables future migrations
   - Field name: `schema_version`
   - Format: Semantic versioning (e.g., "1.0.0")
   - Purpose: Future-proofing for version migrations

3. **Timestamp** - Last update time
   - Field name: `last_updated` (or `timestamp` in logs)
   - Format: ISO-8601 in UTC timezone
   - Example: "2025-01-15T10:15:00Z"

4. **Protocol Compliance** - All fields conform to `league.v2`
   - Field name: `protocol_version` or `protocol`
   - Value: "league.v2"

### 7.2 File Naming Conventions

**Configuration files:**
- Pattern: `<category>_<type>.json`
- Location: `config/<category>/`
- Examples: `system.json`, `agents_config.json`

**Data files:**
- Pattern: `<entity_id>.json`
- Location: `data/<category>/<league_id>/`
- Examples: `standings.json`, `R1M1.json`, `P01/history.json`

**Log files:**
- Pattern: `<entity_id>.log.jsonl`
- Format: JSON Lines (one JSON object per line)
- Location: `logs/<category>/<league_id>/`
- Examples: `league.log.jsonl`, `P01.log.jsonl`

### 7.3 Data Layer Update Rules

**Who updates what:**

| File Type | Updated By | Trigger Event |
|-----------|------------|---------------|
| `standings.json` | League Manager | After MATCH_RESULT_REPORT |
| `rounds.json` | League Manager | After ROUND_COMPLETED |
| `matches/<match_id>.json` | Referee | Throughout match lifecycle |
| `players/<player_id>/history.json` | Player Agent | After receiving GAME_OVER |
| `league.log.jsonl` | League Manager | Any league event |
| `<agent_id>.log.jsonl` | Individual Agent | Any sent/received message |

### 7.4 Version Management

**Version fields serve different purposes:**

1. **Schema Version** (`schema_version`):
   - Indicates the structure format of the file
   - Changes when field definitions change
   - Example: "1.0.0" → "2.0.0" if new mandatory fields added

2. **Data Version** (`version`):
   - Incremental counter for data updates
   - Used in files like `standings.json`
   - Increments by 1 with each update
   - Purpose: Detect concurrent modifications

3. **Protocol Version** (`protocol_version`):
   - Indicates which protocol specification is used
   - Currently: "league.v2"
   - All components must use the same protocol version

---

## 8. Notes and Ambiguities

### 8.1 Missing Specifications

The following aspects are mentioned but not fully specified in the document:

1. **Agent registry structure** (`agents_config.json`):
   - Field structure for league_manager object not detailed
   - Field structure for referees array entries not detailed
   - Field structure for players array entries not detailed

2. **Rounds history structure** (`rounds.json`):
   - Complete field specification not provided
   - Only mentioned that it's updated after ROUND_COMPLETED

3. **Match data structure** (`matches/<match_id>.json`):
   - Lifecycle object structure not fully detailed
   - Transcript array entry format not fully specified
   - Result object should conform to GAME_OVER but details not provided

4. **Default settings** (`config/defaults/`):
   - Field specifications for player.json not provided
   - Field specifications for referee.json not provided

5. **Agent log format** (`logs/agents/<agent_id>.log.jsonl`):
   - Field structure not fully specified
   - Mentioned to be similar to league log but differences unclear

### 8.2 Implementation Guidance Needed

The document provides high-level descriptions but leaves implementation details to be inferred:

1. **Concurrency control:**
   - Version numbers mentioned but no locking mechanism specified
   - No guidance on handling concurrent writes to shared files

2. **File access patterns:**
   - Read/write permissions not specified
   - Shared vs. agent-private file access not detailed

3. **Error handling:**
   - No specification for invalid or corrupted file handling
   - No specification for missing required files

4. **Backwards compatibility:**
   - Schema versioning mentioned but migration process not described
   - No guidance on handling mixed protocol versions

### 8.3 Relationship to Protocol Messages

**Important Note:** This chapter describes the **data layer protocol** (JSON file structures for persistence), not the **message protocol** (messages exchanged between agents like GAME_INVITATION, GAME_OVER, etc.).

The data layer supports the message protocol by:
- Storing configuration that agents use to communicate
- Persisting state changes triggered by protocol messages
- Logging message exchanges for debugging and analytics

### 8.4 Scalability Considerations

The document mentions the system is designed to scale to "thousands of agents and leagues" but doesn't detail:

1. **File system organization at scale:**
   - How directories are structured when there are 10,000+ players
   - Whether sharding or partitioning strategies are used

2. **Performance optimization:**
   - Caching strategies for frequently accessed files
   - When to read from files vs. maintain in-memory state

3. **Storage management:**
   - Log rotation policies
   - Archive and cleanup procedures for old data

---

## 9. Summary

The three-layer architecture we presented - configuration, runtime data, and logs - provides the necessary infrastructure for building an agent system at scale.

**As in human society, here too:**

- **Configuration** is the "law" - the fundamental rules everyone knows
- **Runtime data** is the "historical archive" - the collective memory
- **Logs** are the "newspapers" - documentation of what happens in real-time

This structure prepares the system for growth of thousands of agents and leagues, while maintaining order, traceability, and complexity management.

---

**End of Chapter 9 - League Data Protocol Documentation**
