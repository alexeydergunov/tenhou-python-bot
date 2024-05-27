from mahjong.constants import FIVE_RED_MAN, FIVE_RED_PIN, FIVE_RED_SOU

import mortal.mortal_helpers as mortal_helpers
from mortal.mortal_bot import MortalBot
from mortal.mortal_helpers import MortalEvent

MORTAL_BOT_0 = MortalBot(player_id=0)


def test_tile_conversion():
    tiles_136_lists = []
    mortal_tiles_lists = []

    index = 0
    for suit in "mps":
        for num in range(1, 10):
            tiles_136_lists.append(list(range(index, index + 4)))
            mortal_tiles_lists.append([str(num) + suit] * 4)
            if num == 5:
                mortal_tiles_lists[-1][-1] += "r"
            index += 4
    for num0, honor in enumerate("ESWNPFC"):
        tiles_136_lists.append(list(range(index, index + 4)))
        mortal_tiles_lists.append([honor] * 4)
        index += 4
    assert index == 136

    assert len(tiles_136_lists) == len(mortal_tiles_lists) == 34

    for tiles_136, mortal_tiles in zip(tiles_136_lists, mortal_tiles_lists):
        assert sorted(mortal_tiles) == sorted(map(mortal_helpers.convert_tile_to_mortal, tiles_136))

    assert mortal_helpers.convert_tile_to_mortal(tile_136=FIVE_RED_MAN) == "5mr"
    assert mortal_helpers.convert_tile_to_mortal(tile_136=FIVE_RED_PIN) == "5pr"
    assert mortal_helpers.convert_tile_to_mortal(tile_136=FIVE_RED_SOU) == "5sr"


def test_9_terminals_redeal():
    events: list[MortalEvent] = [
        mortal_helpers.start_game(),
        mortal_helpers.start_hand(
            round_wind="E", dora_marker="5m", round_id=1, honba=0, riichi_sticks=0, dealer_id=0, scores=[25000] * 4,
            start_hands=[["1m", "5m", "9m", "1p", "5p", "9p", "1s", "5s", "9s", "E", "S", "W", "N"], ["?"] * 13, ["?"] * 13, ["?"] * 13],
        ),
        mortal_helpers.draw_tile(player_id=0, tile="4p"),
    ]
    action = MORTAL_BOT_0.react_one(events=events)
    assert action["type"] == "ryukyoku"


def test_tsumo():
    events: list[MortalEvent] = [
        mortal_helpers.start_game(),
        mortal_helpers.start_hand(
            round_wind="E", dora_marker="5m", round_id=1, honba=0, riichi_sticks=0, dealer_id=0, scores=[25000] * 4,
            start_hands=[["1m", "2m", "3m", "7m", "7m", "7m", "7s", "8s", "9s", "E", "E", "W", "W"], ["?"] * 13, ["?"] * 13, ["?"] * 13],
        ),
        mortal_helpers.draw_tile(player_id=0, tile="W"),
    ]
    action = MORTAL_BOT_0.react_one(events=events)
    assert action["type"] == "hora"
    assert action["actor"] == 0
    assert action["target"] == 0


def test_riichi():
    events: list[MortalEvent] = [
        mortal_helpers.start_game(),
        mortal_helpers.start_hand(
            round_wind="E", dora_marker="5m", round_id=1, honba=0, riichi_sticks=0, dealer_id=0, scores=[25000] * 4,
            start_hands=[["1m", "2m", "3m", "7m", "7m", "7m", "7s", "8s", "9s", "E", "E", "W", "W"], ["?"] * 13, ["?"] * 13, ["?"] * 13],
        ),
        mortal_helpers.draw_tile(player_id=0, tile="N"),
    ]
    action = MORTAL_BOT_0.react_one(events=events)
    assert action["type"] == "reach"
    assert action["actor"] == 0


def test_ron():
    events: list[MortalEvent] = [
        mortal_helpers.start_game(),
        mortal_helpers.start_hand(
            round_wind="E", dora_marker="5m", round_id=1, honba=0, riichi_sticks=0, dealer_id=0, scores=[25000] * 4,
            start_hands=[["1m", "2m", "3m", "7m", "7m", "7m", "7s", "8s", "9s", "E", "E", "W", "W"], ["?"] * 13, ["?"] * 13, ["?"] * 13],
        ),
        mortal_helpers.draw_tile(player_id=0, tile="N"),
        mortal_helpers.discard_tile(player_id=0, tile="N", tsumogiri=True),
        mortal_helpers.draw_unknown_tile(player_id=1),
        mortal_helpers.discard_tile(player_id=1, tile="E", tsumogiri=False),
    ]
    action = MORTAL_BOT_0.react_one(events=events)
    assert action["type"] == "hora"
    assert action["actor"] == 0
    assert action["target"] == 1


def test_robbing_a_kan():
    events: list[MortalEvent] = [
        mortal_helpers.start_game(),
        mortal_helpers.start_hand(
            round_wind="E", dora_marker="5m", round_id=1, honba=0, riichi_sticks=0, dealer_id=0, scores=[25000] * 4,
            start_hands=[["5mr", "7m", "5pr", "5p", "5p", "5sr", "6s", "7s", "E", "E", "W", "W", "W"], ["?"] * 13, ["?"] * 13, ["?"] * 13],
        ),
        mortal_helpers.draw_tile(player_id=0, tile="N"),
        mortal_helpers.discard_tile(player_id=0, tile="N", tsumogiri=True),
        mortal_helpers.draw_unknown_tile(player_id=1),
        mortal_helpers.discard_tile(player_id=1, tile="6m", tsumogiri=False),
        mortal_helpers.pon(player_id=3, from_whom=1, tile="6m"),
        mortal_helpers.discard_tile(player_id=3, tile="S", tsumogiri=False),
        mortal_helpers.draw_tile(player_id=0, tile="N"),
        mortal_helpers.discard_tile(player_id=0, tile="N", tsumogiri=True),
        mortal_helpers.draw_unknown_tile(player_id=1),
        mortal_helpers.discard_tile(player_id=1, tile="C", tsumogiri=True),
        mortal_helpers.draw_unknown_tile(player_id=2),
        mortal_helpers.discard_tile(player_id=2, tile="F", tsumogiri=True),
        mortal_helpers.draw_unknown_tile(player_id=3),
        mortal_helpers.added_kan(player_id=3, tile="6m"),
    ]
    action = MORTAL_BOT_0.react_one(events=events)
    assert action["type"] == "hora"
    assert action["actor"] == 0
    assert action["target"] == 3


def test_cannot_robbing_a_closed_kan_13_orphans():
    events: list[MortalEvent] = [
        mortal_helpers.start_game(),
        mortal_helpers.start_hand(
            round_wind="E", dora_marker="5m", round_id=1, honba=0, riichi_sticks=0, dealer_id=0, scores=[25000] * 4,
            start_hands=[["1m", "9m", "1p", "9p", "1s", "9s", "E", "S", "W", "N", "P", "F", "F"], ["?"] * 13, ["?"] * 13, ["?"] * 13],
        ),
        mortal_helpers.draw_tile(player_id=0, tile="2m"),
        mortal_helpers.discard_tile(player_id=0, tile="2m", tsumogiri=True),
        mortal_helpers.draw_unknown_tile(player_id=1),
        mortal_helpers.closed_kan(player_id=1, tile="C"),
    ]
    action = MORTAL_BOT_0.react_one(events=events)
    assert action["type"] != "hora"
