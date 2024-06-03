from collections import defaultdict
from typing import Optional

from mahjong.constants import EAST, NORTH, WEST, SOUTH
from mahjong.meld import Meld

from game.ai.configs.bot_mortal import MortalConfig
from game.ai.configs.default import BotDefaultConfig
from game.table import Table
from mortal.mortal_bot import MortalBot
from mortal.mortal_helpers import MortalEvent
from game.player import Player

import mortal.mortal_helpers as mortal_helpers
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

    def log_last_n_events(self, count: int):
        for event in self.events[-count:]:
            self.logger.logger.info("> %s", event)

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
        round_id: int = self.table.round_wind_number % 4 + 1
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
        tile: str = mortal_helpers.convert_tile_to_mortal(tile_136=tile_136)

        self.logger.logger.info("Called draw_tile(), tile: %s", tile)
        self.logger.logger.info("Last previous events:")
        self.log_last_n_events(count=3)

        self.our_tiles_map[tile].append(tile_136)
        event = mortal_helpers.draw_tile(player_id=self.seat, tile=tile)
        self.events.append(event)
        self.logger.logger.info("Our closed tiles after draw_tile(): %s", self.get_our_tiles_list())

    def discard_tile(self, discard_tile: Optional[int] = None, force_tsumogiri: bool = False) -> tuple[int, bool]:
        self.logger.logger.info("Called discard_tile(), force_tsumogiri = %s", force_tsumogiri)
        self.logger.logger.info("Our closed tiles before discard_tile(): %s", self.get_our_tiles_list())
        self.logger.logger.info("Last previous events:")
        self.log_last_n_events(count=12)

        action = self.bot.react_one(events=self.events, with_meta=True)
        self.logger.logger.info("Bot action: %s", action)

        with_riichi = False
        if action["type"] == "reach":
            with_riichi = True
            self.events.append(mortal_helpers.declare_riichi(player_id=self.seat))
            action = self.bot.react_one(events=self.events, with_meta=True)
            self.logger.logger.info("Bot action after riichi: %s", action)

        assert action["type"] == "dahai"
        discarded_tile: str = action["pai"]
        tsumogiri: bool = action["tsumogiri"]
        if force_tsumogiri:
            assert tsumogiri is True
        event = mortal_helpers.discard_tile(player_id=self.seat, tile=discarded_tile, tsumogiri=tsumogiri)
        self.events.append(event)

        if with_riichi:
            # if not successful, will be cleared on next hand
            self.events.append(mortal_helpers.successful_riichi(player_id=self.seat))

        if tsumogiri:
            # tile ids are added to the end of this list
            discarded_tile_136 = self.our_tiles_map[discarded_tile].pop()
        else:
            # remove tile that was in the hand from the earliest moment
            discarded_tile_136 = self.our_tiles_map[discarded_tile].pop(0)
        super().discard_tile(discard_tile=discarded_tile_136, force_tsumogiri=force_tsumogiri)  # maintain table state
        return discarded_tile_136, with_riichi

    def should_call_kan(self, drawn_tile_136: int, open_kan: bool, from_riichi: bool = False) -> Optional[tuple[str, int]]:
        self.logger.logger.info("Called should_call_kan()")
        action = self.bot.react_one(events=self.events, with_meta=True)
        self.logger.logger.info("Bot action: %s", action)
        if action["type"] in {"ankan", "daiminkan", "kakan"}:
            if action["type"] == "kakan":
                kan_tile: str = action["pai"]  # tile that is added from a hand
                tile_136: int = self.our_tiles_map[kan_tile][0]
                return MeldPrint.SHOUMINKAN, tile_136
            if action["type"] == "daiminkan":
                return MeldPrint.KAN, drawn_tile_136  # drawn_tile_136 is not used in client
            if action["type"] == "ankan":
                kan_tile: str = action["consumed"][1]  # definitely not a red five, and we surely have it in hand
                tile_136: int = self.our_tiles_map[kan_tile][0]
                return MeldPrint.KAN, tile_136
        return None

    def should_call_win(self,
                        tile_136: int,
                        is_tsumo: bool,
                        enemy_seat: Optional[int] = None,
                        is_chankan: bool = False,
                        is_tsumogiri: bool = False) -> bool:
        tile: str = mortal_helpers.convert_tile_to_mortal(tile_136=tile_136)

        self.logger.logger.info("Called should_call_win(), tile: %s, is_tsumo: %s, enemy_seat: %s, is_chankan: %s, is_tsumogiri: %s",
                                tile, is_tsumo, enemy_seat, is_chankan, is_tsumogiri)
        self.logger.logger.info("Last previous events:")
        self.log_last_n_events(count=12)

        # when enemies declare open or added kans, kandora event comes before their discards, we need to remove it
        previous_kan_dora_event: Optional[MortalEvent] = None
        if self.events[-1]["type"] == "dora":
            if self.events[-2]["type"] == "tsumo" and self.events[-2]["actor"] == enemy_seat:
                if self.events[-3]["type"] in {"kakan", "daiminkan"} and self.events[-3]["actor"] == enemy_seat:
                    self.logger.logger.info("Found sequence %s -> tsumo -> dora before player %s discard in win check, temporarily delete dora event",
                                            self.events[-3]["type"], enemy_seat)
                    previous_kan_dora_event = self.events[-1]
                    self.events.pop()

        # client first check win, then actually draws/discards tile
        new_events = []
        if is_tsumo:
            new_events.append(mortal_helpers.draw_tile(player_id=self.seat, tile=tile))
        else:
            assert 0 <= enemy_seat <= 3
            assert enemy_seat != self.seat
            if is_chankan:
                assert self.events[-1]["type"] == "kakan"
            else:
                new_events.append(mortal_helpers.discard_tile(player_id=enemy_seat, tile=tile, tsumogiri=is_tsumogiri))

        self.events.extend(new_events)
        action = self.bot.react_one(events=self.events, with_meta=True)
        self.logger.logger.info("Bot action: %s", action)

        for _ in range(len(new_events)):
            self.events.pop()

        # return to initial state, kandora event will be moved after discard in client's code
        if previous_kan_dora_event is not None:
            self.events.append(previous_kan_dora_event)
            assert self.events[-1] == previous_kan_dora_event
            assert self.events[-2]["type"] == "tsumo"
            assert self.events[-3]["type"] in {"kakan", "daiminkan"}

        self.logger.logger.info("At the end of win check, we returned list of events to its initial state:")
        self.log_last_n_events(count=6)

        return action["type"] == "hora"

    def should_call_kyuushu_kyuuhai(self) -> bool:
        self.logger.logger.info("Called should_call_kyuushu_kyuuhai()")
        action = self.bot.react_one(events=self.events, with_meta=True)
        self.logger.logger.info("Bot action: %s", action)
        return action["type"] == "ryukyoku"

    def try_to_call_meld(self, tile: int, is_kamicha_discard: bool) -> tuple[Optional[Meld], Optional[int]]:
        self.logger.logger.info("Called try_to_call_meld()")
        self.logger.logger.info("Last previous events:")
        self.log_last_n_events(count=3)

        call_action = self.bot.react_one(events=self.events, with_meta=True)
        self.logger.logger.info("Bot call action: %s", call_action)

        if call_action["type"] == "chi":
            self.events.append(mortal_helpers.chi(player_id=self.seat, tile=call_action["pai"], chi_tiles=call_action["consumed"]))
            meld_type = MeldPrint.CHI
        elif call_action["type"] == "pon":
            self.events.append(mortal_helpers.pon(player_id=self.seat, from_whom=call_action["target"], tile=call_action["pai"], pon_tiles=call_action["consumed"]))
            meld_type = MeldPrint.PON
        else:
            return None, None

        discard_action = self.bot.react_one(events=self.events, with_meta=True)
        self.logger.logger.info("Bot discard action: %s", discard_action)
        discard_tile: int = self.our_tiles_map[discard_action["pai"]][0]  # will be popped in discard_tile(), pop(0) because not a tsumogiri

        consumed_tiles: list[int] = [self.our_tiles_map[t].pop() for t in call_action["consumed"]]
        assert discard_tile not in consumed_tiles
        meld = Meld(meld_type=meld_type, tiles=consumed_tiles + [tile])

        # add tiles back - they will be deleted later in client's code
        # reason: if we call a chi, someone may call a pon, and out chi becomes invalid
        for tile_136 in reversed(consumed_tiles):
            self.our_tiles_map[mortal_helpers.convert_tile_to_mortal(tile_136=tile_136)].append(tile_136)

        self.events.pop()  # will be added in a client when we get a message about meld
        return meld, discard_tile
