"""Kapitel 19: Handerkennung im Tiefenbild – nur numpy, ohne ROS testbar.

Idee: Eine erhobene Hand ist eine kleine Fläche, die deutlich vor dem Körper liegt.
1. Gültige Tiefenwerte zwischen 0,5 und 4 m.
2. Die vorderste Ebene: alle Punkte bis 10 cm hinter dem nächsten Punkt.
3. Hand = vordere Ebene ist klein (0,3 ... 5 % des Bilds), liegt in der oberen Bildhälfte
   und dahinter (25 cm bis 1 m) steht ein großer Körper (mehr als 2 % des Bilds).
"""
import numpy as np


def hand_im_bild(tiefe_mm, nah=500, fern=4000):
    """Gibt (erkannt, x, y) zurück – x und y als Bildanteil 0 ... 1."""
    d = tiefe_mm.astype(np.int32)
    gueltig = (d > nah) & (d < fern)
    if gueltig.sum() < 0.05 * d.size:
        return False, 0.0, 0.0
    vorne = np.percentile(d[gueltig], 0.5)
    ebene = gueltig & (d <= vorne + 100)
    koerper = gueltig & (d > vorne + 250) & (d < vorne + 1000)
    anteil, anteil_koerper = ebene.mean(), koerper.mean()
    if not (0.003 <= anteil <= 0.05 and anteil_koerper > 0.02):
        return False, 0.0, 0.0
    ys, xs = np.nonzero(ebene)
    x, y = xs.mean() / d.shape[1], ys.mean() / d.shape[0]
    return bool(y < 0.5), float(x), float(y)


class Entpreller:
    """Meldet einen Wechsel erst, wenn er n Bilder hintereinander besteht."""

    def __init__(self, n=3):
        self.n, self.zustand, self.zaehler = n, False, 0

    def __call__(self, wert):
        if wert == self.zustand:
            self.zaehler = 0
            return None
        self.zaehler += 1
        if self.zaehler >= self.n:
            self.zustand, self.zaehler = wert, 0
            return wert
        return None
