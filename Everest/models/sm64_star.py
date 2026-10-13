"""
Everest Model Generator: Super Mario 64 Power Star
Generates Nintendo 64 Fast3D (F3DEX2) vertex tables, display lists,
and full .zobj object containers for the iconic 3D Mario 64 Power Star.
"""

import math
import struct
from typing import Tuple, List

# Vertex structure: 16 bytes (x, y, z, flag, s, t, r, g, b, a)
VTX_STRUCT = struct.Struct('>hhhHhhBBBB')
# Gfx command structure: 8 bytes (w0, w1)
GFX_STRUCT = struct.Struct('>II')

# F3DEX2 Microcode Command Constants
G_VTX = 0x01
G_TRI1 = 0x05
G_TRI2 = 0x06
G_SETCOMBINE = 0xFC
G_SETPRIMCOLOR = 0xFA
G_ENDDL = 0xDF


def make_vtx(x: int, y: int, z: int, r: int = 255, g: int = 220, b: int = 20, a: int = 255, s: int = 0, t: int = 0) -> bytes:
    """Pack an N64 vertex structure."""
    return VTX_STRUCT.pack(int(x), int(y), int(z), 0, int(s), int(t), int(r), int(g), int(b), int(a))


def make_gfx(w0: int, w1: int) -> bytes:
    """Pack an N64 display list command."""
    return GFX_STRUCT.pack(w0, w1)


def make_g_vtx(vtx_count: int, dest_idx: int, segment_offset: int) -> bytes:
    """F3DEX2 gSPVertex command to load vertices into vertex buffer."""
    w0 = (G_VTX << 24) | ((vtx_count & 0xFF) << 12) | ((dest_idx & 0x7F) << 1)
    w1 = 0x06000000 | (segment_offset & 0x00FFFFFF)
    return make_gfx(w0, w1)


def make_g_tri1(v0: int, v1: int, v2: int) -> bytes:
    """F3DEX2 gSP1Triangle command."""
    w0 = (G_TRI1 << 24) | ((v0 * 2) << 16) | ((v1 * 2) << 8) | (v2 * 2)
    return make_gfx(w0, 0)


def make_g_tri2(v0: int, v1: int, v2: int, v3: int, v4: int, v5: int) -> bytes:
    """F3DEX2 gSP2Triangles command."""
    w0 = (G_TRI2 << 24) | ((v0 * 2) << 16) | ((v1 * 2) << 8) | (v2 * 2)
    w1 = ((v3 * 2) << 16) | ((v4 * 2) << 8) | (v5 * 2)
    return make_gfx(w0, w1)


def make_g_enddl() -> bytes:
    """F3DEX2 gSPEndDisplayList command."""
    return make_gfx(G_ENDDL << 24, 0)


def generate_star_geometry() -> Tuple[bytes, bytes, int]:
    """
    Generates vertices and display list for the 3D Mario 64 Power Star.
    Returns:
        (vertex_bytes, display_list_bytes, total_vertices)
    """
    vertices: List[bytes] = []

    # Star Colors
    GOLD_MAIN = (255, 222, 10, 255)
    GOLD_LIGHT = (255, 248, 120, 255)
    GOLD_DARK = (215, 175, 5, 255)
    EYE_BLUE = (20, 35, 140, 255)
    EYE_SHINE = (255, 255, 255, 255)

    # 1. Front center and back center
    # Index 0: Front Apex
    vertices.append(make_vtx(0, 0, 90, *GOLD_LIGHT))
    # Index 1: Back Apex
    vertices.append(make_vtx(0, 0, -90, *GOLD_DARK))

    # Calculate 5 tips and 5 inner valleys
    r_tip = 520.0
    r_inner = 230.0

    # Indices 2..6: 5 Outer tips (Z = 0)
    for i in range(5):
        angle = math.pi / 2.0 + i * (2.0 * math.pi / 5.0)
        x = round(r_tip * math.cos(angle))
        y = round(r_tip * math.sin(angle))
        vertices.append(make_vtx(x, y, 0, *GOLD_MAIN))

    # Indices 7..11: 5 Inner valleys (Front bevel Z = 30)
    for i in range(5):
        angle = math.pi / 2.0 + (i + 0.5) * (2.0 * math.pi / 5.0)
        x = round(r_inner * math.cos(angle))
        y = round(r_inner * math.sin(angle))
        vertices.append(make_vtx(x, y, 30, *GOLD_MAIN))

    # Indices 12..16: 5 Inner valleys (Back bevel Z = -30)
    for i in range(5):
        angle = math.pi / 2.0 + (i + 0.5) * (2.0 * math.pi / 5.0)
        x = round(r_inner * math.cos(angle))
        y = round(r_inner * math.sin(angle))
        vertices.append(make_vtx(x, y, -30, *GOLD_DARK))

    # Iconic Star Eyes (Front face)
    # Left eye: indices 17, 18, 19, 20
    vertices.append(make_vtx(-65, -35, 92, *EYE_BLUE))
    vertices.append(make_vtx(-35, -35, 92, *EYE_BLUE))
    vertices.append(make_vtx(-35, 45, 92, *EYE_BLUE))
    vertices.append(make_vtx(-65, 45, 92, *EYE_BLUE))
    # Left eye shine: index 21
    vertices.append(make_vtx(-50, 30, 95, *EYE_SHINE))

    # Right eye: indices 22, 23, 24, 25
    vertices.append(make_vtx(35, -35, 92, *EYE_BLUE))
    vertices.append(make_vtx(65, -35, 92, *EYE_BLUE))
    vertices.append(make_vtx(65, 45, 92, *EYE_BLUE))
    vertices.append(make_vtx(35, 45, 92, *EYE_BLUE))
    # Right eye shine: index 26
    vertices.append(make_vtx(50, 30, 95, *EYE_SHINE))

    vertex_bytes = b"".join(vertices)
    return vertex_bytes, b"", len(vertices)


def build_star_dlist(vtx_offset: int) -> bytes:
    """
    Builds the display list commands referencing vertices at vtx_offset.
    """
    dl: List[bytes] = []

    # Setup Combiner and Rendering Modes
    dl.append(make_gfx(G_SETCOMBINE << 24, 0x0011FFFF))

    # Load Star Body vertices (indices 0..16 = 17 vertices)
    dl.append(make_g_vtx(17, 0, vtx_offset))

    # Front 5 Points: Center(0) -> Tip(2+i) -> Inner(7+i) & Inner(7+(i-1)%5)
    for i in range(5):
        tip = 2 + i
        inner_curr = 7 + i
        inner_prev = 7 + ((i - 1) % 5)
        # Front triangle 1: 0, inner_prev, tip
        # Front triangle 2: 0, tip, inner_curr
        dl.append(make_g_tri2(0, inner_prev, tip, 0, tip, inner_curr))

    # Back 5 Points: Center(1) -> Tip(2+i) -> InnerBack(12+i) & InnerBack(12+(i-1)%5)
    for i in range(5):
        tip = 2 + i
        inner_curr = 12 + i
        inner_prev = 12 + ((i - 1) % 5)
        dl.append(make_g_tri2(1, tip, inner_prev, 1, inner_curr, tip))

    # Side Bevel Extrusions connecting front inner to back inner
    for i in range(5):
        f_in = 7 + i
        b_in = 12 + i
        tip = 2 + i
        tip_next = 2 + ((i + 1) % 5)
        dl.append(make_g_tri2(tip, f_in, b_in, tip_next, b_in, f_in))

    # Load Eye vertices (indices 17..26 = 10 vertices into buffer slot 0)
    eye_offset = vtx_offset + (17 * VTX_STRUCT.size)
    dl.append(make_g_vtx(10, 0, eye_offset))

    # Left eye quad (0, 1, 2) and (0, 2, 3) relative to loaded slot 0 (indices 17..20)
    # and eye shine (4)
    dl.append(make_g_tri2(0, 1, 2, 0, 2, 3))
    dl.append(make_g_tri1(2, 3, 4))

    # Right eye quad (5, 6, 7) and (5, 7, 8) and shine (9) (indices 22..26)
    dl.append(make_g_tri2(5, 6, 7, 5, 7, 8))
    dl.append(make_g_tri1(7, 8, 9))

    # End of Display List
    dl.append(make_g_enddl())

    return b"".join(dl)


def build_star_zobj() -> bytes:
    """
    Constructs a complete, valid Nintendo 64 .zobj file for the Super Mario 64 Power Star.
    The file contains:
    - 0x0000..: Vertex buffer (27 vertices * 16 bytes = 432 bytes)
    - Aligned offset: F3DEX2 Display List commands
    - Padded to 0x10 boundary.
    """
    vtx_bytes, _, _ = generate_star_geometry()

    # Align display list offset to 16 bytes
    dlist_offset = (len(vtx_bytes) + 15) & ~15
    padding = b"\x00" * (dlist_offset - len(vtx_bytes))

    dlist_bytes = build_star_dlist(0)

    zobj = vtx_bytes + padding + dlist_bytes

    # Pad total zobj to 0x10 bytes
    final_len = (len(zobj) + 15) & ~15
    zobj += b"\x00" * (final_len - len(zobj))

    return zobj


build_sm64_star_zobj = build_star_zobj
