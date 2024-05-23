import json
import logging
import sys
from typing import Any, Optional

import mortal_lib.model as mortal_model


class Bot:
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.model = mortal_model.load_model(player_id)

    def react_all(self, events: list[dict[str, Any]], with_meta: bool = True) -> list[dict[str, Any]]:
        return_actions: list[dict[str, Any]] = []

        for event in events:
            event_str = json.dumps(event, separators=(",", ":"))
            return_action_str: Optional[str] = self.model.react(event_str)
            if return_action_str is not None:
                return_action: dict[str, Any] = json.loads(return_action_str)
                return_actions.append(return_action)

        if len(return_actions) == 0:
            return_actions.append({"type": "none"})

        if not with_meta:
            for return_action in return_actions:
                if "meta" in return_action:
                    return_action.pop("meta")

        return return_actions

    def react_one(self, events: list[dict[str, Any]], with_meta: bool = True) -> dict[str, Any]:
        return_actions = self.react_all(events=events, with_meta=with_meta)
        return return_actions[-1]


# usage:
# bot_single_action.py 2 < log_examples/example_1.jsonl
# bot_single_action.py 2 < log_examples/example_2.jsonl
# (where 2 is player_id, from 0 to 3)
def main():
    player_id = int(sys.argv[1])
    logging.info(f"Player id: {player_id}")
    assert player_id in range(4)
    bot = Bot(player_id=player_id)

    events: list[dict[str, Any]] = []
    for line in sys.stdin:
        event: dict[str, Any] = json.loads(line.strip())
        events.append(event)

    for return_action in bot.react_all(events=events, with_meta=False):
        return_action_str = json.dumps(return_action, separators=(",", ":"))
        sys.stdout.write(return_action_str + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
