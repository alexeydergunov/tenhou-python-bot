import json
import logging
import sys

from mortal.mortal_bot import MortalBot
from mortal.mortal_helpers import MortalEvent


# usage:
# cd project
# python3 mortal/mortal_analyze_log.py 2 < mortal/log_examples/example_1.jsonl
# python3 mortal/mortal_analyze_log.py 2 < mortal/log_examples/example_2.jsonl
# (where 2 is player_id, from 0 to 3)
def main():
    player_id = int(sys.argv[1])
    logging.info(f"Player id: {player_id}")
    assert 0 <= player_id <= 3
    bot = MortalBot(player_id=player_id)

    events: list[MortalEvent] = []
    for line in sys.stdin:
        event: MortalEvent = json.loads(line.strip())
        events.append(event)

    for return_action in bot.react_all(events=events, with_meta=False):
        return_action_str = json.dumps(return_action, separators=(",", ":"))
        sys.stdout.write(return_action_str + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
