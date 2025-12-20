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

    Phase 4: Added state validation
    """
    match_id = invite_data.get('match_id')

    print(f"\n[{player.player_id}] Received GAME_INVITATION for match {match_id}")
    print(f"  Current state: {player.state}")
    print(f"  Opponent: {invite_data.get('opponent_id')}")
    print(f"  Role: {invite_data.get('role_in_match')}")

    # Phase 4: Validate state before processing
    if not player.validate_state_transition(player.state, "GAME_INVITATION"):
        error_msg = f"Invalid state for GAME_INVITATION: current state is {player.state}, expected IDLE"
        print(f"  ❌ REJECTED: {error_msg}")
        player.logger.log_event("INVALID_MESSAGE_STATE", {
            "player_id": player.player_id,
            "message_type": "GAME_INVITATION",
            "current_state": player.state,
            "match_id": match_id,
            "reason": error_msg
        })

        # Return rejection
        return {
            "protocol": "league.v2",
            "message_type": "GAME_JOIN_ACK",
            "sender": f"player:{player.player_id}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "auth_token": "tok-player-placeholder",
            "match_id": match_id,
            "player_id": player.player_id,
            "arrival_timestamp": datetime.utcnow().isoformat() + "Z",
            "accept": False,
            "reject_reason": error_msg
        }

    # Store match context and transition state
    player.current_match = match_id
    player.transition_state("INVITED", f"Received invitation for match {match_id}")

    # Always accept for Phase 4 (if state is valid)
    print(f"  ✅ ACCEPTED")

    return {
        "protocol": "league.v2",
        "message_type": "GAME_JOIN_ACK",
        "sender": f"player:{player.player_id}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "auth_token": "tok-player-placeholder",
        "match_id": match_id,
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

    Phase 4: Added state validation - P01 always chooses "even", P02 always chooses "odd"
    """
    match_id = request_data.get('match_id')

    print(f"\n[{player.player_id}] Received CHOOSE_PARITY_CALL for match {match_id}")
    print(f"  Current state: {player.state}")

    # Phase 4: Validate state before processing
    if not player.validate_state_transition(player.state, "CHOOSE_PARITY_CALL"):
        error_msg = f"Invalid state for CHOOSE_PARITY_CALL: current state is {player.state}, expected INVITED"
        print(f"  ❌ REJECTED: {error_msg}")
        player.logger.log_event("INVALID_MESSAGE_STATE", {
            "player_id": player.player_id,
            "message_type": "CHOOSE_PARITY_CALL",
            "current_state": player.state,
            "match_id": match_id,
            "reason": error_msg
        })

        # Return error response
        raise Exception(error_msg)

    # Transition to CHOOSING state
    player.transition_state("CHOOSING", f"Received parity request for match {match_id}")

    # P01 chooses "even", P02 chooses "odd"
    if player.player_id == "P01":
        choice = "even"
    else:
        choice = "odd"

    print(f"  Choosing: {choice}")

    # After sending response, we're waiting for result
    player.transition_state("WAITING_RESULT", f"Sent parity choice: {choice}")

    return {
        "protocol": "league.v2",
        "message_type": "CHOOSE_PARITY_RESPONSE",
        "sender": f"player:{player.player_id}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "auth_token": "tok-player-placeholder",
        "match_id": match_id,
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

    Phase 4: Added state validation and state reset to IDLE
    """
    match_id = result_data.get('match_id')

    print(f"\n[{player.player_id}] Received GAME_OVER for match {match_id}")
    print(f"  Current state: {player.state}")

    # Phase 4: Validate state before processing
    # Accept GAME_OVER in both CHOOSING and WAITING_RESULT states
    if player.state not in ["CHOOSING", "WAITING_RESULT"]:
        error_msg = f"Invalid state for GAME_OVER: current state is {player.state}, expected CHOOSING or WAITING_RESULT"
        print(f"  ⚠️ WARNING: {error_msg}")
        player.logger.log_event("INVALID_MESSAGE_STATE", {
            "player_id": player.player_id,
            "message_type": "GAME_OVER",
            "current_state": player.state,
            "match_id": match_id,
            "reason": error_msg
        })
        # Continue processing anyway, but log the warning

    game_result = result_data.get("game_result", {})
    print(f"  Status: {game_result.get('status')}")
    print(f"  Drawn number: {game_result.get('drawn_number')} ({game_result.get('number_parity')})")
    print(f"  Winner: {game_result.get('winner_player_id')}")
    print(f"  Reason: {game_result.get('reason')}")

    # Reset state to IDLE after match completes
    player.current_match = None
    player.transition_state("IDLE", f"Match {match_id} completed")

    return {
        "protocol": "league.v2",
        "message_type": "GAME_OVER_ACK",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "ACKNOWLEDGED",
        "player_id": player.player_id,
        "match_id": match_id
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
