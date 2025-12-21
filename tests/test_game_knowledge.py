from app import models


def test_game_knowledge_inference(authorized_client, session):
    game_res = authorized_client.post("/games/", json={"name": "Deduction Night"})
    assert game_res.status_code == 201
    game_id = game_res.json()["id"]

    authorized_client.post(
        f"/games/{game_id}/players",
        json={"name": "Alex", "seat_order": 1},
    )
    authorized_client.post(
        f"/games/{game_id}/players",
        json={"name": "Blake", "seat_order": 2},
    )
    authorized_client.post(
        f"/games/{game_id}/players",
        json={"name": "Casey", "seat_order": 3},
    )

    players = (
        session.query(models.Player)
        .filter(models.Player.game_id == game_id)
        .order_by(models.Player.seat_order.asc())
        .all()
    )
    player_by_name = {player.name: player for player in players}

    cards = [
        models.Card(name="Scarlet", category="suspect"),
        models.Card(name="Mustard", category="suspect"),
        models.Card(name="Knife", category="weapon"),
        models.Card(name="Revolver", category="weapon"),
        models.Card(name="Kitchen", category="room"),
        models.Card(name="Library", category="room"),
    ]
    session.add_all(cards)
    session.commit()
    cards_by_name = {card.name: card for card in session.query(models.Card).all()}

    session.add_all(
        [
            models.PlayerCard(
                game_id=game_id,
                player_id=player_by_name["Alex"].id,
                card_id=cards_by_name["Scarlet"].id,
            ),
            models.PlayerCard(
                game_id=game_id,
                player_id=player_by_name["Blake"].id,
                card_id=cards_by_name["Knife"].id,
            ),
            models.PlayerCard(
                game_id=game_id,
                player_id=player_by_name["Casey"].id,
                card_id=cards_by_name["Kitchen"].id,
            ),
        ]
    )
    session.commit()

    suggestion_one = models.Suggestion(
        game_id=game_id,
        suggester_id=player_by_name["Alex"].id,
        suspect_card_id=cards_by_name["Mustard"].id,
        weapon_card_id=cards_by_name["Revolver"].id,
        room_card_id=cards_by_name["Library"].id,
    )
    session.add(suggestion_one)
    session.commit()
    session.add(
        models.SuggestionResponse(
            suggestion_id=suggestion_one.id,
            shower_id=player_by_name["Blake"].id,
            shown_card_id=cards_by_name["Revolver"].id,
        )
    )
    session.commit()

    suggestion_two = models.Suggestion(
        game_id=game_id,
        suggester_id=player_by_name["Casey"].id,
        suspect_card_id=cards_by_name["Mustard"].id,
        weapon_card_id=cards_by_name["Revolver"].id,
        room_card_id=cards_by_name["Library"].id,
    )
    session.add(suggestion_two)
    session.commit()
    session.add(
        models.SuggestionResponse(
            suggestion_id=suggestion_two.id,
            shower_id=player_by_name["Alex"].id,
            shown_card_id=None,
        )
    )
    session.commit()

    knowledge_res = authorized_client.get(f"/games/{game_id}/knowledge")
    assert knowledge_res.status_code == 200
    knowledge = knowledge_res.json()

    card_by_name = {card["name"]: card for card in knowledge["cards"]}
    assert card_by_name["Revolver"]["owner_known"] is True
    assert card_by_name["Revolver"]["owner_player_id"] == player_by_name["Blake"].id
    assert card_by_name["Mustard"]["owner_known"] is False

    players_by_name = {player["name"]: player for player in knowledge["players"]}
    alex_confirmed = {card["name"] for card in players_by_name["Alex"]["confirmed_cards"]}
    alex_possible = {card["name"] for card in players_by_name["Alex"]["possible_cards"]}
    assert alex_confirmed == {"Scarlet"}
    assert alex_possible == {"Mustard", "Library"}

    envelope = knowledge["envelope_possibilities"]
    assert {card["name"] for card in envelope["suspects"]} == {"Mustard"}
    assert envelope["weapons"] == []
    assert {card["name"] for card in envelope["rooms"]} == {"Library"}
