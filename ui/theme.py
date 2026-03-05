# ui/theme.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Theme:
    # Surfaces
    PANEL_BG: str = "#29334a"
    ENTRY_BG: str = "#87c9a8"

    # Primary action
    BTN_PRIMARY: str = "#00a091"
    BTN_PRIMARY_HOVER: str = "#007a6f"

    # Warning / Danger
    BTN_WARNING: str = "#eb9602"
    BTN_WARNING_HOVER: str = "#c47e04"
    BTN_DANGER: str = "#eb0202"
    BTN_DANGER_HOVER: str = "#a30303"

    # Wheel / axes
    AXIS_ML: str = "#0050a0"
    AXIS_AP: str = "#a01800"
    AXIS_DV: str = "#48a000"

    # Text
    TXT_BLUE: str = "#026afa"
    TXT_LIGHT_BLUE: str ="#5c9cf7"
    TXT_ORANGE: str= "#fa7e02"
    TXT_WHITE: str = "#ffffff"

    # Misc
    SCROLLBAR_BTN: str = "#ffffff"

THEME = Theme()
