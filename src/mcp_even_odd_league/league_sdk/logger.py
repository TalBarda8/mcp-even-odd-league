"""
JSON Logger

Structured JSON Lines logging.
Based on class_map.md - JsonLogger class for JSONL format logging.
"""

from pathlib import Path
from typing import Optional, Any
from datetime import datetime


class JsonLogger:
    """Structured JSONL logging"""

    def __init__(self, component: str, league_id: Optional[str] = None, logs_root: Path = None):
        """
        Initialize JsonLogger.

        Args:
            component: Component name (e.g., "league_manager", "referee:REF01", "player:P01")
            league_id: Optional league identifier
            logs_root: Root directory for log files (defaults to SHARED/logs)
        """
        self.component = component
        self.league_id = league_id

        if logs_root is None:
            # TODO: Set default to SHARED/logs
            self.logs_root = Path("SHARED/logs")
        else:
            self.logs_root = logs_root

        # Determine log file path based on component type
        if component == "league_manager" and league_id:
            self.log_path = self.logs_root / "league" / league_id / "league.log.jsonl"
        elif component.startswith("referee:") or component.startswith("player:"):
            agent_id = component.split(":")[-1]
            self.log_path = self.logs_root / "agents" / f"{agent_id}.log.jsonl"
        else:
            self.log_path = self.logs_root / "system" / f"{component}.log.jsonl"

    def log(self, event_type: str, level: str = "INFO", **details) -> None:
        """
        Log an event.

        Args:
            event_type: Type of event (e.g., "PLAYER_REGISTERED")
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            **details: Additional key-value pairs to include in log entry
        """
        import json

        # Ensure log directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Create log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent_id": self.component,
            "level": level,
            "event_type": event_type,
            "data": details
        }

        # Append to log file as JSON line
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def log_event(self, event_type: str, data: Optional[dict] = None) -> None:
        """
        Log an event with optional data.

        Args:
            event_type: Type of event (e.g., "TIMEOUT_GAME_JOIN_ACK")
            data: Optional dictionary of event data

        This method is called by agents (Referee/Player) for Phase 4 logging.
        """
        if data is None:
            data = {}

        # Use the log method with data as keyword arguments
        self.log(event_type, level="INFO", **data)

    def debug(self, event_type: str, **details) -> None:
        """Log debug event"""
        self.log(event_type, level="DEBUG", **details)

    def info(self, event_type: str, **details) -> None:
        """Log info event"""
        self.log(event_type, level="INFO", **details)

    def warning(self, event_type: str, **details) -> None:
        """Log warning event"""
        self.log(event_type, level="WARNING", **details)

    def error(self, event_type: str, **details) -> None:
        """Log error event"""
        self.log(event_type, level="ERROR", **details)

    def log_message_sent(self, message_type: str, recipient: str, **details) -> None:
        """
        Log outgoing message.

        Args:
            message_type: MCP message type (e.g., "GAME_INVITATION")
            recipient: Recipient identifier
            **details: Additional message details

        TODO: Implement message logging
        """
        self.info("MESSAGE_SENT", message_type=message_type, recipient=recipient, **details)

    def log_message_received(self, message_type: str, sender: str, **details) -> None:
        """
        Log incoming message.

        Args:
            message_type: MCP message type
            sender: Sender identifier
            **details: Additional message details

        TODO: Implement message logging
        """
        self.info("MESSAGE_RECEIVED", message_type=message_type, sender=sender, **details)
