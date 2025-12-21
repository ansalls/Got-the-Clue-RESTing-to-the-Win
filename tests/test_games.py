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
