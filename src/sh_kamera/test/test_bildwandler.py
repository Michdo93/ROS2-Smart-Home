"""Kapitel 13: Tests für die Umwandlung Image <-> NumPy."""
import numpy as np
from sensor_msgs.msg import Image

from sh_kamera.bildwandler import array_zu_bild, bild_zu_array


def test_farbbild_hin_und_zurueck():
    a = np.random.randint(0, 256, (48, 64, 3), np.uint8)
    assert np.array_equal(bild_zu_array(array_zu_bild(a, "rgb8")), a)


def test_tiefenbild_millimeter():
    a = np.array([[0, 500], [3000, 65535]], np.uint16)
    m = array_zu_bild(a, "16UC1")
    assert m.step == 4 and len(m.data) == 8
    assert np.array_equal(bild_zu_array(m), a)


def test_auffuellbytes_am_zeilenende():
    # 3 Pixel rgb8 = 9 Byte Nutzdaten, aber step 12 (3 Füllbytes je Zeile)
    zeilen = np.zeros((2, 12), np.uint8)
    zeilen[:, :9] = np.arange(9)
    m = Image(height=2, width=3, encoding="rgb8", step=12, data=zeilen.tobytes())
    a = bild_zu_array(m)
    assert a.shape == (2, 3, 3) and a[1, 2].tolist() == [6, 7, 8]


def test_big_endian():
    a = np.array([[1000, 2000]], np.uint16)
    m = Image(height=1, width=2, encoding="16UC1", is_bigendian=1, step=4,
              data=a.astype(">u2").tobytes())
    assert bild_zu_array(m).tolist() == [[1000, 2000]]
