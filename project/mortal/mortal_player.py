from collections import defaultdict
from typing import Optional

from mahjong.constants import EAST, NORTH, WEST, SOUTH
from mahjong.meld import Meld

from game.ai.configs.bot_mortal import MortalConfig
from game.ai.configs.default import BotDefaultConfig
from game.table import Table
from mortal.bot_single_action import Bot as MortalBot
from mortal.mortal_helpers import MortalEvent
from project.game.player import Player

import project.mortal.mortal_helpers as mortal_helpers
from utils.decisions_logger import MeldPrint


class MortalPlayer(Player):
    def __init__(self, table: Table, seat: int, dealer_seat: int, bot_config: Optional[BotDefaultConfig]):
        assert isinstance(bot_config, MortalConfig)
        self.events: list[MortalEvent] = []
        self.our_tiles_map: dict[str, list[int]] = defaultdict(list)
        super().__init__(table, seat, dealer_seat, bot_config)
        self.bot = MortalBot(player_id=seat)
        self.ai = None  # disable old MahjongAI class, will use MortalBot instead

    def get_our_tiles_list(self) -> list[str]:
        tiles = []
        for tile, tile_136_list in self.our_tiles_map.items():
            if len(tile_136_list) > 0:
                tiles.extend([tile] * len(tile_136_list))
        tiles.sort(key=lambda t: mortal_helpers.TILES.index(t))
        return tiles

    def erase_state(self):
        super().erase_state()
        self.events.clear()
        self.our_tiles_map.clear()

    def init_hand(self, tiles: list[int]):
        super().init_hand(tiles=tiles)

        round_wind: str = {
            EAST: "E",
            SOUTH: "S",
            WEST: "W",
            NORTH: "N",
        }[self.table.round_wind_tile]
        dora_marker: str = mortal_helpers.convert_tile_to_mortal(tile_136=self.table.dora_indicators[0])
        round_id: int = self.table.round_wind_number // 4 + 1
        honba: int = self.table.count_of_honba_sticks
        riichi_sticks: int = self.table.count_of_riichi_sticks
        dealer_id: int = self.dealer_seat
        scores: list[int] = [int(player.scores) for player in self.table.players]
        start_hands: list[list[str]] = [
            ["?"] * 13,
            ["?"] * 13,
            ["?"] * 13,
            ["?"] * 13,
        ]
        start_hands[self.seat].clear()
        for tile_136 in tiles:
            tile = mortal_helpers.convert_tile_to_mortal(tile_136=tile_136)
            start_hands[self.seat].append(tile)
            self.our_tiles_map[tile].append(tile_136)

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
        super().draw_tile(tile_136=tile_136)

        self.logger.logger.info("Called draw_tile()")
        self.logger.logger.info("Last previous events:")
        for event in self.events[-5:]:
            self.logger.logger.info("> %s", event)

        tile: str = mortal_helpers.convert_tile_to_mortal(tile_136=tile_136)
        self.our_tiles_map[tile].append(tile_136)
        event = mortal_helpers.draw_tile(player_id=self.seat, tile=tile)
        self.events.append(event)

    def discard_tile(self, discard_tile: Optional[int] = None, force_tsumogiri: bool = False) -> tuple[int, bool]:
        self.logger.logger.info("Called discard_tile()")
        self.logger.logger.info("Last previous events:")
        for event in self.events[-5:]:
            self.logger.logger.info("> %s", event)

        action = self.bot.react_one(events=self.events, with_meta=True)
        self.logger.logger.info("Bot action: %s", action)

        with_riichi = False
        if action["type"] == "reach":
            with_riichi = True
            self.events.append(mortal_helpers.declare_riichi(player_id=self.seat))
            action = self.bot.react_one(events=self.events, with_meta=True)
            self.logger.logger.info("Bot action: %s", action)

        assert action["type"] == "dahai"
        discarded_tile: str = action["pai"]
        event = mortal_helpers.discard_tile(player_id=self.seat, tile=discarded_tile, tsumogiri=force_tsumogiri)
        self.events.append(event)

        if with_riichi:
            # if not successful, will be cleared on next hand
            self.events.append(mortal_helpers.successful_riichi(player_id=self.seat))

        discarded_tile_136 = self.our_tiles_map[discarded_tile].pop()
        super().discard_tile(discard_tile=discarded_tile_136, force_tsumogiri=force_tsumogiri)  # maintain table state
        return discarded_tile_136, with_riichi

    def should_call_kan(self, tile: int, open_kan: bool, from_riichi: bool = False):
        self.logger.logger.info("Called should_call_kan()")
        action = self.bot.react_one(events=self.events, with_meta=True)
        self.logger.logger.info("Bot action: %s", action)
        return action["type"] in {"ankan", "kakan", "daiminkan"}

    def should_call_win(self,
                        tile_136: int,
                        is_tsumo: bool,
                        enemy_seat: Optional[int] = None,
                        is_chankan: bool = False,
                        is_tsumogiri: bool = False) -> bool:
        self.logger.logger.info("Called should_call_win()")
        tile: str = mortal_helpers.convert_tile_to_mortal(tile_136=tile_136)

        # client first check win, then actually draws/discards tile
        new_events = []
        if is_tsumo:
            new_events.append(mortal_helpers.draw_tile(player_id=self.seat, tile=tile))
        else:
            assert 0 <= enemy_seat <= 3
            assert enemy_seat != self.seat
            if is_chankan:
                new_events.append(mortal_helpers.added_kan(player_id=enemy_seat, tile=tile))
            else:
                new_events.append(mortal_helpers.draw_unknown_tile(player_id=enemy_seat))
                new_events.append(mortal_helpers.discard_tile(player_id=enemy_seat, tile=tile, tsumogiri=is_tsumogiri))

        self.events.extend(new_events)
        action = self.bot.react_one(events=self.events, with_meta=True)
        self.logger.logger.info("Bot action: %s", action)

        for _ in range(len(new_events)):
            self.events.pop()

        return action["type"] == "hora"

    def should_call_kyuushu_kyuuhai(self) -> bool:
        self.logger.logger.info("Called should_call_kyuushu_kyuuhai()")
        action = self.bot.react_one(events=self.events, with_meta=True)
        self.logger.logger.info("Bot action: %s", action)
        return action["type"] == "ryukyoku"

    def try_to_call_meld(self, tile: int, is_kamicha_discard: bool) -> tuple[Optional[Meld], Optional[int]]:
        self.logger.logger.info("Called try_to_call_meld()")
        self.logger.logger.info("Last previous events:")
        for event in self.events[-5:]:
            self.logger.logger.info("> %s", event)

        call_action = self.bot.react_one(events=self.events, with_meta=True)
        self.logger.logger.info("Bot call action: %s", call_action)

        if call_action["type"] == "none":
            return None, None

        if call_action["type"] == "chi":
            self.events.append(mortal_helpers.chi(player_id=self.seat, tile=call_action["pai"], chi_tiles=call_action["consumed"]))
            meld_type = MeldPrint.CHI
        elif call_action["type"] == "pon":
            self.events.append(mortal_helpers.pon(player_id=self.seat, tile=call_action["pai"], from_whom=call_action["target"]))
            meld_type = MeldPrint.PON
        elif call_action["type"] == "daiminkan":
            self.events.append(mortal_helpers.open_kan(player_id=self.seat, tile=call_action["pai"], from_whom=call_action["target"]))
            meld_type = MeldPrint.KAN
        else:
            return None, None

        discard_action = self.bot.react_one(events=self.events, with_meta=True)
        self.logger.logger.info("Bot discard action: %s", discard_action)
        discard_tile: int = self.our_tiles_map[discard_action["pai"]][-1]  # will be popped in discard_tile()

        consumed_tiles: list[int] = [self.our_tiles_map[t].pop() for t in call_action["consumed"]]
        meld = Meld(meld_type=meld_type, tiles=consumed_tiles + [tile])

        self.events.pop()  # will be added in a client when we get a message about meld
        return meld, discard_tile
