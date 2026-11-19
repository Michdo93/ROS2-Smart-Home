"""Kapitel 13: sensor_msgs/Image in ein NumPy-Array umwandeln und zurück – ohne cv_bridge.

Die Zeilenlänge 'step' kann größer sein als Breite x Bytes pro Pixel (Auffüllbytes am
Zeilenende). Darum erst Zeilen bilden, dann auf die Breite zuschneiden.
"""
import numpy as np
from sensor_msgs.msg import Image

# encoding -> (Datentyp, Kanäle)
FORMATE = {"rgb8": (np.uint8, 3), "bgr8": (np.uint8, 3), "mono8": (np.uint8, 1),
           "mono16": (np.uint16, 1), "16UC1": (np.uint16, 1), "32FC1": (np.float32, 1)}


def bild_zu_array(m: Image) -> np.ndarray:
    typ, kanaele = FORMATE[m.encoding]
    dtype = np.dtype(typ).newbyteorder(">" if m.is_bigendian else "<")
    zeilen = np.frombuffer(m.data, np.uint8).reshape(m.height, m.step)
    pixel = zeilen[:, : m.width * kanaele * dtype.itemsize].copy().view(dtype)
    return pixel.reshape(m.height, m.width, kanaele) if kanaele > 1 else pixel


def array_zu_bild(a: np.ndarray, encoding: str, kopf=None) -> Image:
    m = Image(encoding=encoding, height=a.shape[0], width=a.shape[1])
    if kopf is not None:
        m.header = kopf
    m.is_bigendian = 0
    m.step = a.strides[0]
    m.data = np.ascontiguousarray(a).tobytes()
    return m
