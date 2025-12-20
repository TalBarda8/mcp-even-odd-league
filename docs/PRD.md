# Product Requirements Document (PRD)
## MCP Even/Odd League System

**Document Version:** 1.0
**Date:** 2025-01-20
**Protocol Version:** league.v2
**Status:** Active Development

---

## Table of Contents

1. [Problem Definition & Learning Goals](#1-problem-definition--learning-goals)
2. [System Scope & Assumptions](#2-system-scope--assumptions)
3. [Actors & Responsibilities](#3-actors--responsibilities)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Constraints](#6-constraints)
7. [Engineering Success Metrics](#7-engineering-success-metrics)
8. [Out of Scope](#8-out-of-scope)
9. [References](#9-references)

---

## 1. Problem Definition & Learning Goals

### 1.1 Problem Statement

Students in advanced computer science programs need practical experience with distributed multi-agent systems that communicate using standardized protocols. Traditional assignments focus on single-agent implementations or tightly-coupled systems that don't prepare students for real-world distributed architectures.

**Core Challenge:** Design and implement a distributed multi-agent system where autonomous agents communicate via the Model Context Protocol (MCP), coordinate without centralized control, and operate under real-time constraints with fault tolerance.

### 1.2 Learning Objectives

Students completing this project will demonstrate mastery of:

1. **Protocol-First Design**
   - Designing systems around formal message contracts (JSON-RPC 2.0)
   - Implementing MCP-compliant communication patterns
   - Understanding protocol versioning and backward compatibility

2. **Multi-Agent Coordination**
   - Orchestrating multiple independent agents without central control
   - Implementing distributed state management
   - Handling asynchronous message passing between agents

3. **State Machine Design**
   - Modeling agent behavior with formal state machines
   - Implementing state transitions with guards and actions
   - Handling timeout and error recovery in stateful systems

4. **Distributed Systems Concepts**
   - Managing eventual consistency across agents
   - Implementing timeout-based failure detection
   - Handling network failures and retry logic
   - Understanding sources of truth in distributed systems

5. **Software Engineering Practices**
   - Building modular, testable components
   - Implementing clean interfaces and separation of concerns
   - Writing comprehensive documentation
   - Using version control and testing methodologies

### 1.3 Success Criteria for Students

A student successfully completes the project when their implementation:

- ✅ Implements a player agent that can join a league with 3+ other students' agents
- ✅ Responds to all protocol messages within specified timeouts (5s, 30s)
- ✅ Operates continuously through a full league (multiple rounds, multiple matches)
- ✅ Handles errors gracefully without crashes
- ✅ Demonstrates understanding through clean architecture and documentation

---

## 2. System Scope & Assumptions

### 2.1 System Scope

**In Scope:**

The system implements a complete multi-agent league platform for playing a simple even/odd game:

- **Agent Types:** League Manager, Referee, Player
- **Communication:** HTTP-based JSON-RPC 2.0 using MCP protocol
- **Game Type:** Even/Odd parity guessing game (single game type)
- **Tournament Format:** Round-Robin scheduling (every player plays every other player)
- **Scale:** Designed for 2-10,000 players per league
- **Data Persistence:** JSON file-based data storage for configuration, state, and logs
- **Agent Autonomy:** Each player implements their own strategy

**Student Requirements (Mandatory):**

Per `docs/assignment/chapter_06_requirements.md`:

1. Implement a player agent as an MCP server on localhost
2. Support three required MCP tools:
   - `handle_game_invitation` → returns `GAME_JOIN_ACK`
   - `parity_choose` → returns `CHOOSE_PARITY_RESPONSE`
   - `notify_match_result` → updates internal state
3. Register with league manager providing display name, version, endpoint
4. Test locally with 4 players before submission
5. Respond within timeouts: GAME_JOIN_ACK (5s), CHOOSE_PARITY_RESPONSE (30s)
6. Operate without crashes throughout the league

### 2.2 System Assumptions

**Infrastructure Assumptions:**

1. **Network:** All agents run on localhost during development/testing
2. **Reliability:** HTTP is reliable enough for localhost communication (no message loss)
3. **Ordering:** Messages may arrive out of order, agents must handle this
4. **Concurrency:** Referees handle one match at a time (no concurrent match management per referee)
5. **Player Availability:** Players may become unavailable; system handles via technical losses

**Protocol Assumptions:**

1. **Version:** All components use `league.v2` protocol
2. **Time Synchronization:** All timestamps in UTC (ISO 8601)
3. **Message Format:** JSON-RPC 2.0 over HTTP POST to `/mcp` endpoint
4. **Authentication:** Token-based (simple, not cryptographically secure)
5. **Conversation IDs:** Unique per logical conversation for tracing

**Game Logic Assumptions:**

Per `docs/assignment/chapter_08_game_flow.md`:

1. **Random Number:** Drawn from uniform distribution 1-10 (inclusive)
2. **Parity Rules:**
   - Both correct → DRAW
   - Both wrong → DRAW
   - One correct → Winner
3. **Scoring:** Win = 3 points, Draw = 1 point, Loss = 0 points
4. **Technical Loss:** Awarded for timeout after max retries (3)

**Data Assumptions:**

Per `docs/assignment/chapter_09_protocol.md`:

1. **File System:** Shared directory accessible to all agents (`SHARED/`)
2. **File Format:** All config/data files are JSON, logs are JSONL
3. **Persistence:** Agents persist state to files for audit trail
4. **Concurrency:** File writes are atomic (OS-level guarantee)

### 2.3 Environmental Constraints

**Development Environment:**

- Language: Any (Python recommended)
- OS: Cross-platform (tested on macOS, Linux, Windows)
- Dependencies: HTTP server library, JSON library
- Ports: 8000 (League Manager), 8001-8002 (Referees), 8101-8104 (Players)

**Deployment Environment:**

- Deployment: Local only (no production deployment)
- Scalability: Designed for future scaling to thousands of agents
- Monitoring: JSON log files for debugging

---

## 3. Actors & Responsibilities

### 3.1 Primary Actors

Per `docs/architecture/interfaces.md`:

#### 3.1.1 League Manager

**Type:** Top-level orchestrator
**Cardinality:** 1 per league
**Port:** 8000
**Endpoint:** `http://localhost:8000/mcp`

**Core Responsibilities:**

- ✅ Manage agent registration (referees and players)
- ✅ Generate unique IDs (REF01, P01, P02, etc.)
- ✅ Generate and validate authentication tokens
- ✅ Create Round-Robin match schedules
- ✅ Broadcast round announcements to all players
- ✅ Receive and process match results from referees
- ✅ Calculate and update standings after each match
- ✅ Determine champion and declare league completion
- ✅ Persist state to `standings.json` and `rounds.json`
- ✅ Log all events to `league.log.jsonl`

**Source of Truth:**
- Standings table
- Match schedule
- Round status
- League lifecycle state

**Explicit Non-Responsibilities:**
- ❌ Manage individual match gameplay
- ❌ Enforce game rules (even/odd logic)
- ❌ Determine match winners (referee's job)
- ❌ Collect player choices directly

---

#### 3.1.2 Referee

**Type:** Match-level orchestrator
**Cardinality:** 2+ per league
**Ports:** 8001, 8002, ...
**Endpoints:** `http://localhost:8001/mcp`, etc.

**Core Responsibilities:**

- ✅ Manage complete match lifecycle (invitation → result)
- ✅ Send GAME_INVITATION to both players
- ✅ Enforce 5-second timeout for GAME_JOIN_ACK
- ✅ Send CHOOSE_PARITY_CALL to both players
- ✅ Enforce 30-second timeout for CHOOSE_PARITY_RESPONSE
- ✅ Draw random number (1-10) with uniform distribution
- ✅ Apply game rules to determine winner
- ✅ Send GAME_OVER to both players
- ✅ Send MATCH_RESULT_REPORT to League Manager
- ✅ Implement retry logic (max 3 retries)
- ✅ Award technical losses when timeouts exhausted
- ✅ Persist match data to `data/matches/<league_id>/<match_id>.json`

**Source of Truth:**
- Match state (see `docs/architecture/state_machines.md`)
- Player choices
- Match result

**Explicit Non-Responsibilities:**
- ❌ Manage league-wide state
- ❌ Coordinate multiple matches simultaneously (one at a time)
- ❌ Calculate standings
- ❌ Know about other matches

---

#### 3.1.3 Player

**Type:** Autonomous game participant
**Cardinality:** 2-10,000 per league
**Ports:** 8101-8104 (development), dynamic in production
**Endpoints:** `http://localhost:8101/mcp`, etc.

**Core Responsibilities:**

- ✅ Register with League Manager on startup
- ✅ Respond to GAME_INVITATION with GAME_JOIN_ACK **within 5 seconds**
- ✅ Respond to CHOOSE_PARITY_CALL with CHOOSE_PARITY_RESPONSE **within 30 seconds**
- ✅ Invoke strategy module to make parity choice ("even" or "odd")
- ✅ Update personal statistics after each match
- ✅ Persist history to `data/players/<player_id>/history.json`
- ✅ Acknowledge all league messages within timeouts
- ✅ Handle technical losses gracefully
- ✅ Implement strategy algorithm (simple or complex)

**Source of Truth:**
- Personal match history
- Personal statistics (wins, losses, draws, points)

**Explicit Non-Responsibilities:**
- ❌ Manage matches or enforce rules
- ❌ Coordinate other players
- ❌ Determine match winners
- ❌ Draw random numbers
- ❌ Communicate directly with other players

---

### 3.2 Supporting Components

#### 3.2.1 MCP Client

**Purpose:** Protocol-compliant messaging infrastructure
**Location:** `SHARED/league_sdk/mcp_client.py`

**Responsibilities:**
- Format messages with JSON-RPC 2.0 envelope
- Add protocol fields (protocol, message_type, sender, timestamp)
- Send HTTP POST requests to `/mcp` endpoint
- Enforce timeouts
- Parse responses
- Generate conversation IDs

**Not Responsible For:**
- Business logic
- Agent state management
- Strategy decisions

#### 3.2.2 Data Repositories

**Purpose:** Data persistence layer

**Components:**
- `StandingsRepository` - manages `standings.json`
- `RoundsRepository` - manages `rounds.json`
- `MatchRepository` - manages match files
- `PlayerHistoryRepository` - manages player history

**Responsibilities:**
- CRUD operations on JSON files
- Schema validation
- Version management

---

## 4. Functional Requirements

Per `docs/assignment/chapter_08_game_flow.md`, the system must support the complete game lifecycle:

### 4.1 Registration Phase

**FR-REG-001: Referee Registration**

- **Actor:** Referee
- **Trigger:** Referee startup
- **Preconditions:** League Manager is running
- **Flow:**
  1. Referee sends `REFEREE_REGISTER_REQUEST` to League Manager
  2. League Manager validates request (display_name unique, supported game_types)
  3. League Manager assigns referee_id (e.g., "REF01")
  4. League Manager generates auth_token
  5. League Manager responds with `REFEREE_REGISTER_RESPONSE` (status: ACCEPTED)
  6. Referee stores referee_id and auth_token
- **Success:** Referee registered and ready for match assignments
- **Failure:** Registration rejected (duplicate name, unsupported game type) → exit

**FR-REG-002: Player Registration**

- **Actor:** Player
- **Trigger:** Player startup
- **Preconditions:** League Manager is running
- **Flow:**
  1. Player sends `LEAGUE_REGISTER_REQUEST` to League Manager
  2. League Manager validates request (display_name unique, endpoint reachable)
  3. League Manager assigns player_id (sequential: P01, P02, P03, P04)
  4. League Manager generates auth_token
  5. League Manager responds with `LEAGUE_REGISTER_RESPONSE` (status: ACCEPTED)
  6. Player stores player_id and auth_token
- **Success:** Player registered
- **Failure:** Registration rejected (league full, duplicate name) → retry or exit
- **Timeout:** 10 seconds (retry up to 3 times)

**FR-REG-003: Minimum Registration Threshold**

- **Requirement:** League requires minimum 2 players to start
- **Validation:** League Manager checks count before schedule creation

---

### 4.2 Scheduling Phase

**FR-SCHED-001: Round-Robin Schedule Creation**

- **Actor:** League Manager
- **Trigger:** All required players registered
- **Preconditions:** At least 2 players registered, at least 1 referee registered
- **Algorithm:**
  - For N players: N(N-1)/2 total matches
  - Distribute matches across rounds such that each player plays once per round
  - Assign matches to available referees (load balancing)
- **Example (4 players):**
  - Round 1: R1M1 (P01 vs P02), R1M2 (P03 vs P04)
  - Round 2: R2M1 (P03 vs P01), R2M2 (P04 vs P02)
  - Round 3: R3M1 (P04 vs P01), R3M2 (P03 vs P02)
- **Output:** Schedule persisted to `rounds.json`
- **Success:** Schedule created, transition to league running state
- **Failure:** Insufficient players or referees → abort

**FR-SCHED-002: Round Announcement**

- **Actor:** League Manager
- **Trigger:** Round begins
- **Flow:**
  1. League Manager sends `ROUND_ANNOUNCEMENT` to all players
  2. Message includes: round_id, matches array (match_id, player_A_id, player_B_id, referee_endpoint)
  3. Players acknowledge with `ROUND_ANNOUNCEMENT_ACK` (10-second timeout)
  4. Referees begin sending invitations
- **Success:** All players notified
- **Failure:** Player unreachable → log warning, proceed anyway

---

### 4.3 Match Execution Phase

Per `docs/architecture/state_machines.md`, referees manage matches through the following states:
`IDLE → WAITING_FOR_PLAYERS → COLLECTING_CHOICES → DRAWING_NUMBER → NOTIFYING_PLAYERS → REPORTING_RESULT → MATCH_COMPLETE`

**FR-MATCH-001: Game Invitation**

- **Actor:** Referee
- **Trigger:** Match assigned from round announcement
- **Preconditions:** Referee is idle, match details loaded
- **Flow:**
  1. Referee transitions to WAITING_FOR_PLAYERS
  2. Referee sends `GAME_INVITATION` to Player A
     - Fields: match_id, league_id, round_id, game_type: "even_odd", role_in_match: "PLAYER_A", opponent_id
  3. Referee sends `GAME_INVITATION` to Player B
     - Fields: same, role_in_match: "PLAYER_B"
  4. Referee starts 5-second timer for each player
- **Success:** Both players receive invitations
- **Failure:** Player unreachable → retry up to 3 times → award technical loss

**FR-MATCH-002: Player Arrival Confirmation**

- **Actor:** Player
- **Trigger:** Receive `GAME_INVITATION`
- **Preconditions:** Player is registered and idle
- **Flow:**
  1. Player transitions to INVITED_TO_MATCH
  2. Player validates invitation (match_id, opponent_id)
  3. Player sends `GAME_JOIN_ACK` **within 5 seconds**
     - Fields: match_id, player_id, accept: true, arrival_timestamp
  4. Player transitions to WAITING_FOR_CHOICE_REQUEST
- **Success:** Referee receives ACK within 5 seconds
- **Failure:**
  - accept: false → immediate technical loss
  - Timeout (5s) → retry (max 3) → technical loss
- **Critical:** **5-second timeout** enforced by referee

**FR-MATCH-003: Both Players Joined**

- **Actor:** Referee
- **Trigger:** Both GAME_JOIN_ACK received
- **Preconditions:** Both players accepted within timeout
- **Flow:**
  1. Referee transitions to COLLECTING_CHOICES
  2. Referee queries current standings for both players (from League Manager or cache)
  3. Referee sends `CHOOSE_PARITY_CALL` to both players
     - Fields: match_id, player_id, game_type, context (opponent_id, standings), deadline (30s from now)
  4. Referee starts 30-second timer for each player
- **Success:** Both players receive choice requests
- **Failure:** Should not fail (best effort)

**FR-MATCH-004: Parity Choice Collection**

- **Actor:** Player
- **Trigger:** Receive `CHOOSE_PARITY_CALL`
- **Preconditions:** Player is waiting for choice request
- **Flow:**
  1. Player transitions to CHOOSING_PARITY
  2. Player invokes strategy module with context
  3. Strategy returns "even" or "odd" (must complete within 30 seconds)
  4. Player sends `CHOOSE_PARITY_RESPONSE` **within 30 seconds**
     - Fields: match_id, player_id, parity_choice ("even" or "odd")
  5. Player transitions to WAITING_FOR_RESULT
- **Success:** Referee receives response within 30 seconds
- **Failure:**
  - Invalid choice (not "even" or "odd") → error, retry
  - Timeout (30s) → retry (max 3) → technical loss
  - Strategy module crash → use fallback choice ("even")
- **Critical:** **30-second timeout** enforced by referee

**FR-MATCH-005: Winner Determination**

- **Actor:** Referee
- **Trigger:** Both parity choices received
- **Preconditions:** Both choices are valid
- **Algorithm:**
  1. Draw random number N from 1 to 10 (uniform distribution)
  2. Calculate parity: "even" if N % 2 == 0, else "odd"
  3. Compare:
     - Player A correct = (choice_A == parity)
     - Player B correct = (choice_B == parity)
  4. Determine winner:
     - Both correct OR both wrong → status: DRAW, winner: null
     - A correct, B wrong → status: WIN, winner: player_A_id
     - B correct, A wrong → status: WIN, winner: player_B_id
  5. Calculate scores:
     - Winner: 3 points, Loser: 0 points
     - Draw: 1 point each
     - Technical loss: 3 points to opponent, 0 to loser
  6. Transition to NOTIFYING_PLAYERS
- **Success:** game_result object created
- **Failure:** Random number generation fails → retry → fallback to DRAW

**FR-MATCH-006: End Notification**

- **Actor:** Referee
- **Trigger:** Winner determined or technical loss awarded
- **Flow:**
  1. Referee sends `GAME_OVER` to both players
     - Fields: match_id, game_type, game_result (status, winner_player_id, drawn_number, number_parity, choices, reason)
  2. Players acknowledge with `GAME_OVER_ACK` (10-second timeout, best effort)
  3. Players update statistics and persist to history.json
- **Success:** Both players notified (acknowledgment optional)
- **Failure:** Player unreachable → log error, proceed to reporting

**FR-MATCH-007: Result Reporting to League Manager**

- **Actor:** Referee
- **Trigger:** Players notified (or timeout)
- **Flow:**
  1. Referee sends `MATCH_RESULT_REPORT` to League Manager
     - Fields: match_id, winner, score (player_id → points), details (drawn_number, choices)
  2. League Manager responds with `MATCH_RESULT_ACK`
  3. Referee persists complete match data to `data/matches/<league_id>/<match_id>.json`
  4. Referee transitions to MATCH_COMPLETE → IDLE
- **Success:** Match result recorded in league
- **Failure:** League Manager unreachable → retry (max 3) → log critical error, proceed to MATCH_COMPLETE anyway
- **Timeout:** 10 seconds for acknowledgment

---

### 4.4 Round Completion Phase

**FR-ROUND-001: Standings Update**

- **Actor:** League Manager
- **Trigger:** All matches in round complete
- **Flow:**
  1. League Manager calculates standings:
     - Sum points for each player
     - Count wins, draws, losses
     - Sort by points (desc), then wins (desc), then alphabetically
     - Assign ranks (1, 2, 3, 4, ...)
  2. League Manager persists to `standings.json` (increment version)
  3. League Manager sends `LEAGUE_STANDINGS_UPDATE` to all players
  4. Players acknowledge (10-second timeout)
- **Success:** All players receive updated standings
- **Failure:** Player unreachable → log warning, proceed

**FR-ROUND-002: Round Completion Announcement**

- **Actor:** League Manager
- **Trigger:** Standings updated
- **Flow:**
  1. League Manager sends `ROUND_COMPLETED` to all players
     - Fields: round_id, matches_played, next_round_id (or null if done)
  2. Players acknowledge
  3. If next_round_id not null → announce next round (FR-SCHED-002)
  4. If next_round_id is null → proceed to league completion
- **Success:** Round marked as complete
- **Failure:** Player unreachable → proceed anyway

---

### 4.5 League Completion Phase

**FR-LEAGUE-001: League Completion**

- **Actor:** League Manager
- **Trigger:** All rounds complete
- **Flow:**
  1. League Manager loads final standings
  2. Determine champion (highest points, then highest wins, then alphabetical)
  3. League Manager sends `LEAGUE_COMPLETED` to all players
     - Fields: total_rounds, total_matches, champion (player_id, display_name, points), final_standings
  4. Players acknowledge
  5. Players transition to LEAGUE_COMPLETE state
  6. Agents prepare for graceful shutdown
- **Success:** League completed, champion declared
- **Failure:** Player unreachable → log warning, proceed to completion

---

### 4.6 Error Handling & Timeouts

**FR-ERROR-001: Timeout Enforcement**

Per `docs/architecture/state_machines.md`:

| State | Timeout | Action | Max Retries |
|-------|---------|--------|-------------|
| WAITING_FOR_PLAYERS | 5s per player | Retry GAME_INVITATION | 3 |
| COLLECTING_CHOICES | 30s per player | Retry CHOOSE_PARITY_CALL | 3 |
| NOTIFYING_PLAYERS | 10s total | Proceed anyway (best effort) | N/A |
| REPORTING_RESULT | 10s | Retry MATCH_RESULT_REPORT | 3 |

- **Critical Timeouts (enforced):** 5s, 30s
- **Non-Critical Timeouts (best effort):** 10s for acknowledgments

**FR-ERROR-002: Technical Loss Conditions**

Technical loss awarded when:
- Player fails to send GAME_JOIN_ACK within 5s after 3 retries
- Player fails to send CHOOSE_PARITY_RESPONSE within 30s after 3 retries
- Player sends accept: false in GAME_JOIN_ACK
- Player sends invalid parity_choice (not "even" or "odd") after retries

**FR-ERROR-003: Retry Logic**

- **Max Retries:** 3 for critical messages
- **Backoff Strategy:** Exponential backoff (optional)
- **Error Messages:** Referee sends `GAME_ERROR` to player before retry
  - error_code: "E001" (TIMEOUT_ERROR) or "E004" (INVALID_CHOICE)
  - Fields: retry_count, max_retries, action_required

**FR-ERROR-004: Invalid State Transitions**

Per `docs/architecture/state_machines.md`, illegal transitions should:
- Log warning
- Send error response to sender (if applicable)
- Remain in current state
- Do not crash

---

## 5. Non-Functional Requirements

### 5.1 Performance

**NFR-PERF-001: Response Time**

- GAME_JOIN_ACK: < 5 seconds (enforced)
- CHOOSE_PARITY_RESPONSE: < 30 seconds (enforced)
- All other acknowledgments: < 10 seconds (best effort)
- Number drawing + winner determination: < 1 second (internal)

**NFR-PERF-002: Throughput**

- League Manager: Handle 10,000 player registrations within 5 minutes
- Referee: Complete one match within 2 minutes (average)
- System: Complete 6-match round (4 players) within 5 minutes

**NFR-PERF-003: Scalability**

- Support 2-10,000 players per league
- Support 1-5,000 concurrent matches (across multiple referees)
- File system scalable to 100,000+ match records

### 5.2 Reliability

**NFR-REL-001: Availability**

- Agents operate continuously throughout league (no crashes)
- Uptime target: 99.9% for League Manager (1 crash allowed per 1000 matches)
- Graceful degradation: System continues even if some players disconnect

**NFR-REL-002: Fault Tolerance**

- Player crashes handled via technical loss
- Referee crashes result in match failure (reported to League Manager)
- League Manager crash requires restart (no automatic recovery)

**NFR-REL-003: Data Integrity**

- All match results persisted to disk before reporting
- Standings updates are atomic (version-controlled)
- No data loss on normal shutdown

### 5.3 Security

**NFR-SEC-001: Authentication**

- Token-based authentication for all inter-agent messages
- Auth tokens generated during registration
- Tokens validated before processing requests
- **Note:** Simple tokens (not cryptographically secure) - acceptable for educational project

**NFR-SEC-002: Input Validation**

- Validate all incoming JSON-RPC messages against schema
- Reject malformed messages with error response
- Sanitize file paths to prevent directory traversal

**NFR-SEC-003: Isolation**

- Each player agent runs in separate process
- Agents cannot access other agents' data directories (file permissions)
- No shared memory between agents

### 5.4 Maintainability

**NFR-MAINT-001: Code Quality**

- Modular architecture (clear separation of concerns)
- Well-defined interfaces (`docs/architecture/interfaces.md`)
- Comprehensive logging (all events logged)
- Code documentation (docstrings for all public methods)

**NFR-MAINT-002: Testability**

- Unit tests for all state transitions
- Integration tests for complete flows
- Mock-based testing for inter-agent communication
- Test coverage target: 70%+ (per submission guidelines)

**NFR-MAINT-003: Debuggability**

- Structured logging (JSONL format)
- Conversation IDs for message tracing
- State machine logging (all transitions logged)
- Match data includes complete transcript

### 5.5 Portability

**NFR-PORT-001: Platform Independence**

- Cross-platform: macOS, Linux, Windows
- Language-agnostic protocol (any language can implement)
- Standard HTTP/JSON (no proprietary protocols)

**NFR-PORT-002: Configuration**

- All configuration externalized to JSON files
- No hardcoded ports or endpoints
- Environment-specific settings in `config/system.json`

### 5.6 Usability (Engineering Focus)

**NFR-USE-001: Error Messages**

- Clear error messages with error codes
- Human-readable reason fields
- Actionable guidance in error responses

**NFR-USE-002: Logging**

- Consistent log format across all agents
- Log levels: INFO, WARNING, ERROR
- Timestamps in UTC (ISO 8601)
- Structured logging (JSONL) for machine parsing

**NFR-USE-003: Documentation**

- README with installation and running instructions
- Architecture documentation (`docs/architecture/`)
- Protocol specification (`docs/assignment/`)
- Inline code comments for complex logic

---

## 6. Constraints

### 6.1 Technical Constraints

**C-TECH-001: Protocol Version**

- **Constraint:** Must use `league.v2` protocol exactly as specified
- **Rationale:** Interoperability with other students' agents
- **Impact:** Cannot deviate from message contracts
- **Reference:** `docs/assignment/chapter_06_requirements.md` - "Use exactly the protocol defined in this document"

**C-TECH-002: Communication Protocol**

- **Constraint:** JSON-RPC 2.0 over HTTP POST to `/mcp` endpoint
- **Rationale:** Standard protocol for MCP communication
- **Impact:** Must implement HTTP server, cannot use websockets or other protocols
- **Reference:** `docs/architecture/mcp_message_contracts.md`

**C-TECH-003: Message Timeouts**

- **Constraint:**
  - GAME_JOIN_ACK: 5 seconds (hard limit)
  - CHOOSE_PARITY_RESPONSE: 30 seconds (hard limit)
  - Other responses: 10 seconds (soft limit)
- **Rationale:** Ensure league progresses in reasonable time
- **Impact:** Strategy module must complete within 30 seconds
- **Reference:** `docs/assignment/chapter_06_requirements.md` Section 3.2

**C-TECH-004: Data Persistence Format**

- **Constraint:** All data files must be JSON or JSONL
- **Rationale:** Human-readable, standard format, specified in protocol
- **Impact:** Cannot use binary formats or databases
- **Reference:** `docs/assignment/chapter_09_protocol.md`

**C-TECH-005: Localhost Deployment**

- **Constraint:** All agents run on localhost during development/testing
- **Rationale:** Educational environment, no network infrastructure
- **Impact:** Cannot test across multiple machines initially
- **Reference:** `docs/assignment/chapter_06_requirements.md` - "listening on localhost"

### 6.2 Scope Constraints

**C-SCOPE-001: Single Game Type**

- **Constraint:** System implements only "even_odd" game type
- **Rationale:** Simplicity for educational assignment
- **Impact:** Game rules module is not pluggable (yet)
- **Note:** System designed for extensibility to multiple game types in future

**C-SCOPE-002: Round-Robin Only**

- **Constraint:** League uses Round-Robin tournament format exclusively
- **Rationale:** Fair, deterministic, simple to implement
- **Impact:** Cannot implement knockout, Swiss, or other formats
- **Note:** Scheduler could be extended for other formats

**C-SCOPE-003: No Real-Time UI**

- **Constraint:** No graphical user interface or real-time dashboard
- **Rationale:** Focus on backend architecture and protocol implementation
- **Impact:** Users interact via logs and JSON files
- **Note:** CLI tools or web UI could be added later

### 6.3 Quality Constraints

**C-QUAL-001: No Crashes**

- **Constraint:** Agents must operate without crashes throughout league
- **Rationale:** Critical requirement for submission
- **Impact:** Extensive error handling required
- **Reference:** `docs/assignment/chapter_06_requirements.md` Section 3.3

**C-QUAL-002: Test Coverage**

- **Constraint:** Minimum 70% test coverage
- **Rationale:** Per software submission guidelines (assumed from educational context)
- **Impact:** Significant testing effort required
- **Measurement:** Using pytest + coverage.py

**C-QUAL-003: Documentation**

- **Constraint:** Comprehensive documentation required
  - README with running instructions
  - Architecture description
  - Strategy explanation
  - Challenges and solutions
  - Development process
  - Conclusions and recommendations
- **Rationale:** Per submission requirements
- **Reference:** `docs/assignment/chapter_06_requirements.md` Section 5.1

### 6.4 Timeline Constraints

**C-TIME-001: Submission Deadline**

- **Constraint:** Final submission is absolute deadline
- **Rationale:** No updates allowed after submission
- **Impact:** Thorough testing required before submission
- **Reference:** `docs/assignment/chapter_06_requirements.md` Section 8 FAQ

---

## 7. Engineering Success Metrics

### 7.1 Functional Correctness Metrics

**M-FUNC-001: Protocol Compliance**

- **Metric:** 100% of messages conform to JSON-RPC 2.0 and `league.v2` schema
- **Measurement:** Schema validation on all sent/received messages
- **Target:** 0 schema validation errors in full league test
- **Verification:** Automated schema validation during testing

**M-FUNC-002: Match Completion Rate**

- **Metric:** Percentage of matches that complete successfully (no crashes)
- **Target:** 100% in local testing with 4 players
- **Measurement:** (Completed matches / Total scheduled matches) × 100
- **Failure Modes:** Player crash, referee crash, network timeout

**M-FUNC-003: League Completion**

- **Metric:** Binary - league runs to completion with champion declared
- **Target:** Success in 100% of test runs
- **Measurement:** Automated test script verifies LEAGUE_COMPLETED message sent
- **Verification:** `test_full_league.py` passes

**M-FUNC-004: Standings Accuracy**

- **Metric:** Standings calculations match expected results
- **Target:** 100% accuracy
- **Measurement:** Compare calculated standings vs. manual verification
- **Verification:** Unit tests for standings calculation logic

### 7.2 Performance Metrics

**M-PERF-001: Response Time Compliance**

- **Metric:** Percentage of messages sent within timeout
  - GAME_JOIN_ACK: < 5s
  - CHOOSE_PARITY_RESPONSE: < 30s
  - Other ACKs: < 10s
- **Target:** 100% compliance
- **Measurement:** Timestamp analysis in logs
- **Verification:** Log analysis script

**M-PERF-002: League Duration**

- **Metric:** Total time to complete 6-match league (4 players, Round-Robin)
- **Target:** < 5 minutes
- **Measurement:** Time from first ROUND_ANNOUNCEMENT to LEAGUE_COMPLETED
- **Baseline:** Average of 10 test runs

**M-PERF-003: Strategy Decision Time**

- **Metric:** Time for player strategy to return parity choice
- **Target:** < 1 second (well under 30s limit)
- **Measurement:** Instrumentation in strategy module
- **Verification:** Log analysis

### 7.3 Reliability Metrics

**M-REL-001: Uptime**

- **Metric:** Agent uptime during league (no crashes)
- **Target:** 100% (0 crashes per league)
- **Measurement:** Monitor for process exits or exceptions
- **Verification:** Automated test runs

**M-REL-002: Error Handling Coverage**

- **Metric:** Percentage of error conditions handled gracefully
- **Target:** 100% of documented error conditions
- **Measurement:** Test all error scenarios from state machine specs
- **Verification:** Integration tests for each error condition

**M-REL-003: Retry Success Rate**

- **Metric:** Percentage of retries that succeed before max retries
- **Target:** > 90% (most transient failures resolve within 3 retries)
- **Measurement:** Count retry attempts vs. technical losses
- **Baseline:** Established during testing

### 7.4 Code Quality Metrics

**M-QUAL-001: Test Coverage**

- **Metric:** Line coverage and branch coverage
- **Target:**
  - Line coverage: > 70%
  - Branch coverage: > 60%
- **Measurement:** coverage.py
- **Verification:** CI integration (if available)

**M-QUAL-002: Code Complexity**

- **Metric:** Cyclomatic complexity per function
- **Target:** < 10 per function (industry standard)
- **Measurement:** Static analysis tools (pylint, radon)
- **Verification:** Pre-commit hooks

**M-QUAL-003: Interface Compliance**

- **Metric:** All public methods match interface specifications
- **Target:** 100% compliance
- **Measurement:** Manual review against `docs/architecture/interfaces.md`
- **Verification:** Code review checklist

**M-QUAL-004: State Machine Conformance**

- **Metric:** All state transitions match state machine specs
- **Target:** 100% conformance
- **Measurement:** Compare implementation vs. `docs/architecture/state_machines.md`
- **Verification:** State transition unit tests

### 7.5 Documentation Metrics

**M-DOC-001: Documentation Completeness**

- **Metric:** Presence of required documentation sections
- **Target:** 100% of required sections present
- **Checklist:**
  - ✅ README.md with installation instructions
  - ✅ README.md with running instructions (6 terminals)
  - ✅ Architecture description
  - ✅ Strategy explanation
  - ✅ Challenges and solutions
  - ✅ Development process
  - ✅ Conclusions and recommendations
- **Verification:** Manual review against submission requirements

**M-DOC-002: Code Documentation**

- **Metric:** Percentage of public methods with docstrings
- **Target:** 100%
- **Measurement:** Static analysis (pydocstyle)
- **Verification:** Pre-commit hooks

### 7.6 Acceptance Metrics

**M-ACC-001: Interoperability**

- **Metric:** Agent successfully plays with other students' agents
- **Target:** Success in 100% of cross-student tests
- **Measurement:** Exchange agents with peer, run test league
- **Verification:** Before submission

**M-ACC-002: Self-Test Pass Rate**

- **Metric:** Percentage of test runs that pass completely
- **Target:** 100% (10 consecutive successful runs)
- **Measurement:** Automated test script (`test_full_league.py`)
- **Verification:** Pre-submission validation

**M-ACC-003: Submission Compliance**

- **Metric:** Checklist of submission requirements
- **Target:** 100% compliance
- **Checklist:**
  - ✅ Agent source code included
  - ✅ README with instructions
  - ✅ Detailed report (all sections)
  - ✅ All required files present
  - ✅ Repository link valid
- **Verification:** Pre-submission audit

---

## 8. Out of Scope

The following items are explicitly **not** part of this project:

### 8.1 Infrastructure & Deployment

**OUT-001: Production Deployment**

- No cloud deployment (AWS, Azure, GCP)
- No containerization (Docker, Kubernetes)
- No CI/CD pipelines (automated deployment)
- **Rationale:** Educational project, localhost only

**OUT-002: Database Systems**

- No SQL databases (PostgreSQL, MySQL)
- No NoSQL databases (MongoDB, Redis)
- No in-memory databases
- **Rationale:** File-based persistence sufficient for scale target

**OUT-003: Message Queues**

- No message brokers (RabbitMQ, Kafka)
- No pub/sub systems
- No async message queuing
- **Rationale:** Direct HTTP communication specified by protocol

### 8.2 User Interface

**OUT-004: Graphical User Interface**

- No web UI (React, Vue, Angular)
- No desktop UI (Electron, Qt)
- No mobile apps
- **Rationale:** Backend focus, logs/JSON sufficient for debugging

**OUT-005: Real-Time Dashboards**

- No live leaderboards
- No real-time match visualization
- No analytics dashboards
- **Rationale:** Static JSON files sufficient for analysis

**OUT-006: User Management**

- No user accounts or profiles
- No password management
- No role-based access control (RBAC)
- **Rationale:** Educational environment, simple agent IDs sufficient

### 8.3 Advanced Features

**OUT-007: Multiple Game Types**

- No additional games beyond even/odd
- No rock-paper-scissors
- No chess, tic-tac-toe, or other games
- **Rationale:** Single game type per requirements
- **Note:** Architecture designed for future extension

**OUT-008: Tournament Formats**

- No knockout brackets
- No Swiss system
- No ELO ratings
- No seeding or rankings
- **Rationale:** Round-Robin only per requirements

**OUT-009: Machine Learning Strategies**

- No trained ML models required
- No neural networks
- No reinforcement learning
- **Rationale:** Strategy complexity not graded
- **Note:** Students may optionally implement ML strategies

**OUT-010: Advanced Analytics**

- No predictive analytics
- No opponent modeling (beyond basic history)
- No strategy optimization algorithms
- **Rationale:** Focus on architecture, not AI/ML

### 8.4 Quality & Operations

**OUT-011: Advanced Monitoring**

- No Prometheus/Grafana
- No distributed tracing (Jaeger, Zipkin)
- No APM tools
- **Rationale:** JSON logs sufficient for debugging

**OUT-012: Load Balancing**

- No load balancers (nginx, HAProxy)
- No automatic scaling
- No failover mechanisms
- **Rationale:** Single-instance deployment

**OUT-013: Security Hardening**

- No OAuth/JWT authentication
- No TLS/SSL encryption
- No rate limiting
- No DDoS protection
- **Rationale:** Localhost deployment, educational environment
- **Note:** Simple token auth is sufficient

### 8.5 Data Management

**OUT-014: Data Backup & Recovery**

- No automated backups
- No point-in-time recovery
- No disaster recovery plan
- **Rationale:** Educational project, data not critical

**OUT-015: Data Analytics**

- No data warehouse
- No ETL pipelines
- No BI tools
- **Rationale:** Simple JSON queries sufficient

**OUT-016: Data Migration**

- No schema migration tools
- No data versioning (beyond schema_version field)
- No backward compatibility for old data formats
- **Rationale:** Single version deployment

### 8.6 Integration

**OUT-017: External Integrations**

- No third-party APIs
- No webhooks
- No email notifications
- No Slack/Discord bots
- **Rationale:** Self-contained system

**OUT-018: Import/Export**

- No CSV export
- No Excel export
- No data import from external sources
- **Rationale:** JSON files are source of truth

### 8.7 Compliance & Governance

**OUT-019: Regulatory Compliance**

- No GDPR compliance
- No HIPAA compliance
- No audit trails (beyond basic logs)
- **Rationale:** Not applicable to educational project

**OUT-020: Legal Documentation**

- No terms of service
- No privacy policy
- No commercial licensing
- **Rationale:** Educational project, not commercial software

---

## 9. References

### 9.1 Assignment Documentation

- **`docs/assignment/chapter_06_requirements.md`**
  Home assignment requirements, mandatory tasks, technical requirements, work process, submission requirements, evaluation criteria

- **`docs/assignment/chapter_08_game_flow.md`**
  Complete system flow, actors, message sequence for each stage, error handling, query tools, edge cases, scoring system

- **`docs/assignment/chapter_09_protocol.md`**
  League data protocol (JSON files), three-layer architecture (config/data/logs), file structures, protocol conventions

### 9.2 Architecture Documentation

- **`docs/architecture/interfaces.md`**
  Formal interface contracts for LeagueManagerInterface, RefereeInterface, PlayerInterface, MCPClientInterface with complete method signatures, responsibilities, error handling

- **`docs/architecture/state_machines.md`**
  State machine specifications for Referee (7 states) and Player (10 states), complete transition tables, timeout semantics, illegal transitions, implementation notes

- **`docs/architecture/mcp_message_contracts.md`**
  Complete MCP message specifications (assumed to exist, referenced in state machines)

### 9.3 Implementation Reference

- **`README.md`**
  System overview, installation instructions, quick start guide, testing procedures

- **`test_full_league.py`**
  Full league test orchestration demonstrating complete system operation

---

## Document Approval

**Author:** Engineering Team
**Review Status:** Draft
**Version:** 1.0
**Last Updated:** 2025-01-20

**Change Log:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-20 | Engineering Team | Initial PRD creation from existing documentation |

---

**END OF DOCUMENT**
