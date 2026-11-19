import numpy as np

from sh_hand.erkennung import Entpreller, hand_im_bild


def szene(hand):
    d = np.full((480, 640), 3000, np.uint16)
    d[140:440, 270:380] = 1800                    # Körper
    if hand:
        d[40:120, 390:430] = 1400                 # Hand 40 cm davor, oben
    return d


def test_hand_erkannt():
    erkannt, x, y = hand_im_bild(szene(True))
    assert erkannt and 0.6 < x < 0.68 and y < 0.25


def test_ohne_hand():
    assert not hand_im_bild(szene(False))[0]


def test_leeres_bild():
    assert not hand_im_bild(np.zeros((424, 512), np.uint16))[0]


def test_entpreller():
    e = Entpreller(3)
    assert [e(v) for v in (True, True, True, True, False, True, False, False, False)] == \
        [None, None, True, None, None, None, None, None, False]
