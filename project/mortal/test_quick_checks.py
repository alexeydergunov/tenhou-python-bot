from mortal.mortal_player import MortalPlayer


def split_hand(hand_str: str) -> list[str]:
    hand = []
    i = 0
    while i < len(hand_str):
        if hand_str[i].isdigit():
            hand.append(hand_str[i:i + 2])
            i += 2
        else:
            hand.append(hand_str[i:i + 1])
            i += 1
    return hand


def check(hand_str: str) -> bool:
    return MortalPlayer.quick_check_winning_hand_structure(hand=split_hand(hand_str=hand_str))


def test_13_orphans():
    assert check(hand_str="1m9m1p9p1s9sESWNPFC1m") is True
    assert check(hand_str="1m9m1p9p1s9sESWNPFCE") is True
    assert check(hand_str="1m9m1p9p1s9sESWNPF1m1m") is False
    assert check(hand_str="1m9m1p9p1s9sESWNPFC2m") is False


def test_7_pairs():
    assert check(hand_str="1m1m2m2m3m3m4m4m5m5m8m8m9m9m") is True
    assert check(hand_str="1m1m2m2m3m3m4m4m5m5m9m9m9m9m") is False
    assert check(hand_str="1m1m2m2m3m3m4m4m5m5m8m9m9m9m") is False


def test_normal():
    assert check(hand_str="1m1m2m2m3m3m4p5p6pEEE8s8s") is True
    assert check(hand_str="1m2m3m4m5m6m7m8m9mEEE7s8s") is False
    assert check(hand_str="1m1m1m2m2m2m3m3m3m4m4m4m5m5m") is True
    assert check(hand_str="1m1m2m2m2m3m3m3m4m4m4m5m5m5m") is True
    assert check(hand_str="EEESSSWWWNNNPP") is True
    assert check(hand_str="EEESSSWWWNNNPC") is False
    assert check(hand_str="1m1m") is True
    assert check(hand_str="1m2m") is False
    assert check(hand_str="1m1m1m2m2m") is True
    assert check(hand_str="1m1m1m2m3m") is True
    assert check(hand_str="1m1m2m2m3m") is False
    assert check(hand_str="1m2m2m2m3m") is True
    assert check(hand_str="1m1m2m3m3m") is False
    assert check(hand_str="1m1m3m3m3m") is True
    assert check(hand_str="1m2m3m3m3m") is True
    assert check(hand_str="1m1m1m2m2m3m3m3m") is True
    assert check(hand_str="1m1m1m2m3m3m3m4m") is True
    assert check(hand_str="1m2m3m4m4m5m6m7m") is True
    assert check(hand_str="1m2m3m4m5m6m6m7m") is False
    assert check(hand_str="1m2m3m4m5m6m7m7m") is True
    assert check(hand_str="1m1m1m2m3m4m5m6m7m8m9m9m9m1m") is True
    assert check(hand_str="1m1m1m2m3m4m5m6m7m8m9m9m9m2m") is True
    assert check(hand_str="1m1m1m2m3m4m5m6m7m8m9m9m9m3m") is True
    assert check(hand_str="1m1m1m2m3m4m5m6m7m8m9m9m9m4m") is True
    assert check(hand_str="1m1m1m2m3m4m5m6m7m8m9m9m9m5m") is True
    assert check(hand_str="1m1m1m2m3m4m5m6m7m8m9m9m9m6m") is True
    assert check(hand_str="1m1m1m2m3m4m5m6m7m8m9m9m9m7m") is True
    assert check(hand_str="1m1m1m2m3m4m5m6m7m8m9m9m9m8m") is True
    assert check(hand_str="1m1m1m2m3m4m5m6m7m8m9m9m9m9m") is True
    assert check(hand_str="1m2m2m2m3m1p2p2p2p3pEEE2m") is True
    assert check(hand_str="1m2m2m2m3m1p2p2p2p3pEEE2p") is True
    assert check(hand_str="1m2m2m2m3m1p2p2p2p3pEEEE") is False
    assert check(hand_str="1m2m2m2m3m1p2p2p2p3pEESS") is False
