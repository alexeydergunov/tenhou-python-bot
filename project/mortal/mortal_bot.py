import json
from typing import Optional

import mortal.mortal_lib.model as mortal_model
from mortal.mortal_helpers import MortalEvent


class MortalBot:
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.model = mortal_model.load_model(player_id)

    def react_all(self, events: list[MortalEvent], with_meta: bool = True) -> list[MortalEvent]:
        return_actions: list[MortalEvent] = []

        for event in events:
            event_str = json.dumps(event, separators=(",", ":"))
            return_action_str: Optional[str] = self.model.react(event_str)
            if return_action_str is not None:
                return_action: MortalEvent = json.loads(return_action_str)
                return_actions.append(return_action)

        if len(return_actions) == 0:
            return_actions.append({"type": "none"})

        if not with_meta:
            for return_action in return_actions:
                if "meta" in return_action:
                    return_action.pop("meta")

        return return_actions

    def react_one(self, events: list[MortalEvent], with_meta: bool = True) -> MortalEvent:
        return_actions = self.react_all(events=events, with_meta=with_meta)
        return return_actions[-1]
