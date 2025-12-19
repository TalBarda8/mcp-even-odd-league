"""
Configuration Models

Dataclass definitions for system configuration.
Based on class_map.md - Chapter 10 class definitions.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class NetworkConfig:
    """Network settings (base_host, ports)"""
    base_host: str = "localhost"
    league_manager_port: int = 8000
    referee_ports: List[int] = None
    player_ports: List[int] = None

    def __post_init__(self):
        if self.referee_ports is None:
            self.referee_ports = [8001, 8002]
        if self.player_ports is None:
            self.player_ports = [8101, 8102, 8103, 8104]


@dataclass
class SecurityConfig:
    """Authentication tokens configuration"""
    enable: bool = True
    token_length: int = 32
    token_ttl_seconds: int = 3600


@dataclass
class TimeoutsConfig:
    """All timeout values (5s, 30s, 10s)"""
    register_referee_timeout_sec: int = 10
    register_player_timeout_sec: int = 10
    game_join_ack_timeout_sec: int = 5
    move_timeout_sec: int = 30
    generic_response_timeout_sec: int = 10


@dataclass
class SystemConfig:
    """Top-level configuration aggregating all settings"""
    protocol_version: str = "league.v2"
    network: NetworkConfig = None
    security: SecurityConfig = None
    timeouts: TimeoutsConfig = None

    def __post_init__(self):
        if self.network is None:
            self.network = NetworkConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.timeouts is None:
            self.timeouts = TimeoutsConfig()


@dataclass
class RefereeConfig:
    """Referee metadata"""
    referee_id: str
    display_name: str
    version: str
    game_types: List[str]
    contact_endpoint: str
    max_concurrent_matches: int = 5


@dataclass
class PlayerConfig:
    """Player metadata"""
    player_id: str
    display_name: str
    version: str
    game_types: List[str]
    contact_endpoint: str
    preferred_leagues: Optional[List[str]] = None


@dataclass
class ScoringConfig:
    """Scoring rules"""
    win_points: int = 3
    draw_points: int = 1
    loss_points: int = 0
    tiebreakers: List[str] = None

    def __post_init__(self):
        if self.tiebreakers is None:
            self.tiebreakers = ["points", "wins", "alphabetical"]


@dataclass
class LeagueConfig:
    """League settings"""
    league_id: str
    game_type: str
    status: str = "WAITING_FOR_REGISTRATIONS"
    scoring: ScoringConfig = None
    min_players: int = 4
    max_players: int = 4

    def __post_init__(self):
        if self.scoring is None:
            self.scoring = ScoringConfig()
