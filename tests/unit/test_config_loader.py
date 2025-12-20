"""
Unit tests for configuration loader.

Tests configuration loading and environment variable handling.
"""

import os
import pytest
from mcp_even_odd_league.league_sdk.config_loader import ConfigLoader
from mcp_even_odd_league.league_sdk.config_models import SystemConfig, NetworkConfig


class TestConfigLoader:
    """Tests for ConfigLoader class."""

    def test_load_system_defaults(self):
        """Test that system config loads with default values."""
        loader = ConfigLoader()
        config = loader.load_system()

        assert isinstance(config, SystemConfig)
        assert config.protocol_version == "league.v2"
        assert isinstance(config.network, NetworkConfig)

    def test_load_system_network_defaults(self):
        """Test that network config has correct defaults."""
        loader = ConfigLoader()
        config = loader.load_system()

        assert config.network.base_host == "localhost"
        assert config.network.league_manager_port == 8000
        assert config.network.player_ports == [8101, 8102, 8103, 8104]

    def test_load_system_timeouts_defaults(self):
        """Test that timeout config has correct defaults."""
        loader = ConfigLoader()
        config = loader.load_system()

        assert config.timeouts.game_join_ack_timeout_sec == 5
        assert config.timeouts.move_timeout_sec == 30
        assert config.timeouts.generic_response_timeout_sec == 10

    def test_load_league_defaults(self):
        """Test that league config loads with defaults."""
        loader = ConfigLoader()
        league_config = loader.load_league("test_league")

        assert league_config.league_id == "test_league"
        assert league_config.game_type == "even_odd"
        assert league_config.scoring.win_points == 3
        assert league_config.scoring.draw_points == 1
        assert league_config.scoring.loss_points == 0

    def test_get_game_number_range_defaults(self):
        """Test game number range helper returns defaults."""
        min_val, max_val = ConfigLoader.get_game_number_range()
        assert min_val == 1
        assert max_val == 10

    def test_get_max_retries_default(self):
        """Test max retries helper returns default."""
        retries = ConfigLoader.get_max_retries()
        assert retries == 1

    def test_load_system_caching(self):
        """Test that system config is cached."""
        loader = ConfigLoader()
        config1 = loader.load_system()
        config2 = loader.load_system()

        # Should return the same instance
        assert config1 is config2

    def test_load_league_caching(self):
        """Test that league config is cached per league_id."""
        loader = ConfigLoader()
        league1 = loader.load_league("league_1")
        league1_again = loader.load_league("league_1")
        league2 = loader.load_league("league_2")

        # Same league_id should return same instance
        assert league1 is league1_again
        # Different league_id should return different instance
        assert league1 is not league2


class TestConfigLoaderEnvironment:
    """Tests for environment variable handling."""

    def test_respects_env_protocol_version(self, monkeypatch):
        """Test that PROTOCOL_VERSION env var is respected."""
        monkeypatch.setenv("PROTOCOL_VERSION", "league.v3")
        loader = ConfigLoader()
        config = loader.load_system()

        assert config.protocol_version == "league.v3"

    def test_respects_env_league_manager_port(self, monkeypatch):
        """Test that LEAGUE_MANAGER_PORT env var is respected."""
        monkeypatch.setenv("LEAGUE_MANAGER_PORT", "9000")
        loader = ConfigLoader()
        config = loader.load_system()

        assert config.network.league_manager_port == 9000

    def test_respects_env_timeout_values(self, monkeypatch):
        """Test that timeout env vars are respected."""
        monkeypatch.setenv("TIMEOUT_GAME_JOIN_ACK", "10")
        monkeypatch.setenv("TIMEOUT_PARITY_CHOICE", "60")
        loader = ConfigLoader()
        config = loader.load_system()

        assert config.timeouts.game_join_ack_timeout_sec == 10
        assert config.timeouts.move_timeout_sec == 60
