"""
Referee - Game Logic Module

Implements even/odd game rules and winner determination.
"""

import random
import sys
from pathlib import Path
from typing import Dict, Any

# Add SHARED to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

from league_sdk.config_loader import ConfigLoader


def draw_random_number(min_value: int = None, max_value: int = None) -> int:
    """
    Draw a random number for the game.

    Args:
        min_value: Minimum value (inclusive), defaults from config or 1
        max_value: Maximum value (inclusive), defaults from config or 10

    Returns:
        Random integer between min_value and max_value
    """
    # Load from config if not provided
    if min_value is None or max_value is None:
        config_min, config_max = ConfigLoader.get_game_number_range()
        min_value = min_value or config_min
        max_value = max_value or config_max

    return random.randint(min_value, max_value)


def determine_winner(drawn_number: int, player_A_choice: str, player_B_choice: str,
                     player_A_id: str, player_B_id: str) -> Dict[str, Any]:
    """
    Determine the winner based on game rules.

    Game Rules:
    - If drawn_number is EVEN and player chose "even" -> player wins
    - If drawn_number is ODD and player chose "odd" -> player wins
    - If both players chose the same parity and it matches -> DRAW
    - Otherwise -> opponent wins

    Args:
        drawn_number: The randomly drawn number
        player_A_choice: Player A's parity choice ("even" or "odd")
        player_B_choice: Player B's parity choice ("even" or "odd")
        player_A_id: Player A's identifier
        player_B_id: Player B's identifier

    Returns:
        Result dictionary containing:
        - winner_id: Player ID of winner or None for draw
        - loser_id: Player ID of loser or None for draw
        - is_draw: Boolean indicating draw
        - drawn_number: The number that was drawn
        - number_parity: "even" or "odd"
        - player_A_choice: Player A's choice
        - player_B_choice: Player B's choice
    """
    # Determine the parity of the drawn number
    number_parity = "even" if drawn_number % 2 == 0 else "odd"

    # Normalize choices to lowercase
    player_A_choice = player_A_choice.lower()
    player_B_choice = player_B_choice.lower()

    # Check if Player A's choice matches the number parity
    player_A_wins = (player_A_choice == number_parity)

    # Check if Player B's choice matches the number parity
    player_B_wins = (player_B_choice == number_parity)

    # Determine outcome
    if player_A_wins and player_B_wins:
        # Both chose correctly -> DRAW
        return {
            "winner_id": None,
            "loser_id": None,
            "is_draw": True,
            "drawn_number": drawn_number,
            "number_parity": number_parity,
            "player_A_choice": player_A_choice,
            "player_B_choice": player_B_choice
        }
    elif player_A_wins:
        # Player A wins
        return {
            "winner_id": player_A_id,
            "loser_id": player_B_id,
            "is_draw": False,
            "drawn_number": drawn_number,
            "number_parity": number_parity,
            "player_A_choice": player_A_choice,
            "player_B_choice": player_B_choice
        }
    elif player_B_wins:
        # Player B wins
        return {
            "winner_id": player_B_id,
            "loser_id": player_A_id,
            "is_draw": False,
            "drawn_number": drawn_number,
            "number_parity": number_parity,
            "player_A_choice": player_A_choice,
            "player_B_choice": player_B_choice
        }
    else:
        # Neither chose correctly -> DRAW (both wrong)
        return {
            "winner_id": None,
            "loser_id": None,
            "is_draw": True,
            "drawn_number": drawn_number,
            "number_parity": number_parity,
            "player_A_choice": player_A_choice,
            "player_B_choice": player_B_choice
        }


def validate_parity_choice(choice: str) -> bool:
    """
    Validate that parity choice is valid.

    Args:
        choice: Parity choice string

    Returns:
        True if valid ("even" or "odd"), False otherwise
    """
    return choice.lower() in ["even", "odd"]
