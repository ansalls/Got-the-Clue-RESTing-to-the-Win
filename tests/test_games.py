def test_create_game(authorized_client, test_user):
    res = authorized_client.post("/games/", json={"name": "My first game"})

    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "My first game"
    assert data["owner_id"] == test_user["id"]
    assert data["status"] == "setup"


def test_list_games_only_owned(authorized_client, test_games, test_user):
    res = authorized_client.get("/games/")

    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert all(game["owner_id"] == test_user["id"] for game in data)


def test_get_game_forbidden_other_user(authorized_client, test_games):
    other_game = test_games[-1]
    res = authorized_client.get(f"/games/{other_game.id}")

    assert res.status_code == 403


def test_add_player_to_game(authorized_client, test_games):
    game = test_games[0]
    res = authorized_client.post(
        f"/games/{game.id}/players",
        json={"name": "Casey", "seat_order": 1},
    )

    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Casey"
    assert data["seat_order"] == 1
    assert data["game_id"] == game.id


def test_add_player_duplicate_seat(authorized_client, test_games):
    game = test_games[0]
    res = authorized_client.post(
        f"/games/{game.id}/players",
        json={"name": "Casey", "seat_order": 1},
    )
    assert res.status_code == 201

    res = authorized_client.post(
        f"/games/{game.id}/players",
        json={"name": "Riley", "seat_order": 1},
    )

    assert res.status_code == 409


def test_ui_homepage(client):
    res = client.get("/ui")

    assert res.status_code == 200
    assert "Got the Clue" in res.text


def test_set_turn_order_updates_players(authorized_client, test_games):
    game = test_games[0]
    first_player = authorized_client.post(
        f"/games/{game.id}/players",
        json={"name": "Casey", "seat_order": 1},
    ).json()
    second_player = authorized_client.post(
        f"/games/{game.id}/players",
        json={"name": "Riley", "seat_order": 2},
    ).json()

    res = authorized_client.put(
        f"/games/{game.id}/turn-order",
        json={"player_ids": [second_player["id"], first_player["id"]]},
    )

    assert res.status_code == 200
    data = res.json()
    assert [player["id"] for player in data] == [second_player["id"], first_player["id"]]
    assert [player["seat_order"] for player in data] == [1, 2]


def test_finalize_setup_blocks_setup_changes(authorized_client, test_games):
    game = test_games[0]
    authorized_client.post(
        f"/games/{game.id}/players",
        json={"name": "Casey", "seat_order": 1},
    )

    res = authorized_client.post(f"/games/{game.id}/finalize")
    assert res.status_code == 200
    assert res.json()["status"] == "active"

    res = authorized_client.post(
        f"/games/{game.id}/players",
        json={"name": "Riley", "seat_order": 2},
    )
    assert res.status_code == 409


def test_log_suggestion_and_showing(authorized_client, test_games):
    game = test_games[0]
    suggester = authorized_client.post(
        f"/games/{game.id}/players",
        json={"name": "Casey", "seat_order": 1},
    ).json()
    shower = authorized_client.post(
        f"/games/{game.id}/players",
        json={"name": "Riley", "seat_order": 2},
    ).json()
    authorized_client.post(f"/games/{game.id}/finalize")

    suggestion_res = authorized_client.post(
        f"/games/{game.id}/suggestions",
        json={
            "suggester_id": suggester["id"],
            "suspect": "Colonel Mustard",
            "weapon": "Candlestick",
            "room": "Library",
        },
    )

    assert suggestion_res.status_code == 201
    suggestion = suggestion_res.json()
    assert suggestion["suggester_id"] == suggester["id"]

    showing_res = authorized_client.post(
        f"/games/{game.id}/showings",
        json={
            "suggestion_id": suggestion["id"],
            "showing_player_id": shower["id"],
            "shown_card": "Library",
        },
    )

    assert showing_res.status_code == 201
    showing = showing_res.json()
    assert showing["suggestion_id"] == suggestion["id"]
    assert showing["shown_card"] == "Library"


def test_showing_requires_suggestion(authorized_client, test_games):
    game = test_games[0]
    shower = authorized_client.post(
        f"/games/{game.id}/players",
        json={"name": "Riley", "seat_order": 1},
    ).json()
    authorized_client.post(f"/games/{game.id}/finalize")

    res = authorized_client.post(
        f"/games/{game.id}/showings",
        json={
            "suggestion_id": 999,
            "showing_player_id": shower["id"],
            "shown_card": "Library",
        },
    )

    assert res.status_code == 400
