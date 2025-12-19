# Interface Specifications

**Even/Odd League System - Formal Interface Contracts**

**Document Version:** 1.0
**Last Updated:** 2025-01-19
**Protocol Version:** league.v2

---

## Table of Contents

1. [Overview](#1-overview)
2. [LeagueManagerInterface](#2-leaguemanagerinterface)
3. [RefereeInterface](#3-refereeinterface)
4. [PlayerInterface](#4-playerinterface)
5. [MCPClientInterface](#5-mcpclientinterface)
6. [Interface Mapping to Project Tree](#6-interface-mapping-to-project-tree)

---

## 1. Overview

### 1.1 Purpose

This document defines formal interface contracts for the four primary components of the MCP Even/Odd League system. These interfaces specify the public methods, responsibilities, and behavior expectations for each component.

### 1.2 Scope

**Covered:**
- Public method signatures for all interfaces
- Input/output specifications
- State-based constraints on method calls
- MCP message handling
- Error and timeout behavior

**Not Covered:**
- Implementation details
- Private/internal methods
- Data structure implementations
- Network layer implementation

### 1.3 Interface Design Philosophy

1. **Protocol-First:** All interfaces align with MCP message contracts
2. **State-Aware:** Methods specify which states they can be called in
3. **Explicit Failures:** All failure modes documented
4. **Separation of Concerns:** Each interface has clear boundaries
5. **Testability:** Interfaces designed for unit testing with mocks

### 1.4 Notation

**Type Notation:**
- `string` - Unicode string
- `integer` - Integer number
- `boolean` - True/False value
- `array[T]` - Array of type T
- `object` - Dictionary/map structure
- `T | null` - T or null
- `Result<T, E>` - Result type containing success value T or error E

**Method Signature Format:**
```
method_name(param1: type, param2: type) -> return_type
```

---

## 2. LeagueManagerInterface

### 2.1 Purpose

**Role:** Top-level orchestrator for the entire league system. Manages league lifecycle, agent registration, match scheduling, and standings calculation.

**Architectural Block:** League Manager Block

**Implementation Location:** `agents/league_manager/`

### 2.2 Public Methods

#### 2.2.1 start_league_manager

```python
start_league_manager(
    league_id: string,
    system_config: SystemConfig,
    league_config: LeagueConfig
) -> Result<void, Error>
```

**Description:** Initializes and starts the League Manager HTTP server. Loads configuration and prepares for agent registration.

**Input Parameters:**
- `league_id` - Unique identifier for the league (e.g., "league_2025_even_odd")
- `system_config` - System configuration object (from ConfigLoader)
- `league_config` - League-specific configuration (from ConfigLoader)

**Output:** Success (void) or error

**Blocking:** Yes (blocks until server starts or fails)

**MCP Messages Sent:** None (initialization only)

**MCP Messages Handled:** None (initialization only)

**Allowed States:** N/A (pre-state initialization)

**State Transition:** None → Internal state initialized

**Responsibilities:**
- Start HTTP server on configured port (typically 8000)
- Initialize endpoint `/mcp` for JSON-RPC requests
- Load system and league configuration
- Initialize data repositories (StandingsRepository, RoundsRepository)
- Initialize JsonLogger for league logging
- Initialize MCP client for outgoing messages

**Failure Handling:**
- If port already in use → Return error "PORT_IN_USE"
- If configuration invalid → Return error "INVALID_CONFIG"
- If repositories fail to initialize → Return error "DATA_INIT_FAILED"

---

#### 2.2.2 register_referee

```python
register_referee(
    referee_meta: RefereeMetadata
) -> Result<RefereeRegistrationResponse, Error>
```

**Description:** Handles referee registration request. Validates referee metadata and assigns unique referee ID.

**Input Parameters:**
- `referee_meta` - Object containing:
  - `display_name: string` - Referee display name
  - `version: string` - Referee version
  - `game_types: array[string]` - Supported game types (e.g., ["even_odd"])
  - `contact_endpoint: string` - Full HTTP URL
  - `max_concurrent_matches: integer` - Max parallel matches

**Output:**
- Success: `RefereeRegistrationResponse` object containing:
  - `status: "ACCEPTED"`
  - `referee_id: string` - Assigned ID (e.g., "REF01")
  - `auth_token: string` - Authentication token
  - `league_id: string`
- Error: `Error` object with error code and message

**Blocking:** Yes (synchronous response)

**MCP Messages Sent:** None (response only)

**MCP Messages Handled:** `REFEREE_REGISTER_REQUEST`

**Allowed States:** WAITING_FOR_REGISTRATIONS

**State Transition:** None (remains in same state)

**Responsibilities:**
- Validate referee_meta completeness and correctness
- Check if max referees limit reached
- Verify contact_endpoint is reachable (optional health check)
- Assign unique referee_id
- Generate auth_token (cryptographically secure)
- Store referee in agents_config registry
- Store endpoint in endpoint mapping
- Log registration event

**Failure Handling:**
- If max referees reached → Return `status: "REJECTED"`, reason: "League full"
- If endpoint invalid → Return `status: "REJECTED"`, reason: "Invalid endpoint"
- If unsupported game_type → Return `status: "REJECTED"`, reason: "Unsupported game type"
- If duplicate display_name → Return `status: "REJECTED"`, reason: "Duplicate name"

**Timeout:** Caller must respond within 10 seconds (enforced by MCP client)

---

#### 2.2.3 register_player

```python
register_player(
    player_meta: PlayerMetadata
) -> Result<PlayerRegistrationResponse, Error>
```

**Description:** Handles player registration request. Validates player metadata and assigns unique player ID.

**Input Parameters:**
- `player_meta` - Object containing:
  - `display_name: string` - Player display name (must be unique)
  - `version: string` - Player version
  - `game_types: array[string]` - Supported game types
  - `contact_endpoint: string` - Full HTTP URL

**Output:**
- Success: `PlayerRegistrationResponse` object containing:
  - `status: "ACCEPTED"`
  - `player_id: string` - Assigned ID (e.g., "P01")
  - `auth_token: string` - Authentication token
  - `league_id: string`
- Error: `Error` object

**Blocking:** Yes (synchronous response)

**MCP Messages Sent:** None (response only)

**MCP Messages Handled:** `LEAGUE_REGISTER_REQUEST`

**Allowed States:** WAITING_FOR_REGISTRATIONS

**State Transition:** None (remains in same state). If all required players registered, triggers schedule creation.

**Responsibilities:**
- Validate player_meta completeness
- Check if max players limit reached
- Verify display_name is unique
- Assign unique player_id (sequential: P01, P02, P03, P04)
- Generate auth_token
- Store player in agents_config registry
- Store endpoint in endpoint mapping
- Log registration event
- If all players registered, trigger schedule creation

**Failure Handling:**
- If max players reached → Return `status: "REJECTED"`, reason: "League full"
- If duplicate display_name → Return `status: "REJECTED"`, reason: "Duplicate name"
- If endpoint invalid → Return `status: "REJECTED"`, reason: "Invalid endpoint"
- If unsupported game_type → Return `status: "REJECTED"`, reason: "Unsupported game type"

**Timeout:** Caller must respond within 10 seconds

---

#### 2.2.4 create_schedule

```python
create_schedule(
    players: array[PlayerConfig],
    referees: array[RefereeConfig]
) -> Result<Schedule, Error>
```

**Description:** Creates Round-Robin match schedule for all registered players. Internal method typically called automatically after all players registered.

**Input Parameters:**
- `players` - Array of registered player configurations
- `referees` - Array of available referees

**Output:**
- Success: `Schedule` object containing:
  - `rounds: array[Round]` - Array of rounds
  - `total_matches: integer`
- Error: `Error` object

**Blocking:** Yes (synchronous computation)

**MCP Messages Sent:** None (internal computation)

**MCP Messages Handled:** None (internal method)

**Allowed States:** WAITING_FOR_REGISTRATIONS (after all registrations complete)

**State Transition:** WAITING_FOR_REGISTRATIONS → RUNNING_LEAGUE

**Responsibilities:**
- Generate Round-Robin pairings (every player plays every other player once)
- Assign matches to available referees
- Ensure fair distribution:
  - Each player plays exactly once per round
  - Matches distributed evenly across referees
- Generate unique match IDs (format: "R{round}M{match}", e.g., "R1M1")
- Store schedule in rounds.json
- Log schedule creation

**Failure Handling:**
- If insufficient players (< 2) → Return error "INSUFFICIENT_PLAYERS"
- If no referees available → Return error "NO_REFEREES"
- If schedule generation fails → Return error "SCHEDULE_GENERATION_FAILED"

**Example Output (4 players, 2 referees):**
```
Round 1: R1M1 (P01 vs P02, REF01), R1M2 (P03 vs P04, REF02)
Round 2: R2M1 (P03 vs P01, REF01), R2M2 (P04 vs P02, REF02)
Round 3: R3M1 (P04 vs P01, REF01), R3M2 (P03 vs P02, REF02)
```

---

#### 2.2.5 announce_round

```python
announce_round(
    round_id: integer,
    matches: array[Match]
) -> Result<void, Error>
```

**Description:** Broadcasts ROUND_ANNOUNCEMENT to all registered players, notifying them of upcoming matches.

**Input Parameters:**
- `round_id` - Round number (1, 2, 3, ...)
- `matches` - Array of match objects for this round

**Output:** Success (void) or error

**Blocking:** Yes (waits for acknowledgments or timeout)

**MCP Messages Sent:** `ROUND_ANNOUNCEMENT` → All Players

**MCP Messages Handled:** `ROUND_ANNOUNCEMENT_ACK` (acknowledgments from players)

**Allowed States:** RUNNING_LEAGUE

**State Transition:** None (remains in RUNNING_LEAGUE)

**Responsibilities:**
- Construct ROUND_ANNOUNCEMENT message for each player
- Send to all registered players concurrently
- Wait for ROUND_ANNOUNCEMENT_ACK from each player (10-second timeout)
- Log announcement event
- Track which players acknowledged
- If all players acknowledge, proceed to allow referees to start matches

**Failure Handling:**
- If player unreachable → Log warning, proceed anyway (player may receive technical loss later)
- If player doesn't acknowledge within 10 seconds → Log timeout, proceed anyway
- If all players unreachable → Return error "NO_PLAYERS_REACHABLE"

**Timeout:** 10 seconds per player for acknowledgment

---

#### 2.2.6 report_match_result

```python
report_match_result(
    match_result: MatchResult
) -> Result<void, Error>
```

**Description:** Handles MATCH_RESULT_REPORT from referee. Updates standings table with match outcome.

**Input Parameters:**
- `match_result` - Object containing:
  - `match_id: string`
  - `winner: string | null` - Winner player_id or null for draw
  - `score: object` - Points awarded (player_id → points)
  - `details: object` - Additional match details

**Output:** Success (void) or error

**Blocking:** Yes (synchronous processing)

**MCP Messages Sent:** `MATCH_RESULT_ACK` → Referee (acknowledgment)

**MCP Messages Handled:** `MATCH_RESULT_REPORT`

**Allowed States:** RUNNING_LEAGUE

**State Transition:** None (remains in RUNNING_LEAGUE). If all matches in round complete, triggers round completion.

**Responsibilities:**
- Validate match_result (match_id exists, valid scores)
- Validate auth_token from referee
- Update standings table:
  - Award points to players (3 for win, 1 for draw, 0 for loss)
  - Increment wins/draws/losses counts
  - Recalculate rankings
- Persist updated standings to standings.json
- Send MATCH_RESULT_ACK to referee
- Log match result
- Check if all matches in current round complete
- If round complete, trigger round completion and standings update

**Failure Handling:**
- If invalid auth_token → Return error "INVALID_AUTH_TOKEN"
- If match_id not found → Return error "MATCH_NOT_FOUND"
- If duplicate report → Return error "DUPLICATE_REPORT"
- If standings update fails → Return error "STANDINGS_UPDATE_FAILED"

**Timeout:** Referee waits 10 seconds for acknowledgment

---

#### 2.2.7 update_standings

```python
update_standings(
    round_id: integer
) -> Result<void, Error>
```

**Description:** Broadcasts LEAGUE_STANDINGS_UPDATE to all players after round completion.

**Input Parameters:**
- `round_id` - Completed round number

**Output:** Success (void) or error

**Blocking:** Yes (waits for acknowledgments or timeout)

**MCP Messages Sent:** `LEAGUE_STANDINGS_UPDATE` → All Players

**MCP Messages Handled:** `STANDINGS_UPDATE_ACK` (acknowledgments)

**Allowed States:** RUNNING_LEAGUE

**State Transition:** None (remains in RUNNING_LEAGUE)

**Responsibilities:**
- Load current standings from standings.json
- Sort standings by points (descending), then by wins, then by alphabetical order
- Assign ranks (1st, 2nd, 3rd, 4th)
- Construct LEAGUE_STANDINGS_UPDATE message
- Send to all registered players concurrently
- Wait for acknowledgments (10-second timeout)
- Log standings update event

**Failure Handling:**
- If player unreachable → Log warning, proceed anyway
- If standings.json corrupt → Return error "STANDINGS_CORRUPT"

**Timeout:** 10 seconds per player for acknowledgment

---

#### 2.2.8 announce_round_completed

```python
announce_round_completed(
    round_id: integer,
    next_round_id: integer | null
) -> Result<void, Error>
```

**Description:** Broadcasts ROUND_COMPLETED to all players. If next_round_id is null, league is complete.

**Input Parameters:**
- `round_id` - Completed round number
- `next_round_id` - Next round number or null if no more rounds

**Output:** Success (void) or error

**Blocking:** Yes (waits for acknowledgments)

**MCP Messages Sent:** `ROUND_COMPLETED` → All Players

**MCP Messages Handled:** `ROUND_COMPLETED_ACK`

**Allowed States:** RUNNING_LEAGUE

**State Transition:**
- If next_round_id is not null → Remains in RUNNING_LEAGUE, prepares for next round
- If next_round_id is null → Transitions to LEAGUE_COMPLETE, triggers league completion

**Responsibilities:**
- Construct ROUND_COMPLETED message
- Send to all players
- Wait for acknowledgments
- Log round completion
- If next_round_id is not null, trigger next round announcement
- If next_round_id is null, trigger league completion

**Failure Handling:**
- If player unreachable → Log warning, proceed anyway

**Timeout:** 10 seconds per player

---

#### 2.2.9 announce_league_completed

```python
announce_league_completed(
    total_rounds: integer,
    total_matches: integer
) -> Result<void, Error>
```

**Description:** Broadcasts LEAGUE_COMPLETED to all players with final standings and champion.

**Input Parameters:**
- `total_rounds` - Total number of rounds played
- `total_matches` - Total matches played

**Output:** Success (void) or error

**Blocking:** Yes (waits for acknowledgments)

**MCP Messages Sent:** `LEAGUE_COMPLETED` → All Players

**MCP Messages Handled:** `LEAGUE_COMPLETED_ACK`

**Allowed States:** LEAGUE_COMPLETE

**State Transition:** LEAGUE_COMPLETE → (terminal, may shutdown)

**Responsibilities:**
- Load final standings from standings.json
- Determine champion (highest points, then highest wins, then alphabetical)
- Construct LEAGUE_COMPLETED message with:
  - Final standings
  - Champion details
  - Total rounds and matches
- Send to all players
- Wait for acknowledgments
- Log league completion
- Persist final state
- Prepare for graceful shutdown

**Failure Handling:**
- If player unreachable → Log warning, proceed anyway
- If standings.json missing → Return error "STANDINGS_MISSING"

**Timeout:** 10 seconds per player

---

#### 2.2.10 query_standings

```python
query_standings(
    player_id: string,
    auth_token: string
) -> Result<Standings, Error>
```

**Description:** Handles LEAGUE_QUERY request from player. Returns current standings.

**Input Parameters:**
- `player_id` - Requesting player's ID
- `auth_token` - Player's authentication token

**Output:**
- Success: `Standings` object (array of player standings)
- Error: `Error` object

**Blocking:** Yes (synchronous query)

**MCP Messages Sent:** None (response only)

**MCP Messages Handled:** `LEAGUE_QUERY` (query_type: "GET_STANDINGS")

**Allowed States:** RUNNING_LEAGUE, LEAGUE_COMPLETE

**State Transition:** None (read-only query)

**Responsibilities:**
- Validate auth_token matches player_id
- Load current standings from standings.json
- Return standings in standard format
- Log query event

**Failure Handling:**
- If invalid auth_token → Return error "INVALID_AUTH_TOKEN"
- If player_id not found → Return error "PLAYER_NOT_FOUND"
- If standings.json missing → Return error "STANDINGS_NOT_AVAILABLE"

**Timeout:** 10 seconds (caller timeout)

---

### 2.3 Responsibilities

**MUST:**
1. ✅ Manage agent registration (referees and players)
2. ✅ Generate unique IDs for all agents (REF01, P01, P02, etc.)
3. ✅ Generate and validate authentication tokens
4. ✅ Create Round-Robin match schedule
5. ✅ Broadcast round announcements to all players
6. ✅ Receive and process match results from referees
7. ✅ Calculate and update standings after each match
8. ✅ Broadcast standings updates after each round
9. ✅ Determine champion and declare league completion
10. ✅ Persist all state to data files (standings.json, rounds.json)
11. ✅ Log all league-level events to league.log.jsonl
12. ✅ Respond to standings queries from players
13. ✅ Maintain endpoint registry for all agents
14. ✅ Enforce response timeouts (10 seconds for most messages)

**Source of Truth:**
- Standings table
- Match schedule
- Round status
- League lifecycle state

### 2.4 Explicit Non-Responsibilities

**MUST NOT:**
1. ❌ Manage individual match gameplay or state
2. ❌ Enforce game rules (even/odd logic)
3. ❌ Determine match winners (referee's responsibility)
4. ❌ Send game invitations to players (referee's responsibility)
5. ❌ Collect player choices (referee's responsibility)
6. ❌ Implement timeout enforcement at match level (referee's responsibility)
7. ❌ Handle match-specific errors (referee's responsibility)
8. ❌ Store individual match transcripts (referee's responsibility)
9. ❌ Directly communicate with players during matches
10. ❌ Manage player strategies
11. ❌ Modify referee behavior or match assignments mid-match

### 2.5 Failure & Timeout Handling

**Error Surfacing:**
- All methods return `Result<T, Error>` type
- Errors include error code and human-readable message
- Errors logged to league.log.jsonl

**Timeout Enforcement:**
- 10-second timeout for all acknowledgments (ROUND_ANNOUNCEMENT_ACK, STANDINGS_UPDATE_ACK, etc.)
- Timeouts logged but do not block progression
- Best-effort message delivery: proceed even if some players unreachable

**Critical Failures:**
- Port binding failure → Exit with error
- Configuration loading failure → Exit with error
- Standings.json corruption → Attempt recovery, log critical error

**Non-Critical Failures:**
- Player unreachable during announcement → Log warning, proceed
- Acknowledgment timeout → Log timeout, proceed
- Duplicate match result report → Ignore duplicate, log warning

---

## 3. RefereeInterface

### 3.1 Purpose

**Role:** Match-level orchestrator. Manages complete lifecycle of a single match from invitation through result reporting. Enforces game rules and timeouts.

**Architectural Block:** Referee Block

**Implementation Location:** `agents/referee_REF01/`

### 3.2 Public Methods

#### 3.2.1 start_referee

```python
start_referee(
    referee_id: string,
    system_config: SystemConfig,
    game_config: GameConfig
) -> Result<void, Error>
```

**Description:** Initializes and starts the Referee HTTP server. Loads game rules and prepares for match assignments.

**Input Parameters:**
- `referee_id` - Assigned referee ID (e.g., "REF01")
- `system_config` - System configuration
- `game_config` - Game-specific configuration (even/odd rules)

**Output:** Success (void) or error

**Blocking:** Yes (blocks until server starts)

**MCP Messages Sent:** `REFEREE_REGISTER_REQUEST` → League Manager

**MCP Messages Handled:** None (initialization only)

**Allowed States:** N/A (pre-state initialization)

**State Transition:** None → IDLE

**Responsibilities:**
- Start HTTP server on configured port (typically 8001 or 8002)
- Initialize endpoint `/mcp`
- Load game rules module (even_odd_rules.py)
- Initialize MatchRepository for match data persistence
- Initialize JsonLogger for referee logging
- Initialize MCP client for outgoing messages
- Send registration request to League Manager
- Wait for registration confirmation

**Failure Handling:**
- If port in use → Return error "PORT_IN_USE"
- If game rules loading fails → Return error "GAME_RULES_LOAD_FAILED"
- If registration fails → Return error "REGISTRATION_FAILED"

---

#### 3.2.2 handle_match_assignment

```python
handle_match_assignment(
    match_id: string,
    player_A_id: string,
    player_B_id: string,
    league_id: string,
    round_id: integer
) -> Result<void, Error>
```

**Description:** Internal method triggered when referee receives match assignment from round announcement. Initializes match and invites players.

**Input Parameters:**
- `match_id` - Unique match identifier (e.g., "R1M1")
- `player_A_id` - First player ID
- `player_B_id` - Second player ID
- `league_id` - League identifier
- `round_id` - Round number

**Output:** Success (void) or error

**Blocking:** Yes (sends invitations and starts timers)

**MCP Messages Sent:** `GAME_INVITATION` → Player A, `GAME_INVITATION` → Player B

**MCP Messages Handled:** None (internal trigger from round announcement)

**Allowed States:** IDLE

**State Transition:** IDLE → WAITING_FOR_PLAYERS

**Responsibilities:**
- Initialize match context
- Set match status to WAITING_FOR_PLAYERS
- Construct GAME_INVITATION messages:
  - Player A: role_in_match = "PLAYER_A", opponent_id = player_B_id
  - Player B: role_in_match = "PLAYER_B", opponent_id = player_A_id
- Send invitations concurrently to both players
- Start 5-second timeout timer for each player
- Log match start event

**Failure Handling:**
- If player endpoint unreachable → Award technical loss to unreachable player
- If sending invitation fails → Retry up to 3 times
- If both players unreachable → Report match as failed to League Manager

**Timeout:** 5 seconds per player for GAME_JOIN_ACK

---

#### 3.2.3 handle_game_join_ack

```python
handle_game_join_ack(
    player_id: string,
    match_id: string,
    accept: boolean,
    arrival_timestamp: string
) -> Result<void, Error>
```

**Description:** Handles GAME_JOIN_ACK from player. Marks player as arrived. If both players arrived, transitions to choice collection.

**Input Parameters:**
- `player_id` - Responding player's ID
- `match_id` - Match identifier
- `accept` - Whether player accepts invitation (true/false)
- `arrival_timestamp` - When player confirmed arrival

**Output:** Success (void) or error

**Blocking:** No (asynchronous event handling)

**MCP Messages Sent:**
- If both players arrived: `CHOOSE_PARITY_CALL` → Player A, `CHOOSE_PARITY_CALL` → Player B
- If timeout/reject: `GAME_ERROR` → Player (if retry)

**MCP Messages Handled:** `GAME_JOIN_ACK`

**Allowed States:** WAITING_FOR_PLAYERS

**State Transition:**
- If one player arrived: Remains WAITING_FOR_PLAYERS
- If both players arrived: WAITING_FOR_PLAYERS → COLLECTING_CHOICES
- If accept == false: WAITING_FOR_PLAYERS → NOTIFYING_PLAYERS (technical loss)

**Responsibilities:**
- Validate match_id matches current match
- Validate player_id is one of the expected players
- Cancel timeout timer for this player
- Mark player as arrived
- Store arrival timestamp
- If accept == false, award technical loss to this player
- If both players arrived with accept == true:
  - Query current standings for both players (from League Manager or cache)
  - Construct CHOOSE_PARITY_CALL messages
  - Send to both players
  - Start 30-second timeout timers

**Failure Handling:**
- If match_id invalid → Send GAME_ERROR, error_code: "MATCH_NOT_FOUND"
- If player_id invalid → Send GAME_ERROR, error_code: "PLAYER_NOT_FOUND"
- If already marked arrived → Ignore duplicate, log warning
- If accept == false → Award technical loss, proceed to NOTIFYING_PLAYERS

**Timeout:** If no GAME_JOIN_ACK within 5 seconds, timeout handler triggered

---

#### 3.2.4 handle_game_join_timeout

```python
handle_game_join_timeout(
    player_id: string,
    retry_count: integer
) -> Result<void, Error>
```

**Description:** Internal timeout handler. Called when player doesn't send GAME_JOIN_ACK within 5 seconds.

**Input Parameters:**
- `player_id` - Player who timed out
- `retry_count` - Current retry attempt number

**Output:** Success (void) or error

**Blocking:** No (asynchronous timeout handling)

**MCP Messages Sent:**
- `GAME_ERROR` → Player (if retrying)
- `GAME_INVITATION` → Player (retry)
- `GAME_OVER` → Both players (if max retries exhausted)

**MCP Messages Handled:** None (internal timeout event)

**Allowed States:** WAITING_FOR_PLAYERS

**State Transition:**
- If retry_count < max_retries (3): Remains WAITING_FOR_PLAYERS
- If retry_count >= max_retries: WAITING_FOR_PLAYERS → NOTIFYING_PLAYERS

**Responsibilities:**
- Increment retry_count for this player
- Log timeout event
- If retry_count < max_retries:
  - Send GAME_ERROR to player (error_code: "TIMEOUT_ERROR", retry_count, max_retries)
  - Resend GAME_INVITATION
  - Restart 5-second timer
- If retry_count >= max_retries:
  - Award technical loss to this player
  - Award win to opponent (by default)
  - Transition to NOTIFYING_PLAYERS

**Failure Handling:**
- If sending GAME_ERROR fails → Log error, proceed to award technical loss

**Timeout:** 5 seconds (timer restarted on retry)

---

#### 3.2.5 handle_choose_parity_response

```python
handle_choose_parity_response(
    player_id: string,
    match_id: string,
    parity_choice: string  # "even" or "odd"
) -> Result<void, Error>
```

**Description:** Handles CHOOSE_PARITY_RESPONSE from player. Stores player's choice. If both players responded, transitions to number drawing.

**Input Parameters:**
- `player_id` - Responding player's ID
- `match_id` - Match identifier
- `parity_choice` - Player's choice ("even" or "odd")

**Output:** Success (void) or error

**Blocking:** No (asynchronous event handling)

**MCP Messages Sent:**
- If both choices received: None (internal transition to DRAWING_NUMBER)

**MCP Messages Handled:** `CHOOSE_PARITY_RESPONSE`

**Allowed States:** COLLECTING_CHOICES

**State Transition:**
- If one choice received: Remains COLLECTING_CHOICES
- If both choices received: COLLECTING_CHOICES → DRAWING_NUMBER

**Responsibilities:**
- Validate match_id matches current match
- Validate player_id is one of the expected players
- Validate parity_choice is "even" or "odd"
- Cancel timeout timer for this player
- Store player's choice
- Store choice timestamp
- If both players have chosen:
  - Transition to DRAWING_NUMBER
  - Trigger number drawing and winner determination

**Failure Handling:**
- If parity_choice invalid → Send GAME_ERROR, error_code: "INVALID_CHOICE", request retry
- If match_id invalid → Send GAME_ERROR, error_code: "MATCH_NOT_FOUND"
- If duplicate choice → Use latest choice, log warning
- If timeout before both choices → Award technical loss

**Timeout:** If no CHOOSE_PARITY_RESPONSE within 30 seconds, timeout handler triggered

---

#### 3.2.6 handle_choose_parity_timeout

```python
handle_choose_parity_timeout(
    player_id: string,
    retry_count: integer
) -> Result<void, Error>
```

**Description:** Timeout handler for CHOOSE_PARITY_RESPONSE. Retries or awards technical loss.

**Input Parameters:**
- `player_id` - Player who timed out
- `retry_count` - Current retry attempt

**Output:** Success (void) or error

**Blocking:** No

**MCP Messages Sent:**
- `GAME_ERROR` → Player (if retrying)
- `CHOOSE_PARITY_CALL` → Player (retry)
- `GAME_OVER` → Both players (if max retries exhausted)

**MCP Messages Handled:** None (timeout event)

**Allowed States:** COLLECTING_CHOICES

**State Transition:**
- If retry_count < max_retries: Remains COLLECTING_CHOICES
- If retry_count >= max_retries: COLLECTING_CHOICES → NOTIFYING_PLAYERS

**Responsibilities:**
- Increment retry_count
- Log timeout
- If retry_count < max_retries:
  - Send GAME_ERROR (error_code: "TIMEOUT_ERROR", action_required: "CHOOSE_PARITY_RESPONSE")
  - Resend CHOOSE_PARITY_CALL
  - Restart 30-second timer
- If retry_count >= max_retries:
  - Award technical loss to this player
  - Award win to opponent
  - Transition to NOTIFYING_PLAYERS

**Failure Handling:**
- If sending GAME_ERROR fails → Award technical loss anyway

**Timeout:** 30 seconds (restarted on retry)

---

#### 3.2.7 draw_number_and_determine_winner

```python
draw_number_and_determine_winner(
    player_A_choice: string,
    player_B_choice: string
) -> Result<MatchResult, Error>
```

**Description:** Internal method. Draws random number (1-10), applies game rules, determines winner.

**Input Parameters:**
- `player_A_choice` - Player A's parity choice ("even" or "odd")
- `player_B_choice` - Player B's parity choice ("even" or "odd")

**Output:**
- Success: `MatchResult` object containing:
  - `status: "WIN" | "DRAW" | "TECHNICAL_LOSS"`
  - `winner_player_id: string | null`
  - `drawn_number: integer` (1-10)
  - `number_parity: "even" | "odd"`
  - `choices: object` (player_id → choice)
  - `reason: string`
- Error: `Error` object

**Blocking:** Yes (synchronous computation, very fast)

**MCP Messages Sent:** None (internal computation)

**MCP Messages Handled:** None (internal method)

**Allowed States:** DRAWING_NUMBER

**State Transition:** DRAWING_NUMBER → NOTIFYING_PLAYERS

**Responsibilities:**
- Draw random number from 1 to 10 (inclusive, uniform distribution)
- Calculate number_parity:
  - If drawn_number % 2 == 0 → "even"
  - Else → "odd"
- Compare choices to number_parity:
  - Player A correct = (player_A_choice == number_parity)
  - Player B correct = (player_B_choice == number_parity)
- Determine winner:
  - If both correct OR both wrong → status = "DRAW", winner_player_id = null
  - If Player A correct AND Player B wrong → status = "WIN", winner_player_id = player_A_id
  - If Player B correct AND Player A wrong → status = "WIN", winner_player_id = player_B_id
- Calculate scores:
  - Winner: 3 points
  - Loser: 0 points
  - Draw: 1 point each
- Generate reason string (e.g., "Number 8 is even. P01 chose 'even' correctly. P01 wins.")
- Log match result

**Failure Handling:**
- If random number generation fails → Retry, if fails repeatedly declare DRAW (fallback)

**Timeout:** N/A (instant computation)

---

#### 3.2.8 notify_players_and_report

```python
notify_players_and_report(
    match_result: MatchResult
) -> Result<void, Error>
```

**Description:** Sends GAME_OVER to both players and MATCH_RESULT_REPORT to League Manager.

**Input Parameters:**
- `match_result` - Complete match result object

**Output:** Success (void) or error

**Blocking:** Yes (waits for acknowledgments or timeout)

**MCP Messages Sent:**
- `GAME_OVER` → Player A
- `GAME_OVER` → Player B
- `MATCH_RESULT_REPORT` → League Manager

**MCP Messages Handled:**
- `GAME_OVER_ACK` (optional, doesn't block)
- `MATCH_RESULT_ACK`

**Allowed States:** NOTIFYING_PLAYERS

**State Transition:**
- NOTIFYING_PLAYERS → REPORTING_RESULT → MATCH_COMPLETE

**Responsibilities:**
- Construct GAME_OVER message with complete game_result
- Send GAME_OVER to Player A (10-second timeout for ack)
- Send GAME_OVER to Player B (10-second timeout for ack)
- Wait for acknowledgments (best effort, doesn't block)
- Construct MATCH_RESULT_REPORT message
- Send MATCH_RESULT_REPORT to League Manager
- Wait for MATCH_RESULT_ACK (10-second timeout)
- If MATCH_RESULT_ACK received:
  - Persist complete match data to `data/matches/<league_id>/<match_id>.json`
  - Log match lifecycle
  - Transition to MATCH_COMPLETE
- If timeout, retry up to 3 times

**Failure Handling:**
- If sending GAME_OVER to player fails → Log error, proceed anyway (best effort)
- If GAME_OVER_ACK not received → Log timeout, proceed anyway
- If sending MATCH_RESULT_REPORT fails → Retry up to 3 times
- If all retries exhausted → Log critical error, transition to MATCH_COMPLETE anyway (referee cannot block on League Manager)

**Timeout:** 10 seconds for GAME_OVER_ACK, 10 seconds for MATCH_RESULT_ACK

---

#### 3.2.9 reset_for_next_match

```python
reset_for_next_match() -> Result<void, Error>
```

**Description:** Cleans up match-specific state and prepares referee for next match assignment.

**Input Parameters:** None

**Output:** Success (void) or error

**Blocking:** Yes (synchronous cleanup)

**MCP Messages Sent:** None

**MCP Messages Handled:** None

**Allowed States:** MATCH_COMPLETE

**State Transition:** MATCH_COMPLETE → IDLE

**Responsibilities:**
- Clear match context (match_id, player IDs, choices)
- Reset retry counters
- Cancel any remaining timers
- Mark referee as available for next match
- Log cleanup event

**Failure Handling:**
- If cleanup fails → Log error but proceed to IDLE (best effort)

**Timeout:** N/A

---

### 3.3 Responsibilities

**MUST:**
1. ✅ Manage complete match lifecycle from invitation to result reporting
2. ✅ Send GAME_INVITATION to both players
3. ✅ Enforce 5-second timeout for GAME_JOIN_ACK
4. ✅ Send CHOOSE_PARITY_CALL to both players
5. ✅ Enforce 30-second timeout for CHOOSE_PARITY_RESPONSE
6. ✅ Draw random number (1-10) with uniform distribution
7. ✅ Apply game rules to determine winner
8. ✅ Send GAME_OVER to both players with complete result
9. ✅ Send MATCH_RESULT_REPORT to League Manager
10. ✅ Implement retry logic (max 3 retries) for timeouts
11. ✅ Award technical losses when retry limit exhausted
12. ✅ Persist complete match data to match file
13. ✅ Log all match events to referee log
14. ✅ Handle invalid choices (not "even" or "odd")

**Source of Truth:**
- Match state (WAITING_FOR_PLAYERS, COLLECTING_CHOICES, etc.)
- Player choices
- Match result

### 3.4 Explicit Non-Responsibilities

**MUST NOT:**
1. ❌ Manage league-wide state or standings
2. ❌ Coordinate multiple matches simultaneously (each referee manages one match at a time)
3. ❌ Register players or referees
4. ❌ Create match schedules
5. ❌ Calculate league standings or rankings
6. ❌ Know about other matches in the round
7. ❌ Manage round lifecycle
8. ❌ Send round announcements
9. ❌ Communicate with League Manager except for registration and result reporting
10. ❌ Store player history (player's responsibility)
11. ❌ Implement player strategies
12. ❌ Make strategic decisions

### 3.5 Failure & Timeout Handling

**Error Surfacing:**
- All methods return `Result<T, Error>` type
- Errors include error code and message
- Errors logged to referee.log.jsonl

**Timeout Enforcement:**
- **5 seconds** for GAME_JOIN_ACK (critical)
- **30 seconds** for CHOOSE_PARITY_RESPONSE (critical)
- **10 seconds** for GAME_OVER_ACK (non-critical, best effort)
- **10 seconds** for MATCH_RESULT_ACK (retry up to 3 times)

**Retry Logic:**
- Max 3 retries for player timeouts
- Exponential backoff optional
- After max retries, award technical loss

**Critical Failures:**
- Both players unreachable → Report match failure to League Manager
- Game rules loading failure → Exit with error
- Port binding failure → Exit with error

**Non-Critical Failures:**
- One player unreachable → Award technical loss to that player, proceed
- GAME_OVER_ACK not received → Proceed anyway (best effort notification)
- MATCH_RESULT_ACK timeout → Retry, proceed after max retries

---

## 4. PlayerInterface

### 4.1 Purpose

**Role:** Autonomous game participant. Responds to invitations, makes strategic decisions, maintains personal history.

**Architectural Block:** Player Agent Block

**Implementation Location:** `agents/player_P01/`

### 4.2 Public Methods

#### 4.2.1 start_player

```python
start_player(
    display_name: string,
    version: string,
    game_types: array[string],
    contact_endpoint: string
) -> Result<void, Error>
```

**Description:** Initializes and starts the Player HTTP server. Registers with League Manager.

**Input Parameters:**
- `display_name` - Player's display name (must be unique)
- `version` - Player version string
- `game_types` - Array of supported game types (e.g., ["even_odd"])
- `contact_endpoint` - Player's HTTP endpoint

**Output:** Success (void) or error

**Blocking:** Yes (blocks until server starts and registration complete)

**MCP Messages Sent:** `LEAGUE_REGISTER_REQUEST` → League Manager

**MCP Messages Handled:** None (initialization only)

**Allowed States:** UNREGISTERED

**State Transition:** UNREGISTERED → REGISTERING → REGISTERED

**Responsibilities:**
- Start HTTP server on configured port (typically 8101-8104)
- Initialize endpoint `/mcp`
- Initialize PlayerHistoryRepository
- Initialize JsonLogger for player logging
- Initialize MCP client
- Initialize strategy module
- Send LEAGUE_REGISTER_REQUEST to League Manager
- Wait for LEAGUE_REGISTER_RESPONSE
- Store player_id and auth_token on successful registration
- Load personal history from history.json (if exists)

**Failure Handling:**
- If port in use → Return error "PORT_IN_USE"
- If registration rejected → Return error "REGISTRATION_REJECTED" with reason
- If League Manager unreachable → Retry up to 3 times, then exit with error

---

#### 4.2.2 handle_round_announcement

```python
handle_round_announcement(
    league_id: string,
    round_id: integer,
    matches: array[Match]
) -> Result<void, Error>
```

**Description:** Handles ROUND_ANNOUNCEMENT from League Manager. Prepares for upcoming matches.

**Input Parameters:**
- `league_id` - League identifier
- `round_id` - Round number
- `matches` - Array of match objects

**Output:** Success (void) or error

**Blocking:** No (asynchronous event handling)

**MCP Messages Sent:** `ROUND_ANNOUNCEMENT_ACK` → League Manager

**MCP Messages Handled:** `ROUND_ANNOUNCEMENT`

**Allowed States:** REGISTERED, MATCH_COMPLETE

**State Transition:** REGISTERED → WAITING_FOR_ROUND (or MATCH_COMPLETE → WAITING_FOR_ROUND)

**Responsibilities:**
- Validate league_id matches player's league
- Parse matches array
- Find match(es) where player is participant (player_A_id or player_B_id)
- Store match context (match_id, opponent_id, referee_endpoint)
- Send ROUND_ANNOUNCEMENT_ACK to League Manager (within 10 seconds)
- Log round announcement
- Prepare to receive GAME_INVITATION from referee

**Failure Handling:**
- If player not in any match → Log warning (sitting out this round), stay in REGISTERED
- If league_id mismatch → Log error, ignore message
- If sending acknowledgment fails → Retry up to 3 times

**Timeout:** 10 seconds for acknowledgment

---

#### 4.2.3 handle_game_invitation

```python
handle_game_invitation(
    match_id: string,
    league_id: string,
    round_id: integer,
    game_type: string,
    role_in_match: string,  # "PLAYER_A" or "PLAYER_B"
    opponent_id: string,
    auth_token: string
) -> Result<void, Error>
```

**Description:** Handles GAME_INVITATION from referee. Must respond with GAME_JOIN_ACK within 5 seconds.

**Input Parameters:**
- `match_id` - Match identifier
- `league_id` - League identifier
- `round_id` - Round number
- `game_type` - Game type (e.g., "even_odd")
- `role_in_match` - Player's role ("PLAYER_A" or "PLAYER_B")
- `opponent_id` - Opponent's player ID
- `auth_token` - Referee's auth token

**Output:** Success (void) or error

**Blocking:** Yes (MUST respond within 5 seconds)

**MCP Messages Sent:** `GAME_JOIN_ACK` → Referee (within 5 seconds)

**MCP Messages Handled:** `GAME_INVITATION`

**Allowed States:** WAITING_FOR_ROUND

**State Transition:** WAITING_FOR_ROUND → INVITED_TO_MATCH → WAITING_FOR_CHOICE_REQUEST

**Responsibilities:**
- Validate match_id matches expected match
- Validate league_id, opponent_id
- Store role_in_match
- Store referee sender for future messages
- Construct GAME_JOIN_ACK message:
  - `accept: true`
  - `arrival_timestamp: current UTC time`
- Send GAME_JOIN_ACK to referee **within 5 seconds**
- Log invitation and join confirmation

**Failure Handling:**
- If validation fails → Log error, still send GAME_JOIN_ACK to avoid technical loss
- If sending GAME_JOIN_ACK fails → Retry immediately (within 5-second window)
- If 5-second window expires → Player receives technical loss from referee

**Timeout:** **CRITICAL: 5 seconds** to send GAME_JOIN_ACK

**Note:** Player always accepts invitations (accept = true). Declining would result in immediate technical loss.

---

#### 4.2.4 handle_choose_parity_call

```python
handle_choose_parity_call(
    match_id: string,
    player_id: string,
    game_type: string,
    context: ChoiceContext,
    deadline: string,  # ISO timestamp
    auth_token: string
) -> Result<void, Error>
```

**Description:** Handles CHOOSE_PARITY_CALL from referee. Must invoke strategy and respond with CHOOSE_PARITY_RESPONSE within 30 seconds.

**Input Parameters:**
- `match_id` - Match identifier
- `player_id` - This player's ID (for validation)
- `game_type` - Game type
- `context` - Object containing:
  - `opponent_id: string`
  - `round_id: integer`
  - `your_standings: object` (wins, losses, draws, points)
- `deadline` - ISO 8601 timestamp (30 seconds from now)
- `auth_token` - Referee's auth token

**Output:** Success (void) or error

**Blocking:** Yes (MUST respond within 30 seconds)

**MCP Messages Sent:** `CHOOSE_PARITY_RESPONSE` → Referee (within 30 seconds)

**MCP Messages Handled:** `CHOOSE_PARITY_CALL`

**Allowed States:** WAITING_FOR_CHOICE_REQUEST

**State Transition:** WAITING_FOR_CHOICE_REQUEST → CHOOSING_PARITY → WAITING_FOR_RESULT

**Responsibilities:**
- Validate match_id, player_id
- Parse context (opponent, standings)
- Invoke strategy module to make choice:
  - Pass context to strategy
  - Strategy returns "even" or "odd"
- Validate strategy output is "even" or "odd"
- Construct CHOOSE_PARITY_RESPONSE message
- Send to referee **within 30 seconds**
- Log choice (for strategy learning)

**Failure Handling:**
- If strategy module fails → Use fallback choice ("even")
- If strategy takes too long → Cancel strategy, use fallback, send immediately
- If sending CHOOSE_PARITY_RESPONSE fails → Retry immediately (within 30-second window)
- If 30-second window expires → Player receives technical loss from referee

**Timeout:** **CRITICAL: 30 seconds** to send CHOOSE_PARITY_RESPONSE

**Note:** Strategy module MUST return choice within 30 seconds or player risks technical loss.

---

#### 4.2.5 make_strategy_decision

```python
make_strategy_decision(
    context: ChoiceContext
) -> Result<string, Error>  # Returns "even" or "odd"
```

**Description:** Internal method (or separate strategy module). Makes strategic choice based on context.

**Input Parameters:**
- `context` - Choice context (opponent, standings, history)

**Output:**
- Success: "even" or "odd"
- Error: Error object (strategy failure)

**Blocking:** Yes (synchronous computation, MUST complete within 30 seconds)

**MCP Messages Sent:** None (internal computation)

**MCP Messages Handled:** None (internal method)

**Allowed States:** CHOOSING_PARITY

**State Transition:** None (internal computation)

**Responsibilities:**
- Analyze context (opponent history, current standings, round number)
- Load personal history if needed
- Apply strategy algorithm:
  - Random strategy: randomly choose "even" or "odd"
  - Pattern-based: analyze opponent's past choices
  - ML-based: use trained model
- Return choice within allocated time
- Log decision rationale (for learning)

**Failure Handling:**
- If computation takes > 30 seconds → Timeout, use fallback
- If strategy crashes → Return error, caller uses fallback

**Timeout:** Strategy MUST return within 30 seconds (enforced by caller)

---

#### 4.2.6 handle_game_over

```python
handle_game_over(
    match_id: string,
    game_type: string,
    game_result: GameResult,
    auth_token: string
) -> Result<void, Error>
```

**Description:** Handles GAME_OVER from referee. Updates personal statistics and history.

**Input Parameters:**
- `match_id` - Match identifier
- `game_type` - Game type
- `game_result` - Object containing:
  - `status: "WIN" | "DRAW" | "TECHNICAL_LOSS"`
  - `winner_player_id: string | null`
  - `drawn_number: integer`
  - `number_parity: "even" | "odd"`
  - `choices: object` (player_id → choice)
  - `reason: string`
- `auth_token` - Referee's auth token

**Output:** Success (void) or error

**Blocking:** No (asynchronous event handling)

**MCP Messages Sent:** `GAME_OVER_ACK` → Referee (within 10 seconds)

**MCP Messages Handled:** `GAME_OVER`

**Allowed States:** WAITING_FOR_RESULT

**State Transition:** WAITING_FOR_RESULT → MATCH_COMPLETE

**Responsibilities:**
- Parse game_result
- Determine outcome for this player:
  - If winner_player_id == player_id → Win
  - If winner_player_id == opponent_id → Loss
  - If status == "DRAW" → Draw
  - If status == "TECHNICAL_LOSS" and affected player is self → Technical loss
- Update internal statistics:
  - Increment wins/losses/draws/technical_losses
  - Update points (win=3, draw=1, loss=0)
  - Update total matches played
- Store match result in personal history:
  - Match ID, opponent, result, choices, drawn number
- Persist history to `data/players/<player_id>/history.json`
- Send GAME_OVER_ACK to referee (within 10 seconds)
- Log match outcome
- Optionally: Feed result to strategy module for learning

**Failure Handling:**
- If game_result parsing fails → Log error, still acknowledge
- If history persistence fails → Log critical error, still acknowledge
- If sending acknowledgment fails → Retry up to 3 times

**Timeout:** 10 seconds for acknowledgment (best effort, doesn't cause technical loss)

---

#### 4.2.7 handle_standings_update

```python
handle_standings_update(
    league_id: string,
    round_id: integer,
    standings: array[Standing]
) -> Result<void, Error>
```

**Description:** Handles LEAGUE_STANDINGS_UPDATE from League Manager. Updates internal standings cache.

**Input Parameters:**
- `league_id` - League identifier
- `round_id` - Completed round number
- `standings` - Array of standings (rank, player_id, points, wins, losses, draws, played)

**Output:** Success (void) or error

**Blocking:** No (asynchronous event handling)

**MCP Messages Sent:** `STANDINGS_UPDATE_ACK` → League Manager (within 10 seconds)

**MCP Messages Handled:** `LEAGUE_STANDINGS_UPDATE`

**Allowed States:** MATCH_COMPLETE

**State Transition:** None (remains in MATCH_COMPLETE)

**Responsibilities:**
- Parse standings array
- Find player's rank and statistics
- Update internal standings cache
- Send STANDINGS_UPDATE_ACK to League Manager
- Log standings update
- Optionally: Display standings to user or use for strategy

**Failure Handling:**
- If standings parsing fails → Log error, still acknowledge
- If sending acknowledgment fails → Retry up to 3 times

**Timeout:** 10 seconds for acknowledgment

---

#### 4.2.8 handle_round_completed

```python
handle_round_completed(
    league_id: string,
    round_id: integer,
    matches_played: integer,
    next_round_id: integer | null
) -> Result<void, Error>
```

**Description:** Handles ROUND_COMPLETED from League Manager. Prepares for next round or league completion.

**Input Parameters:**
- `league_id` - League identifier
- `round_id` - Completed round number
- `matches_played` - Number of matches in round
- `next_round_id` - Next round number or null if done

**Output:** Success (void) or error

**Blocking:** No

**MCP Messages Sent:** `ROUND_COMPLETED_ACK` → League Manager (within 10 seconds)

**MCP Messages Handled:** `ROUND_COMPLETED`

**Allowed States:** MATCH_COMPLETE

**State Transition:**
- If next_round_id not null: MATCH_COMPLETE → REGISTERED
- If next_round_id is null: MATCH_COMPLETE → (waiting for LEAGUE_COMPLETED)

**Responsibilities:**
- Mark current round as complete
- Send ROUND_COMPLETED_ACK to League Manager
- Log round completion
- If next_round_id not null, prepare for next round announcement
- If next_round_id is null, expect LEAGUE_COMPLETED

**Failure Handling:**
- If sending acknowledgment fails → Retry

**Timeout:** 10 seconds for acknowledgment

---

#### 4.2.9 handle_league_completed

```python
handle_league_completed(
    league_id: string,
    total_rounds: integer,
    total_matches: integer,
    champion: Champion,
    final_standings: array[Standing]
) -> Result<void, Error>
```

**Description:** Handles LEAGUE_COMPLETED from League Manager. Finalizes player state and prepares for shutdown.

**Input Parameters:**
- `league_id` - League identifier
- `total_rounds` - Total rounds played
- `total_matches` - Total matches played
- `champion` - Champion object (player_id, display_name, points)
- `final_standings` - Final standings array

**Output:** Success (void) or error

**Blocking:** No

**MCP Messages Sent:** `LEAGUE_COMPLETED_ACK` → League Manager (within 10 seconds)

**MCP Messages Handled:** `LEAGUE_COMPLETED`

**Allowed States:** MATCH_COMPLETE, REGISTERED

**State Transition:** → LEAGUE_COMPLETE

**Responsibilities:**
- Parse final standings
- Find player's final rank
- Log final statistics
- Persist final state
- Send LEAGUE_COMPLETED_ACK to League Manager
- Optionally: Display final standings and champion to user
- Prepare for graceful shutdown

**Failure Handling:**
- If acknowledgment fails → Retry once, then proceed to shutdown

**Timeout:** 10 seconds for acknowledgment

---

#### 4.2.10 shutdown_gracefully

```python
shutdown_gracefully() -> Result<void, Error>
```

**Description:** Performs graceful shutdown after league completion.

**Input Parameters:** None

**Output:** Success (void) or error

**Blocking:** Yes (shutdown process)

**MCP Messages Sent:** None

**MCP Messages Handled:** None

**Allowed States:** LEAGUE_COMPLETE

**State Transition:** LEAGUE_COMPLETE → (process exit)

**Responsibilities:**
- Persist any remaining data
- Close HTTP server
- Close file handles
- Flush logs
- Log shutdown event
- Exit process cleanly

**Failure Handling:**
- Best effort shutdown, log any errors

**Timeout:** N/A

---

### 4.3 Responsibilities

**MUST:**
1. ✅ Register with League Manager on startup
2. ✅ Respond to GAME_INVITATION with GAME_JOIN_ACK **within 5 seconds**
3. ✅ Respond to CHOOSE_PARITY_CALL with CHOOSE_PARITY_RESPONSE **within 30 seconds**
4. ✅ Invoke strategy module to make choice
5. ✅ Update personal statistics after each match
6. ✅ Persist personal history to history.json after each match
7. ✅ Acknowledge all messages within specified timeouts
8. ✅ Handle technical losses gracefully
9. ✅ Log all events to personal log
10. ✅ Implement strategy algorithm (can be simple or complex)
11. ✅ Maintain internal standings cache

**Source of Truth:**
- Personal history
- Personal statistics (wins, losses, draws, points)

### 4.4 Explicit Non-Responsibilities

**MUST NOT:**
1. ❌ Manage matches or enforce rules
2. ❌ Coordinate other players
3. ❌ Maintain league-wide state (only tracks, doesn't manage)
4. ❌ Assign matches or create schedules
5. ❌ Validate other players' choices
6. ❌ Determine match winners (referee's responsibility)
7. ❌ Draw random numbers
8. ❌ Send messages to other players directly
9. ❌ Broadcast to multiple recipients
10. ❌ Manage timeouts for other players
11. ❌ Register other agents
12. ❌ Modify league configuration
13. ❌ Access other players' histories or strategies

### 4.5 Failure & Timeout Handling

**Error Surfacing:**
- All methods return `Result<T, Error>` type
- Errors logged to player log

**Timeout Enforcement (Player MUST Meet):**
- **5 seconds** for GAME_JOIN_ACK (enforced by referee)
- **30 seconds** for CHOOSE_PARITY_RESPONSE (enforced by referee)
- Missing these timeouts → Technical loss from referee

**Non-Critical Timeouts (Best Effort):**
- 10 seconds for acknowledgments (ROUND_ANNOUNCEMENT_ACK, etc.)
- Missing these doesn't cause technical loss

**Critical Failures:**
- Registration failure → Exit with error
- Port binding failure → Exit with error
- Strategy module crash → Use fallback choice to avoid technical loss

**Non-Critical Failures:**
- Acknowledgment send failure → Retry, log error
- History persistence failure → Log critical error, continue
- Standings update parse failure → Log error, continue

**Strategy Module Protection:**
- Wrap strategy call in timeout (30 seconds max)
- If strategy times out → Cancel, use fallback choice ("even")
- If strategy crashes → Catch exception, use fallback
- Always ensure CHOOSE_PARITY_RESPONSE sent within 30 seconds

---

## 5. MCPClientInterface

### 5.1 Purpose

**Role:** Protocol-compliant messaging infrastructure. Handles JSON-RPC 2.0 formatting, HTTP transport, and timeout enforcement. Abstracts communication from business logic.

**Architectural Block:** MCP Communication Layer

**Implementation Location:** `SHARED/league_sdk/mcp_client.py`

### 5.2 Public Methods

#### 5.2.1 initialize

```python
initialize(
    protocol_version: string,
    base_timeout: integer
) -> Result<void, Error>
```

**Description:** Initializes the MCP client with protocol version and default timeout.

**Input Parameters:**
- `protocol_version` - Protocol version (e.g., "league.v2")
- `base_timeout` - Default timeout in seconds (e.g., 10)

**Output:** Success (void) or error

**Blocking:** Yes (initialization)

**Responsibilities:**
- Set protocol version for all messages
- Set default timeout
- Initialize HTTP client library
- Initialize request ID generator
- Initialize conversation ID generator

**Failure Handling:**
- If HTTP client initialization fails → Return error

---

#### 5.2.2 send_request

```python
send_request(
    method: string,
    params: object,
    endpoint: string,
    timeout: integer | null
) -> Result<object, Error>
```

**Description:** Sends JSON-RPC 2.0 request to specified endpoint and waits for response.

**Input Parameters:**
- `method` - JSON-RPC method name (e.g., "register_player")
- `params` - Message payload (already formatted with protocol fields)
- `endpoint` - Target HTTP endpoint (e.g., "http://localhost:8000/mcp")
- `timeout` - Optional timeout override (uses default if null)

**Output:**
- Success: Response `result` object
- Error: Error object (network error, timeout, or JSON-RPC error)

**Blocking:** Yes (waits for response or timeout)

**Responsibilities:**
- Generate unique request ID
- Construct JSON-RPC 2.0 request envelope:
  ```json
  {
    "jsonrpc": "2.0",
    "method": method,
    "params": params,
    "id": request_id
  }
  ```
- Add HTTP headers:
  - `Content-Type: application/json`
- Send POST request to endpoint
- Wait for response with timeout
- Parse JSON-RPC response
- Validate response structure
- Extract `result` or `error` from response
- Return result or throw error

**Failure Handling:**
- If endpoint unreachable → Return error "ENDPOINT_UNREACHABLE"
- If connection timeout → Return error "CONNECTION_TIMEOUT"
- If response timeout → Return error "RESPONSE_TIMEOUT"
- If response invalid JSON → Return error "INVALID_JSON"
- If JSON-RPC error in response → Return error with JSON-RPC error details
- If HTTP error (4xx, 5xx) → Return error with HTTP status

**Timeout:** Specified timeout (or default)

---

#### 5.2.3 send_notification

```python
send_notification(
    method: string,
    params: object,
    endpoint: string
) -> Result<void, Error>
```

**Description:** Sends JSON-RPC 2.0 notification (no response expected, no `id` field).

**Input Parameters:**
- `method` - JSON-RPC method name
- `params` - Message payload
- `endpoint` - Target endpoint

**Output:** Success (void) or error

**Blocking:** No (fire-and-forget)

**Responsibilities:**
- Construct JSON-RPC 2.0 notification (without `id` field)
- Send POST request
- Do not wait for response
- Log send event

**Failure Handling:**
- If endpoint unreachable → Return error (but don't block)
- Log any errors

**Timeout:** N/A (no response expected)

---

#### 5.2.4 format_message

```python
format_message(
    message_type: string,
    sender: string,
    payload: object
) -> object
```

**Description:** Formats message payload with common protocol fields.

**Input Parameters:**
- `message_type` - MCP message type (e.g., "ROUND_ANNOUNCEMENT")
- `sender` - Sender identifier (e.g., "league_manager")
- `payload` - Message-specific payload

**Output:** Formatted message object with all required fields

**Blocking:** No (synchronous formatting)

**Responsibilities:**
- Add common fields to payload:
  - `protocol: "league.v2"`
  - `message_type: message_type`
  - `sender: sender`
  - `timestamp: current UTC time in ISO 8601 format`
  - `conversation_id: generated conversation ID`
- Merge with message-specific payload
- Return complete message object

**Failure Handling:**
- If timestamp generation fails → Use fallback timestamp

---

#### 5.2.5 validate_response

```python
validate_response(
    response: object,
    expected_message_type: string | null
) -> Result<object, Error>
```

**Description:** Validates JSON-RPC response structure and protocol fields.

**Input Parameters:**
- `response` - Raw response object
- `expected_message_type` - Expected message_type in result (optional)

**Output:**
- Success: Validated result object
- Error: Validation error

**Blocking:** No (synchronous validation)

**Responsibilities:**
- Validate JSON-RPC structure:
  - `jsonrpc == "2.0"`
  - Has `result` or `error` field
- If `result`:
  - Validate protocol fields present
  - If expected_message_type specified, validate message_type matches
- If `error`:
  - Extract error details
  - Return error

**Failure Handling:**
- If validation fails → Return error with details

---

#### 5.2.6 generate_conversation_id

```python
generate_conversation_id(
    prefix: string
) -> string
```

**Description:** Generates unique conversation ID for message tracing.

**Input Parameters:**
- `prefix` - Prefix for conversation ID (e.g., "conv-round-1")

**Output:** Unique conversation ID string

**Blocking:** No

**Responsibilities:**
- Generate unique ID (UUID or sequential)
- Prepend prefix
- Return formatted conversation ID (e.g., "conv-round-1-abc123")

**Failure Handling:**
- If UUID generation fails → Use timestamp-based ID

---

#### 5.2.7 set_timeout

```python
set_timeout(
    timeout_seconds: integer
) -> void
```

**Description:** Sets default timeout for future requests.

**Input Parameters:**
- `timeout_seconds` - Timeout in seconds

**Output:** None

**Blocking:** No

**Responsibilities:**
- Update internal default timeout
- All future requests use this timeout unless overridden

---

### 5.3 Responsibilities

**MUST:**
1. ✅ Format all messages with JSON-RPC 2.0 envelope
2. ✅ Add protocol fields (protocol, message_type, sender, timestamp, conversation_id)
3. ✅ Send HTTP POST requests to /mcp endpoint
4. ✅ Enforce timeouts on all requests
5. ✅ Parse JSON-RPC responses
6. ✅ Validate response structure
7. ✅ Extract result or error from responses
8. ✅ Handle network errors gracefully
9. ✅ Generate unique request IDs and conversation IDs
10. ✅ Log all communication events
11. ✅ Support both requests (with response) and notifications (no response)

### 5.4 Explicit Non-Responsibilities

**MUST NOT:**
1. ❌ Implement business logic
2. ❌ Maintain agent state
3. ❌ Make strategic decisions
4. ❌ Validate business rules (only validates protocol structure)
5. ❌ Persist data to files (passes through)
6. ❌ Manage registration or standings
7. ❌ Determine message recipients (caller specifies)
8. ❌ Create schedules or assign matches
9. ❌ Retry based on business logic (only network-level retries)
10. ❌ Authenticate users (passes through auth tokens)
11. ❌ Modify message payloads (passes through what caller provides)
12. ❌ Know about game semantics (even/odd, wins/losses)

### 5.5 Failure & Timeout Handling

**Error Surfacing:**
- All methods return `Result<T, Error>` or throw exceptions
- Errors include:
  - Network errors (unreachable, timeout)
  - JSON parsing errors
  - Protocol validation errors
  - JSON-RPC errors from server

**Timeout Enforcement:**
- HTTP connection timeout (configurable)
- HTTP read timeout (configurable)
- Request-specific timeouts (5s, 10s, 30s)
- Caller specifies timeout per request

**Retry Logic:**
- Network-level retries for transient failures (optional)
- Exponential backoff (optional)
- Max retries configurable (typically 3)

**Critical Failures:**
- HTTP client initialization failure → Cannot proceed, return error

**Non-Critical Failures:**
- Single request timeout → Return timeout error to caller
- Network unreachable → Return network error to caller
- Invalid response → Return parse error to caller

---

## 6. Interface Mapping to Project Tree

### 6.1 Interface to Directory Mapping

| Interface | Implementation Location | Source Files |
|-----------|------------------------|--------------|
| **LeagueManagerInterface** | `agents/league_manager/` | `main.py` (initialization)<br/>`handlers.py` (message handlers)<br/>`scheduler.py` (schedule creation) |
| **RefereeInterface** | `agents/referee_REF01/`<br/>`agents/referee_REF02/` | `main.py` (initialization)<br/>`handlers.py` (message handlers)<br/>`game_logic.py` (game rules) |
| **PlayerInterface** | `agents/player_P01/`<br/>`agents/player_P02/`<br/>`agents/player_P03/`<br/>`agents/player_P04/` | `main.py` (initialization)<br/>`handlers.py` (MCP tool implementations)<br/>`strategy.py` (decision making) |
| **MCPClientInterface** | `SHARED/league_sdk/` | `mcp_client.py` (MCP protocol client) |

### 6.2 Interface Dependencies

**LeagueManagerInterface depends on:**
- MCPClientInterface (for sending messages)
- ConfigLoader (for loading configuration)
- StandingsRepository, RoundsRepository (for data persistence)
- JsonLogger (for logging)

**RefereeInterface depends on:**
- MCPClientInterface (for sending messages)
- MatchRepository (for match data persistence)
- JsonLogger (for logging)
- Game rules module (game_logic.py)

**PlayerInterface depends on:**
- MCPClientInterface (for sending messages)
- PlayerHistoryRepository (for history persistence)
- JsonLogger (for logging)
- Strategy module (strategy.py)

**MCPClientInterface depends on:**
- HTTP client library (requests, httpx, etc.)
- JSON library (json)

### 6.3 Interface Implementation Pattern

**Recommended Implementation:**

```python
# agents/league_manager/main.py

from league_sdk.mcp_client import MCPClient
from league_sdk.config_loader import ConfigLoader
from league_sdk.repositories import StandingsRepository, RoundsRepository
from league_sdk.logger import JsonLogger

class LeagueManager:
    """Implementation of LeagueManagerInterface"""

    def __init__(self, league_id: str):
        self.league_id = league_id
        self.mcp_client = MCPClient()
        self.config_loader = ConfigLoader()
        self.standings_repo = StandingsRepository(league_id)
        self.rounds_repo = RoundsRepository(league_id)
        self.logger = JsonLogger("league_manager", league_id)
        self.state = "WAITING_FOR_REGISTRATIONS"

    def start_league_manager(self, system_config, league_config):
        # Implementation of interface method
        ...

    def register_referee(self, referee_meta):
        # Implementation of interface method
        ...

    # ... other interface methods
```

### 6.4 Testing Strategy

**Unit Testing:**
- Mock MCPClientInterface for testing LeagueManager/Referee/Player in isolation
- Mock repositories for testing data operations
- Mock strategy module for testing Player decision flow

**Integration Testing:**
- Test interface interactions between components
- Use real MCPClient with test endpoints
- Test complete flows (registration, match, standings)

**Contract Testing:**
- Verify each interface implementation conforms to specification
- Test all error conditions
- Test timeout behavior

---

## 7. Summary

### 7.1 Interface Overview

| Interface | Methods | Critical Timeouts | Key Responsibilities |
|-----------|---------|-------------------|---------------------|
| **LeagueManagerInterface** | 10 | 10s (acknowledgments) | Registration, scheduling, standings |
| **RefereeInterface** | 9 | 5s, 30s, 10s | Match orchestration, rule enforcement |
| **PlayerInterface** | 10 | 5s, 30s (MUST meet) | Game participation, strategy |
| **MCPClientInterface** | 7 | Configurable | Message formatting, HTTP transport |

### 7.2 Design Principles Enforced

1. **Separation of Concerns:** Each interface has clear, non-overlapping responsibilities
2. **Protocol Compliance:** All methods aligned with MCP message contracts
3. **State Awareness:** Methods specify allowed states
4. **Explicit Failures:** All error conditions documented
5. **Timeout Enforcement:** Critical timeouts (5s, 30s) clearly marked
6. **Testability:** Interfaces designed for mocking and unit testing

### 7.3 Implementation Checklist

For each interface:
- [ ] Implement all public methods with correct signatures
- [ ] Return Result<T, Error> types as specified
- [ ] Enforce state constraints (check current state before method execution)
- [ ] Implement timeout enforcement
- [ ] Handle all documented error conditions
- [ ] Log all events to appropriate log file
- [ ] Write unit tests for each method
- [ ] Write integration tests for interface interactions
- [ ] Validate against MCP message contracts
- [ ] Test timeout scenarios

---

**Document Status:** Complete Interface Specifications
**Coverage:** 4 interfaces, 36 public methods fully documented
**Ready For:** Implementation, testing, and grading
