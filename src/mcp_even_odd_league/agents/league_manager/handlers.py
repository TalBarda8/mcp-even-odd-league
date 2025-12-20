"""
League Manager - Message Handlers

Handles incoming MCP messages.
"""


def handle_referee_register_request(league_manager, request_data: dict) -> dict:
    """
    Handle REFEREE_REGISTER_REQUEST message.

    Args:
        league_manager: LeagueManager instance
        request_data: Request payload

    Returns:
        Response payload (without protocol/message_type/timestamp - added by caller)

    NOTE: This is a stub implementation returning static data.
    """
    import uuid

    # Validate required fields
    if "referee_meta" not in request_data:
        return {
            "status": "REJECTED",
            "reason": "Missing 'referee_meta' field"
        }

    referee_meta = request_data["referee_meta"]
    required_fields = ["display_name", "version", "game_types", "contact_endpoint", "max_concurrent_matches"]

    for field in required_fields:
        if field not in referee_meta:
            return {
                "status": "REJECTED",
                "reason": f"Missing required field: referee_meta.{field}"
            }

    # Static stub response - ACCEPTED
    referee_id = f"REF{str(uuid.uuid4())[:2].upper()}"
    auth_token = f"tok-{referee_id.lower()}-{str(uuid.uuid4())[:8]}"

    return {
        "status": "ACCEPTED",
        "referee_id": referee_id,
        "auth_token": auth_token,
        "league_id": league_manager.league_id if league_manager else "league_2025_even_odd",
        "reason": None
    }


def handle_league_register_request(league_manager, request_data: dict) -> dict:
    """
    Handle LEAGUE_REGISTER_REQUEST message.

    Args:
        league_manager: LeagueManager instance
        request_data: Request payload

    Returns:
        Response payload (without protocol/message_type/timestamp - added by caller)

    NOTE: This is a stub implementation returning static data.
    Real implementation would validate, assign IDs, generate tokens, persist to registry.
    """
    import uuid

    # Validate required fields
    if "player_meta" not in request_data:
        return {
            "status": "REJECTED",
            "reason": "Missing 'player_meta' field"
        }

    player_meta = request_data["player_meta"]
    required_fields = ["display_name", "version", "game_types", "contact_endpoint"]

    for field in required_fields:
        if field not in player_meta:
            return {
                "status": "REJECTED",
                "reason": f"Missing required field: player_meta.{field}"
            }

    # Static stub response - ACCEPTED
    # In real implementation:
    # - Check if league is full
    # - Check for duplicate display_name
    # - Validate contact_endpoint
    # - Assign unique player_id (P01, P02, P03, P04)
    # - Generate auth_token
    # - Store in agents registry

    # For now, generate a simple player_id and token
    player_id = f"P{str(uuid.uuid4())[:2].upper()}"  # Simplified ID
    auth_token = f"tok-{player_id.lower()}-{str(uuid.uuid4())[:8]}"

    return {
        "status": "ACCEPTED",
        "player_id": player_id,
        "auth_token": auth_token,
        "league_id": league_manager.league_id if league_manager else "league_2025_even_odd",
        "reason": None
    }


def handle_match_result_report(league_manager, request_data: dict) -> dict:
    """
    Handle MATCH_RESULT_REPORT message from Referee.

    Args:
        league_manager: LeagueManager instance
        request_data: Request payload

    Returns:
        MATCH_RESULT_ACK response payload

    Phase 5: Now updates standings
    """
    from datetime import datetime

    match_id = request_data.get("match_id")
    round_id = request_data.get("round_id")
    result = request_data.get("result", {})

    print(f"\n[League Manager] Received MATCH_RESULT_REPORT")
    print(f"  Match ID: {match_id}")
    print(f"  Round ID: {round_id}")
    print(f"  Winner: {result.get('winner')}")
    print(f"  Score: {result.get('score')}")
    print(f"  Details: {result.get('details')}")

    # Phase 5: Update standings
    league_manager.update_standings_from_match(request_data)

    return {
        "protocol": "league.v2",
        "message_type": "MATCH_RESULT_ACK",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "ACCEPTED",
        "match_id": match_id,
        "round_id": round_id
    }


def handle_league_query(request_data: dict) -> dict:
    """
    Handle LEAGUE_QUERY message.

    Args:
        request_data: Request payload

    Returns:
        Response payload

    TODO: Implement standings query handling
    """
    pass
