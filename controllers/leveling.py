# controllers/leveling.py
from core.ui_helpers import set_entry, get_int, get_float
from core.math_utils import apml_to_xy
from tkinter import messagebox
import math

class LevelingController:
    def __init__(self, state, device, widgets):
        self.state = state
        self.device = device
        self.widgets = widgets

    def _pos(self):
        self.state.curr_pos = self.device.get_pos()
        return self.state.curr_pos

    def left_level(self):
        cp = self._pos()
        self.state.left_level = cp[2] + cp[3]
        self.state.left_set = 1

        set_entry(self.widgets.get("LeftRoll_label"), f"L:{round(self.state.left_level, 2)}")

        if self.state.right_set:
            set_entry(self.widgets.get("RightRoll_label"), f" R:{round(self.state.right_level, 2)}")
            offset = self.state.left_level - self.state.right_level
            msg = f"Left is {'below' if offset>0 else 'above'} by {abs(round(offset, 2))}"
            set_entry(self.widgets.get("RollOff_label"), msg)

    def right_level(self):
        cp = self._pos()
        self.state.right_level = cp[2] + cp[3]
        self.state.right_set = 1

        set_entry(self.widgets.get("RightRoll_label"), f" R:{round(self.state.right_level, 1)}")

        if self.state.left_set:
            set_entry(self.widgets.get("LeftRoll_label"), f"L:{round(self.state.left_level, 1)}")
            offset = self.state.left_level - self.state.right_level
            msg = f"Left is {'below' if offset>0 else 'above'} by {abs(round(offset, 1))}"
            set_entry(self.widgets.get("RollOff_label"), msg)

    def ant_level(self):
        cp = self._pos()
        self.state.ant_level = cp[2] + cp[3]
        self.state.ant_set = 1

        set_entry(self.widgets.get("AntPitch_label"), f"A:{round(self.state.ant_level, 1)}")

        if self.state.pos_set:
            set_entry(self.widgets.get("PosPitch_label"), f" P:{round(self.state.pos_level, 1)}")
            offset = self.state.ant_level - self.state.pos_level
            msg = f"Ant. is {'below' if offset>0 else 'above'} by {abs(round(offset, 1))}"
            set_entry(self.widgets.get("PitchOff_label"), msg)

    def pos_level(self):
        cp = self._pos()
        self.state.pos_level = cp[2] + cp[3]
        self.state.pos_set = 1

        set_entry(self.widgets.get("PosPitch_label"), f" P:{round(self.state.pos_level, 1)}")

        if self.state.ant_set:
            set_entry(self.widgets.get("AntPitch_label"), f"A:{round(self.state.ant_level, 1)}")
            offset = self.state.ant_level - self.state.pos_level
            msg = f"Ant. is {'below' if offset>0 else 'above'} by {abs(round(offset, 1))}"
            set_entry(self.widgets.get("PitchOff_label"), msg)
    
    def go_right(self):
        cp = self._pos()
        diff = get_float(self.widgets.get("GoLR_box"), key_name="GoLR_box")
        # diff = get_int(self.widgets.get("GoLR_box"), default=0)
    
        dx, dy = self._apml_delta_to_xy(0, +diff)
        target = list(cp)
        target[0] = cp[0] + dx
        target[1] = cp[1] + dy
        
        # read USER speed or set default
        Gospeed = get_int(self.widgets.get("SpeedLevel_box"), default=2000)
        if Gospeed == "":
            set_entry(self.widgets.get("SpeedLevel_box"), "2000")
            
        self.device.goto(target, speed=Gospeed)
    
    
    def go_left(self):
        cp = self._pos()
        diff = get_float(self.widgets.get("GoLR_box"), key_name="GoLR_box")
        # diff = get_int(self.widgets.get("GoLR_box"), default=0)
    
        dx, dy = self._apml_delta_to_xy(0, -diff)
        target = list(cp)
        target[0] = cp[0] + dx
        target[1] = cp[1] + dy
        
        # read USER speed or set default
        Gospeed = get_int(self.widgets.get("SpeedLevel_box"), default=2000)
        if Gospeed == "":
            set_entry(self.widgets.get("SpeedLevel_box"), "2000")
            
        self.device.goto(target, speed=Gospeed)
    
    
    def go_anterior(self):
        cp = self._pos()
        diff = get_float(self.widgets.get("GoFB_box"), key_name="GoLR_box")
        # diff = get_int(self.widgets.get("GoFB_box"), default=0)
    
        dx, dy = self._apml_delta_to_xy(-diff, 0)
        target = list(cp)
        target[0] = cp[0] + dx
        target[1] = cp[1] + dy
        
        # read USER speed or set default
        Gospeed = get_int(self.widgets.get("SpeedLevel_box"), default=2000)
        if Gospeed == "":
            set_entry(self.widgets.get("SpeedLevel_box"), "2000")
            
        self.device.goto(target, speed=Gospeed)
    
    
    def go_posterior(self):
        cp = self._pos()
        diff = get_float(self.widgets.get("GoFB_box"), key_name="GoLR_box")
        # diff = get_int(self.widgets.get("GoFB_box"), default=0)
    
        dx, dy = self._apml_delta_to_xy(+diff, 0)
        target = list(cp)
        target[0] = cp[0] + dx
        target[1] = cp[1] + dy
        
        # read USER speed or set default
        Gospeed = get_int(self.widgets.get("SpeedLevel_box"), default=2000)
        if Gospeed == "":
            set_entry(self.widgets.get("SpeedLevel_box"), "2000")
            
        self.device.goto(target, speed=Gospeed)

        
    # def update_mapping_label(self):
    #     """
    #     Show how user axes (AP/ML) map to device axes (X/Y) given rotation_deg.
    #     Based on the swap logic in math_utils.xy_to_apml / apml_to_xy.
    #     """
    #     rot = int(self.state.rotation_deg) % 360

    #     if rot in (0, 180):
    #         msg = "Mapping: AP→X, ML→Y"
    #     elif rot in (90, 270):
    #         msg = "Mapping: AP→Y, ML→X"
    #     else:
    #         # In case rotation_deg ever becomes non-90-multiples
    #         msg = f"Mapping: rot={rot}° (unsupported)"

    #     set_entry(self.widgets.get("Mapping_label"), msg, key_name="Mapping_label")
    
    
    def _apml_delta_to_xy(self, d_ap: float, d_ml: float):
        """
        Convert a USER-SPACE delta (AP, ML) into a DEVICE-SPACE delta (X, Y)
        using the current rotation mapping.
        """
        dx, dy = apml_to_xy(d_ap, d_ml, self.state.rotation_deg)
        return int(round(dx)), int(round(dy))


    def _dominant_mapping_signature(self, rotation_deg: float) -> str:
        """
        Return a stable signature describing the *dominant* AP and ML alignment
        to device axes, including sign.
    
        For true rotation:
          X =  c*AP - s*ML
          Y =  s*AP + c*ML
    
        Dominant mapping = which axis has larger |coefficient|.
        """
        theta = math.radians(rotation_deg % 360)
        c = math.cos(theta)
        s = math.sin(theta)
    
        # AP contributes: X coeff = c, Y coeff = s
        if abs(c) >= abs(s):
            ap_axis = "X"
            ap_sign = "+" if c >= 0 else "-"
        else:
            ap_axis = "Y"
            ap_sign = "+" if s >= 0 else "-"
    
        # ML contributes: X coeff = -s, Y coeff = c
        # (note the sign on X coeff)
        if abs(-s) >= abs(c):
            ml_axis = "X"
            ml_sign = "+" if (-s) >= 0 else "-"
        else:
            ml_axis = "Y"
            ml_sign = "+" if c >= 0 else "-"
    
        return f"AP->{ap_sign}{ap_axis},ML->{ml_sign}{ml_axis}"
    
    
    def update_mapping_label(self):
        """
        Update on-screen label showing mapping at current rotation.
        Uses exact text for multiples of 90°, and a coefficient view otherwise.
        """
        rot = float(self.state.rotation_deg) % 360
        theta = math.radians(rot)
        c = math.cos(theta)
        s = math.sin(theta)
    
        # Pretty + exact for the common 90° steps
        r_int = int(round(rot)) % 360
        if abs(rot - r_int) < 1e-6 and r_int in (0, 90, 180, 270):
            if r_int == 0:
                msg = "Mapping (0°):  AP→+X, ML→+Y"
            elif r_int == 90:
                msg = "Mapping (90°): AP→+Y, ML→−X"
            elif r_int == 180:
                msg = "Mapping (180°): AP→−X, ML→−Y"
            else:  # 270
                msg = "Mapping (270°): AP→−Y, ML→+X"
        else:
            # General-angle view
            # X = c*AP - s*ML ; Y = s*AP + c*ML
            sig = self._dominant_mapping_signature(rot)
            msg = (
                f"Mapping ({rot:.1f}°): "
                f"X={c:+.2f}·AP {(-s):+.2f}·ML, "
                f"Y={s:+.2f}·AP {c:+.2f}·ML | {sig}"
            )
    
        set_entry(self.widgets.get("Mapping_label"), msg, key_name="Mapping_label")


