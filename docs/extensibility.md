# Extensibility Guide - MCP Even/Odd League

**Document Purpose:** Guide for extending the system with new agents, strategies, and game types

**Course:** AI Agents with Model Context Protocol
**Document Version:** 1.0
**Last Updated:** 2025-01-20

---

## Table of Contents

1. [Extension Points Overview](#1-extension-points-overview)
2. [Adding a New Player Agent](#2-adding-a-new-player-agent)
3. [Implementing Custom Strategies](#3-implementing-custom-strategies)
4. [Supporting New Game Types](#4-supporting-new-game-types)
5. [LLM-Based Agents](#5-llm-based-agents)
6. [Advanced Extensions](#6-advanced-extensions)

---

## 1. Extension Points Overview

### 1.1 Design Philosophy

The system is designed with **extension in mind**:
- All components interact through **formal interfaces** (see `docs/architecture/interfaces.md`)
- Protocol-based communication enables **heterogeneous implementations**
- Clear separation of concerns allows **independent evolution**

### 1.2 Extension Categories

| Extension Type | Difficulty | Impact | Interface Changes Required |
|----------------|-----------|--------|----------------------------|
| New Player Agent | Easy | Low | None (implement PlayerInterface) |
| Custom Strategy | Easy | Low | None (plugin pattern) |
| New Game Type | Medium | Medium | Modify game_logic.py |
| LLM-Based Player | Medium | Medium | None (implement PlayerInterface) |
| Persistence Layer | Medium | Low | Implement repositories |
| New League Format | Hard | High | Extend LeagueManager |

---

## 2. Adding a New Player Agent

### 2.1 Overview

**Goal:** Add a 5th player (P05) to the league.

**Required Steps:**
1. Copy existing player directory
2. Update configuration
3. Implement strategy
4. Register with League Manager
5. Update tests

**Time Estimate:** 30-60 minutes

---

### 2.2 Step-by-Step Guide

#### Step 1: Create Player Directory Structure

```bash
# Copy existing player as template
cp -r src/mcp_even_odd_league/agents/player_P01 src/mcp_even_odd_league/agents/player_P05

# Verify structure
tree src/mcp_even_odd_league/agents/player_P05
```

**Expected Structure:**
```
player_P05/
├── __init__.py
├── main.py           # Flask server and Player class
├── handlers.py       # MCP message handlers
└── strategy.py       # Parity choice logic
```

#### Step 2: Update Player ID

**File:** `src/mcp_even_odd_league/agents/player_P05/main.py`

**Change:**
```python
# Line ~336: Update default player ID
player_id = sys.argv[1] if len(sys.argv) > 1 else "P05"  # Changed from P01
```

#### Step 3: Configure Port Assignment

**File:** `SHARED/data/config/system_config.json`

**Add:**
```json
{
  "network": {
    "player_ports": [8101, 8102, 8103, 8104, 8105]  // Added 8105
  }
}
```

**File:** `src/mcp_even_odd_league/agents/player_P05/main.py`

**Update port mapping:**
```python
# Line ~343
player_index = {
    "P01": 0,
    "P02": 1,
    "P03": 2,
    "P04": 3,
    "P05": 4   # Added
}.get(player_id, 0)
```

#### Step 4: Implement Strategy

**File:** `src/mcp_even_odd_league/agents/player_P05/strategy.py`

**Example: Adaptive Strategy**
```python
"""
Player P05 Strategy - Adaptive Counter-Strategy

Tracks opponent history and adapts parity choice.
"""

def choose_parity(player_id: str, match_context: dict) -> str:
    """
    Choose parity based on opponent history.

    Args:
        player_id: This player's ID
        match_context: Contains opponent_id, match_history

    Returns:
        "even" or "odd"
    """
    opponent_id = match_context.get("opponent_id")
    history = match_context.get("match_history", {})

    # Get opponent's past choices (from history)
    opponent_choices = history.get(opponent_id, {}).get("choices", [])

    if not opponent_choices:
        # No history: default to even
        return "even"

    # Count opponent's even/odd preferences
    even_count = sum(1 for c in opponent_choices if c == "even")
    odd_count = len(opponent_choices) - even_count

    # Predict opponent's next choice (assume they repeat majority)
    if even_count > odd_count:
        opponent_likely_choice = "even"
    else:
        opponent_likely_choice = "odd"

    # Choose opposite to increase conflict (better chance of sole winner)
    return "odd" if opponent_likely_choice == "even" else "even"
```

**Integrate into handlers:**
```python
# File: handlers.py
from mcp_even_odd_league.agents.player_P05 import strategy

def handle_parity_choose(player: Player, params: dict) -> dict:
    # ...existing code...

    # Build context
    match_context = {
        "opponent_id": player.current_match["opponent_id"],
        "match_history": player.history_repo.get_opponent_history()
    }

    # Use strategy module
    choice = strategy.choose_parity(player.player_id, match_context)

    # ...rest of implementation...
```

#### Step 5: Start the New Player

```bash
# Terminal window
python3 -m mcp_even_odd_league.agents.player_P05.main P05
```

**Expected Output:**
```
Player initialized: P05
Starting Player P05

=== Player Starting ===
Player ID: P05
Port: 8105
Endpoint: http://localhost:8105/mcp
=======================
```

#### Step 6: Register with League

The player is now ready to receive invitations. Update your test/orchestrator script to include P05 in the player list.

**Example:**
```python
# test_full_league.py
PLAYERS = ["P01", "P02", "P03", "P04", "P05"]
```

---

### 2.3 Testing the New Player

```bash
# Run unit tests
pytest tests/unit/test_game_logic.py -v

# Run integration test with P05
python3 test_match.py  # Modify to use P05 vs P01
```

---

### 2.4 Verification Checklist

- [ ] Player starts without errors
- [ ] Port 8105 is bound correctly (`lsof -ti:8105`)
- [ ] Player responds to `/mcp` endpoint (`curl -X POST http://localhost:8105/mcp`)
- [ ] Player receives and responds to game invitations
- [ ] Strategy logic executes correctly
- [ ] State transitions logged properly

---

## 3. Implementing Custom Strategies

### 3.1 Strategy Interface

**File:** `src/mcp_even_odd_league/agents/player_*/strategy.py`

**Required Function Signature:**
```python
def choose_parity(player_id: str, match_context: dict) -> str:
    """
    Make parity choice for a match.

    Args:
        player_id: This player's identifier
        match_context: {
            "opponent_id": str,
            "match_id": str,
            "round_id": int,
            "match_history": dict,  # Past results
            "standings": dict,      # Current standings (if available)
        }

    Returns:
        "even" or "odd" (lowercase)

    Raises:
        ValueError: If cannot make decision
    """
    pass
```

---

### 3.2 Example Strategies

#### 3.2.1 Always Even (Current Implementation)

```python
def choose_parity(player_id: str, match_context: dict) -> str:
    """Always choose even."""
    return "even"
```

**Use Case:** Baseline/deterministic strategy

---

#### 3.2.2 Always Odd

```python
def choose_parity(player_id: str, match_context: dict) -> str:
    """Always choose odd."""
    return "odd"
```

**Use Case:** Complementary to "always even"

---

#### 3.2.3 Random

```python
import random

def choose_parity(player_id: str, match_context: dict) -> str:
    """Randomly choose even or odd."""
    return random.choice(["even", "odd"])
```

**Use Case:** Unpredictable opponent

---

#### 3.2.4 Opponent Modeling

```python
def choose_parity(player_id: str, match_context: dict) -> str:
    """
    Model opponent and choose counter-strategy.

    Strategy: Track opponent's pattern and exploit it.
    """
    opponent_id = match_context.get("opponent_id")
    history = match_context.get("match_history", {})

    # Get opponent's past choices
    opponent_history = history.get(opponent_id, {})
    past_choices = opponent_history.get("choices", [])

    if len(past_choices) < 2:
        # Insufficient data: default to even
        return "even"

    # Check if opponent alternates
    if is_alternating(past_choices):
        # Predict next in sequence
        last_choice = past_choices[-1]
        return "odd" if last_choice == "even" else "even"

    # Check if opponent has bias
    even_count = sum(1 for c in past_choices if c == "even")
    if even_count / len(past_choices) > 0.6:
        # Opponent prefers even: choose odd
        return "odd"
    elif even_count / len(past_choices) < 0.4:
        # Opponent prefers odd: choose even
        return "even"

    # No clear pattern: random
    return random.choice(["even", "odd"])

def is_alternating(choices: list) -> bool:
    """Check if choices alternate even/odd."""
    if len(choices) < 2:
        return False
    for i in range(len(choices) - 1):
        if choices[i] == choices[i + 1]:
            return False
    return True
```

**Use Case:** Adaptive strategy against non-random opponents

---

#### 3.2.5 Standings-Aware

```python
def choose_parity(player_id: str, match_context: dict) -> str:
    """
    Choose based on current standings.

    Strategy: If winning, play safe. If losing, take risks.
    """
    standings = match_context.get("standings", {})
    opponent_id = match_context.get("opponent_id")

    # Get ranks
    my_rank = standings.get(player_id, {}).get("rank", 999)
    opponent_rank = standings.get(opponent_id, {}).get("rank", 999)

    if my_rank < opponent_rank:
        # Winning: play conservatively (even)
        return "even"
    else:
        # Losing: take risk (random)
        return random.choice(["even", "odd"])
```

**Use Case:** Tournament-aware play

---

### 3.3 Strategy Testing

**File:** `tests/unit/test_strategy.py`

```python
import pytest
from mcp_even_odd_league.agents.player_P05 import strategy

class TestStrategy:
    def test_choose_parity_returns_valid_value(self):
        """Strategy must return 'even' or 'odd'."""
        context = {"opponent_id": "P01", "match_history": {}}
        result = strategy.choose_parity("P05", context)
        assert result in ["even", "odd"]

    def test_strategy_with_empty_history(self):
        """Strategy handles no history gracefully."""
        context = {"opponent_id": "P01", "match_history": {}}
        result = strategy.choose_parity("P05", context)
        assert isinstance(result, str)

    def test_strategy_with_opponent_history(self):
        """Strategy uses opponent history."""
        context = {
            "opponent_id": "P01",
            "match_history": {
                "P01": {"choices": ["even", "even", "even"]}
            }
        }
        result = strategy.choose_parity("P05", context)
        # Should choose odd to counter even-biased opponent
        assert result == "odd"
```

---

## 4. Supporting New Game Types

### 4.1 Overview

**Current Game:** Even/Odd (binary choice)

**Extension Goal:** Support other games (Rock-Paper-Scissors, Number Guessing, etc.)

**Architecture Impact:** Modify `game_logic.py`, update message contracts

---

### 4.2 Game Logic Extension Point

**File:** `src/mcp_even_odd_league/agents/referee_REF01/game_logic.py`

**Current Interface:**
```python
def determine_winner(
    drawn_number: int,
    player_A_choice: str,
    player_B_choice: str,
    player_A_id: str,
    player_B_id: str
) -> dict:
    """Determine winner based on parity."""
    pass
```

**Required Changes for New Game:**
1. Update function signature to accept new game parameters
2. Implement new game rules
3. Update tests

---

### 4.3 Example: Rock-Paper-Scissors

#### Step 1: Update Game Logic

**File:** `game_logic.py`

```python
def determine_winner_rps(
    player_A_choice: str,
    player_B_choice: str,
    player_A_id: str,
    player_B_id: str
) -> dict:
    """
    Determine winner for Rock-Paper-Scissors.

    Args:
        player_A_choice: "rock", "paper", or "scissors"
        player_B_choice: "rock", "paper", or "scissors"
        player_A_id: Player A identifier
        player_B_id: Player B identifier

    Returns:
        {
            "winner_id": str or None,
            "is_draw": bool,
            "reason": str,
            "choices": {player_A_id: str, player_B_id: str}
        }
    """
    choices = {player_A_id: player_A_choice, player_B_id: player_B_choice}

    # Normalize choices
    player_A_choice = player_A_choice.lower()
    player_B_choice = player_B_choice.lower()

    # Check for draw
    if player_A_choice == player_B_choice:
        return {
            "winner_id": None,
            "is_draw": True,
            "reason": f"Both chose {player_A_choice}",
            "choices": choices
        }

    # Determine winner
    wins = {
        ("rock", "scissors"): True,
        ("scissors", "paper"): True,
        ("paper", "rock"): True,
    }

    if wins.get((player_A_choice, player_B_choice)):
        winner_id = player_A_id
        reason = f"{player_A_choice} beats {player_B_choice}"
    else:
        winner_id = player_B_id
        reason = f"{player_B_choice} beats {player_A_choice}"

    return {
        "winner_id": winner_id,
        "is_draw": False,
        "reason": reason,
        "choices": choices
    }
```

#### Step 2: Update MCP Messages

**File:** `docs/architecture/mcp_message_contracts.md`

**Add new message type:**
```json
{
  "jsonrpc": "2.0",
  "method": "parity_choose",
  "params": {
    "protocol": "league.v2",
    "message_type": "CHOOSE_RPS_CALL",
    "match_id": "MATCH_001",
    "valid_choices": ["rock", "paper", "scissors"]
  }
}
```

#### Step 3: Update Strategy Interface

**File:** `strategy.py`

```python
def choose_rps(player_id: str, match_context: dict) -> str:
    """
    Choose rock, paper, or scissors.

    Returns:
        "rock", "paper", or "scissors"
    """
    import random
    return random.choice(["rock", "paper", "scissors"])
```

#### Step 4: Update Configuration

**File:** `SHARED/data/config/league_config.json`

```json
{
  "game_type": "rock_paper_scissors",  // Changed from "even_odd"
  "game_rules": {
    "choices": ["rock", "paper", "scissors"],
    "win_conditions": {
      "rock": "scissors",
      "scissors": "paper",
      "paper": "rock"
    }
  }
}
```

---

### 4.4 Backward Compatibility Strategy

To support multiple game types simultaneously:

```python
# game_logic.py
def determine_winner(game_type: str, **kwargs) -> dict:
    """Dispatcher for different game types."""
    if game_type == "even_odd":
        return determine_winner_even_odd(**kwargs)
    elif game_type == "rock_paper_scissors":
        return determine_winner_rps(**kwargs)
    else:
        raise ValueError(f"Unknown game type: {game_type}")
```

---

## 5. LLM-Based Agents

### 5.1 Overview

**Goal:** Replace deterministic strategy with LLM-powered decision-making

**Architecture:** Player remains same, strategy calls LLM API

**Models Supported:** GPT-4, Claude, Gemini, local LLMs

---

### 5.2 Implementation

#### Step 1: Install LLM SDK

```bash
pip install openai  # For GPT-4
# or
pip install anthropic  # For Claude
```

#### Step 2: Implement LLM Strategy

**File:** `src/mcp_even_odd_league/agents/player_P05/strategy.py`

```python
"""
LLM-Based Strategy for Even/Odd Game

Uses GPT-4 to make strategic parity choices.
"""

import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def choose_parity(player_id: str, match_context: dict) -> str:
    """
    Use GPT-4 to choose parity.

    Args:
        player_id: This player's ID
        match_context: Match and history information

    Returns:
        "even" or "odd"
    """
    opponent_id = match_context.get("opponent_id")
    history = match_context.get("match_history", {})

    # Build prompt
    prompt = build_strategy_prompt(player_id, opponent_id, history)

    # Call GPT-4
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a strategic game player."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=10,
        temperature=0.7
    )

    # Extract choice
    choice_text = response.choices[0].message.content.strip().lower()

    # Validate and return
    if "even" in choice_text:
        return "even"
    elif "odd" in choice_text:
        return "odd"
    else:
        # Fallback to even if LLM response is unclear
        return "even"

def build_strategy_prompt(player_id: str, opponent_id: str, history: dict) -> str:
    """Build LLM prompt from match context."""
    prompt = f"""You are player {player_id} in an Even/Odd guessing game.

Game Rules:
- A referee draws a random number from 1-10
- You and your opponent ({opponent_id}) each choose "even" or "odd"
- If the number's parity matches your choice and not your opponent's, you win
- If both match or both miss, it's a draw

Opponent History:
{json.dumps(history.get(opponent_id, {}), indent=2)}

Question: Should you choose "even" or "odd"?

Think strategically. Consider:
1. Does the opponent have a pattern?
2. Is there a bias toward even or odd?
3. Should you exploit or randomize?

Answer with just one word: "even" or "odd"
"""
    return prompt
```

#### Step 3: Set API Key

```bash
export OPENAI_API_KEY="sk-..."
```

#### Step 4: Test LLM Strategy

```python
# test_llm_strategy.py
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

from mcp_even_odd_league.agents.player_P05 import strategy

context = {
    "opponent_id": "P01",
    "match_history": {
        "P01": {"choices": ["even", "even", "odd", "even"]}
    }
}

choice = strategy.choose_parity("P05", context)
print(f"LLM chose: {choice}")
```

---

### 5.3 Advanced: Multi-Agent LLM Debate

```python
def choose_parity_with_debate(player_id: str, match_context: dict) -> str:
    """
    Use multiple LLM agents to debate strategy.

    Process:
    1. Agent A proposes "even" with reasoning
    2. Agent B proposes "odd" with reasoning
    3. Judge agent picks winner based on arguments
    """
    # Agent A: Argues for "even"
    even_argument = get_llm_response(
        "Argue why choosing 'even' is the best strategy",
        match_context
    )

    # Agent B: Argues for "odd"
    odd_argument = get_llm_response(
        "Argue why choosing 'odd' is the best strategy",
        match_context
    )

    # Judge: Picks winner
    judge_prompt = f"""Two agents debated the best strategy:

Agent Even: {even_argument}

Agent Odd: {odd_argument}

Which argument is more convincing? Answer "even" or "odd".
"""

    final_choice = get_llm_response(judge_prompt, match_context)

    return "even" if "even" in final_choice.lower() else "odd"
```

---

## 6. Advanced Extensions

### 6.1 Persistence Layer

**Goal:** Add database-backed persistence for standings and history

**Implementation Guide:**

#### Step 1: Choose Database

Options:
- **SQLite:** Simple, file-based (recommended for prototype)
- **PostgreSQL:** Production-ready RDBMS
- **MongoDB:** Document store for JSON data

#### Step 2: Implement Repository Interface

**File:** `src/mcp_even_odd_league/league_sdk/repositories.py`

```python
import sqlite3
from typing import Dict, List, Optional

class StandingsRepository:
    """
    Persistent storage for league standings.

    Current: In-memory (stub)
    TODO: Implement with SQLite/PostgreSQL
    """

    def __init__(self, league_id: str, db_path: str = "data/league.db"):
        self.league_id = league_id
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS standings (
                league_id TEXT,
                player_id TEXT,
                wins INTEGER,
                losses INTEGER,
                draws INTEGER,
                points INTEGER,
                matches_played INTEGER,
                PRIMARY KEY (league_id, player_id)
            )
        """)
        conn.commit()
        conn.close()

    def save_standings(self, standings: Dict[str, dict]):
        """Save current standings to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for player_id, stats in standings.items():
            cursor.execute("""
                INSERT OR REPLACE INTO standings VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                self.league_id,
                player_id,
                stats["wins"],
                stats["losses"],
                stats["draws"],
                stats["points"],
                stats["matches_played"]
            ))

        conn.commit()
        conn.close()

    def load_standings(self) -> Dict[str, dict]:
        """Load standings from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT player_id, wins, losses, draws, points, matches_played
            FROM standings
            WHERE league_id = ?
        """, (self.league_id,))

        standings = {}
        for row in cursor.fetchall():
            player_id, wins, losses, draws, points, matches_played = row
            standings[player_id] = {
                "wins": wins,
                "losses": losses,
                "draws": draws,
                "points": points,
                "matches_played": matches_played
            }

        conn.close()
        return standings
```

#### Step 3: Integrate into League Manager

**File:** `src/mcp_even_odd_league/agents/league_manager/main.py`

```python
# Replace in-memory standings
class LeagueManager:
    def __init__(self, league_id: str):
        # ...existing code...

        # Use persistent repository
        self.standings_repo = StandingsRepository(league_id, db_path="data/league.db")
        self.standings = self.standings_repo.load_standings()  # Load from DB

    def update_standings_from_match(self, match_result: dict):
        # ...existing update logic...

        # Persist to database
        self.standings_repo.save_standings(self.standings)
```

---

### 6.2 Multiple Concurrent Leagues

**Goal:** Run multiple leagues simultaneously

**Implementation:**
- Add league routing based on `league_id`
- Create league registry
- Isolate standings per league

---

### 6.3 Web Dashboard

**Goal:** Real-time web UI for league monitoring

**Technology Stack:**
- **Backend:** Flask (already used) + SocketIO
- **Frontend:** React or Vue.js
- **Real-Time:** WebSockets for live updates

**Features:**
- Live standings table
- Match-by-match results
- Player statistics
- Game replay

---

## 7. Conclusion

### 7.1 Extension Summary

This guide documented extension points for:
- ✓ Adding new players (easy, 30 min)
- ✓ Custom strategies (easy, 1-2 hours)
- ✓ New game types (medium, 4-6 hours)
- ✓ LLM-based agents (medium, 2-4 hours)
- ✓ Persistence layer (medium, 4-8 hours)

### 7.2 Architecture Benefits

The system's architecture enables extensions without breaking changes:
- **Interface stability:** PlayerInterface unchanged since v1.0
- **Protocol versioning:** `league.v2` supports backward compatibility
- **Separation of concerns:** Strategy, logic, communication are independent

### 7.3 Next Steps

To extend the system:
1. Read `docs/architecture/interfaces.md` for formal contracts
2. Study existing implementations in `src/mcp_even_odd_league/agents/`
3. Follow this guide's step-by-step instructions
4. Test thoroughly with unit and integration tests

---

**Document Version:** 1.0
**Author:** MCP League Team
**Course:** AI Agents with Model Context Protocol
**Last Updated:** 2025-01-20

**Related Documentation:**
- [Engineering Analysis](analysis.md) - Architecture tradeoffs
- [Interface Specifications](architecture/interfaces.md) - Formal contracts
- [State Machines](architecture/state_machines.md) - Agent behavior
- [MCP Messages](architecture/mcp_message_contracts.md) - Protocol spec
