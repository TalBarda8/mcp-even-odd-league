"""
Unit tests for game logic module.

Tests the core even/odd game rules without requiring Flask servers.
"""

import pytest
from mcp_even_odd_league.agents.referee_REF01 import game_logic


class TestDrawRandomNumber:
    """Tests for draw_random_number function."""

    def test_draw_number_in_range(self):
        """Test that drawn number is within specified range."""
        min_val, max_val = 1, 10
        number = game_logic.draw_random_number(min_val, max_val)
        assert min_val <= number <= max_val

    def test_draw_number_single_value(self):
        """Test drawing when min equals max."""
        number = game_logic.draw_random_number(5, 5)
        assert number == 5

    def test_draw_number_with_defaults(self):
        """Test that default range works (1-10)."""
        number = game_logic.draw_random_number()
        assert 1 <= number <= 10


class TestDetermineWinner:
    """Tests for determine_winner function."""

    def test_both_choose_even_even_number(self):
        """Test draw when both choose even and number is even."""
        result = game_logic.determine_winner(
            drawn_number=4,
            player_A_choice="even",
            player_B_choice="even",
            player_A_id="P01",
            player_B_id="P02"
        )
        assert result["is_draw"] is True
        assert result["winner_id"] is None
        assert result["loser_id"] is None
        assert result["drawn_number"] == 4
        assert result["number_parity"] == "even"

    def test_both_choose_odd_odd_number(self):
        """Test draw when both choose odd and number is odd."""
        result = game_logic.determine_winner(
            drawn_number=7,
            player_A_choice="odd",
            player_B_choice="odd",
            player_A_id="P01",
            player_B_id="P02"
        )
        assert result["is_draw"] is True
        assert result["winner_id"] is None
        assert result["drawn_number"] == 7
        assert result["number_parity"] == "odd"

    def test_player_a_wins_with_even(self):
        """Test Player A wins when choosing even and number is even."""
        result = game_logic.determine_winner(
            drawn_number=6,
            player_A_choice="even",
            player_B_choice="odd",
            player_A_id="P01",
            player_B_id="P02"
        )
        assert result["is_draw"] is False
        assert result["winner_id"] == "P01"
        assert result["loser_id"] == "P02"
        assert result["number_parity"] == "even"

    def test_player_b_wins_with_odd(self):
        """Test Player B wins when choosing odd and number is odd."""
        result = game_logic.determine_winner(
            drawn_number=9,
            player_A_choice="even",
            player_B_choice="odd",
            player_A_id="P01",
            player_B_id="P02"
        )
        assert result["is_draw"] is False
        assert result["winner_id"] == "P02"
        assert result["loser_id"] == "P01"
        assert result["number_parity"] == "odd"

    def test_both_wrong_is_draw(self):
        """Test draw when both players choose incorrectly."""
        result = game_logic.determine_winner(
            drawn_number=8,
            player_A_choice="odd",
            player_B_choice="odd",
            player_A_id="P01",
            player_B_id="P02"
        )
        assert result["is_draw"] is True
        assert result["winner_id"] is None

    def test_case_insensitive_choices(self):
        """Test that choice comparison is case-insensitive."""
        result = game_logic.determine_winner(
            drawn_number=2,
            player_A_choice="EVEN",
            player_B_choice="ODD",
            player_A_id="P01",
            player_B_id="P02"
        )
        assert result["winner_id"] == "P01"
        assert result["player_A_choice"] == "even"
        assert result["player_B_choice"] == "odd"


class TestValidateParityChoice:
    """Tests for validate_parity_choice function."""

    def test_valid_even(self):
        """Test that 'even' is valid."""
        assert game_logic.validate_parity_choice("even") is True

    def test_valid_odd(self):
        """Test that 'odd' is valid."""
        assert game_logic.validate_parity_choice("odd") is True

    def test_case_insensitive(self):
        """Test validation is case-insensitive."""
        assert game_logic.validate_parity_choice("EVEN") is True
        assert game_logic.validate_parity_choice("ODD") is True
        assert game_logic.validate_parity_choice("Even") is True

    def test_invalid_choice(self):
        """Test that invalid choices are rejected."""
        assert game_logic.validate_parity_choice("invalid") is False
        assert game_logic.validate_parity_choice("") is False
        assert game_logic.validate_parity_choice("both") is False
