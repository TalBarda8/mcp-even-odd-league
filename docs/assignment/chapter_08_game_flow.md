# Chapter 8 - League System Flow

**Source:** Chapter 8 - Running the League System

This document presents a practical guide for running the complete league system, demonstrating how to operate all agents and the league manager with one league manager, two referees, and four players.

---

## 1. System Actors

### 1.1 Primary Actors

| # | Actor | Type | Port | Endpoint |
|---|-------|------|------|----------|
| 1 | League Manager | Orchestrator | 8000 | http://localhost:8000/mcp |
| 2 | REF01 (Referee Alpha) | Orchestrator | 8001 | http://localhost:8001/mcp |
| 3 | REF02 (Referee Beta) | Orchestrator | 8002 | http://localhost:8002/mcp |
| 4 | P01 (Player Agent) | Player | 8101 | http://localhost:8101/mcp |
| 5 | P02 (Player Agent) | Player | 8102 | http://localhost:8102/mcp |
| 6 | P03 (Player Agent) | Player | 8103 | http://localhost:8103/mcp |
| 7 | P04 (Player Agent) | Player | 8104 | http://localhost:8104/mcp |

### 1.2 Orchestrator Roles

**League Manager:**
- Top-level orchestrator for the entire league
- Source of truth for: standings table, match schedule, round status

**Referees (REF01, REF02):**
- Local orchestrators for individual matches
- Each referee is the source of truth for the state of their assigned match

---

## 2. High-Level Flow (Step-by-Step)

### Activation Order Principle

**CRITICAL:** The following activation order is essential for proper system operation:

1. **League Manager** - Must start first
2. **Referees** - Start and register with League Manager
3. **Players** - Start and register with League Manager
4. **League Begins** - Only after all registrations are complete

### Complete Game Lifecycle

```
Stage 1: Referee Registration
  └─> Referees send REFEREE_REGISTER_REQUEST
  └─> League Manager responds with REFEREE_REGISTER_RESPONSE

Stage 2: Player Registration
  └─> Players send LEAGUE_REGISTER_REQUEST
  └─> League Manager responds with LEAGUE_REGISTER_RESPONSE

Stage 3: Match Schedule Creation
  └─> League Manager creates Round-Robin schedule
  └─> Generates match pairings for all rounds

Stage 4: Round Announcement
  └─> League Manager sends ROUND_ANNOUNCEMENT to all players
  └─> Players receive match assignments

Stage 5: Individual Match Execution
  5.1: Game Invitation
    └─> Referee sends GAME_INVITATION to both players

  5.2: Arrival Confirmation
    └─> Players respond with GAME_JOIN_ACK (within 5 seconds)

  5.3: Choice Collection
    └─> Referee sends CHOOSE_PARITY_CALL to each player
    └─> Players respond with CHOOSE_PARITY_RESPONSE (within 30 seconds)

  5.4: Number Draw and Winner Determination
    └─> Referee draws random number (1-10)
    └─> Applies game rules to determine winner

  5.5: End Notification
    └─> Referee sends GAME_OVER to both players

  5.6: Report to League
    └─> Referee sends MATCH_RESULT_REPORT to League Manager

Stage 6: Round Completion and Standings Update
  └─> League Manager calculates standings (points, wins, draws, losses)
  └─> Sends LEAGUE_STANDINGS_UPDATE to all players
  └─> Sends ROUND_COMPLETED notification

Stage 7: League Completion
  └─> After all rounds, League Manager sends LEAGUE_COMPLETED
  └─> Declares champion and final standings
```

---

## 3. Detailed Message Sequence

### 3.1 Stage 1: Referee Registration

**Direction:** Referee → League Manager

**Message:** `REFEREE_REGISTER_REQUEST`

**Sender:** Referee (e.g., "referee:alpha")

**Content:**
- `protocol`: "league.v2"
- `message_type`: "REFEREE_REGISTER_REQUEST"
- `referee_meta`:
  - `display_name`: Referee display name
  - `version`: Referee version
  - `game_types`: ["even_odd"]
  - `contact_endpoint`: Referee HTTP endpoint
  - `max_concurrent_matches`: Maximum concurrent matches

**Response:** `REFEREE_REGISTER_RESPONSE`

**Direction:** League Manager → Referee

**Content:**
- `status`: "ACCEPTED"
- `referee_id`: Assigned ID (e.g., "REF01")
- `auth_token`: Authentication token for future requests
- `league_id`: League identifier
- `reason`: null (or error reason if rejected)

**Note:** The second referee (on port 8002) sends a similar request and receives `referee_id: "REF02"`.

---

### 3.2 Stage 2: Player Registration

**Direction:** Player → League Manager

**Message:** `LEAGUE_REGISTER_REQUEST`

**Sender:** Player (e.g., "player:alpha")

**Method:** `register_player`

**Content:**
- `protocol`: "league.v2"
- `message_type`: "LEAGUE_REGISTER_REQUEST"
- `player_meta`:
  - `display_name`: Player display name
  - `version`: Player version
  - `game_types`: ["even_odd"]
  - `contact_endpoint`: Player HTTP endpoint

**Response:** `LEAGUE_REGISTER_RESPONSE`

**Direction:** League Manager → Player

**Content:**
- `status`: "ACCEPTED"
- `player_id`: Assigned ID (e.g., "P01", "P02", "P03", "P04")
- `auth_token`: Authentication token
- `league_id`: League identifier
- `reason`: null (or error reason if rejected)

**League Manager State:**
- Maintains mapping: `player_id` → `contact_endpoint`
- Maintains mapping: `referee_id` → `contact_endpoint`

---

### 3.3 Stage 3: Match Schedule Creation

**Internal Process** (No message exchange)

After all players and referees are registered, League Manager:
1. Activates `create_schedule` logic
2. Creates Round-Robin schedule for 4 players

**Generated Schedule:**

| Match ID | Round | Player A | Player B |
|----------|-------|----------|----------|
| R1M1 | 1 | P01 | P02 |
| R1M2 | 1 | P03 | P04 |
| R2M1 | 2 | P03 | P01 |
| R2M2 | 2 | P04 | P02 |
| R3M1 | 3 | P04 | P01 |
| R3M2 | 3 | P03 | P02 |

---

### 3.4 Stage 4: Round Announcement

**Direction:** League Manager → All Players

**Message:** `ROUND_ANNOUNCEMENT`

**Method:** `notify_round`

**Content:**
- `protocol`: "league.v2"
- `message_type`: "ROUND_ANNOUNCEMENT"
- `league_id`: League identifier
- `round_id`: Current round number (e.g., 1)
- `matches`: Array of match objects
  - Each match contains:
    - `match_id`: Match identifier (e.g., "R1M1")
    - `game_type`: "even_odd"
    - `player_A_id`: First player ID
    - `player_B_id`: Second player ID
    - `referee_endpoint`: Referee's endpoint URL

**Important:** From the moment `ROUND_ANNOUNCEMENT` is sent, the games themselves begin the round logic. Matches only start when the referee invites the participants.

---

### 3.5 Stage 5: Individual Match Management

**Example:** Match R1M1: Player P01 vs Player P02, Referee REF01

#### 3.5.1 Game Invitation

**Internal State Change:**
- Referee changes match status to `WAITING_FOR_PLAYERS`

**Direction:** Referee → Player (sent to both players)

**Message:** `GAME_INVITATION`

**Method:** `handle_game_invitation`

**Content for P01:**
- `protocol`: "league.v2"
- `message_type`: "GAME_INVITATION"
- `sender`: "referee:REF01"
- `auth_token`: Referee's auth token
- `league_id`: League identifier
- `round_id`: Current round
- `match_id`: "R1M1"
- `game_type`: "even_odd"
- `role_in_match`: "PLAYER_A"
- `opponent_id`: "P02"

**Content for P02:**
- Same as above except:
  - `role_in_match`: "PLAYER_B"
  - `opponent_id`: "P01"

#### 3.5.2 Arrival Confirmation

**Direction:** Player → Referee (from both players)

**Message:** `GAME_JOIN_ACK`

**Timeout:** Within 5 seconds

**Content:**
- `protocol`: "league.v2"
- `message_type`: "GAME_JOIN_ACK"
- `sender`: Player identifier (e.g., "player:P01")
- `auth_token`: Player's auth token
- `match_id`: Match identifier
- `player_id`: Player ID
- `arrival_timestamp`: When player confirmed
- `accept`: true

**Internal State Change:**
- When referee receives both positive ACKs within allowed time:
  - Match status changes to `COLLECTING_CHOICES`

#### 3.5.3 Choice Collection

**Direction:** Referee → Player (sent to both players)

**Message:** `CHOOSE_PARITY_CALL`

**Method:** `choose_parity`

**Content:**
- `protocol`: "league.v2"
- `message_type`: "CHOOSE_PARITY_CALL"
- `sender`: "referee:REF01"
- `auth_token`: Referee's auth token
- `match_id`: Match identifier
- `player_id`: Target player ID
- `game_type`: "even_odd"
- `context`:
  - `opponent_id`: Opponent's ID
  - `round_id`: Current round
  - `your_standings`: Current stats (wins, losses, draws)
- `deadline`: ISO timestamp (30 seconds from now)

**Response:** `CHOOSE_PARITY_RESPONSE`

**Direction:** Player → Referee

**Timeout:** Within 30 seconds

**Content:**
- `protocol`: "league.v2"
- `message_type`: "CHOOSE_PARITY_RESPONSE"
- `sender`: Player identifier
- `auth_token`: Player's auth token
- `match_id`: Match identifier
- `player_id`: Player ID
- `parity_choice`: "even" or "odd"

**Example:**
- P01 responds with `parity_choice: "even"`
- P02 responds with `parity_choice: "odd"`

**Internal State Change:**
- When both valid choices received on time:
  - Match status changes to `DRAWING_NUMBER`

#### 3.5.4 Number Draw and Winner Determination

**Internal Process** (Referee only)

1. Referee draws random number between 1-10 (e.g., 8)
2. Applies game rules modulo:
   - `drawn_number = 8`
   - `number_parity = "even"`
   - P01 choice = "even" → **Correct**
   - P02 choice = "odd" → **Incorrect**
   - `winner_player_id = "P01"`
   - `status = "WIN"`

**Internal State Change:**
- Match status transitions to `FINISHED`

#### 3.5.5 End Notification to Players

**Direction:** Referee → Both Players

**Message:** `GAME_OVER`

**Method:** `notify_match_result`

**Content:**
- `protocol`: "league.v2"
- `message_type`: "GAME_OVER"
- `sender`: "referee:REF01"
- `auth_token`: Referee's auth token
- `match_id`: Match identifier
- `game_type`: "even_odd"
- `game_result`:
  - `status`: "WIN" (or "DRAW", "TECHNICAL_LOSS")
  - `winner_player_id`: Winner's ID (e.g., "P01")
  - `drawn_number`: The drawn number (e.g., 8)
  - `number_parity`: Parity of drawn number (e.g., "even")
  - `choices`:
    - `P01`: "even"
    - `P02`: "odd"
  - `reason`: Explanation text

**Player Action:**
- Each player updates internal state (history, statistics)
- Returns generic response

#### 3.5.6 Report to League Manager

**Direction:** Referee → League Manager

**Message:** `MATCH_RESULT_REPORT`

**Method:** `report_match_result`

**Content:**
- `protocol`: "league.v2"
- `message_type`: "MATCH_RESULT_REPORT"
- `sender`: "referee:REF01"
- `auth_token`: Referee's auth token
- `league_id`: League identifier
- `round_id`: Current round
- `match_id`: Match identifier
- `game_type`: "even_odd"
- `result`:
  - `winner`: Winner's player ID
  - `score`:
    - `P01`: 3 (points awarded)
    - `P02`: 0
  - `details`:
    - `drawn_number`: Number that was drawn
    - `choices`:
      - `P01`: Player's choice
      - `P02`: Player's choice

**League Manager Action:**
- Updates points table according to scoring system (win = 3 points)

---

### 3.6 Stage 6: Round End and Standings Update

**Trigger:** Round 1 ends when all matches have received `MATCH_RESULT_REPORT`

**League Manager Actions:**

1. **Declares round closed** (can move to `round_id = 2`)

2. **Calculates standings table** for each player:
   - `points`: Total points earned
   - `wins`: Number of wins
   - `draws`: Number of draws
   - `losses`: Number of losses
   - `played`: Total matches played

3. **Sends standings update**

**Direction:** League Manager → All Players

**Message:** `LEAGUE_STANDINGS_UPDATE`

**Method:** `update_standings`

**Content:**
- `protocol`: "league.v2"
- `message_type`: "LEAGUE_STANDINGS_UPDATE"
- `sender`: "league_manager"
- `league_id`: League identifier
- `round_id`: Completed round number
- `standings`: Array of player standings
  - Each entry contains:
    - `rank`: Current rank position
    - `player_id`: Player identifier
    - `display_name`: Player display name
    - `played`: Matches played
    - `wins`: Wins count
    - `draws`: Draws count
    - `losses`: Losses count
    - `points`: Total points

4. **Sends round completion notification**

**Direction:** League Manager → All Players

**Message:** `ROUND_COMPLETED`

**Method:** `notify_round_completed`

**Content:**
- `protocol`: "league.v2"
- `message_type`: "ROUND_COMPLETED"
- `sender`: "league_manager"
- `league_id`: League identifier
- `round_id`: Completed round number
- `matches_played`: Number of matches in round
- `next_round_id`: Next round number (or null if league complete)

---

### 3.7 Stage 7: League Completion

**Trigger:** After all rounds are complete

**Direction:** League Manager → All Players

**Message:** `LEAGUE_COMPLETED`

**Method:** `notify_league_completed`

**Content:**
- `protocol`: "league.v2"
- `message_type`: "LEAGUE_COMPLETED"
- `sender`: "league_manager"
- `league_id`: League identifier
- `total_rounds`: Total number of rounds
- `total_matches`: Total matches played
- `champion`:
  - `player_id`: Champion's ID
  - `display_name`: Champion's name
  - `points`: Final points
- `final_standings`: Array of final rankings
  - Each entry: `rank`, `player_id`, `points`

---

## 4. Error Handling

### 4.1 Registration Error

**Direction:** League Manager → Player/Referee

**Message:** `LEAGUE_ERROR`

**Content:**
- `protocol`: "league.v2"
- `message_type`: "LEAGUE_ERROR"
- `sender`: "league_manager"
- `error_code`: Error code (e.g., "E012")
- `error_description`: Error type (e.g., "AUTH_TOKEN_INVALID")
- `context`:
  - Additional error details
  - `provided_token`: Token that was rejected
  - `action`: Action that was attempted

### 4.2 Game Timeout Error

**Direction:** Referee → Player

**Message:** `GAME_ERROR`

**Method:** `notify_game_error`

**Content:**
- `protocol`: "league.v2"
- `message_type`: "GAME_ERROR"
- `sender`: Referee identifier
- `match_id`: Match identifier
- `error_code`: Error code (e.g., "E001")
- `error_description`: Error type (e.g., "TIMEOUT_ERROR")
- `affected_player`: Player who caused the error
- `action_required`: What action timed out (e.g., "CHOOSE_PARITY_RESPONSE")
- `retry_count`: Current retry attempt
- `max_retries`: Maximum retries allowed
- `consequence`: Description of consequence if no response

---

## 5. Query Tools (Optional)

### 5.1 Standings Query

**Direction:** Player → League Manager

**Message:** `LEAGUE_QUERY`

**Method:** `league_query`

**Content:**
- `protocol`: "league.v2"
- `message_type`: "LEAGUE_QUERY"
- `sender`: Player identifier
- `auth_token`: Player's auth token
- `league_id`: League identifier
- `query_type`: "GET_STANDINGS"

**Response:**
- League Manager returns result object containing `standings` in same format as `LEAGUE_STANDINGS_UPDATE`

### 5.2 Additional Available Tools

**In League Manager:**
- `get_standings`: Returns current table state

**In Referee:**
- `get_match_state`: Returns current match state (for debugging purposes)

**In Player:**
- `get_player_state`: Provides match history of the player

---

## 6. Notes and Edge Cases

### 6.1 Timeout Enforcement

**GAME_JOIN_ACK timeout:** 5 seconds
- If player doesn't respond within 5 seconds, referee may:
  - Retry the invitation
  - Award technical loss
  - Report error to League Manager

**CHOOSE_PARITY_RESPONSE timeout:** 30 seconds
- If player doesn't respond within 30 seconds, referee may:
  - Retry up to `max_retries` (typically 3)
  - Award technical loss after all retries exhausted
  - Report error to League Manager

**Any other response:** 10 seconds

### 6.2 Match State Transitions

```
WAITING_FOR_PLAYERS
  ↓ (both players sent GAME_JOIN_ACK)
COLLECTING_CHOICES
  ↓ (both players sent CHOOSE_PARITY_RESPONSE)
DRAWING_NUMBER
  ↓ (referee drew number and determined winner)
FINISHED
```

### 6.3 Agent Crash During League

**What happens if an agent crashes?**
- The agent suffers a technical loss in the current game
- If it doesn't return to operation, it exits the league

### 6.4 Communication Protocol

**All communication:**
- Uses JSON-RPC 2.0 format
- Transported over HTTP POST
- Endpoint path: `/mcp`
- All messages include unified envelope with mandatory fields:
  - `protocol`: "league.v2"
  - `message_type`: Specific message type
  - `sender`: Sender identifier
  - `timestamp`: ISO 8601 format in UTC timezone
  - `conversation_id`: Unique conversation identifier

**Orchestrators manage message flow:**
- League Manager manages: round flow, standings updates
- Referees manage: match state, player turns, result determination

### 6.5 Conversation IDs

Each logical conversation has a unique `conversation_id`:
- Referee registration: e.g., "conv-ref-alpha-reg-001"
- Player registration: e.g., "conv-player-alpha-reg-001"
- Match execution: e.g., "conv-r1m1-001"
- Round announcements: e.g., "conv-round-1-announce"
- Standings updates: e.g., "conv-round-1-standings"

### 6.6 Scoring System

**Standard scoring:**
- Win: 3 points
- Draw: 1 point
- Loss: 0 points

**Technical loss:**
- Awarded when player fails to respond within timeout
- Results in 0 points for affected player
- Opponent receives 3 points (win by default)

### 6.7 Authentication

**auth_token:**
- Issued during registration (REFEREE_REGISTER_RESPONSE, LEAGUE_REGISTER_RESPONSE)
- Must be included in all subsequent requests
- League Manager validates token before processing requests
- Invalid token results in LEAGUE_ERROR with error_code: "AUTH_TOKEN_INVALID"

### 6.8 Round-Robin Schedule Logic

For 4 players (P01, P02, P03, P04):
- Total rounds: 3
- Matches per round: 2
- Total matches: 6
- Each player plays 3 matches (one against each opponent)

**Fair distribution:**
- Every player plays exactly once per round
- Every player plays against every other player exactly once

---

## 7. Complete Flow Summary

1. **System Startup:**
   - League Manager starts (port 8000)
   - 2 Referees start and register (ports 8001, 8002)
   - 4 Players start and register (ports 8101-8104)

2. **Pre-Game:**
   - League Manager creates Round-Robin schedule
   - Sends ROUND_ANNOUNCEMENT for Round 1

3. **Match Execution (per match):**
   - Referee invites players (GAME_INVITATION)
   - Players confirm (GAME_JOIN_ACK - 5s timeout)
   - Referee requests choices (CHOOSE_PARITY_CALL)
   - Players choose (CHOOSE_PARITY_RESPONSE - 30s timeout)
   - Referee draws number and determines winner
   - Referee notifies players (GAME_OVER)
   - Referee reports to league (MATCH_RESULT_REPORT)

4. **Round Completion:**
   - League Manager updates standings (LEAGUE_STANDINGS_UPDATE)
   - League Manager announces round complete (ROUND_COMPLETED)
   - Repeats for next round

5. **League Completion:**
   - After all rounds, League Manager sends LEAGUE_COMPLETED
   - Declares champion and final standings

---

## 8. Message Direction Reference

### Messages FROM League Manager:
- `REFEREE_REGISTER_RESPONSE` → Referee
- `LEAGUE_REGISTER_RESPONSE` → Player
- `ROUND_ANNOUNCEMENT` → All Players
- `LEAGUE_STANDINGS_UPDATE` → All Players
- `ROUND_COMPLETED` → All Players
- `LEAGUE_COMPLETED` → All Players
- `LEAGUE_ERROR` → Player/Referee

### Messages TO League Manager:
- `REFEREE_REGISTER_REQUEST` ← Referee
- `LEAGUE_REGISTER_REQUEST` ← Player
- `MATCH_RESULT_REPORT` ← Referee
- `LEAGUE_QUERY` ← Player

### Messages FROM Referee:
- `GAME_INVITATION` → Both Players
- `CHOOSE_PARITY_CALL` → Both Players
- `GAME_OVER` → Both Players
- `GAME_ERROR` → Player

### Messages TO Referee:
- `GAME_JOIN_ACK` ← Player
- `CHOOSE_PARITY_RESPONSE` ← Player

---

**End of Chapter 8 - Game Flow Documentation**
