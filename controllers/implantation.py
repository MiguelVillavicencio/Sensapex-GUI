# controllers/implantation.py
from core.ui_helpers import set_entry, get_int
from tkinter import messagebox

class ImplantationController:
    def __init__(self, state, device, widgets, nav_controller=None):
        self.state = state
        self.device = device
        self.widgets = widgets
        self.nav = nav_controller  # optional: reuse nav.fetch if you want

    def _fetch_pos(self):
        self.state.curr_pos = self.device.get_pos()
        return self.state.curr_pos

    def zero_dv(self):
        cp = self._fetch_pos()
        self.state.DVzero_pos[0] = cp[2]
        self.state.DVzero_pos[1] = cp[3]
        self.state.DVzeroed = 1

        dv_level = self.state.DVzero_pos[0] + self.state.DVzero_pos[1]
        set_entry(self.widgets.get("RawImplant_label"), str(abs(round(dv_level, 1))))
        set_entry(self.widgets.get("ZroImplant_label"), "0.0")

    def _dvlevel_disp(self):
        cp = self._fetch_pos()
        raw = cp[2] + cp[3]
        set_entry(self.widgets.get("RawImplant_label"), str(abs(round(raw, 1))))

        z = self.state.DVzero_pos
        zeroed = (cp[2] - z[0]) + (cp[3] - z[1])
        set_entry(self.widgets.get("ZroImplant_label"), str(round(zeroed, 1)))

    def fetch_dv(self):
        if self.state.DVzeroed:
            self._dvlevel_disp()
        else:
            self.zero_dv()

    def zcheck_fun(self):
        # if D is on, turn it off
        dcb = self.widgets.get("DImplant_checkbox")
        if dcb and dcb.get() == "on":
            dcb.toggle()

    def dcheck_fun(self):
        # if Z is on, turn it off
        zcb = self.widgets.get("ZImplant_checkbox")
        if zcb and zcb.get() == "on":
            zcb.toggle()

    def implant(self):
        cp = self._fetch_pos()
        speed = get_int(self.widgets.get("SpeedImplant_box"), default=50)

        zcb = self.widgets.get("ZImplant_checkbox")
        dcb = self.widgets.get("DImplant_checkbox")

        z_move = (zcb.get() == "on") if zcb else False
        d_move = (dcb.get() == "on") if dcb else False

        zdiff = get_int(self.widgets.get("ZImplant_box"), default=0)
        ddiff = get_int(self.widgets.get("DImplant_box"), default=0)

        if z_move:
            target = list(cp)
            target[2] = cp[2] + zdiff
            self.device.goto(target, speed=speed)
            self._dvlevel_disp()
            z_track = (cp[2] - self.state.DVzero_pos[0]) + zdiff
            set_entry(self.widgets.get("ZTrack_label"), str(round(z_track, 1)))

        if d_move:
            target = list(cp)
            target[3] = cp[3] + ddiff
            self.device.goto(target, speed=speed)
            self._dvlevel_disp()
            d_track = (cp[3] - self.state.DVzero_pos[1]) + ddiff
            set_entry(self.widgets.get("DTrack_label"), str(round(d_track, 1)))

        while self.device.is_busy():
            self._dvlevel_disp()

    def explant(self):
        cp = self._fetch_pos()
        speed = get_int(self.widgets.get("SpeedImplant_box"), default=50)

        zcb = self.widgets.get("ZImplant_checkbox")
        dcb = self.widgets.get("DImplant_checkbox")

        z_move = (zcb.get() == "on") if zcb else False
        d_move = (dcb.get() == "on") if dcb else False

        zdiff = get_int(self.widgets.get("ZImplant_box"), default=0)
        ddiff = get_int(self.widgets.get("DImplant_box"), default=0)

        if z_move:
            target = list(cp)
            target[2] = cp[2] - zdiff
            self.device.goto(target, speed=speed)
            self._dvlevel_disp()
            z_track = (cp[2] - self.state.DVzero_pos[0]) - zdiff
            set_entry(self.widgets.get("ZTrack_label"), str(round(z_track, 1)))

        if d_move:
            target = list(cp)
            target[3] = cp[3] - ddiff
            self.device.goto(target, speed=speed)
            self._dvlevel_disp()
            d_track = (cp[3] - self.state.DVzero_pos[1]) - ddiff
            set_entry(self.widgets.get("DTrack_label"), str(round(d_track, 1)))

        while self.device.is_busy():
            self._dvlevel_disp()
