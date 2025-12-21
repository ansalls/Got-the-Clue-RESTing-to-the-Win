import pytest
from pydantic import ValidationError

from app import schemas


@pytest.mark.parametrize(
    "hand_id,envelope_id,is_unknown",
    [
        (None, None, True),
        (1, None, False),
        (None, 2, False),
    ],
)
def test_card_create_allows_single_location(hand_id, envelope_id, is_unknown):
    card = schemas.CardCreate(
        name="Candlestick",
        card_type="weapon",
        game_id=1,
        hand_id=hand_id,
        envelope_id=envelope_id,
        is_unknown=is_unknown,
    )

    assert card.name == "Candlestick"


@pytest.mark.parametrize(
    "hand_id,envelope_id,is_unknown",
    [
        (1, 2, False),
        (1, None, True),
        (None, 2, True),
        (None, None, False),
    ],
)
def test_card_create_rejects_multiple_or_missing_locations(hand_id, envelope_id, is_unknown):
    with pytest.raises(ValidationError):
        schemas.CardCreate(
            name="Rope",
            card_type="weapon",
            game_id=1,
            hand_id=hand_id,
            envelope_id=envelope_id,
            is_unknown=is_unknown,
        )
