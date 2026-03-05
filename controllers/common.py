# controllers/common.py
from ui.theme import THEME
from ui.figure3d import update_fig
from core.math_utils import  apml_to_xy
from tkinter import messagebox

class CommonController:
    def __init__(self, state, device, widgets, plot_handle, nav_ctrl=None, lvl_ctrl=None):
        self.state = state
        self.device = device
        self.widgets = widgets
        self.plot = plot_handle
        self.nav_ctrl = nav_ctrl  # NEW
        self.lvl_ctrl = lvl_ctrl  # NEW

    def stop(self):
        self.device.stop()

    def rotate_space(self):

        # calculate candidate rotation FIRST
        old_rot = float(self.state.rotation_deg) % 360
        new_rot = (old_rot + 90) % 360
    
        old_sig = self._dominant_mapping_signature(old_rot)
        new_sig = self._dominant_mapping_signature(new_rot)
    
        # Ask permission BEFORE any visual or state change
        if old_sig != new_sig:
            ok = messagebox.askyesno(
                "Mapping will change",
                "The dominant AP/ML → X/Y mapping will change.\n\n"
                f"Current: {old_sig}\n"
                f"New:     {new_sig}\n\n"
                "Proceed with rotation?"
            )
            if not ok:
                return
    
        # ===============================
        # User accepted → NOW apply changes
        # ===============================
    
        self.state.rotation_deg = new_rot
        self.state.Space_orientation = (self.state.Space_orientation + 1) % 4
    
        xwheel = self.widgets.get("XWheel")
        ywheel = self.widgets.get("YWheel")
    
        if self.state.Space_orientation in (0, 2):
            # if xwheel: xwheel.configure(fg_color=THEME.AXIS_ML, text="ML")
            # if ywheel: ywheel.configure(fg_color=THEME.AXIS_AP, text="AP")
            if xwheel: xwheel.configure( text="AP")
            if ywheel: ywheel.configure( text="ML")
        else:
            # if xwheel: xwheel.configure(fg_color=THEME.AXIS_AP, text="AP")
            # if ywheel: ywheel.configure(fg_color=THEME.AXIS_ML, text="ML")
            if xwheel: xwheel.configure( text="ML")
            if ywheel: ywheel.configure( text="AP")
    
        # --- figure
        update_fig(self.plot.ax, self.state.rotation_deg)
        self.plot.canvas.draw()
    
        # --- recompute absolute from stored AP/ML
        self.state.CoordX_MarkD.clear()
        self.state.CoordY_MarkD.clear()
        self.state.CoordZ_MarkD.clear()
        self.state.CoordD_MarkD.clear()
    
        for i in range(self.state.markD_idx):
            ap = self.state.RelAP_MkD[i]
            ml = self.state.RelML_MkD[i]
            dv = self.state.RelDV_MkD[i]
            aa = self.state.RelAA_MkD[i]
    
            x_rel, y_rel = apml_to_xy(ap, ml, self.state.rotation_deg)
    
            abs_x = int(round(self.state.zero_pos[0] + x_rel))
            abs_y = int(round(self.state.zero_pos[1] + y_rel))
            abs_z = int(round(self.state.zero_pos[2] + dv))
            abs_d = int(round(self.state.zero_pos[3] + aa))
    
            self.state.CoordX_MarkD.append(abs_x)
            self.state.CoordY_MarkD.append(abs_y)
            self.state.CoordZ_MarkD.append(abs_z)
            self.state.CoordD_MarkD.append(abs_d)
    
        # --- update dependent UIs
        if self.lvl_ctrl is not None:
            self.lvl_ctrl.update_mapping_label()
    
        if self.nav_ctrl is not None:
            self.nav_ctrl.refresh_targets_list()
            self.nav_ctrl.fetch()


    def _dominant_mapping_signature(self, rotation_deg: float) -> str:
        """
        Delegate dominant mapping signature to leveling controller if available.
        Fallback to a local computation if needed.
        """
        if getattr(self, "lvl_ctrl", None) is not None and hasattr(self.lvl_ctrl, "_dominant_mapping_signature"):
            return self.lvl_ctrl._dominant_mapping_signature(rotation_deg)
    
        import math
        theta = math.radians(rotation_deg % 360)
        c = math.cos(theta)
        s = math.sin(theta)
    
        ap_axis = "X" if abs(c) >= abs(s) else "Y"
        ap_sign = "+" if (c if ap_axis == "X" else s) >= 0 else "-"
    
        ml_x = -s
        ml_y = c
        ml_axis = "X" if abs(ml_x) >= abs(ml_y) else "Y"
        ml_sign = "+" if (ml_x if ml_axis == "X" else ml_y) >= 0 else "-"

        return f"AP->{ap_sign}{ap_axis},ML->{ml_sign}{ml_axis}"
