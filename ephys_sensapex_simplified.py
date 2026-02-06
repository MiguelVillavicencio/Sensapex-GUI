"""
Simplified Sensapex (UMP) GUI

Key changes vs original:
- No sprawling globals: state lives in AppState.
- Controller wrapper for UMP/device actions.
- One set of small helpers for reading entries, updating UI, bounds checking.
- Consolidated "Go" / "Mark" logic (parse coords -> rotate -> absolute -> clamp -> move).
- Reduced repetitive widget creation via small factories.

NOTE: This is a functional *simplification*, not a pixel-perfect UI clone.
It keeps the core workflow: Connect/Calibrate/Center/Zero/Fetch, Mark targets,
Rotate basis, Go to target, DV zero + Implant/Explant, Stop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import customtkinter as ctk
from tkinter import messagebox

import numpy as np
from sensapex import UMP


# -----------------------------
# Helpers
# -----------------------------
def i(entry, default: int = 0) -> int:
    """Parse int from a CTkEntry-like widget (or string)."""
    if entry is None:
        return default
    s = entry.get() if hasattr(entry, "get") else str(entry)
    s = s.strip()
    return default if not s else int(float(s))


def f(entry, default: float = 0.0) -> float:
    s = entry.get() if hasattr(entry, "get") else str(entry)
    s = s.strip()
    return default if not s else float(s)


def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(v, hi))


# -----------------------------
# State + Controller
# -----------------------------
@dataclass
class AppState:
    zeroed: bool = False
    zero_pos: List[int] = field(default_factory=lambda: [0, 0, 0, 0])

    rotation_deg: int = 0  # 0, 90, 180, 270

    # Markers stored in *relative* coordinates (ML/AP/DV/D) so we can re-rotate basis.
    marker_names: List[str] = field(default_factory=list)
    marker_rel: List[List[int]] = field(default_factory=list)  # each = [x,y,z,d]

    # DV tracking
    dv_zeroed: bool = False
    dv_zero_zd: List[int] = field(default_factory=lambda: [0, 0])  # [z0, d0]


class SensapexController:
    """Small wrapper around sensapex UMP + device, with safe guardrails."""
    AXES = ("x", "y", "z", "d")
    LO, HI = 0, 20000  # stage limits in original code

    def __init__(self) -> None:
        self.ump = None
        self.device = None

    def connect_first(self) -> None:
        self.ump = UMP.get_ump()
        dev_ids = self.ump.list_devices()
        if not dev_ids:
            raise RuntimeError("No Sensapex devices found.")
        self.device = self.ump.get_device(dev_ids[0])

    def pos(self) -> List[int]:
        if self.device is None:
            raise RuntimeError("Not connected.")
        return list(self.device.get_pos())

    def calibrate(self) -> None:
        if self.device is None:
            raise RuntimeError("Not connected.")
        self.device.calibrate_zero_position()

    def stop(self) -> None:
        if self.device is None:
            return
        # original called stop multiple times; keep that habit
        for _ in range(3):
            self.device.stop()

    def goto(self, pos: List[int], speed: int) -> None:
        if self.device is None:
            raise RuntimeError("Not connected.")
        self.device.goto_pos(list(pos), speed=int(speed))

    def clamp_pos(self, pos: List[int]) -> Tuple[bool, List[int], List[Tuple[str, int]]]:
        """Return (changed?, clamped_pos, out_of_range list)."""
        out = []
        clamped = []
        changed = False
        for axis, v in zip(self.AXES, pos):
            if self.LO <= v <= self.HI:
                clamped.append(v)
            else:
                changed = True
                out.append((axis, v))
                clamped.append(clamp(v, self.LO, self.HI))
        return changed, clamped, out


# -----------------------------
# Math: basis rotation
# -----------------------------
def rotate_xy(x: int, y: int, deg: int) -> Tuple[int, int]:
    """Rotate (x,y) in the XY plane by deg about origin."""
    rad = np.deg2rad(deg % 360)
    c, s = float(np.cos(rad)), float(np.sin(rad))
    xr = int(round(c * x - s * y))
    yr = int(round(s * x + c * y))
    return xr, yr


def apply_rotation(rel: List[int], deg: int) -> List[int]:
    """Rotate relative coordinates; only X/Y are rotated."""
    x, y, z, d = rel
    xr, yr = rotate_xy(x, y, deg)
    return [xr, yr, int(z), int(d)]


# -----------------------------
# GUI
# -----------------------------
class App(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        # appearance
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        ctk.set_widget_scaling(1.6)
        ctk.set_window_scaling(1.1)

        self.title("Sensapex UI (simplified)")
        self.geometry("1100x650")
        self.resizable(True, True)

        self.state = AppState()
        self.ctrl = SensapexController()

        # widgets we'll update frequently
        self.pos_entries = {}
        self.speed_entry = None

        self.go_entries = {}
        self.marker_name_entry = None
        self.marker_listbox = None

        self.dv_labels = {}

        self._build_ui()

    # -------- UI factories
    def _btn(self, parent, text, cmd, *, w=110, fg="#00a091", hover="#007a6f"):
        return ctk.CTkButton(parent, text=text, command=cmd, width=w,
                             fg_color=fg, hover_color=hover, corner_radius=6,
                             font=("Verdana", 12, "bold"))

    def _entry(self, parent, placeholder="", *, w=90):
        return ctk.CTkEntry(parent, placeholder_text=placeholder, width=w,
                            font=("Verdana", 11, "bold"),
                            corner_radius=6)

    # -------- build UI
    def _build_ui(self) -> None:
        # Tabs
        self.tabs = ctk.CTkTabview(self, width=600, height=500)
        self.tabs.pack(padx=10, pady=10, fill="both", expand=True)

        self.tabs.add("Navigation")
        self.tabs.add("Implantation")
        self.tabs.add("Markers")
        self.tabs.set("Navigation")

        self._build_nav_tab(self.tabs.tab("Navigation"))
        self._build_implant_tab(self.tabs.tab("Implantation"))
        self._build_markers_tab(self.tabs.tab("Markers"))

        # bottom row
        bottom = ctk.CTkFrame(self)
        bottom.pack(fill="x", padx=10, pady=(0, 10))
        self._btn(bottom, "STOP", self.on_stop, fg="#eb0202", hover="#a30303").pack(side="left", padx=5)
        self._btn(bottom, "Quit", self.destroy).pack(side="right", padx=5)

    def _build_nav_tab(self, tab):
        row1 = ctk.CTkFrame(tab)
        row1.pack(fill="x", padx=10, pady=10)

        self._btn(row1, "Connect/Reset", self.on_connect, w=140).pack(side="left", padx=5)
        self._btn(row1, "Calibrate", self.on_calibrate).pack(side="left", padx=5)
        self._btn(row1, "Center", self.on_center).pack(side="left", padx=5)
        self._btn(row1, "Zero", self.on_zero).pack(side="left", padx=5)
        self._btn(row1, "Fetch", self.on_fetch).pack(side="left", padx=5)

        # speed + rotation
        row2 = ctk.CTkFrame(tab)
        row2.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(row2, text="Speed (um/s):").pack(side="left", padx=(5, 2))
        self.speed_entry = self._entry(row2, "2000", w=90)
        self.speed_entry.pack(side="left", padx=5)

        self._btn(row2, "Rotate 90°", self.on_rotate, w=120).pack(side="left", padx=10)

        self.rot_label = ctk.CTkLabel(row2, text="Rotation: 0°")
        self.rot_label.pack(side="left", padx=10)

        # Current position display
        row3 = ctk.CTkFrame(tab)
        row3.pack(fill="x", padx=10, pady=10)

        for axis in ("X", "Y", "Z", "D"):
            ctk.CTkLabel(row3, text=f"{axis}:").pack(side="left", padx=(5, 2))
            e = self._entry(row3, "", w=110)
            e.pack(side="left", padx=5)
            e.configure(state="disabled")
            self.pos_entries[axis] = e

    def _build_markers_tab(self, tab):
        top = ctk.CTkFrame(tab)
        top.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top, text="Name:").pack(side="left", padx=(5, 2))
        self.marker_name_entry = self._entry(top, "target_1", w=160)
        self.marker_name_entry.pack(side="left", padx=5)

        # go/mark coordinate entries (relative, in your rotated anatomical basis)
        coords = ctk.CTkFrame(tab)
        coords.pack(fill="x", padx=10, pady=10)

        for axis in ("X", "Y", "Z", "D"):
            ctk.CTkLabel(coords, text=f"{axis} (rel):").pack(side="left", padx=(5, 2))
            self.go_entries[axis] = self._entry(coords, "0", w=90)
            self.go_entries[axis].pack(side="left", padx=5)

        actions = ctk.CTkFrame(tab)
        actions.pack(fill="x", padx=10, pady=10)

        self._btn(actions, "Add Marker", self.on_add_marker, w=140).pack(side="left", padx=5)
        self._btn(actions, "Remove Selected", self.on_remove_marker, w=170, fg="#eb9602", hover="#c47e04").pack(side="left", padx=5)
        self._btn(actions, "Go (coords or selected)", self.on_go, w=220).pack(side="left", padx=5)

        # marker list
        list_frame = ctk.CTkFrame(tab)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(10, 10))

        self.marker_listbox = ctk.CTkTextbox(list_frame, height=220)
        self.marker_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.marker_listbox.insert("1.0", "Markers:\n")

        hint = ctk.CTkLabel(tab, text="Tip: If X/Y are blank, Go uses the first marker in the list.")
        hint.pack(padx=10, pady=(0, 10))

    def _build_implant_tab(self, tab):
        top = ctk.CTkFrame(tab)
        top.pack(fill="x", padx=10, pady=10)

        self._btn(top, "Zero DV", self.on_dv_zero, w=120).pack(side="left", padx=5)
        self._btn(top, "Fetch DV", self.on_dv_fetch, w=120).pack(side="left", padx=5)

        labels = ctk.CTkFrame(tab)
        labels.pack(fill="x", padx=10, pady=10)

        self.dv_labels["raw"] = ctk.CTkLabel(labels, text="Raw DV: --")
        self.dv_labels["raw"].pack(side="left", padx=10)
        self.dv_labels["zeroed"] = ctk.CTkLabel(labels, text="Zeroed DV: --")
        self.dv_labels["zeroed"].pack(side="left", padx=10)

        moves = ctk.CTkFrame(tab)
        moves.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(moves, text="ΔZ:").pack(side="left", padx=(5, 2))
        self.dz_entry = self._entry(moves, "0", w=90)
        self.dz_entry.pack(side="left", padx=5)

        ctk.CTkLabel(moves, text="ΔD:").pack(side="left", padx=(5, 2))
        self.dd_entry = self._entry(moves, "0", w=90)
        self.dd_entry.pack(side="left", padx=5)

        ctk.CTkLabel(moves, text="Speed:").pack(side="left", padx=(10, 2))
        self.dv_speed_entry = self._entry(moves, "50", w=90)
        self.dv_speed_entry.pack(side="left", padx=5)

        self._btn(moves, "Implant (+)", self.on_implant, w=140).pack(side="left", padx=10)
        self._btn(moves, "Explant (-)", self.on_explant, w=140).pack(side="left", padx=5)

    # -------- core actions
    def _require_connected(self) -> bool:
        try:
            if self.ctrl.device is None:
                self.ctrl.connect_first()
            return True
        except Exception as e:
            messagebox.showerror("Connection error", str(e))
            return False

    def _set_pos_display(self, pos: List[int]) -> None:
        # display either absolute or zeroed relative
        if self.state.zeroed:
            rel = [pos[i] - self.state.zero_pos[i] for i in range(4)]
        else:
            rel = pos

        for axis, value in zip(("X", "Y", "Z", "D"), rel):
            e = self.pos_entries[axis]
            e.configure(state="normal")
            e.delete(0, "end")
            e.insert(0, f"{value:.1f}" if isinstance(value, float) else str(round(value, 1)))
            e.configure(state="disabled")

    def _current_pos(self) -> List[int]:
        return self.ctrl.pos()

    def _speed(self) -> int:
        return i(self.speed_entry, 2000)

    def on_connect(self):
        try:
            self.ctrl.connect_first()
            self.on_fetch()
        except Exception as e:
            messagebox.showerror("Connection error", str(e))

    def on_calibrate(self):
        if not self._require_connected():
            return
        try:
            self.ctrl.calibrate()
        except Exception as e:
            messagebox.showerror("Calibrate error", str(e))

    def on_center(self):
        if not self._require_connected():
            return
        try:
            self.ctrl.goto([10000, 10000, 0, 0], speed=1000)
            self.on_fetch()
        except Exception as e:
            messagebox.showerror("Center error", str(e))

    def on_zero(self):
        if not self._require_connected():
            return
        pos = self._current_pos()
        self.state.zero_pos = pos
        self.state.zeroed = True
        self.on_fetch()

    def on_fetch(self):
        if not self._require_connected():
            return
        try:
            pos = self._current_pos()
            self._set_pos_display(pos)
        except Exception as e:
            messagebox.showerror("Fetch error", str(e))

    def on_stop(self):
        self.ctrl.stop()

    # ----- rotation
    def on_rotate(self):
        self.state.rotation_deg = (self.state.rotation_deg + 90) % 360
        self.rot_label.configure(text=f"Rotation: {self.state.rotation_deg}°")
        # Re-express stored marker REL coordinates into the new basis:
        # In the original code, when the basis rotates, you *rewrite* rel coords by applying
        # the same rotation. We keep that behavior.
        self.state.marker_rel = [apply_rotation(m, 90) for m in self.state.marker_rel]
        self._render_markers()

    # ----- markers
    def _render_markers(self):
        self.marker_listbox.delete("1.0", "end")
        self.marker_listbox.insert("1.0", "Markers:\n")
        for idx, (name, rel) in enumerate(zip(self.state.marker_names, self.state.marker_rel), start=1):
            self.marker_listbox.insert("end", f"{idx:02d}. {name:15s}  rel={rel}\n")

    def on_add_marker(self):
        if not self.state.zeroed:
            messagebox.showwarning("Zero first", "Please Zero the basis before adding markers.")
            return

        name = (self.marker_name_entry.get() or "").strip() or f"target_{len(self.state.marker_names)+1}"

        rel = [i(self.go_entries["X"], 0), i(self.go_entries["Y"], 0),
               i(self.go_entries["Z"], 0), i(self.go_entries["D"], 0)]

        self.state.marker_names.append(name)
        self.state.marker_rel.append(rel)
        self._render_markers()

    def on_remove_marker(self):
        # simplified selection: remove last
        if not self.state.marker_names:
            return
        self.state.marker_names.pop()
        self.state.marker_rel.pop()
        self._render_markers()

    # ----- move logic (shared by Go + Implant)
    def _confirm_and_clamp(self, abs_pos: List[int]) -> Optional[List[int]]:
        changed, clamped_pos, out = self.ctrl.clamp_pos(abs_pos)
        if not changed:
            return clamped_pos

        msg = "Following targets are out of range and will be clamped:\n\n" + \
              "\n".join([f"{a}: {v}" for a, v in out]) + \
              "\n\nContinue?"
        if messagebox.askyesno("Out of range", msg):
            return clamped_pos
        return None

    def _rel_to_abs(self, rel: List[int]) -> List[int]:
        """Relative (basis coords) -> rotated -> absolute (stage coords)."""
        rotated = apply_rotation(rel, self.state.rotation_deg)
        return [self.state.zero_pos[i] + rotated[i] for i in range(4)]

    def _go_routine(self, target_abs: List[int], speed: int) -> None:
        """
        Reduced version of your Go_routine:
        1) move to current XY with Z/D=0
        2) move to target XY with Z/D=0
        3) descend to Z/D=500 (safe-ish) then stop
        """
        cur = self._current_pos()
        cur_safe = [cur[0], cur[1], 0, 0]
        tgt_safe = [target_abs[0], target_abs[1], 0, 0]
        tgt_final = [target_abs[0], target_abs[1], 500, 500]

        self.ctrl.goto(cur_safe, speed=speed)
        self.ctrl.goto(tgt_safe, speed=speed)
        self.ctrl.goto(tgt_final, speed=250)
        self.on_fetch()

    def on_go(self):
        if not self._require_connected():
            return
        if not self.state.zeroed:
            messagebox.showwarning("Zero first", "Please Zero the basis before moving.")
            return

        speed = self._speed()

        # If X or Y is entered, use those coordinates; else use first marker if present.
        x_txt = self.go_entries["X"].get().strip()
        y_txt = self.go_entries["Y"].get().strip()

        if x_txt or y_txt:
            if not x_txt or not y_txt:
                messagebox.showwarning("Missing X/Y", "Enter both X and Y.")
                return
            rel = [i(self.go_entries["X"], 0), i(self.go_entries["Y"], 0),
                   i(self.go_entries["Z"], 0), i(self.go_entries["D"], 0)]
        else:
            if not self.state.marker_rel:
                messagebox.showwarning("No target", "Enter X/Y or add at least one marker.")
                return
            rel = self.state.marker_rel[0]

        abs_pos = self._rel_to_abs(rel)
        abs_pos = self._confirm_and_clamp(abs_pos)
        if abs_pos is None:
            return

        try:
            self._go_routine(abs_pos, speed)
        except Exception as e:
            messagebox.showerror("Move error", str(e))

    # ----- DV helpers
    def _dv_values(self) -> Tuple[int, int, int]:
        """Return (raw_dv, zeroed_dv, current_z, current_d)."""
        pos = self._current_pos()
        z, d = pos[2], pos[3]
        raw = z + d
        if self.state.dv_zeroed:
            zeroed = (z - self.state.dv_zero_zd[0]) + (d - self.state.dv_zero_zd[1])
        else:
            zeroed = 0
        return raw, zeroed, z, d

    def on_dv_zero(self):
        if not self._require_connected():
            return
        pos = self._current_pos()
        self.state.dv_zero_zd = [pos[2], pos[3]]
        self.state.dv_zeroed = True
        self.on_dv_fetch()

    def on_dv_fetch(self):
        if not self._require_connected():
            return
        raw, zeroed, _, _ = self._dv_values()
        self.dv_labels["raw"].configure(text=f"Raw DV: {raw:.1f}")
        self.dv_labels["zeroed"].configure(text=f"Zeroed DV: {zeroed:.1f}")

    def _move_dv(self, sign: int):
        if not self._require_connected():
            return
        speed = i(self.dv_speed_entry, 50)
        dz = i(self.dz_entry, 0) * sign
        dd = i(self.dd_entry, 0) * sign

        pos = self._current_pos()
        target = [pos[0], pos[1], pos[2] + dz, pos[3] + dd]
        target = self._confirm_and_clamp(target)
        if target is None:
            return

        try:
            self.ctrl.goto(target, speed=speed)
            self.on_dv_fetch()
        except Exception as e:
            messagebox.showerror("DV move error", str(e))

    def on_implant(self):
        self._move_dv(+1)

    def on_explant(self):
        self._move_dv(-1)


if __name__ == "__main__":
    App().mainloop()
