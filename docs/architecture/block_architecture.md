# High-Level Block Architecture

**Even/Odd League System - MCP-Based Multi-Agent Architecture**

**Document Version:** 1.0
**Last Updated:** 2025-01-19

---

## 1. System Overview

### 1.1 Architectural Philosophy

The Even/Odd League System is a distributed multi-agent system based on the Model Context Protocol (MCP). The architecture follows these principles:

- **Orchestrated Autonomy:** Agents are autonomous but coordinated by orchestrators
- **Separation of Concerns:** Clear boundaries between league management, match management, and gameplay
- **Protocol-First:** All communication follows the league.v2 protocol specification
- **Data-Centric:** Persistent state management through structured JSON files
- **Scalability:** Design supports thousands of agents and concurrent leagues

### 1.2 System Topology

```
┌─────────────────────────────────────────────────────────────┐
│                     League Manager                          │
│                   (Top Orchestrator)                        │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
      ┌──────┴──────┐            ┌───────┴────────┐
      │   Referee   │            │    Referee     │
      │ (Match Orch)│            │  (Match Orch)  │
      └──────┬──────┘            └────────┬───────┘
             │                            │
      ┌──────┴──────┐            ┌───────┴────────┐
      │   Player    │            │     Player     │
      │   Agent     │            │     Agent      │
      └─────────────┘            └────────────────┘
```

### 1.3 Core Architectural Blocks

1. **League Manager Block** - Top-level orchestrator
2. **Referee Block** - Match-level orchestrator
3. **Player Agent Block** - Game participant
4. **MCP Communication Layer** - Protocol messaging infrastructure
5. **Data Persistence Layer** - File-based state management

---

## 2. Block Specifications

### 2.1 League Manager Block

#### Purpose

Serves as the top-level orchestrator for the entire league system. Manages league lifecycle from registration through completion, maintains the source of truth for standings and schedules, and coordinates all referees and players.

#### Inputs

**Registration Requests:**
- Referee registration requests (REFEREE_REGISTER_REQUEST)
- Player registration requests (LEAGUE_REGISTER_REQUEST)

**Match Results:**
- Match result reports from referees (MATCH_RESULT_REPORT)

**Queries:**
- Standings queries from players (LEAGUE_QUERY)
- Status queries from external systems

**Configuration:**
- System configuration file (system.json)
- League configuration file (league_<id>.json)
- Agent registry (agents_config.json)

#### Outputs

**Registration Responses:**
- Referee registration confirmations (REFEREE_REGISTER_RESPONSE)
- Player registration confirmations (LEAGUE_REGISTER_RESPONSE)

**Round Coordination:**
- Round announcements to all players (ROUND_ANNOUNCEMENT)
- Round completion notifications (ROUND_COMPLETED)

**Standings Updates:**
- Standings updates to all players (LEAGUE_STANDINGS_UPDATE)

**League Events:**
- League completion announcements (LEAGUE_COMPLETED)

**Error Notifications:**
- League-level errors (LEAGUE_ERROR)

**Persistent State:**
- Updated standings table (standings.json)
- Round history (rounds.json)
- League logs (league.log.jsonl)

#### Configuration

**System Settings:**
- Network configuration (ports, endpoints)
- Timeout values (generic response timeout)
- Retry policies (max retries, backoff strategy)

**League Settings:**
- Scoring rules (win/draw/loss points)
- Participant limits (min/max players)
- Game type specification
- League status (ACTIVE, COMPLETED, etc.)

**Agent Registry:**
- List of registered referees with endpoints
- List of registered players with endpoints
- Mapping of IDs to contact endpoints

#### Responsibilities

**Registration Management:**
- Accept and validate referee registrations
- Accept and validate player registrations
- Assign unique IDs to referees and players
- Generate and manage authentication tokens
- Maintain agent registry

**Schedule Management:**
- Create Round-Robin match schedule for all players
- Assign matches to available referees
- Determine round structure and sequencing
- Manage round lifecycle (announcement, execution, completion)

**Standings Management:**
- Maintain current standings table as source of truth
- Calculate points based on match results
- Update wins, losses, draws counts
- Calculate rankings
- Broadcast standings updates to all participants

**League Coordination:**
- Determine when league can start (all registrations complete)
- Announce rounds to players
- Track round completion across all matches
- Determine league completion
- Declare champion and final standings

**State Persistence:**
- Write and update standings table
- Maintain round history
- Log all league-level events
- Ensure data consistency

**Query Handling:**
- Respond to standings queries
- Provide league status information
- Validate authentication tokens

#### Explicit Non-Responsibilities

**Does NOT:**
- Manage individual match gameplay or state
- Enforce game rules or determine match winners
- Send invitations to players for specific matches
- Collect player choices or decisions
- Implement timeout enforcement at match level
- Handle match-specific errors
- Store individual match transcripts
- Know or care about specific game rules (even/odd logic)
- Manage player strategies
- Directly communicate with players during matches

---

### 2.2 Referee Block

#### Purpose

Serves as the match-level orchestrator. Manages the complete lifecycle of a single match from invitation through result reporting. Acts as the source of truth for match state and enforces game rules and timeouts.

#### Inputs

**Match Assignments:**
- Match assignments from round announcement (implicitly through schedule)
- Referee endpoint specified in ROUND_ANNOUNCEMENT

**Player Responses:**
- Arrival confirmations (GAME_JOIN_ACK)
- Parity choices (CHOOSE_PARITY_RESPONSE)

**Configuration:**
- Game rules configuration (games_registry.json)
- Timeout values from system configuration
- Match details from round announcement

#### Outputs

**Player Communications:**
- Game invitations to both players (GAME_INVITATION)
- Choice requests to both players (CHOOSE_PARITY_CALL)
- Game over notifications to both players (GAME_OVER)
- Game errors to affected players (GAME_ERROR)

**League Reporting:**
- Match result report to League Manager (MATCH_RESULT_REPORT)

**Persistent State:**
- Complete match data file (match_<id>.json)
- Match lifecycle state
- Complete message transcript
- Final match result

**Logs:**
- Match-specific log entries

#### Configuration

**Game Rules:**
- Game type (even_odd)
- Rules module to load
- Maximum round time
- Number range (1-10)

**Timeout Values:**
- GAME_JOIN_ACK timeout (5 seconds)
- CHOOSE_PARITY_RESPONSE timeout (30 seconds)
- Retry limits (max_retries: 3)

**Match Context:**
- Match ID
- League ID
- Round ID
- Player A ID and endpoint
- Player B ID and endpoint
- Game type

#### Responsibilities

**Match Initialization:**
- Read match assignment from round announcement
- Initialize match state (WAITING_FOR_PLAYERS)
- Load appropriate game rules module
- Set up match data structures

**Player Invitation:**
- Send GAME_INVITATION to Player A with role PLAYER_A
- Send GAME_INVITATION to Player B with role PLAYER_B
- Include match context (match_id, opponent_id, round_id)
- Transition to WAITING_FOR_PLAYERS state

**Arrival Management:**
- Wait for GAME_JOIN_ACK from both players
- Enforce 5-second timeout per player
- Handle timeouts with retries
- Award technical loss if player fails to respond
- Transition to COLLECTING_CHOICES when both players arrive

**Choice Collection:**
- Send CHOOSE_PARITY_CALL to both players
- Provide context (opponent_id, standings, deadline)
- Enforce 30-second timeout per player
- Handle timeouts with retry logic
- Collect choices from both players
- Transition to DRAWING_NUMBER when both choices received

**Game Execution:**
- Draw random number (1-10)
- Apply game rules module (even/odd logic)
- Determine number parity
- Compare choices to number parity
- Determine winner (or draw if applicable)
- Calculate scores (3 points for win)
- Transition to FINISHED state

**Result Notification:**
- Send GAME_OVER to both players
- Include complete game result (winner, drawn_number, choices)
- Provide reason/explanation

**Result Reporting:**
- Send MATCH_RESULT_REPORT to League Manager
- Include match_id, winner, scores, details
- Include choices and drawn number

**State Management:**
- Maintain match state machine (WAITING → COLLECTING → DRAWING → FINISHED)
- Track message timestamps
- Record complete message transcript
- Ensure state consistency

**Error Handling:**
- Detect timeouts and missing responses
- Send GAME_ERROR notifications
- Implement retry logic with exponential backoff
- Award technical losses when appropriate

**Data Persistence:**
- Write complete match data file
- Include lifecycle state transitions
- Store full message transcript
- Record final result

#### Explicit Non-Responsibilities

**Does NOT:**
- Manage league-wide state or standings
- Coordinate multiple matches simultaneously (each referee manages one match)
- Register players or referees
- Create match schedules
- Calculate league standings or rankings
- Know about other matches in the round
- Manage round lifecycle
- Send round announcements
- Communicate with League Manager except for result reporting
- Store player history or statistics beyond single match
- Implement player strategies
- Make strategic decisions

---

### 2.3 Player Agent Block

#### Purpose

Represents an autonomous game participant. Responds to game invitations, makes strategic decisions (even/odd choices), maintains personal history, and implements strategy for maximizing wins.

#### Inputs

**League Communications:**
- Registration confirmation (LEAGUE_REGISTER_RESPONSE)
- Round announcements (ROUND_ANNOUNCEMENT)
- Standings updates (LEAGUE_STANDINGS_UPDATE)
- Round completed notifications (ROUND_COMPLETED)
- League completed notifications (LEAGUE_COMPLETED)

**Match Communications:**
- Game invitations from referee (GAME_INVITATION)
- Choice requests from referee (CHOOSE_PARITY_CALL)
- Game over notifications from referee (GAME_OVER)
- Game errors from referee (GAME_ERROR)

**Configuration:**
- Player default settings (player.json)
- Strategy configuration (if applicable)

**Historical Data:**
- Personal match history (history.json)
- Past performance statistics

#### Outputs

**Registration:**
- Player registration request (LEAGUE_REGISTER_REQUEST)
- Player metadata (display_name, version, game_types, endpoint)

**Match Responses:**
- Arrival confirmations (GAME_JOIN_ACK)
- Parity choices (CHOOSE_PARITY_RESPONSE)
- Generic acknowledgments

**Queries:**
- Standings queries (LEAGUE_QUERY) - optional

**Persistent State:**
- Updated personal history (history.json)
- Updated statistics (wins, losses, draws)

**Logs:**
- Agent-specific logs (agent_<id>.log.jsonl)

#### Configuration

**Identity:**
- Display name
- Agent version
- Supported game types

**Network:**
- Server port (8101-8104 range)
- HTTP endpoint (/mcp)

**Strategy Settings:**
- Strategy algorithm selection (random, pattern-based, ML-based, etc.)
- Strategy parameters
- Learning settings (if applicable)

**Defaults:**
- Response timeout values
- Retry behavior

#### Responsibilities

**Registration:**
- Send registration request to League Manager on startup
- Provide required metadata (name, version, endpoint, game types)
- Store received player_id and auth_token

**Match Participation:**
- Listen for game invitations on assigned endpoint
- Respond to GAME_INVITATION with GAME_JOIN_ACK within 5 seconds
- Validate match context (match_id, league_id, opponent_id)

**Decision Making:**
- Receive CHOOSE_PARITY_CALL from referee
- Analyze game context (opponent, standings, history)
- Apply strategy algorithm
- Select "even" or "odd" choice
- Send CHOOSE_PARITY_RESPONSE within 30 seconds

**Strategy Implementation:**
- Maintain strategy state
- Use historical data to inform decisions
- Implement chosen strategy algorithm (random, adaptive, ML, etc.)
- Update strategy based on outcomes (if learning-enabled)

**History Management:**
- Record every match played
- Store match results (win/loss/draw)
- Store own choices and opponent choices
- Update statistics (total matches, wins, losses, draws)
- Persist history to personal history file

**State Tracking:**
- Track current league status
- Track current standings
- Maintain awareness of round progression
- Know current win/loss record

**Logging:**
- Log all received messages
- Log all sent messages
- Log decision-making process (for debugging)
- Enable end-to-end tracing

#### Explicit Non-Responsibilities

**Does NOT:**
- Manage matches or enforce rules
- Coordinate other players
- Maintain league-wide state or standings (only tracks, doesn't manage)
- Assign matches or create schedules
- Validate other players' choices
- Determine match winners
- Draw random numbers
- Send messages to other players directly
- Broadcast to multiple recipients
- Manage timeouts for other players
- Register other agents
- Modify league configuration
- Access other players' histories or strategies

---

### 2.4 MCP Communication Layer

#### Purpose

Provides protocol-compliant messaging infrastructure for all agent communications. Handles JSON-RPC 2.0 message formatting, HTTP transport, endpoint management, and timeout enforcement. Abstracts communication complexity from business logic.

#### Inputs

**High-Level Commands:**
- Send registration request
- Send game invitation
- Send choice response
- Query standings
- Report match result
- etc.

**Message Parameters:**
- Protocol version
- Message type
- Sender identification
- Payload data
- Target endpoint
- Timeout value

**Configuration:**
- Endpoint mappings (agent_id → URL)
- Default timeout values
- Retry policies
- Protocol version

#### Outputs

**JSON-RPC Messages:**
- Properly formatted JSON-RPC 2.0 requests
- Properly formatted JSON-RPC 2.0 responses
- Error responses in JSON-RPC format

**HTTP Requests:**
- POST requests to /mcp endpoints
- Proper headers (Content-Type: application/json)
- Request bodies containing JSON-RPC messages

**Status Indicators:**
- Success/failure status
- Timeout notifications
- Network error notifications

**Parsed Responses:**
- Extracted result objects
- Extracted error objects
- Response validation status

#### Configuration

**Protocol Settings:**
- Protocol version: "league.v2"
- JSON-RPC version: "2.0"

**Network Settings:**
- HTTP method: POST
- Endpoint path: /mcp
- Host: localhost
- Port range: 8000-8104

**Timeout Settings:**
- Connection timeout
- Read timeout
- Request-specific timeouts (5s, 30s, 10s)

**Retry Settings:**
- Maximum retries
- Backoff strategy
- Retry-eligible status codes

**Message Settings:**
- Timestamp format (UTC/ISO-8601)
- Conversation ID generation
- Request ID generation

#### Responsibilities

**Message Construction:**
- Build JSON-RPC 2.0 request envelope
- Add required protocol fields (protocol, message_type, sender, timestamp)
- Generate unique conversation_id
- Generate unique request id
- Validate message structure before sending

**Message Sending:**
- Establish HTTP connection to target endpoint
- Send POST request with JSON body
- Include proper HTTP headers
- Enforce request-specific timeout
- Handle network errors gracefully

**Response Handling:**
- Receive HTTP response
- Parse JSON-RPC response
- Validate response structure
- Extract result or error object
- Return parsed data to caller

**Timeout Enforcement:**
- Apply appropriate timeout based on message type
- Cancel requests that exceed timeout
- Return timeout error to caller
- Log timeout events

**Error Translation:**
- Convert HTTP errors to application errors
- Convert JSON parsing errors
- Convert timeout errors
- Provide meaningful error messages

**Endpoint Management:**
- Maintain endpoint registry (id → URL mapping)
- Look up endpoint by agent ID
- Validate endpoint URLs
- Handle endpoint discovery

**Logging and Tracing:**
- Log all outgoing requests
- Log all incoming responses
- Include timestamps
- Support end-to-end tracing with conversation_id

#### Explicit Non-Responsibilities

**Does NOT:**
- Implement business logic or game rules
- Maintain agent state or match state
- Make strategic decisions
- Validate business rules (only validates protocol structure)
- Persist data to files
- Manage registration or standings
- Determine message recipients (caller specifies)
- Create schedules or assign matches
- Retry based on business logic (only network-level retries)
- Authenticate users (passes through auth tokens)
- Modify message payloads (passes through what caller provides)
- Know about game semantics (even/odd, wins/losses)

---

### 2.5 Data Persistence Layer

#### Purpose

Manages all file-based data storage and retrieval. Provides consistent access to configuration files, runtime data files, and logs across the three-layer architecture (config, data, logs). Ensures data integrity and handles concurrent access.

#### Inputs

**Write Requests:**
- Configuration updates
- Standings table updates
- Round history updates
- Match data writes
- Player history updates
- Log entries

**Read Requests:**
- Configuration file reads
- Standings queries
- Match data retrieval
- Player history retrieval
- Log queries

**File Metadata:**
- File path
- Schema version
- Data version (for versioned files)

**Configuration:**
- Base directory paths (config/, data/, logs/)
- File naming conventions
- Schema versions

#### Outputs

**File Operations:**
- Written files (JSON, JSONL)
- Read file contents
- File existence checks
- Directory creation

**Data Objects:**
- Parsed JSON objects
- Validated data structures
- Version information

**Status:**
- Success/failure status
- File not found errors
- Parse errors
- Version mismatch warnings

#### Configuration

**Directory Structure:**
- SHARED/config/ - Configuration files
- SHARED/data/ - Runtime data files
- SHARED/logs/ - Log files

**File Conventions:**
- JSON for structured data
- JSONL for logs (one JSON object per line)
- UTF-8 encoding
- Indented JSON (4 spaces) for readability

**Schema Management:**
- Current schema versions
- Schema validation rules
- Migration policies (future)

**Concurrency:**
- File locking strategy (if applicable)
- Atomic write operations
- Read consistency level

#### Responsibilities

**Configuration Management:**
- Read system.json
- Read agents_config.json
- Read league configuration files
- Read game registry
- Read default settings
- Cache frequently accessed config

**Data File Management:**
- Write and update standings.json
- Write and update rounds.json
- Write and update match data files
- Write and update player history files
- Maintain data file versions
- Ensure atomic updates

**Log Management:**
- Append to league log (JSONL format)
- Append to agent logs (JSONL format)
- Rotate logs if needed
- Provide log query capability

**File Organization:**
- Create directory structure as needed
- Organize files by league_id
- Organize files by player_id
- Maintain consistent naming conventions

**Data Validation:**
- Validate JSON structure on read
- Validate schema version compatibility
- Validate required fields present
- Return validation errors

**Version Management:**
- Track schema_version in files
- Track data version in versioned files (standings)
- Detect version mismatches
- Support version migration (future)

**Error Handling:**
- Handle file not found
- Handle parse errors
- Handle write failures
- Handle permission errors
- Provide meaningful error messages

#### Explicit Non-Responsibilities

**Does NOT:**
- Implement business logic or game rules
- Make decisions about what data to persist (caller decides)
- Validate business rules (only validates file structure)
- Send network messages
- Manage agent lifecycle
- Enforce timeouts
- Calculate standings or scores (only persists calculated results)
- Determine file contents (receives content from caller)
- Implement retry logic for business operations
- Manage authentication or authorization
- Know about protocol messages or MCP semantics
- Filter or transform data (passes through as provided)

---

## 3. Block Interactions

### 3.1 Registration Flow

```
Player Agent → MCP Layer → League Manager → Data Persistence → MCP Layer → Player Agent
```

1. Player Agent constructs registration request
2. MCP Layer formats and sends JSON-RPC message
3. League Manager validates and processes registration
4. Data Persistence updates agents_config.json
5. League Manager generates response
6. MCP Layer returns response to Player Agent

### 3.2 Match Execution Flow

```
League Manager → MCP Layer → Player Agents (round announcement)
Referee → MCP Layer → Player Agents (invitations)
Player Agents → MCP Layer → Referee (responses)
Referee → Data Persistence (match data)
Referee → MCP Layer → League Manager (result report)
League Manager → Data Persistence (standings update)
```

### 3.3 Data Access Patterns

**Read-Heavy:**
- Configuration files (read at startup, cached)
- Player history (read for strategy decisions)

**Write-Heavy:**
- Logs (constant appending)

**Read-Write:**
- Standings table (read for queries, written after matches)
- Match data (written during match, read for analytics)

### 3.4 Communication Patterns

**One-to-One:**
- Player registration → League Manager
- Player responses → Referee

**One-to-Many:**
- Round announcement → All Players
- Standings update → All Players

**Many-to-One:**
- Match results → League Manager

---

## 4. Cross-Cutting Concerns

### 4.1 Error Handling Strategy

**League Manager:**
- Returns LEAGUE_ERROR for registration failures
- Logs all errors to league log
- Continues operation despite individual agent failures

**Referee:**
- Returns GAME_ERROR for match-specific issues
- Implements retry logic for timeouts
- Awards technical loss as last resort
- Reports errors in match result

**Player Agent:**
- Logs errors to personal log
- Accepts technical losses gracefully
- Continues to next match

**MCP Layer:**
- Translates network errors to application errors
- Returns timeout errors after deadline
- Logs all communication failures

**Data Persistence:**
- Returns file operation errors
- Does not corrupt files on error
- Logs persistence failures

### 4.2 Timeout Management

**Enforcement Levels:**

1. **MCP Layer:** Enforces HTTP-level timeouts
2. **Referee:** Enforces game-level timeouts (5s, 30s)
3. **League Manager:** Enforces league-level timeouts (10s generic)

**Timeout Values:**
- GAME_JOIN_ACK: 5 seconds
- CHOOSE_PARITY_RESPONSE: 30 seconds
- Generic response: 10 seconds

**Timeout Handling:**
- Retry up to max_retries (3)
- Exponential backoff between retries
- Award technical loss after exhausting retries

### 4.3 State Consistency

**Source of Truth:**
- League Manager: Standings table, schedule
- Referee: Match state
- Data Persistence: Persisted files

**Consistency Model:**
- Eventually consistent for standings (updated after each match)
- Strongly consistent within match (referee is authority)
- Append-only logs (no consistency issues)

**Version Management:**
- Schema version in all files
- Data version in standings.json
- Detect version mismatches

### 4.4 Scalability Considerations

**Horizontal Scaling:**
- Multiple leagues can run independently
- Multiple referees can run concurrent matches
- Thousands of players supported

**Performance:**
- Configuration caching in memory
- Minimal file I/O (only on state changes)
- Asynchronous message sending (non-blocking)

**Resource Management:**
- One HTTP server per agent (lightweight)
- File-based storage (no database overhead)
- Stateless request handling (except match state in referee)

### 4.5 Logging and Observability

**Logging Levels:**
- League Manager: League-level events (league.log.jsonl)
- Referee: Match-level events (in match data file)
- Player Agent: Agent-level events (agent_<id>.log.jsonl)
- MCP Layer: Communication events (in respective agent logs)

**Tracing:**
- conversation_id links related messages
- timestamp enables chronological reconstruction
- End-to-end tracing from request to response

**Debugging:**
- Complete message transcripts in match data
- Player decision logs in agent logs
- Error context in error messages

---

## 5. Deployment Architecture

### 5.1 Process Model

**Single-Machine Deployment (Development/Testing):**
```
Terminal 1: League Manager (port 8000)
Terminal 2: Referee 1 (port 8001)
Terminal 3: Referee 2 (port 8002)
Terminal 4: Player 1 (port 8101)
Terminal 5: Player 2 (port 8102)
Terminal 6: Player 3 (port 8103)
Terminal 7: Player 4 (port 8104)
```

**Shared Resources:**
- SHARED/ directory accessible to all processes
- File-based coordination through data files

### 5.2 Startup Sequence

**Required Order:**
1. League Manager must start first
2. Referees start and register
3. Players start and register
4. League begins after all registrations complete

**Initialization:**
- Each agent reads configuration from SHARED/config/
- Each agent starts HTTP server on assigned port
- Each agent sends registration request
- Each agent waits for registration confirmation

### 5.3 Network Topology

**All communication via HTTP:**
- POST to http://localhost:<port>/mcp
- JSON-RPC 2.0 in request/response body
- Synchronous request-response pattern

**Port Allocation:**
- 8000: League Manager
- 8001-8002: Referees
- 8101-8104: Players

---

## 6. Architecture Decisions and Rationale

### 6.1 Why File-Based Persistence?

**Chosen:** JSON files in shared directory
**Alternative:** Database (SQL or NoSQL)

**Rationale:**
- Simplicity for educational project
- Human-readable for debugging
- Version control friendly
- No database setup required
- Sufficient for thousands of agents
- Easy backup and portability

### 6.2 Why Synchronous HTTP?

**Chosen:** Synchronous HTTP POST with JSON-RPC
**Alternative:** WebSockets, Message Queue, gRPC

**Rationale:**
- Request-response pattern matches game flow
- Timeouts naturally enforced
- Simple to implement in any language
- Standard HTTP infrastructure
- JSON-RPC provides clear semantics

### 6.3 Why Three-Layer Data Architecture?

**Chosen:** config/ data/ logs/
**Alternative:** Flat structure or database tables

**Rationale:**
- Clear separation of static vs dynamic data
- Configuration easy to modify without affecting runtime
- Logs separate for performance and clarity
- Maps to system lifecycle (setup, runtime, analysis)

### 6.4 Why Orchestrator Pattern?

**Chosen:** League Manager and Referee as orchestrators
**Alternative:** Peer-to-peer, centralized coordinator

**Rationale:**
- League Manager provides global coordination
- Referee provides local (match) coordination
- Clear responsibility boundaries
- Scalable (multiple matches in parallel)
- Matches real-world sports organization

### 6.5 Why File-Per-Match?

**Chosen:** Separate JSON file per match
**Alternative:** All matches in one file, or database rows

**Rationale:**
- Parallel writes (different referees)
- Easy to archive completed matches
- Clear ownership (one referee per match)
- Debugging isolation (can examine single match)
- No lock contention

---

## 7. Future Extension Points

### 7.1 Additional Game Types

**Current:** Even/Odd only
**Extension:** Rock-Paper-Scissors, Poker, etc.

**Architecture Support:**
- Game rules in pluggable modules (games_registry.json)
- Referee loads appropriate rules module
- Player agents specify supported game_types
- League configuration specifies game_type

### 7.2 Advanced Strategies

**Current:** Simple strategy (random or basic pattern)
**Extension:** Machine learning, opponent modeling

**Architecture Support:**
- Player history provides training data
- Strategy configuration in player defaults
- Player block has full autonomy over decisions
- No changes needed in other blocks

### 7.3 Multiple Leagues

**Current:** Single league
**Extension:** Parallel leagues, tournament brackets

**Architecture Support:**
- League configuration per league_id
- Separate data files per league
- Players can register to multiple leagues
- League Manager can manage multiple leagues

### 7.4 Real-Time Analytics

**Current:** Post-game analysis only
**Extension:** Live dashboards, streaming stats

**Architecture Support:**
- Logs provide event stream
- JSONL format easy to tail
- Match data files readable during match
- No changes to core blocks needed

### 7.5 Distributed Deployment

**Current:** Single machine (localhost)
**Extension:** Multi-machine deployment

**Architecture Support:**
- Endpoint URLs can include remote hosts
- File system shared via network mount or sync
- MCP Layer already abstracts network communication
- No business logic changes needed

---

## 8. Implementation Guidelines

### 8.1 Block Independence

Each block should be:
- Implementable in isolation
- Testable independently
- Replaceable without affecting others (within interface contracts)

### 8.2 Interface Contracts

Blocks communicate through:
- **MCP Protocol Messages:** As specified in protocol documentation
- **File Formats:** As specified in data protocol
- **HTTP Endpoints:** Standard /mcp path, POST method

### 8.3 Error Resilience

Each block should:
- Validate all inputs
- Handle missing or malformed data gracefully
- Log errors for debugging
- Continue operation when possible
- Fail gracefully when necessary

### 8.4 Testing Strategy

**Unit Testing:**
- Each block tested independently
- Mock external dependencies (other blocks)

**Integration Testing:**
- Test block interactions
- Test complete flows (registration, match, standings)

**System Testing:**
- Run complete league with multiple agents
- Verify end-to-end functionality

---

## 9. Summary

This architecture provides:

✅ **Clear Separation of Concerns:** Each block has well-defined responsibilities
✅ **Scalability:** Supports thousands of agents through stateless design and file-based coordination
✅ **Extensibility:** New game types, strategies, and features can be added without core changes
✅ **Simplicity:** File-based persistence and HTTP communication keep complexity low
✅ **Testability:** Blocks can be tested independently through clear interfaces
✅ **Observability:** Comprehensive logging enables debugging and analysis
✅ **Protocol Compliance:** All blocks follow league.v2 specification

The architecture balances:
- **Autonomy** (agents make independent decisions) with **Coordination** (orchestrators manage lifecycle)
- **Simplicity** (files, HTTP) with **Scalability** (thousands of agents)
- **Structure** (clear blocks) with **Flexibility** (pluggable strategies, game types)

---

**Document Status:** Architecture Design Complete
**Next Steps:** Implementation of individual blocks following this specification
