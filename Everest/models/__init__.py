"""
Everest Models Module:
Provides 3D model generators, Fast3D display list compilers,
and cross-game asset descriptors.
"""

from .sm64_star import build_star_zobj, generate_star_geometry, build_star_dlist
from .sm64_mushroom import build_mushroom_zobj
from .sm64_key import build_key_zobj
from .oot_sword import get_oot_sword_sm64_spec, get_oot_shield_sm64_spec, get_oot_hammer_sm64_spec

__all__ = [
    "build_star_zobj",
    "generate_star_geometry",
    "build_star_dlist",
    "build_mushroom_zobj",
    "build_key_zobj",
    "get_oot_sword_sm64_spec",
    "get_oot_shield_sm64_spec",
    "get_oot_hammer_sm64_spec",
]
