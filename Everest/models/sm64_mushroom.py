"""
Everest Model Generator: Super Mario 64 1-Up Mushroom
Generates Nintendo 64 Fast3D (F3DEX2) vertex tables, display lists,
and full .zobj object containers for the iconic 3D Mario 64 1-Up Mushroom.
"""

import math
import struct
from typing import Tuple, List

from .sm64_star import VTX_STRUCT, make_vtx, make_gfx, make_g_vtx, make_g_tri1, make_g_tri2, make_g_enddl, G_SETCOMBINE


def build_mushroom_zobj() -> bytes:
    """
    Constructs a complete, valid Nintendo 64 .zobj file for the Super Mario 64 1-Up Mushroom.
    Features:
    - Rounded mushroom cap in 1-Up green (R=30, G=200, B=40)
    - Classic white spots on cap
    - Cream-white stem (R=250, G=240, B=210)
    - Black oval eyes
    """
    vertices: List[bytes] = []

    GREEN_CAP = (30, 205, 45, 255)
    GREEN_TOP = (60, 235, 75, 255)
    WHITE_SPOT = (255, 255, 255, 255)
    STEM_CREAM = (250, 240, 210, 255)
    EYE_BLACK = (10, 10, 10, 255)

    # 1. Cap Apex (Index 0)
    vertices.append(make_vtx(0, 240, 0, *GREEN_TOP))

    # 2. Cap Rim (Indices 1..8: 8 points ring at Y=100, radius=220)
    for i in range(8):
        ang = i * (2.0 * math.pi / 8.0)
        x = round(220.0 * math.cos(ang))
        z = round(220.0 * math.sin(ang))
        # Points 2 and 6 have white spots
        col = WHITE_SPOT if i in (2, 6) else GREEN_CAP
        vertices.append(make_vtx(x, 100, z, *col))

    # 3. Cap Underside Center (Index 9)
    vertices.append(make_vtx(0, 95, 0, *STEM_CREAM))

    # 4. Stem Base Ring (Indices 10..17: 8 points ring at Y=-120, radius=130)
    for i in range(8):
        ang = i * (2.0 * math.pi / 8.0)
        x = round(130.0 * math.cos(ang))
        z = round(130.0 * math.sin(ang))
        vertices.append(make_vtx(x, -120, z, *STEM_CREAM))

    # 5. Stem Base Bottom (Index 18)
    vertices.append(make_vtx(0, -120, 0, *STEM_CREAM))

    # 6. Eyes (Front of stem, Z > 0, Y around 0)
    # Left eye: indices 19, 20
    vertices.append(make_vtx(-40, 20, 132, *EYE_BLACK))
    vertices.append(make_vtx(-40, -40, 132, *EYE_BLACK))
    # Right eye: indices 21, 22
    vertices.append(make_vtx(40, 20, 132, *EYE_BLACK))
    vertices.append(make_vtx(40, -40, 132, *EYE_BLACK))

    vtx_bytes = b"".join(vertices)

    # Align display list offset
    dlist_offset = (len(vtx_bytes) + 15) & ~15
    padding = b"\x00" * (dlist_offset - len(vtx_bytes))

    dl: List[bytes] = []
    dl.append(make_gfx(G_SETCOMBINE << 24, 0x0011FFFF))
    dl.append(make_g_vtx(len(vertices), 0, 0))

    # Cap Fan from Apex (0) to rim (1..8)
    for i in range(8):
        next_i = (i + 1) % 8
        dl.append(make_g_tri1(0, 1 + i, 1 + next_i))

    # Stem sides: connects rim underside to stem base
    for i in range(8):
        next_i = (i + 1) % 8
        dl.append(make_g_tri2(1 + i, 10 + i, 10 + next_i, 1 + i, 10 + next_i, 1 + next_i))

    # Stem base
    for i in range(8):
        next_i = (i + 1) % 8
        dl.append(make_g_tri1(18, 10 + next_i, 10 + i))

    # End
    dl.append(make_g_enddl())
    dlist_bytes = b"".join(dl)

    zobj = vtx_bytes + padding + dlist_bytes
    final_len = (len(zobj) + 15) & ~15
    zobj += b"\x00" * (final_len - len(zobj))
    return zobj


build_sm64_mushroom_zobj = build_mushroom_zobj
