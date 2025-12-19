"""
Player - Message Handlers

Handles incoming MCP messages and coordinates responses.
"""

from datetime import datetime


def handle_game_invitation(player, invite_data: dict) -> dict:
    """
    Handle GAME_INVITATION from Referee.

    Args:
        player: Player instance
        invite_data: Game invitation payload

    Returns:
        GAME_JOIN_ACK response payload

    NOTE: Phase 3 - Always accept invitations
    """
    print(f"\n[{player.player_id}] Received GAME_INVITATION for match {invite_data.get('match_id')}")
    print(f"  Opponent: {invite_data.get('opponent_id')}")
    print(f"  Role: {invite_data.get('role_in_match')}")

    # Always accept for Phase 3
    return {
        "protocol": "league.v2",
        "message_type": "GAME_JOIN_ACK",
        "sender": f"player:{player.player_id}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "auth_token": "tok-player-placeholder",  # Placeholder for Phase 3
        "match_id": invite_data.get("match_id"),
        "player_id": player.player_id,
        "arrival_timestamp": datetime.utcnow().isoformat() + "Z",
        "accept": True
    }


def handle_parity_choose(player, request_data: dict) -> dict:
    """
    Handle CHOOSE_PARITY_CALL from Referee.

    Args:
        player: Player instance
        request_data: Parity request payload

    Returns:
        CHOOSE_PARITY_RESPONSE payload with parity choice

    NOTE: Phase 3 - P01 always chooses "even", P02 always chooses "odd"
    """
    print(f"\n[{player.player_id}] Received CHOOSE_PARITY_CALL for match {request_data.get('match_id')}")

    # P01 chooses "even", P02 chooses "odd"
    if player.player_id == "P01":
        choice = "even"
    else:
        choice = "odd"

    print(f"  Choosing: {choice}")

    return {
        "protocol": "league.v2",
        "message_type": "CHOOSE_PARITY_RESPONSE",
        "sender": f"player:{player.player_id}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "auth_token": "tok-player-placeholder",
        "match_id": request_data.get("match_id"),
        "player_id": player.player_id,
        "parity_choice": choice
    }


def handle_notify_match_result(player, result_data: dict) -> dict:
    """
    Handle GAME_OVER notification from Referee.

    Args:
        player: Player instance
        result_data: Game over payload

    Returns:
        GAME_OVER_ACK response payload

    NOTE: Phase 3 - Just log the result
    """
    print(f"\n[{player.player_id}] Received GAME_OVER for match {result_data.get('match_id')}")

    game_result = result_data.get("game_result", {})
    print(f"  Status: {game_result.get('status')}")
    print(f"  Drawn number: {game_result.get('drawn_number')} ({game_result.get('number_parity')})")
    print(f"  Winner: {game_result.get('winner_player_id')}")
    print(f"  Reason: {game_result.get('reason')}")

    return {
        "protocol": "league.v2",
        "message_type": "GAME_OVER_ACK",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "ACKNOWLEDGED",
        "player_id": player.player_id,
        "match_id": result_data.get("match_id")
    }


def handle_league_standings_update(player, standings_data: dict) -> dict:
    """
    Handle LEAGUE_STANDINGS_UPDATE from League Manager.

    Args:
        player: Player instance
        standings_data: Standings update payload

    Returns:
        Response payload

    TODO: Implement standings update processing
    """
    pass


def handle_round_completed(player, completion_data: dict) -> dict:
    """
    Handle ROUND_COMPLETED from League Manager.

    Args:
        player: Player instance
        completion_data: Round completion payload

    Returns:
        Response payload

    TODO: Implement round completion handling
    """
    pass


def handle_league_completed(player, completion_data: dict) -> dict:
    """
    Handle LEAGUE_COMPLETED from League Manager.

    Args:
        player: Player instance
        completion_data: League completion payload

    Returns:
        Response payload

    TODO: Implement league completion handling
    """
    pass
