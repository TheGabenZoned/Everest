"""
Everest Model Generator: Super Mario 64 Bowser Castle Key
Generates Nintendo 64 Fast3D (F3DEX2) vertex tables, display lists,
and full .zobj object containers for the SM64 Bowser Key.
"""

import math
import struct
from typing import List

from .sm64_star import VTX_STRUCT, make_vtx, make_gfx, make_g_vtx, make_g_tri1, make_g_tri2, make_g_enddl, G_SETCOMBINE


def build_key_zobj() -> bytes:
    """
    Constructs a complete, valid Nintendo 64 .zobj file for the Super Mario 64 Bowser Key.
    Features:
    - Gold ornate bow head
    - Long golden shaft
    - Bowser-toothed bit
    """
    vertices: List[bytes] = []

    KEY_GOLD = (235, 190, 30, 255)
    KEY_LIGHT = (255, 230, 90, 255)
    KEY_DARK = (180, 140, 15, 255)

    # 1. Bow Ring (Top of key)
    # Ring center: Y=180. 6 outer ring vertices and 6 inner vertices
    r_out = 90.0
    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0)
        x = round(r_out * math.cos(ang))
        y = round(180.0 + r_out * math.sin(ang))
        vertices.append(make_vtx(x, y, 15, *KEY_LIGHT))

    for i in range(6):
        ang = i * (2.0 * math.pi / 6.0)
        x = round(r_out * math.cos(ang))
        y = round(180.0 + r_out * math.sin(ang))
        vertices.append(make_vtx(x, y, -15, *KEY_DARK))

    # 2. Shaft (Y from 90 down to -140)
    vertices.append(make_vtx(-15, 90, 15, *KEY_GOLD))   # 12
    vertices.append(make_vtx(15, 90, 15, *KEY_GOLD))    # 13
    vertices.append(make_vtx(15, -140, 15, *KEY_GOLD))  # 14
    vertices.append(make_vtx(-15, -140, 15, *KEY_GOLD)) # 15

    # 3. Bit (Teeth sticking out to the right)
    vertices.append(make_vtx(15, -100, 15, *KEY_GOLD))  # 16
    vertices.append(make_vtx(65, -100, 15, *KEY_LIGHT)) # 17
    vertices.append(make_vtx(65, -135, 15, *KEY_LIGHT)) # 18
    vertices.append(make_vtx(15, -135, 15, *KEY_GOLD))  # 19

    vtx_bytes = b"".join(vertices)

    dlist_offset = (len(vtx_bytes) + 15) & ~15
    padding = b"\x00" * (dlist_offset - len(vtx_bytes))

    dl: List[bytes] = []
    dl.append(make_gfx(G_SETCOMBINE << 24, 0x0011FFFF))
    dl.append(make_g_vtx(len(vertices), 0, 0))

    # Bow Ring front/back
    dl.append(make_g_tri2(0, 1, 2, 0, 2, 3))
    dl.append(make_g_tri2(0, 3, 4, 0, 4, 5))
    dl.append(make_g_tri2(6, 7, 8, 6, 8, 9))
    dl.append(make_g_tri2(6, 9, 10, 6, 10, 11))

    # Shaft Quad
    dl.append(make_g_tri2(12, 13, 14, 12, 14, 15))

    # Bit Quad
    dl.append(make_g_tri2(16, 17, 18, 16, 18, 19))

    dl.append(make_g_enddl())
    dlist_bytes = b"".join(dl)

    zobj = vtx_bytes + padding + dlist_bytes
    final_len = (len(zobj) + 15) & ~15
    zobj += b"\x00" * (final_len - len(zobj))
    return zobj


build_sm64_key_zobj = build_key_zobj
