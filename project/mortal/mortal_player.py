from typing import Any, Optional

from mahjong.constants import EAST, NORTH, WEST, SOUTH
from mahjong.meld import Meld

from game.ai.configs.default import BotDefaultConfig
from game.table import Table
from mortal.bot_single_action import Bot as MortalBot
from mortal.mortal_helpers import MortalEvent
from project.game.player import Player

import project.mortal.mortal_helpers as mortal_helpers
from utils.decisions_logger import MeldPrint


class MortalPlayer(Player):
    def __init__(self, table: Table, seat: int, dealer_seat: int, bot_config: Optional[BotDefaultConfig]):
        super().__init__(table, seat, dealer_seat, bot_config)
        self.events: list[MortalEvent] = []
        self.bot = MortalBot(player_id=seat)

    def erase_state(self):
        self.events.clear()

    def init_hand(self, tiles: list[int]):
        round_wind: str = {
            EAST: "E",
            SOUTH: "S",
            WEST: "W",
            NORTH: "N",
        }[self.table.round_wind_tile]
        dora_marker: str = mortal_helpers.convert_tile_to_mortal(tile_136=self.table.dora_indicators[0])
        round_id: int = (self.table.round_wind_number + 1) // 4
        honba: int = self.table.count_of_honba_sticks
        riichi_sticks: int = self.table.count_of_riichi_sticks
        dealer_id: int = self.dealer_seat
        scores: list[int] = [player.scores for player in self.table.players]
        start_hands: list[list[str]] = [
            ["?"] * 13,
            ["?"] * 13,
            ["?"] * 13,
            ["?"] * 13,
        ]
        start_hands[self.seat] = [mortal_helpers.convert_tile_to_mortal(tile_136=tile_136) for tile_136 in tiles]

        event = mortal_helpers.start_hand(
            round_wind=round_wind,
            dora_marker=dora_marker,
            round_id=round_id,
            honba=honba,
            riichi_sticks=riichi_sticks,
            dealer_id=dealer_id,
            scores=scores,
            start_hands=start_hands,
        )
        self.events.append(event)

    def draw_tile(self, tile_136: int):
        tile: str = mortal_helpers.convert_tile_to_mortal(tile_136=tile_136)
        event = mortal_helpers.draw_tile(player_id=self.seat, tile=tile)
        self.events.append(event)

    def discard_tile(self, discard_tile: Optional[int] = None, force_tsumogiri: bool = False) -> tuple[int, bool]:
        actions = self.bot.react_all(events=self.events, with_meta=True)
        assert actions[-1]["type"] == "dahai"
        discarded_tile: str = actions[-1]["pai"]
        with_riichi: bool = (len(actions) > 1) and (actions[-2]["type"] == "reach")
        event = mortal_helpers.discard_tile(player_id=self.seat, tile=discarded_tile, tsumogiri=force_tsumogiri)
        if with_riichi:
            self.events.append(mortal_helpers.declare_riichi(player_id=self.seat))
        self.events.append(event)
        if with_riichi:
            # if not successful, will be cleared on next hand
            self.events.append(mortal_helpers.successful_riichi(player_id=self.seat))
        return mortal_helpers.convert_tile_from_mortal(tile=discarded_tile), with_riichi

    def should_call_kan(self, tile: int, open_kan: bool, from_riichi: bool = False):
        action = self.bot.react_one(events=self.events, with_meta=False)
        return action["type"] in {"ankan", "kakan", "daiminkan"}

    def should_call_win(self,
                        tile: int,
                        is_tsumo: bool,
                        enemy_seat: Optional[int] = None,
                        is_chankan: bool = False) -> bool:
        action = self.bot.react_one(events=self.events, with_meta=False)
        return action["type"] == "hora"

    def should_call_kyuushu_kyuuhai(self) -> bool:
        action = self.bot.react_one(events=self.events, with_meta=False)
        return action["type"] == "ryukyoku"

    def try_to_call_meld(self, tile: int, is_kamicha_discard: bool) -> tuple[Optional[Meld], Optional[int]]:
        actions = self.bot.react_all(events=self.events, with_meta=False)
        if len(actions) <= 1 or actions[-1]["type"] == "none":
            return None, None

        call_action = actions[-2]
        assert call_action["type"] in {"chi", "pon", "daiminkan"}
        discard_action = actions[-1]
        discard_tile: int = mortal_helpers.convert_tile_from_mortal(discard_action["pai"])

        meld_type = {
            "chi": MeldPrint.CHI,
            "pon": MeldPrint.PON,
            "daiminkan": MeldPrint.KAN,
        }[call_action["type"]]

        consumed_tiles: list[int] = [mortal_helpers.convert_tile_from_mortal(tile=t) for t in call_action["consumed"]]
        meld = Meld(meld_type=meld_type, tiles=consumed_tiles)
        return meld, discard_tile
