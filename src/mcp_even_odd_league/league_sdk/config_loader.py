"""
Configuration Loader

Loads configuration files from SHARED/config/.
Based on class_map.md - ConfigLoader class with lazy loading and caching.
"""

import os
from pathlib import Path
from typing import Optional, Dict
from .config_models import SystemConfig, LeagueConfig, RefereeConfig, PlayerConfig
from .config_models import NetworkConfig, TimeoutsConfig, ScoringConfig

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    # Look for .env in project root (2 levels up from this file)
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, use environment variables directly


class ConfigLoader:
    """Configuration file loader with lazy loading and caching"""

    def __init__(self, root: Path = None):
        """
        Initialize ConfigLoader.

        Args:
            root: Root directory for configuration files (defaults to SHARED/config)
        """
        if root is None:
            # TODO: Set default to SHARED/config relative to project root
            self.root = Path("SHARED/config")
        else:
            self.root = root

        # Lazy loading caches
        self._system: Optional[SystemConfig] = None
        self._agents: Optional[Dict] = None
        self._leagues: Dict[str, LeagueConfig] = {}

    def load_system(self) -> SystemConfig:
        """
        Load system configuration from environment variables and files.

        Returns:
            SystemConfig object with values from environment variables or defaults
        """
        if self._system is None:
            # Load network configuration from environment
            network = NetworkConfig(
                base_host=os.getenv('LEAGUE_MANAGER_HOST', 'localhost'),
                league_manager_port=int(os.getenv('LEAGUE_MANAGER_PORT', '8000')),
                player_ports=[
                    int(os.getenv('PLAYER_P01_PORT', '8101')),
                    int(os.getenv('PLAYER_P02_PORT', '8102')),
                    int(os.getenv('PLAYER_P03_PORT', '8103')),
                    int(os.getenv('PLAYER_P04_PORT', '8104'))
                ]
            )

            # Load timeout configuration from environment
            timeouts = TimeoutsConfig(
                game_join_ack_timeout_sec=int(os.getenv('TIMEOUT_GAME_JOIN_ACK', '5')),
                move_timeout_sec=int(os.getenv('TIMEOUT_PARITY_CHOICE', '30')),
                generic_response_timeout_sec=int(os.getenv('TIMEOUT_DEFAULT', '10'))
            )

            # Create system config
            self._system = SystemConfig(
                protocol_version=os.getenv('PROTOCOL_VERSION', 'league.v2'),
                network=network,
                timeouts=timeouts
            )
        return self._system

    def load_agents(self) -> Dict:
        """
        Load agents configuration from agents/agents_config.json

        Returns:
            Dict containing referee and player configurations

        TODO: Implement JSON loading and parsing
        """
        if self._agents is None:
            # TODO: Load from self.root / "agents" / "agents_config.json"
            self._agents = {
                "referees": [],
                "players": []
            }
        return self._agents

    def load_league(self, league_id: str) -> LeagueConfig:
        """
        Load league configuration from environment variables and files.

        Args:
            league_id: League identifier

        Returns:
            LeagueConfig object with values from environment variables or defaults
        """
        if league_id not in self._leagues:
            # Load scoring configuration from environment
            scoring = ScoringConfig(
                win_points=int(os.getenv('POINTS_WIN', '3')),
                draw_points=int(os.getenv('POINTS_DRAW', '1')),
                loss_points=int(os.getenv('POINTS_LOSS', '0'))
            )

            self._leagues[league_id] = LeagueConfig(
                league_id=league_id,
                game_type="even_odd",
                scoring=scoring
            )
        return self._leagues[league_id]

    def load_games_registry(self) -> Dict:
        """
        Load games registry from games/games_registry.json

        Returns:
            Dict containing supported game types

        TODO: Implement JSON loading and parsing
        """
        # TODO: Load from self.root / "games" / "games_registry.json"
        return {
            "even_odd": {
                "name": "Even/Odd",
                "rules_module": "even_odd_rules"
            }
        }

    def get_referee_by_id(self, referee_id: str) -> Optional[RefereeConfig]:
        """
        Get referee configuration by ID

        Args:
            referee_id: Referee identifier

        Returns:
            RefereeConfig or None if not found

        TODO: Implement lookup in agents registry
        """
        # TODO: Load agents and search for referee
        pass

    def get_player_by_id(self, player_id: str) -> Optional[PlayerConfig]:
        """
        Get player configuration by ID

        Args:
            player_id: Player identifier

        Returns:
            PlayerConfig or None if not found

        TODO: Implement lookup in agents registry
        """
        # TODO: Load agents and search for player
        pass

    @staticmethod
    def get_game_number_range() -> tuple:
        """
        Get game number range from environment variables.

        Returns:
            Tuple of (min_value, max_value) for random number generation
        """
        min_val = int(os.getenv('GAME_NUMBER_MIN', '1'))
        max_val = int(os.getenv('GAME_NUMBER_MAX', '10'))
        return (min_val, max_val)

    @staticmethod
    def get_max_retries() -> int:
        """
        Get maximum retry count from environment variables.

        Returns:
            Maximum number of retries
        """
        return int(os.getenv('MAX_RETRIES', '1'))
