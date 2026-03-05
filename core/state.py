# core/state.py
from dataclasses import dataclass, field
from typing import List

@dataclass
class AppState:
    curr_pos: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    zero_pos: List[int] = field(default_factory=lambda: [0, 0, 0, 0])

    markD_idx: int = 0
    MarkD_names: List[str] = field(default_factory=list)

    CoordX_MarkD: List[int] = field(default_factory=list)
    CoordY_MarkD: List[int] = field(default_factory=list)
    CoordZ_MarkD: List[int] = field(default_factory=list)
    CoordD_MarkD: List[int] = field(default_factory=list)

    CoordX_RelMkD: List[int] = field(default_factory=list)
    CoordY_RelMkD: List[int] = field(default_factory=list)
    CoordZ_RelMkD: List[int] = field(default_factory=list)
    CoordD_RelMkD: List[int] = field(default_factory=list)

    Zeroed: int = 0
    rotation_deg: int = 0
    Space_orientation: int = 0

    DVzeroed: int = 0
    DVzero_pos: List[int] = field(default_factory=lambda: [0, 0])

    left_set: int = 0
    right_set: int = 0
    ant_set: int = 0
    pos_set: int = 0

    left_level: float = 0.0
    right_level: float = 0.0
    ant_level: float = 0.0
    pos_level: float = 0.0
    
    display_mode: str = "user"  # "user" (AP/ML/DV/A∠) or "device" (X/Y/Z/D)
    RelAP_MkD: List[int] = field(default_factory=list)
    RelML_MkD: List[int] = field(default_factory=list)
    RelDV_MkD: List[int] = field(default_factory=list)
    RelAA_MkD: List[int] = field(default_factory=list)
    
    RelColor_MkD = []   # stores RGBA color per MkD target
    
