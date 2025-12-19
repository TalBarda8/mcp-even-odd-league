# MCP Message Contracts

**Even/Odd League System - Complete Message Protocol Specification**

**Document Version:** 1.0
**Last Updated:** 2025-01-19
**Protocol Version:** league.v2
**Transport:** HTTP POST to `/mcp` endpoint
**Format:** JSON-RPC 2.0

---

## Table of Contents

1. [Protocol Foundation](#1-protocol-foundation)
2. [Registration Messages](#2-registration-messages)
3. [League Coordination Messages](#3-league-coordination-messages)
4. [Match Execution Messages](#4-match-execution-messages)
5. [Result and Status Messages](#5-result-and-status-messages)
6. [Error Messages](#6-error-messages)
7. [Query Messages](#7-query-messages)
8. [Coverage Checklist](#8-coverage-checklist)

---

## 1. Protocol Foundation

### 1.1 Common Envelope Structure

All messages MUST be wrapped in JSON-RPC 2.0 format:

```yaml
# Request envelope
{
  jsonrpc: "2.0"                    # string, REQUIRED, MUST be "2.0"
  method: string                     # string, REQUIRED, MCP method name
  params: object                     # object, REQUIRED, message payload
  id: string | number                # string or number, REQUIRED for requests expecting response
}

# Response envelope (success)
{
  jsonrpc: "2.0"                    # string, REQUIRED
  result: object                     # object, REQUIRED for success
  id: string | number                # string or number, REQUIRED, matches request id
}

# Response envelope (error)
{
  jsonrpc: "2.0"                    # string, REQUIRED
  error: {                           # object, REQUIRED for errors
    code: integer                    # integer, REQUIRED, error code
    message: string                  # string, REQUIRED, error message
    data: object                     # object, OPTIONAL, additional error data
  }
  id: string | number                # string or number, REQUIRED, matches request id
}
```

### 1.2 Common Payload Fields

All message payloads MUST include these fields:

```yaml
protocol: "league.v2"                # string, REQUIRED, protocol version
message_type: string                 # string, REQUIRED, specific message type
sender: string                       # string, REQUIRED, sender identifier
timestamp: string                    # string, REQUIRED, ISO 8601 UTC format
conversation_id: string              # string, REQUIRED, unique conversation identifier
```

### 1.3 Timeout Requirements

Per Chapter 6 Requirements:

| Message Type | Timeout | Enforcement Point |
|--------------|---------|------------------|
| GAME_JOIN_ACK | 5 seconds | Referee |
| CHOOSE_PARITY_RESPONSE | 30 seconds | Referee |
| All other responses | 10 seconds | Sender |

### 1.4 Authentication

After registration, all requests MUST include:

```yaml
auth_token: string                   # string, REQUIRED, issued during registration
```

---

## 2. Registration Messages

### 2.1 REFEREE_REGISTER_REQUEST

**Direction:** Referee → League Manager
**JSON-RPC Method:** `register_referee`
**Trigger:** Referee startup, before any match assignment
**Timeout:** 10 seconds

#### Request Payload Schema

```yaml
# Required fields
protocol: "league.v2"                      # string, REQUIRED
message_type: "REFEREE_REGISTER_REQUEST"   # string, REQUIRED
sender: string                             # string, REQUIRED, e.g., "referee:alpha"
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
conversation_id: string                    # string, REQUIRED, e.g., "conv-ref-alpha-reg-001"

referee_meta:                              # object, REQUIRED
  display_name: string                     # string, REQUIRED, human-readable name
  version: string                          # string, REQUIRED, referee version (e.g., "1.0.0")
  game_types: array[string]                # array, REQUIRED, supported games (e.g., ["even_odd"])
  contact_endpoint: string                 # string, REQUIRED, full HTTP URL
  max_concurrent_matches: integer          # integer, REQUIRED, max parallel matches

# Optional fields
# (none defined)
```

#### Example Request

```json
{
  "jsonrpc": "2.0",
  "method": "register_referee",
  "params": {
    "protocol": "league.v2",
    "message_type": "REFEREE_REGISTER_REQUEST",
    "sender": "referee:alpha",
    "timestamp": "2025-01-19T10:00:00Z",
    "conversation_id": "conv-ref-alpha-reg-001",
    "referee_meta": {
      "display_name": "Referee Alpha",
      "version": "1.0.0",
      "game_types": ["even_odd"],
      "contact_endpoint": "http://localhost:8001/mcp",
      "max_concurrent_matches": 5
    }
  },
  "id": "req-001"
}
```

#### Response Payload Schema

```yaml
# Success response (in result object)
status: "ACCEPTED" | "REJECTED"      # string, REQUIRED
referee_id: string                   # string, REQUIRED if ACCEPTED, assigned ID (e.g., "REF01")
auth_token: string                   # string, REQUIRED if ACCEPTED, authentication token
league_id: string                    # string, REQUIRED if ACCEPTED, league identifier
reason: string | null                # string, OPTIONAL, rejection reason if REJECTED

# Additional fields
protocol: "league.v2"                # string, REQUIRED
message_type: "REFEREE_REGISTER_RESPONSE"  # string, REQUIRED
timestamp: string                    # string, REQUIRED, ISO 8601 UTC
```

#### Example Response (Success)

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "REFEREE_REGISTER_RESPONSE",
    "timestamp": "2025-01-19T10:00:01Z",
    "status": "ACCEPTED",
    "referee_id": "REF01",
    "auth_token": "tok-ref-01-xyz789",
    "league_id": "league_2025_even_odd",
    "reason": null
  },
  "id": "req-001"
}
```

#### Example Response (Rejection)

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "REFEREE_REGISTER_RESPONSE",
    "timestamp": "2025-01-19T10:00:01Z",
    "status": "REJECTED",
    "reason": "Maximum referees already registered"
  },
  "id": "req-001"
}
```

#### Error Cases

| Error Code | Message | Cause |
|------------|---------|-------|
| -32602 | Invalid params | Missing required fields or invalid field types |
| -32603 | Internal error | League Manager internal failure |
| 1001 | League full | Maximum referees already registered |
| 1002 | Invalid endpoint | contact_endpoint is not reachable |
| 1003 | Unsupported game type | game_types contains unsupported game |

#### Example Error Response

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 1001,
    "message": "League full",
    "data": {
      "max_referees": 2,
      "current_referees": 2
    }
  },
  "id": "req-001"
}
```

#### Side Effects

**On Success:**
- League Manager adds referee to `config/agents/agents_config.json`
- Referee endpoint stored in endpoint registry
- auth_token generated and stored
- Referee marked as available for match assignment

**On Failure:**
- No state change
- Referee must retry or handle rejection

---

### 2.2 LEAGUE_REGISTER_REQUEST

**Direction:** Player → League Manager
**JSON-RPC Method:** `register_player`
**Trigger:** Player startup, before league begins
**Timeout:** 10 seconds

#### Request Payload Schema

```yaml
# Required fields
protocol: "league.v2"                      # string, REQUIRED
message_type: "LEAGUE_REGISTER_REQUEST"    # string, REQUIRED
sender: string                             # string, REQUIRED, e.g., "player:alpha"
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
conversation_id: string                    # string, REQUIRED, e.g., "conv-player-alpha-reg-001"

player_meta:                               # object, REQUIRED
  display_name: string                     # string, REQUIRED, unique player name
  version: string                          # string, REQUIRED, player version (e.g., "1.0.0")
  game_types: array[string]                # array, REQUIRED, supported games (e.g., ["even_odd"])
  contact_endpoint: string                 # string, REQUIRED, full HTTP URL

# Optional fields
# (none defined)
```

#### Example Request

```json
{
  "jsonrpc": "2.0",
  "method": "register_player",
  "params": {
    "protocol": "league.v2",
    "message_type": "LEAGUE_REGISTER_REQUEST",
    "sender": "player:alpha",
    "timestamp": "2025-01-19T10:00:05Z",
    "conversation_id": "conv-player-alpha-reg-001",
    "player_meta": {
      "display_name": "AlphaPlayer",
      "version": "1.0.0",
      "game_types": ["even_odd"],
      "contact_endpoint": "http://localhost:8101/mcp"
    }
  },
  "id": "req-002"
}
```

#### Response Payload Schema

```yaml
# Success response (in result object)
status: "ACCEPTED" | "REJECTED"      # string, REQUIRED
player_id: string                    # string, REQUIRED if ACCEPTED, assigned ID (e.g., "P01")
auth_token: string                   # string, REQUIRED if ACCEPTED, authentication token
league_id: string                    # string, REQUIRED if ACCEPTED, league identifier
reason: string | null                # string, OPTIONAL, rejection reason if REJECTED

# Additional fields
protocol: "league.v2"                # string, REQUIRED
message_type: "LEAGUE_REGISTER_RESPONSE"  # string, REQUIRED
timestamp: string                    # string, REQUIRED, ISO 8601 UTC
```

#### Example Response (Success)

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "LEAGUE_REGISTER_RESPONSE",
    "timestamp": "2025-01-19T10:00:06Z",
    "status": "ACCEPTED",
    "player_id": "P01",
    "auth_token": "tok-p01-abc123",
    "league_id": "league_2025_even_odd",
    "reason": null
  },
  "id": "req-002"
}
```

#### Error Cases

| Error Code | Message | Cause |
|------------|---------|-------|
| -32602 | Invalid params | Missing required fields or invalid types |
| -32603 | Internal error | League Manager internal failure |
| 2001 | League full | Maximum players already registered |
| 2002 | Duplicate name | display_name already taken |
| 2003 | Invalid endpoint | contact_endpoint not reachable |
| 2004 | Unsupported game type | game_types contains unsupported game |

#### Example Error Response

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 2002,
    "message": "Duplicate name",
    "data": {
      "display_name": "AlphaPlayer",
      "suggestion": "Choose a different display_name"
    }
  },
  "id": "req-002"
}
```

#### Side Effects

**On Success:**
- League Manager adds player to `config/agents/agents_config.json`
- Player endpoint stored in endpoint registry
- auth_token generated and stored
- Player marked as available for matches
- If all players registered, League Manager may start creating schedule

**On Failure:**
- No state change
- Player must retry or handle rejection

---

## 3. League Coordination Messages

### 3.1 ROUND_ANNOUNCEMENT

**Direction:** League Manager → All Players
**JSON-RPC Method:** `notify_round`
**Trigger:** League Manager starts new round after schedule creation or previous round completion
**Timeout:** 10 seconds (for player acknowledgment)

#### Request Payload Schema

```yaml
# Required fields
protocol: "league.v2"                      # string, REQUIRED
message_type: "ROUND_ANNOUNCEMENT"         # string, REQUIRED
sender: "league_manager"                   # string, REQUIRED
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
conversation_id: string                    # string, REQUIRED, e.g., "conv-round-1-announce"

league_id: string                          # string, REQUIRED, league identifier
round_id: integer                          # integer, REQUIRED, round number (1, 2, 3, ...)
matches: array[object]                     # array, REQUIRED, list of matches in this round

# Each match object contains:
matches[].match_id: string                 # string, REQUIRED, match identifier (e.g., "R1M1")
matches[].game_type: string                # string, REQUIRED, game type (e.g., "even_odd")
matches[].player_A_id: string              # string, REQUIRED, first player ID
matches[].player_B_id: string              # string, REQUIRED, second player ID
matches[].referee_endpoint: string         # string, REQUIRED, referee's contact endpoint

# Optional fields
# (none defined)
```

#### Example Request

```json
{
  "jsonrpc": "2.0",
  "method": "notify_round",
  "params": {
    "protocol": "league.v2",
    "message_type": "ROUND_ANNOUNCEMENT",
    "sender": "league_manager",
    "timestamp": "2025-01-19T10:00:10Z",
    "conversation_id": "conv-round-1-announce",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "matches": [
      {
        "match_id": "R1M1",
        "game_type": "even_odd",
        "player_A_id": "P01",
        "player_B_id": "P02",
        "referee_endpoint": "http://localhost:8001/mcp"
      },
      {
        "match_id": "R1M2",
        "game_type": "even_odd",
        "player_A_id": "P03",
        "player_B_id": "P04",
        "referee_endpoint": "http://localhost:8002/mcp"
      }
    ]
  },
  "id": "req-003"
}
```

#### Response Payload Schema

```yaml
# Success response (in result object)
status: "ACKNOWLEDGED"               # string, REQUIRED
player_id: string                    # string, REQUIRED, acknowledging player's ID
round_id: integer                    # integer, REQUIRED, acknowledged round number

# Additional fields
protocol: "league.v2"                # string, REQUIRED
message_type: "ROUND_ANNOUNCEMENT_ACK"  # string, REQUIRED
timestamp: string                    # string, REQUIRED, ISO 8601 UTC
```

#### Example Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "ROUND_ANNOUNCEMENT_ACK",
    "timestamp": "2025-01-19T10:00:11Z",
    "status": "ACKNOWLEDGED",
    "player_id": "P01",
    "round_id": 1
  },
  "id": "req-003"
}
```

#### Error Cases

| Error Code | Message | Cause |
|------------|---------|-------|
| -32602 | Invalid params | Missing required fields |
| 3001 | Invalid auth token | Player's auth_token invalid |
| 3002 | Player not registered | Player not found in registry |

#### Example Error Response

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 3001,
    "message": "Invalid auth token",
    "data": {
      "player_id": "P01"
    }
  },
  "id": "req-003"
}
```

#### Side Effects

**On Success (Player side):**
- Player stores round information
- Player prepares to receive GAME_INVITATION from referee
- Player updates internal state to track current round

**On Success (League Manager side):**
- Tracks acknowledgments from all players
- Once all players acknowledge, referees can start inviting players

---

### 3.2 LEAGUE_STANDINGS_UPDATE

**Direction:** League Manager → All Players
**JSON-RPC Method:** `update_standings`
**Trigger:** After all matches in a round complete and standings are recalculated
**Timeout:** 10 seconds

#### Request Payload Schema

```yaml
# Required fields
protocol: "league.v2"                      # string, REQUIRED
message_type: "LEAGUE_STANDINGS_UPDATE"    # string, REQUIRED
sender: "league_manager"                   # string, REQUIRED
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
conversation_id: string                    # string, REQUIRED, e.g., "conv-round-1-standings"

league_id: string                          # string, REQUIRED, league identifier
round_id: integer                          # integer, REQUIRED, completed round number
standings: array[object]                   # array, REQUIRED, ordered standings (rank 1 first)

# Each standing object contains:
standings[].rank: integer                  # integer, REQUIRED, current rank (1-based)
standings[].player_id: string              # string, REQUIRED, player identifier
standings[].display_name: string           # string, REQUIRED, player display name
standings[].played: integer                # integer, REQUIRED, total matches played
standings[].wins: integer                  # integer, REQUIRED, total wins
standings[].draws: integer                 # integer, REQUIRED, total draws
standings[].losses: integer                # integer, REQUIRED, total losses
standings[].points: integer                # integer, REQUIRED, total points

# Optional fields
# (none defined)
```

#### Example Request

```json
{
  "jsonrpc": "2.0",
  "method": "update_standings",
  "params": {
    "protocol": "league.v2",
    "message_type": "LEAGUE_STANDINGS_UPDATE",
    "sender": "league_manager",
    "timestamp": "2025-01-19T10:05:00Z",
    "conversation_id": "conv-round-1-standings",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "standings": [
      {
        "rank": 1,
        "player_id": "P01",
        "display_name": "AlphaPlayer",
        "played": 1,
        "wins": 1,
        "draws": 0,
        "losses": 0,
        "points": 3
      },
      {
        "rank": 2,
        "player_id": "P03",
        "display_name": "GammaPlayer",
        "played": 1,
        "wins": 1,
        "draws": 0,
        "losses": 0,
        "points": 3
      },
      {
        "rank": 3,
        "player_id": "P02",
        "display_name": "BetaPlayer",
        "played": 1,
        "wins": 0,
        "draws": 0,
        "losses": 1,
        "points": 0
      },
      {
        "rank": 4,
        "player_id": "P04",
        "display_name": "DeltaPlayer",
        "played": 1,
        "wins": 0,
        "draws": 0,
        "losses": 1,
        "points": 0
      }
    ]
  },
  "id": "req-004"
}
```

#### Response Payload Schema

```yaml
# Success response (in result object)
status: "ACKNOWLEDGED"               # string, REQUIRED
player_id: string                    # string, REQUIRED, acknowledging player's ID
round_id: integer                    # integer, REQUIRED, acknowledged round number

# Additional fields
protocol: "league.v2"                # string, REQUIRED
message_type: "STANDINGS_UPDATE_ACK" # string, REQUIRED
timestamp: string                    # string, REQUIRED, ISO 8601 UTC
```

#### Example Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "STANDINGS_UPDATE_ACK",
    "timestamp": "2025-01-19T10:05:01Z",
    "status": "ACKNOWLEDGED",
    "player_id": "P01",
    "round_id": 1
  },
  "id": "req-004"
}
```

#### Error Cases

| Error Code | Message | Cause |
|------------|---------|-------|
| -32602 | Invalid params | Missing required fields |
| 3001 | Invalid auth token | Player's auth_token invalid |

#### Side Effects

**On Success (Player side):**
- Player updates internal standings cache
- Player can use standings for strategic decisions in future matches

**On Success (League Manager side):**
- Tracks acknowledgments
- Proceeds to next round announcement or league completion

---

### 3.3 ROUND_COMPLETED

**Direction:** League Manager → All Players
**JSON-RPC Method:** `notify_round_completed`
**Trigger:** After all matches in round complete and standings update sent
**Timeout:** 10 seconds

#### Request Payload Schema

```yaml
# Required fields
protocol: "league.v2"                      # string, REQUIRED
message_type: "ROUND_COMPLETED"            # string, REQUIRED
sender: "league_manager"                   # string, REQUIRED
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
conversation_id: string                    # string, REQUIRED, e.g., "conv-round-1-complete"

league_id: string                          # string, REQUIRED, league identifier
round_id: integer                          # integer, REQUIRED, completed round number
matches_played: integer                    # integer, REQUIRED, number of matches in round
next_round_id: integer | null              # integer or null, REQUIRED, next round number or null if done

# Optional fields
# (none defined)
```

#### Example Request

```json
{
  "jsonrpc": "2.0",
  "method": "notify_round_completed",
  "params": {
    "protocol": "league.v2",
    "message_type": "ROUND_COMPLETED",
    "sender": "league_manager",
    "timestamp": "2025-01-19T10:05:05Z",
    "conversation_id": "conv-round-1-complete",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "matches_played": 2,
    "next_round_id": 2
  },
  "id": "req-005"
}
```

#### Response Payload Schema

```yaml
# Success response (in result object)
status: "ACKNOWLEDGED"               # string, REQUIRED
player_id: string                    # string, REQUIRED, acknowledging player's ID
round_id: integer                    # integer, REQUIRED, acknowledged round number

# Additional fields
protocol: "league.v2"                # string, REQUIRED
message_type: "ROUND_COMPLETED_ACK"  # string, REQUIRED
timestamp: string                    # string, REQUIRED, ISO 8601 UTC
```

#### Example Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "ROUND_COMPLETED_ACK",
    "timestamp": "2025-01-19T10:05:06Z",
    "status": "ACKNOWLEDGED",
    "player_id": "P01",
    "round_id": 1
  },
  "id": "req-005"
}
```

#### Error Cases

| Error Code | Message | Cause |
|------------|---------|-------|
| -32602 | Invalid params | Missing required fields |
| 3001 | Invalid auth token | Player's auth_token invalid |

#### Side Effects

**On Success (Player side):**
- Player marks round as complete in internal state
- Player prepares for next round announcement

**On Success (League Manager side):**
- Tracks acknowledgments
- May proceed to announce next round or declare league complete

---

### 3.4 LEAGUE_COMPLETED

**Direction:** League Manager → All Players
**JSON-RPC Method:** `notify_league_completed`
**Trigger:** After all rounds complete
**Timeout:** 10 seconds

#### Request Payload Schema

```yaml
# Required fields
protocol: "league.v2"                      # string, REQUIRED
message_type: "LEAGUE_COMPLETED"           # string, REQUIRED
sender: "league_manager"                   # string, REQUIRED
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
conversation_id: string                    # string, REQUIRED, e.g., "conv-league-complete"

league_id: string                          # string, REQUIRED, league identifier
total_rounds: integer                      # integer, REQUIRED, total number of rounds
total_matches: integer                     # integer, REQUIRED, total matches played
champion: object                           # object, REQUIRED, champion details
final_standings: array[object]             # array, REQUIRED, final rankings

# Champion object contains:
champion.player_id: string                 # string, REQUIRED, champion's ID
champion.display_name: string              # string, REQUIRED, champion's name
champion.points: integer                   # integer, REQUIRED, final points

# Each final standing object contains:
final_standings[].rank: integer            # integer, REQUIRED, final rank
final_standings[].player_id: string        # string, REQUIRED, player identifier
final_standings[].display_name: string     # string, REQUIRED, player display name
final_standings[].points: integer          # integer, REQUIRED, total points
final_standings[].wins: integer            # integer, REQUIRED, total wins
final_standings[].draws: integer           # integer, REQUIRED, total draws
final_standings[].losses: integer          # integer, REQUIRED, total losses

# Optional fields
# (none defined)
```

#### Example Request

```json
{
  "jsonrpc": "2.0",
  "method": "notify_league_completed",
  "params": {
    "protocol": "league.v2",
    "message_type": "LEAGUE_COMPLETED",
    "sender": "league_manager",
    "timestamp": "2025-01-19T10:20:00Z",
    "conversation_id": "conv-league-complete",
    "league_id": "league_2025_even_odd",
    "total_rounds": 3,
    "total_matches": 6,
    "champion": {
      "player_id": "P01",
      "display_name": "AlphaPlayer",
      "points": 9
    },
    "final_standings": [
      {
        "rank": 1,
        "player_id": "P01",
        "display_name": "AlphaPlayer",
        "points": 9,
        "wins": 3,
        "draws": 0,
        "losses": 0
      },
      {
        "rank": 2,
        "player_id": "P03",
        "display_name": "GammaPlayer",
        "points": 6,
        "wins": 2,
        "draws": 0,
        "losses": 1
      },
      {
        "rank": 3,
        "player_id": "P02",
        "display_name": "BetaPlayer",
        "points": 3,
        "wins": 1,
        "draws": 0,
        "losses": 2
      },
      {
        "rank": 4,
        "player_id": "P04",
        "display_name": "DeltaPlayer",
        "points": 0,
        "wins": 0,
        "draws": 0,
        "losses": 3
      }
    ]
  },
  "id": "req-006"
}
```

#### Response Payload Schema

```yaml
# Success response (in result object)
status: "ACKNOWLEDGED"               # string, REQUIRED
player_id: string                    # string, REQUIRED, acknowledging player's ID

# Additional fields
protocol: "league.v2"                # string, REQUIRED
message_type: "LEAGUE_COMPLETED_ACK" # string, REQUIRED
timestamp: string                    # string, REQUIRED, ISO 8601 UTC
```

#### Example Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "LEAGUE_COMPLETED_ACK",
    "timestamp": "2025-01-19T10:20:01Z",
    "status": "ACKNOWLEDGED",
    "player_id": "P01"
  },
  "id": "req-006"
}
```

#### Error Cases

| Error Code | Message | Cause |
|------------|---------|-------|
| -32602 | Invalid params | Missing required fields |
| 3001 | Invalid auth token | Player's auth_token invalid |

#### Side Effects

**On Success (Player side):**
- Player marks league as complete
- Player may shut down gracefully
- Player saves final statistics

**On Success (League Manager side):**
- League lifecycle complete
- May persist final results and shut down

---

## 4. Match Execution Messages

### 4.1 GAME_INVITATION

**Direction:** Referee → Player (sent to both players in match)
**JSON-RPC Method:** `handle_game_invitation`
**Trigger:** Referee begins match after receiving round assignment
**Timeout:** Player must respond with GAME_JOIN_ACK within 5 seconds

#### Request Payload Schema

```yaml
# Required fields
protocol: "league.v2"                      # string, REQUIRED
message_type: "GAME_INVITATION"            # string, REQUIRED
sender: string                             # string, REQUIRED, referee identifier (e.g., "referee:REF01")
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
conversation_id: string                    # string, REQUIRED, e.g., "conv-r1m1-001"
auth_token: string                         # string, REQUIRED, referee's auth token

league_id: string                          # string, REQUIRED, league identifier
round_id: integer                          # integer, REQUIRED, current round number
match_id: string                           # string, REQUIRED, match identifier (e.g., "R1M1")
game_type: string                          # string, REQUIRED, game type (e.g., "even_odd")
role_in_match: "PLAYER_A" | "PLAYER_B"     # string, REQUIRED, player's role in match
opponent_id: string                        # string, REQUIRED, opponent's player ID

# Optional fields
# (none defined)
```

#### Example Request (to Player A)

```json
{
  "jsonrpc": "2.0",
  "method": "handle_game_invitation",
  "params": {
    "protocol": "league.v2",
    "message_type": "GAME_INVITATION",
    "sender": "referee:REF01",
    "timestamp": "2025-01-19T10:01:00Z",
    "conversation_id": "conv-r1m1-001",
    "auth_token": "tok-ref-01-xyz789",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "match_id": "R1M1",
    "game_type": "even_odd",
    "role_in_match": "PLAYER_A",
    "opponent_id": "P02"
  },
  "id": "req-007"
}
```

#### Response Payload Schema (GAME_JOIN_ACK)

```yaml
# Success response (in result object)
protocol: "league.v2"                      # string, REQUIRED
message_type: "GAME_JOIN_ACK"              # string, REQUIRED
sender: string                             # string, REQUIRED, player identifier (e.g., "player:P01")
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
auth_token: string                         # string, REQUIRED, player's auth token

match_id: string                           # string, REQUIRED, match identifier
player_id: string                          # string, REQUIRED, player's ID
arrival_timestamp: string                  # string, REQUIRED, ISO 8601 UTC when player confirmed
accept: boolean                            # boolean, REQUIRED, true if accepting, false if declining

# Optional fields
# (none defined)
```

#### Example Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "GAME_JOIN_ACK",
    "sender": "player:P01",
    "timestamp": "2025-01-19T10:01:01Z",
    "auth_token": "tok-p01-abc123",
    "match_id": "R1M1",
    "player_id": "P01",
    "arrival_timestamp": "2025-01-19T10:01:01Z",
    "accept": true
  },
  "id": "req-007"
}
```

#### Error Cases

| Error Code | Message | Cause |
|------------|---------|-------|
| -32602 | Invalid params | Missing required fields |
| 4001 | Invalid auth token | Referee's auth_token invalid |
| 4002 | Player not found | Player ID not registered |
| 4003 | Match not found | Match ID unknown |
| -1 | Timeout | Player didn't respond within 5 seconds |

#### Example Error Response (Timeout)

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -1,
    "message": "Timeout waiting for GAME_JOIN_ACK",
    "data": {
      "player_id": "P01",
      "timeout_seconds": 5,
      "retry_count": 1,
      "max_retries": 3
    }
  },
  "id": "req-007"
}
```

#### Side Effects

**On Success (Player side):**
- Player confirms participation in match
- Player prepares to receive CHOOSE_PARITY_CALL
- Player stores match context (opponent, role, match_id)

**On Success (Referee side):**
- Referee marks player as arrived
- When both players send GAME_JOIN_ACK, referee transitions to COLLECTING_CHOICES state
- If player doesn't respond within 5 seconds, referee may retry or award technical loss

**On Timeout:**
- Referee retries up to max_retries (typically 3)
- After exhausting retries, referee awards technical loss to non-responding player
- Referee sends GAME_ERROR to player
- Referee reports match result with technical loss to League Manager

---

### 4.2 CHOOSE_PARITY_CALL

**Direction:** Referee → Player (sent to both players)
**JSON-RPC Method:** `parity_choose`
**Trigger:** After both players send GAME_JOIN_ACK
**Timeout:** Player must respond with CHOOSE_PARITY_RESPONSE within 30 seconds

#### Request Payload Schema

```yaml
# Required fields
protocol: "league.v2"                      # string, REQUIRED
message_type: "CHOOSE_PARITY_CALL"         # string, REQUIRED
sender: string                             # string, REQUIRED, referee identifier
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
conversation_id: string                    # string, REQUIRED, matches invitation conversation_id
auth_token: string                         # string, REQUIRED, referee's auth token

match_id: string                           # string, REQUIRED, match identifier
player_id: string                          # string, REQUIRED, target player's ID
game_type: string                          # string, REQUIRED, game type
context: object                            # object, REQUIRED, additional context for decision
deadline: string                           # string, REQUIRED, ISO 8601 UTC (30s from now)

# Context object contains:
context.opponent_id: string                # string, REQUIRED, opponent's ID
context.round_id: integer                  # integer, REQUIRED, current round number
context.your_standings: object             # object, REQUIRED, player's current standings

# your_standings object contains:
context.your_standings.wins: integer       # integer, REQUIRED, player's total wins
context.your_standings.losses: integer     # integer, REQUIRED, player's total losses
context.your_standings.draws: integer      # integer, REQUIRED, player's total draws
context.your_standings.points: integer     # integer, REQUIRED, player's total points

# Optional fields
# (none defined)
```

#### Example Request

```json
{
  "jsonrpc": "2.0",
  "method": "parity_choose",
  "params": {
    "protocol": "league.v2",
    "message_type": "CHOOSE_PARITY_CALL",
    "sender": "referee:REF01",
    "timestamp": "2025-01-19T10:01:05Z",
    "conversation_id": "conv-r1m1-001",
    "auth_token": "tok-ref-01-xyz789",
    "match_id": "R1M1",
    "player_id": "P01",
    "game_type": "even_odd",
    "context": {
      "opponent_id": "P02",
      "round_id": 1,
      "your_standings": {
        "wins": 0,
        "losses": 0,
        "draws": 0,
        "points": 0
      }
    },
    "deadline": "2025-01-19T10:01:35Z"
  },
  "id": "req-008"
}
```

#### Response Payload Schema (CHOOSE_PARITY_RESPONSE)

```yaml
# Success response (in result object)
protocol: "league.v2"                      # string, REQUIRED
message_type: "CHOOSE_PARITY_RESPONSE"     # string, REQUIRED
sender: string                             # string, REQUIRED, player identifier
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
auth_token: string                         # string, REQUIRED, player's auth token

match_id: string                           # string, REQUIRED, match identifier
player_id: string                          # string, REQUIRED, player's ID
parity_choice: "even" | "odd"              # string, REQUIRED, player's choice

# Optional fields
# (none defined)
```

#### Example Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "CHOOSE_PARITY_RESPONSE",
    "sender": "player:P01",
    "timestamp": "2025-01-19T10:01:10Z",
    "auth_token": "tok-p01-abc123",
    "match_id": "R1M1",
    "player_id": "P01",
    "parity_choice": "even"
  },
  "id": "req-008"
}
```

#### Error Cases

| Error Code | Message | Cause |
|------------|---------|-------|
| -32602 | Invalid params | Missing required fields or invalid parity_choice |
| 4001 | Invalid auth token | Player's auth_token invalid |
| 4004 | Invalid choice | parity_choice not "even" or "odd" |
| 4005 | Match state error | Match not in COLLECTING_CHOICES state |
| -1 | Timeout | Player didn't respond within 30 seconds |

#### Example Error Response (Timeout)

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -1,
    "message": "Timeout waiting for CHOOSE_PARITY_RESPONSE",
    "data": {
      "player_id": "P01",
      "timeout_seconds": 30,
      "retry_count": 1,
      "max_retries": 3
    }
  },
  "id": "req-008"
}
```

#### Side Effects

**On Success (Player side):**
- Player submits choice to referee
- Player waits for GAME_OVER notification

**On Success (Referee side):**
- Referee stores player's choice
- When both players respond, referee transitions to DRAWING_NUMBER state
- Referee draws random number (1-10)
- Referee determines winner
- Referee transitions to FINISHED state

**On Timeout:**
- Referee retries up to max_retries (typically 3)
- After exhausting retries, referee awards technical loss to non-responding player
- Referee sends GAME_ERROR to player
- Referee proceeds with match completion

---

### 4.3 GAME_OVER

**Direction:** Referee → Player (sent to both players)
**JSON-RPC Method:** `notify_match_result`
**Trigger:** After referee determines winner and match completes
**Timeout:** 10 seconds

#### Request Payload Schema

```yaml
# Required fields
protocol: "league.v2"                      # string, REQUIRED
message_type: "GAME_OVER"                  # string, REQUIRED
sender: string                             # string, REQUIRED, referee identifier
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
conversation_id: string                    # string, REQUIRED, matches invitation conversation_id
auth_token: string                         # string, REQUIRED, referee's auth token

match_id: string                           # string, REQUIRED, match identifier
game_type: string                          # string, REQUIRED, game type
game_result: object                        # object, REQUIRED, complete game result

# game_result object contains:
game_result.status: "WIN" | "DRAW" | "TECHNICAL_LOSS"  # string, REQUIRED, match outcome
game_result.winner_player_id: string | null            # string, REQUIRED if WIN, winner's ID
game_result.drawn_number: integer                      # integer, REQUIRED, the drawn number (1-10)
game_result.number_parity: "even" | "odd"              # string, REQUIRED, parity of drawn number
game_result.choices: object                            # object, REQUIRED, both players' choices
game_result.reason: string                             # string, REQUIRED, explanation text

# choices object contains player_id → choice mapping:
game_result.choices.<player_id>: "even" | "odd"        # string, REQUIRED for each player

# Optional fields
# (none defined)
```

#### Example Request

```json
{
  "jsonrpc": "2.0",
  "method": "notify_match_result",
  "params": {
    "protocol": "league.v2",
    "message_type": "GAME_OVER",
    "sender": "referee:REF01",
    "timestamp": "2025-01-19T10:01:15Z",
    "conversation_id": "conv-r1m1-001",
    "auth_token": "tok-ref-01-xyz789",
    "match_id": "R1M1",
    "game_type": "even_odd",
    "game_result": {
      "status": "WIN",
      "winner_player_id": "P01",
      "drawn_number": 8,
      "number_parity": "even",
      "choices": {
        "P01": "even",
        "P02": "odd"
      },
      "reason": "Number 8 is even. P01 chose 'even' correctly. P01 wins."
    }
  },
  "id": "req-009"
}
```

#### Response Payload Schema

```yaml
# Success response (in result object)
status: "ACKNOWLEDGED"               # string, REQUIRED
player_id: string                    # string, REQUIRED, acknowledging player's ID
match_id: string                     # string, REQUIRED, match identifier

# Additional fields
protocol: "league.v2"                # string, REQUIRED
message_type: "GAME_OVER_ACK"        # string, REQUIRED
timestamp: string                    # string, REQUIRED, ISO 8601 UTC
```

#### Example Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "GAME_OVER_ACK",
    "timestamp": "2025-01-19T10:01:16Z",
    "status": "ACKNOWLEDGED",
    "player_id": "P01",
    "match_id": "R1M1"
  },
  "id": "req-009"
}
```

#### Error Cases

| Error Code | Message | Cause |
|------------|---------|-------|
| -32602 | Invalid params | Missing required fields |
| 4001 | Invalid auth token | Referee's auth_token invalid |

#### Side Effects

**On Success (Player side):**
- Player updates internal match history
- Player updates statistics (wins, losses, draws)
- Player stores match result for strategy learning (optional)
- Player persists history to `SHARED/data/players/<player_id>/history.json`

**On Success (Referee side):**
- Referee waits for acknowledgments from both players
- Referee proceeds to report result to League Manager

---

## 5. Result and Status Messages

### 5.1 MATCH_RESULT_REPORT

**Direction:** Referee → League Manager
**JSON-RPC Method:** `report_match_result`
**Trigger:** After match completes and GAME_OVER sent to both players
**Timeout:** 10 seconds

#### Request Payload Schema

```yaml
# Required fields
protocol: "league.v2"                      # string, REQUIRED
message_type: "MATCH_RESULT_REPORT"        # string, REQUIRED
sender: string                             # string, REQUIRED, referee identifier
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
conversation_id: string                    # string, REQUIRED, e.g., "conv-r1m1-report"
auth_token: string                         # string, REQUIRED, referee's auth token

league_id: string                          # string, REQUIRED, league identifier
round_id: integer                          # integer, REQUIRED, round number
match_id: string                           # string, REQUIRED, match identifier
game_type: string                          # string, REQUIRED, game type
result: object                             # object, REQUIRED, match result details

# result object contains:
result.winner: string | null               # string, REQUIRED, winner's player_id or null for draw
result.score: object                       # object, REQUIRED, points awarded to each player
result.details: object                     # object, REQUIRED, additional match details

# score object contains player_id → points mapping:
result.score.<player_id>: integer          # integer, REQUIRED for each player (e.g., 3 for win, 0 for loss)

# details object contains:
result.details.drawn_number: integer       # integer, REQUIRED, the drawn number
result.details.choices: object             # object, REQUIRED, player choices
result.details.status: string              # string, REQUIRED, match outcome (WIN, DRAW, TECHNICAL_LOSS)

# choices object contains player_id → choice mapping:
result.details.choices.<player_id>: "even" | "odd"  # string, REQUIRED for each player

# Optional fields
# (none defined)
```

#### Example Request

```json
{
  "jsonrpc": "2.0",
  "method": "report_match_result",
  "params": {
    "protocol": "league.v2",
    "message_type": "MATCH_RESULT_REPORT",
    "sender": "referee:REF01",
    "timestamp": "2025-01-19T10:01:20Z",
    "conversation_id": "conv-r1m1-report",
    "auth_token": "tok-ref-01-xyz789",
    "league_id": "league_2025_even_odd",
    "round_id": 1,
    "match_id": "R1M1",
    "game_type": "even_odd",
    "result": {
      "winner": "P01",
      "score": {
        "P01": 3,
        "P02": 0
      },
      "details": {
        "drawn_number": 8,
        "choices": {
          "P01": "even",
          "P02": "odd"
        },
        "status": "WIN"
      }
    }
  },
  "id": "req-010"
}
```

#### Response Payload Schema

```yaml
# Success response (in result object)
status: "ACCEPTED"                   # string, REQUIRED
match_id: string                     # string, REQUIRED, match identifier
round_id: integer                    # integer, REQUIRED, round number

# Additional fields
protocol: "league.v2"                # string, REQUIRED
message_type: "MATCH_RESULT_ACK"     # string, REQUIRED
timestamp: string                    # string, REQUIRED, ISO 8601 UTC
```

#### Example Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "MATCH_RESULT_ACK",
    "timestamp": "2025-01-19T10:01:21Z",
    "status": "ACCEPTED",
    "match_id": "R1M1",
    "round_id": 1
  },
  "id": "req-010"
}
```

#### Error Cases

| Error Code | Message | Cause |
|------------|---------|-------|
| -32602 | Invalid params | Missing required fields |
| 5001 | Invalid auth token | Referee's auth_token invalid |
| 5002 | Match not found | Match ID unknown or not assigned to this referee |
| 5003 | Duplicate report | Match result already reported |

#### Example Error Response

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 5003,
    "message": "Duplicate report",
    "data": {
      "match_id": "R1M1",
      "previous_report_time": "2025-01-19T10:01:20Z"
    }
  },
  "id": "req-010"
}
```

#### Side Effects

**On Success (League Manager side):**
- League Manager updates standings table
- League Manager increments wins/losses/draws counts for players
- League Manager awards points (3 for win, 1 for draw, 0 for loss)
- League Manager persists updated standings to `SHARED/data/leagues/<league_id>/standings.json`
- League Manager checks if all matches in round complete
- If round complete, League Manager sends LEAGUE_STANDINGS_UPDATE and ROUND_COMPLETED

**On Success (Referee side):**
- Referee marks match as reported
- Referee persists match data to `SHARED/data/matches/<league_id>/<match_id>.json`
- Referee becomes available for next match assignment

---

## 6. Error Messages

### 6.1 LEAGUE_ERROR

**Direction:** League Manager → Player or Referee
**JSON-RPC Method:** N/A (sent as error response or notification)
**Trigger:** When league-level error occurs (invalid token, registration failure, etc.)
**Timeout:** N/A (one-way notification or error response)

#### Payload Schema

```yaml
# Required fields
protocol: "league.v2"                      # string, REQUIRED
message_type: "LEAGUE_ERROR"               # string, REQUIRED
sender: "league_manager"                   # string, REQUIRED
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
conversation_id: string                    # string, REQUIRED

error_code: string                         # string, REQUIRED, error code (e.g., "E012")
error_description: string                  # string, REQUIRED, error type (e.g., "AUTH_TOKEN_INVALID")
context: object                            # object, REQUIRED, additional error details

# context object (varies by error type)
# For AUTH_TOKEN_INVALID:
context.provided_token: string             # string, OPTIONAL, the invalid token
context.action: string                     # string, REQUIRED, action that failed
context.player_id: string                  # string, OPTIONAL, affected player

# Optional fields
# (varies by error type)
```

#### Example (as JSON-RPC error response)

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 12,
    "message": "AUTH_TOKEN_INVALID",
    "data": {
      "protocol": "league.v2",
      "message_type": "LEAGUE_ERROR",
      "sender": "league_manager",
      "timestamp": "2025-01-19T10:02:00Z",
      "conversation_id": "conv-error-001",
      "error_code": "E012",
      "error_description": "AUTH_TOKEN_INVALID",
      "context": {
        "provided_token": "invalid-token-xyz",
        "action": "LEAGUE_QUERY",
        "player_id": "P01"
      }
    }
  },
  "id": "req-011"
}
```

#### Common Error Codes

| Error Code | Description | Typical Context |
|------------|-------------|-----------------|
| E001 | INVALID_PROTOCOL_VERSION | Protocol version mismatch |
| E002 | MISSING_REQUIRED_FIELD | Required field missing from payload |
| E003 | INVALID_FIELD_TYPE | Field has wrong type |
| E012 | AUTH_TOKEN_INVALID | Authentication token invalid or expired |
| E013 | AUTH_TOKEN_MISSING | Authentication token not provided |
| E020 | LEAGUE_FULL | Maximum participants reached |
| E021 | DUPLICATE_NAME | Display name already taken |
| E030 | LEAGUE_NOT_STARTED | Action not allowed before league starts |
| E031 | LEAGUE_ALREADY_COMPLETE | Action not allowed after league ends |

#### Side Effects

**On Recipient:**
- Recipient logs error
- Recipient may retry operation (if retryable error)
- Recipient may alert user or take corrective action

---

### 6.2 GAME_ERROR

**Direction:** Referee → Player
**JSON-RPC Method:** `notify_game_error`
**Trigger:** When match-level error occurs (timeout, invalid move, player disconnect)
**Timeout:** 10 seconds

#### Request Payload Schema

```yaml
# Required fields
protocol: "league.v2"                      # string, REQUIRED
message_type: "GAME_ERROR"                 # string, REQUIRED
sender: string                             # string, REQUIRED, referee identifier
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
conversation_id: string                    # string, REQUIRED
auth_token: string                         # string, REQUIRED, referee's auth token

match_id: string                           # string, REQUIRED, match identifier
error_code: string                         # string, REQUIRED, error code (e.g., "E001")
error_description: string                  # string, REQUIRED, error type (e.g., "TIMEOUT_ERROR")
affected_player: string                    # string, REQUIRED, player who caused error
action_required: string                    # string, REQUIRED, what action timed out or failed
retry_count: integer                       # integer, REQUIRED, current retry attempt
max_retries: integer                       # integer, REQUIRED, maximum retries allowed
consequence: string                        # string, REQUIRED, description of consequence

# Optional fields
# (none defined)
```

#### Example Request

```json
{
  "jsonrpc": "2.0",
  "method": "notify_game_error",
  "params": {
    "protocol": "league.v2",
    "message_type": "GAME_ERROR",
    "sender": "referee:REF01",
    "timestamp": "2025-01-19T10:01:36Z",
    "conversation_id": "conv-r1m1-001",
    "auth_token": "tok-ref-01-xyz789",
    "match_id": "R1M1",
    "error_code": "E001",
    "error_description": "TIMEOUT_ERROR",
    "affected_player": "P02",
    "action_required": "CHOOSE_PARITY_RESPONSE",
    "retry_count": 1,
    "max_retries": 3,
    "consequence": "If no response after 3 retries, technical loss will be awarded"
  },
  "id": "req-012"
}
```

#### Response Payload Schema

```yaml
# Success response (in result object)
status: "ACKNOWLEDGED"               # string, REQUIRED
player_id: string                    # string, REQUIRED, acknowledging player's ID
match_id: string                     # string, REQUIRED, match identifier

# Additional fields
protocol: "league.v2"                # string, REQUIRED
message_type: "GAME_ERROR_ACK"       # string, REQUIRED
timestamp: string                    # string, REQUIRED, ISO 8601 UTC
```

#### Example Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "GAME_ERROR_ACK",
    "timestamp": "2025-01-19T10:01:37Z",
    "status": "ACKNOWLEDGED",
    "player_id": "P02",
    "match_id": "R1M1"
  },
  "id": "req-012"
}
```

#### Common Error Codes

| Error Code | Description | Consequence |
|------------|-------------|-------------|
| E001 | TIMEOUT_ERROR | Retry or technical loss |
| E002 | INVALID_MOVE | Move rejected, retry requested |
| E003 | PLAYER_DISCONNECT | Technical loss if doesn't reconnect |
| E004 | INVALID_STATE | Match in wrong state for action |

#### Side Effects

**On Recipient (Player):**
- Player logs error
- Player may retry action if within retry limit
- Player prepares for possible technical loss

**On Sender (Referee):**
- Referee tracks retry count
- After max_retries exhausted, referee awards technical loss
- Referee sends GAME_OVER with TECHNICAL_LOSS status
- Referee reports result to League Manager

---

## 7. Query Messages

### 7.1 LEAGUE_QUERY

**Direction:** Player → League Manager
**JSON-RPC Method:** `league_query`
**Trigger:** Player wants to query current standings or league status
**Timeout:** 10 seconds

#### Request Payload Schema

```yaml
# Required fields
protocol: "league.v2"                      # string, REQUIRED
message_type: "LEAGUE_QUERY"               # string, REQUIRED
sender: string                             # string, REQUIRED, player identifier
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
conversation_id: string                    # string, REQUIRED
auth_token: string                         # string, REQUIRED, player's auth token

league_id: string                          # string, REQUIRED, league identifier
query_type: "GET_STANDINGS" | "GET_STATUS" # string, REQUIRED, type of query

# Optional fields
# (none defined)
```

#### Example Request

```json
{
  "jsonrpc": "2.0",
  "method": "league_query",
  "params": {
    "protocol": "league.v2",
    "message_type": "LEAGUE_QUERY",
    "sender": "player:P01",
    "timestamp": "2025-01-19T10:03:00Z",
    "conversation_id": "conv-query-001",
    "auth_token": "tok-p01-abc123",
    "league_id": "league_2025_even_odd",
    "query_type": "GET_STANDINGS"
  },
  "id": "req-013"
}
```

#### Response Payload Schema (for GET_STANDINGS)

```yaml
# Success response (in result object)
protocol: "league.v2"                      # string, REQUIRED
message_type: "LEAGUE_QUERY_RESPONSE"      # string, REQUIRED
timestamp: string                          # string, REQUIRED, ISO 8601 UTC
query_type: "GET_STANDINGS"                # string, REQUIRED, echoes request

standings: array[object]                   # array, REQUIRED, current standings
current_round: integer                     # integer, REQUIRED, current round number

# Each standing object (same as LEAGUE_STANDINGS_UPDATE):
standings[].rank: integer                  # integer, REQUIRED
standings[].player_id: string              # string, REQUIRED
standings[].display_name: string           # string, REQUIRED
standings[].played: integer                # integer, REQUIRED
standings[].wins: integer                  # integer, REQUIRED
standings[].draws: integer                 # integer, REQUIRED
standings[].losses: integer                # integer, REQUIRED
standings[].points: integer                # integer, REQUIRED

# Optional fields
# (none defined)
```

#### Example Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "protocol": "league.v2",
    "message_type": "LEAGUE_QUERY_RESPONSE",
    "timestamp": "2025-01-19T10:03:01Z",
    "query_type": "GET_STANDINGS",
    "current_round": 1,
    "standings": [
      {
        "rank": 1,
        "player_id": "P01",
        "display_name": "AlphaPlayer",
        "played": 1,
        "wins": 1,
        "draws": 0,
        "losses": 0,
        "points": 3
      },
      {
        "rank": 2,
        "player_id": "P03",
        "display_name": "GammaPlayer",
        "played": 1,
        "wins": 1,
        "draws": 0,
        "losses": 0,
        "points": 3
      }
    ]
  },
  "id": "req-013"
}
```

#### Error Cases

| Error Code | Message | Cause |
|------------|---------|-------|
| -32602 | Invalid params | Missing required fields |
| 6001 | Invalid auth token | Player's auth_token invalid |
| 6002 | Invalid query type | query_type not supported |
| 6003 | League not found | league_id unknown |

#### Side Effects

**On Success:**
- No state change (read-only query)
- Player receives current standings data

---

## 8. Coverage Checklist

### 8.1 All Messages Documented

✅ **Registration Messages (2)**
- REFEREE_REGISTER_REQUEST / REFEREE_REGISTER_RESPONSE
- LEAGUE_REGISTER_REQUEST / LEAGUE_REGISTER_RESPONSE

✅ **League Coordination Messages (4)**
- ROUND_ANNOUNCEMENT
- LEAGUE_STANDINGS_UPDATE
- ROUND_COMPLETED
- LEAGUE_COMPLETED

✅ **Match Execution Messages (3)**
- GAME_INVITATION → GAME_JOIN_ACK
- CHOOSE_PARITY_CALL → CHOOSE_PARITY_RESPONSE
- GAME_OVER

✅ **Result Messages (1)**
- MATCH_RESULT_REPORT

✅ **Error Messages (2)**
- LEAGUE_ERROR
- GAME_ERROR

✅ **Query Messages (1)**
- LEAGUE_QUERY

**Total: 14 message types fully documented**

### 8.2 Required Elements for Each Message

For each message, the following elements are documented:

✅ Message name
✅ Sender → Receiver direction
✅ Trigger / when sent
✅ Timeout requirement (where applicable)
✅ Request payload schema (required + optional fields with types)
✅ Response payload schema (required + optional fields with types)
✅ Error cases + error response format (JSON-RPC 2.0)
✅ Side effects / state updates
✅ Example requests and responses in JSON format

### 8.3 Timeout Summary

| Message Type | Timeout | Specified in |
|--------------|---------|--------------|
| GAME_JOIN_ACK | 5 seconds | Chapter 6, Section 3.2 |
| CHOOSE_PARITY_RESPONSE | 30 seconds | Chapter 6, Section 3.2 |
| All other responses | 10 seconds | Chapter 6, Section 3.2 |

### 8.4 JSON-RPC 2.0 Compliance

All messages documented with:
✅ Proper JSON-RPC 2.0 envelope structure
✅ Request format with `jsonrpc`, `method`, `params`, `id`
✅ Success response format with `jsonrpc`, `result`, `id`
✅ Error response format with `jsonrpc`, `error`, `id`
✅ Standard error codes (-32xxx for JSON-RPC, custom for application)

### 8.5 Protocol Version Compliance

All messages include:
✅ `protocol: "league.v2"` field
✅ Consistent field naming across messages
✅ ISO 8601 UTC timestamps
✅ Unique conversation_id for tracing

---

## 9. Implementation Notes

### 9.1 Message Flow Summary

```
┌──────────────────┐
│ League Manager   │
│   (Port 8000)    │
└────────┬─────────┘
         │
         ├─────► REFEREE_REGISTER_REQUEST/RESPONSE ◄──┐
         │                                             │
         ├─────► LEAGUE_REGISTER_REQUEST/RESPONSE ◄───┤
         │                                             │
         ├─────► ROUND_ANNOUNCEMENT ────────────────► │
         │                                             │
         ├─────► LEAGUE_STANDINGS_UPDATE ──────────► │
         │                                             │
         ├─────► ROUND_COMPLETED ──────────────────► │
         │                                             │
         └─────► LEAGUE_COMPLETED ─────────────────► │
                                                       │
┌──────────────────┐                                  │
│ Referee REF01    │◄─── MATCH_RESULT_REPORT ─────────┘
│   (Port 8001)    │
└────────┬─────────┘
         │
         ├─────► GAME_INVITATION ────────────────────┐
         │                                            │
         │◄────── GAME_JOIN_ACK ◄─────────────────────┤
         │                                            │
         ├─────► CHOOSE_PARITY_CALL ─────────────────┤
         │                                            │
         │◄────── CHOOSE_PARITY_RESPONSE ◄────────────┤
         │                                            │
         └─────► GAME_OVER ──────────────────────────►│
                                                       │
                                         ┌─────────────▼────────────┐
                                         │ Player P01 (Port 8101)   │
                                         └──────────────────────────┘
```

### 9.2 State Transitions

**League Manager States:**
1. WAITING_FOR_REGISTRATIONS
2. CREATING_SCHEDULE
3. RUNNING_LEAGUE (per round)
4. LEAGUE_COMPLETED

**Referee Match States:**
1. WAITING_FOR_PLAYERS
2. COLLECTING_CHOICES
3. DRAWING_NUMBER
4. FINISHED

**Player States:**
1. UNREGISTERED
2. REGISTERED
3. WAITING_FOR_ROUND
4. IN_MATCH
5. WAITING_FOR_RESULT

### 9.3 Authentication Flow

1. Agent sends registration request (no auth_token)
2. League Manager responds with auth_token
3. All subsequent requests include auth_token
4. League Manager validates auth_token on each request
5. Invalid token → LEAGUE_ERROR with error_code E012

### 9.4 Error Handling Strategy

**Retryable Errors:**
- Network timeouts
- Temporary unavailability
- Rate limiting

**Non-Retryable Errors:**
- Invalid auth token (must re-register)
- Invalid field types (must fix payload)
- Duplicate registration (must use different name)

**Technical Loss Conditions:**
- GAME_JOIN_ACK timeout after max_retries
- CHOOSE_PARITY_RESPONSE timeout after max_retries
- Player disconnect during match

### 9.5 Testing Recommendations

**Unit Tests:**
- Validate schema compliance for each message type
- Test JSON-RPC envelope wrapping/unwrapping
- Test timeout enforcement
- Test error response generation

**Integration Tests:**
- Complete registration flow (referee + players)
- Complete match flow (invitation → choice → result)
- Complete round flow (announcement → matches → standings)
- Complete league flow (registration → rounds → completion)

**Edge Case Tests:**
- Timeout scenarios (5s, 30s, 10s)
- Invalid auth token scenarios
- Duplicate registration attempts
- Malformed payload handling
- Network failure scenarios

---

**Document Status:** Complete Message Contracts Specification
**Coverage:** 14 message types fully documented
**Ready For:** Implementation and testing
