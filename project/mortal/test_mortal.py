from mahjong.constants import FIVE_RED_MAN, FIVE_RED_PIN, FIVE_RED_SOU

import mortal.mortal_helpers as mortal_helpers
from mortal.mortal_bot import MortalBot

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
