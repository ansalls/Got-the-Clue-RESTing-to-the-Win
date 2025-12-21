from app.inference.engine import CardInferenceEngine, KnowledgeType


def test_player_showing_card_is_in_hand() -> None:
    engine = CardInferenceEngine()

    engine.record_card_shown("Avery", "Rope")

    knowledge = engine.knowledge_for_player("Avery")
    assert len(knowledge) == 1
    assert knowledge[0].card == "Rope"
    assert knowledge[0].knowledge == KnowledgeType.HAS_CARD


def test_player_cannot_show_means_no_suggested_cards() -> None:
    engine = CardInferenceEngine()

    engine.record_cannot_show("Blake", ["Knife", "Library", "Plum"])

    knowledge = engine.knowledge_for_player("Blake")
    assert [entry.card for entry in knowledge] == ["Knife", "Library", "Plum"]
    assert all(entry.knowledge == KnowledgeType.DOES_NOT_HAVE_CARD for entry in knowledge)
