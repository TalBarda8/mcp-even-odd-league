"""
Configuration Loader

Loads configuration files from SHARED/config/.
Based on class_map.md - ConfigLoader class with lazy loading and caching.
"""

from pathlib import Path
from typing import Optional, Dict
from .config_models import SystemConfig, LeagueConfig, RefereeConfig, PlayerConfig


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
        Load system configuration from system.json

        Returns:
            SystemConfig object

        TODO: Implement JSON loading and parsing
        """
        if self._system is None:
            # TODO: Load from self.root / "system.json"
            # For now, return default config
            self._system = SystemConfig()
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
        Load league configuration from leagues/<league_id>.json

        Args:
            league_id: League identifier

        Returns:
            LeagueConfig object

        TODO: Implement JSON loading and parsing
        """
        if league_id not in self._leagues:
            # TODO: Load from self.root / "leagues" / f"{league_id}.json"
            # For now, return default config
            self._leagues[league_id] = LeagueConfig(
                league_id=league_id,
                game_type="even_odd"
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
