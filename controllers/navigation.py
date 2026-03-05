# controllers/navigation.py
from tkinter import messagebox
from core.ui_helpers import set_entry, get_int, get_str, get_float, normalize_listbox_selection
from core.math_utils import evaluate_new_coordinates, go_routine, apml_to_xy, xy_to_apml
from ui.figure3d import update_fig
import matplotlib.pyplot as plt
import numpy as np


class NavigationController:
    def __init__(self, state, device, widgets, plot_handle):
        self.state = state
        self.device = device
        self.widgets = widgets
        self.plot = plot_handle

    def connect(self):
        self.device.connect_first()
        self.fetch()

    def calibrate(self):
        self.device.calibrate_zero()

    def center(self):
        self.device.goto([10000, 10000, 0, 0], speed=1000)
        self.fetch()

    def fetch(self):
        self.state.curr_pos = self.device.get_pos()
        curr = self.state.curr_pos
        zero = self.state.zero_pos
        
        if self.state.Zeroed:
            x = curr[0] - zero[0]
            y = curr[1] - zero[1]
            z = curr[2] - zero[2]
            d = curr[3] - zero[3]
        else:
            x, y, z, d = curr

    # Device view: X/Y/Z/D
        if getattr(self.state, "display_mode", "user") == "device":
            set_entry(self.widgets.get("Xfield_box"), f"X= {x:.1f}", key_name="Xfield_box")
            set_entry(self.widgets.get("Yfield_box"), f"Y= {y:.1f}", key_name="Yfield_box")
            set_entry(self.widgets.get("Zfield_box"), f"Z= {z:.1f}", key_name="Zfield_box")
            set_entry(self.widgets.get("Dfield_box"), f"D= {d:.1f}", key_name="Dfield_box")
            return

        
        # User view: AP/ML/DV/A∠
        # ap, ml = xy_to_apml(int(round(x)), int(round(y)), self.state.rotation_deg)
        # set_entry(self.widgets.get("Xfield_box"), f"AP= {ap}",           key_name="Xfield_box")
        # set_entry(self.widgets.get("Yfield_box"), f"ML= {ml}",           key_name="Yfield_box")
        # set_entry(self.widgets.get("Zfield_box"), f"DV= {round(z, 1)}",  key_name="Zfield_box")
        # set_entry(self.widgets.get("Dfield_box"), f"A∠= {round(d, 1)}", key_name="Dfield_box")
        
        ap, ml = xy_to_apml(x, y, self.state.rotation_deg)
        set_entry(self.widgets.get("Xfield_box"), f"AP= {ap:.1f}", key_name="Xfield_box")
        set_entry(self.widgets.get("Yfield_box"), f"ML= {ml:.1f}", key_name="Yfield_box")
        set_entry(self.widgets.get("Zfield_box"), f"DV= {z:.1f}",  key_name="Zfield_box")
        set_entry(self.widgets.get("Dfield_box"), f"A∠= {d:.1f}", key_name="Dfield_box")

        
    def toggle_display_mode(self):
        self.state.display_mode = "device" if self.state.display_mode == "user" else "user"
        self.fetch()
        self.refresh_targets_list()

    def zero_basis(self):
        self.fetch()
        self.state.zero_pos = list(self.state.curr_pos)

        set_entry(self.widgets.get("Xfield_box"), "X= 0.0")
        set_entry(self.widgets.get("Yfield_box"), "Y= 0.0")
        set_entry(self.widgets.get("Zfield_box"), "Z= 0.0")
        set_entry(self.widgets.get("Dfield_box"), "D= 0.0")

        if self.state.Zeroed == 1:
            zp = self.state.zero_pos

            # Recompute absolute device coords from stored user-relative targets
            # 1. delete old abs target coord.
            self.state.CoordX_MarkD = []
            self.state.CoordY_MarkD = []
            self.state.CoordZ_MarkD = []
            self.state.CoordD_MarkD = []
            
            # 2. collect stored user-relative targets
            for i in range(self.state.markD_idx):
                ap = self.state.RelAP_MkD[i]
                ml = self.state.RelML_MkD[i]
                dv = self.state.RelDV_MkD[i]
                aa = self.state.RelAA_MkD[i]
                
                # 3. transform relvative to absolute
                x_rel, y_rel = apml_to_xy(ap, ml, self.state.rotation_deg)
                self.state.CoordX_MarkD.append(int(round(zp[0] + x_rel)))
                self.state.CoordY_MarkD.append(int(round(zp[1] + y_rel)))
                self.state.CoordZ_MarkD.append(int(round(zp[2] + dv)))
                self.state.CoordD_MarkD.append(int(round(zp[3] + aa)))
                
                # 4. cache new abs, zero-corrected targets
                self.state.CoordX_MarkD.append(zp[0] + x_rel)
                self.state.CoordY_MarkD.append(zp[1] + y_rel)
                self.state.CoordZ_MarkD.append(zp[2] + dv)
                self.state.CoordD_MarkD.append(zp[3] + aa)

            self.refresh_targets_list()
        else:
            self.state.Zeroed = 1

    def scape(self):
        self.fetch()
        cp = list(self.state.curr_pos)
        cp[2] = 0
        cp[3] = 0
        self.device.goto(cp, speed=1000)
        
    def selection_markd(self, _=None):
        lb = self.widgets.get("Targets_box")
        if lb is None:
            return

        try:
            sel = normalize_listbox_selection(lb.curselection())
        except Exception as e:
            print(f"[WARN] Targets_box.curselection() failed: {e}")
            return

        # Normalize selection to a single int
        try:
            if sel is None:
                return
            if isinstance(sel, (tuple, list)):
                if not sel:
                    return
                sel = sel[0]
            if isinstance(sel, str):
                idx = int(float(sel))  # handles "0.0"
            else:
                idx = int(sel)
        except Exception as e:
            print(f"[WARN] Could not normalize selection {sel!r}: {e}")
            return

        # Ignore header row
        if idx <= 0:
            return

        state_idx = idx - 1  # header offset
        self.selected_target_idx = state_idx  # store on controller (safe)
        
        # protects load_selected_target_into_go_boxes from bas entries
        try:
            self.load_selected_target_into_go_boxes(state_idx)
        except Exception as e:
            print(f"[WARN] load_selected_target_into_go_boxes failed for idx={state_idx}: {e}")
            return



    def markd_add(self):
        
        if not self.state.Zeroed:
            messagebox.showwarning("Stop right there", "Zero basis first")
            return

        APs = get_str(self.widgets.get("GoAP_box"), "GoAP_box")
        MLs = get_str(self.widgets.get("GoML_box"), "GoML_box")
        DVs = get_str(self.widgets.get("GoDV_box"), "GoDV_box")
        AAs = get_str(self.widgets.get("GoAA_box"), "GoAA_box")
        
        new_entry = False
        
        # Case 1: user typed AP/ML (coordinate entry)
        if APs or MLs:
            if not APs or not MLs:
                print("APs:", repr(APs), "MLs:", repr(MLs))
                messagebox.showwarning("Warning", "Enter both AP & ML entries!")
                return
            
            # Defaults if DV/A∠ are blank
            if DVs == "" or AAs == "":
                if messagebox.askquestion("Eat that question", "Fill DV and A∠ with zeros?", icon="warning") != "yes":
                    return
                DVs, AAs = "0", "0"
            
            # Parse safely (do NOT crash app)
            try:
                ap = int(APs); ml = int(MLs); dv = int(DVs); aa = int(AAs)
            except ValueError:
                messagebox.showwarning(
                "Invalid input",
                f"AP/ML/DV/A∠ must be integers.\nGot: AP={APs!r}, ML={MLs!r}, DV={DVs!r}, A∠={AAs!r}"
                )
                return
            
            # Store relative in USER coordinates
            self.state.RelAP_MkD.append(ap)
            self.state.RelML_MkD.append(ml)
            self.state.RelDV_MkD.append(dv)
            self.state.RelAA_MkD.append(aa)
            
            # Convert AP/ML -> device XY rel depending on rotation
            x_rel, y_rel = apml_to_xy(ap, ml, self.state.rotation_deg)
            x_rel = int(round(x_rel))
            y_rel = int(round(y_rel))

            
            # Convert device-relative -> device-absolute using zero_pos
            abs_coords = [
                self.state.zero_pos[0] + x_rel,
                self.state.zero_pos[1] + y_rel,
                self.state.zero_pos[2] + dv,
                self.state.zero_pos[3] + aa,
            ]
            
            proceed, corrected = evaluate_new_coordinates(abs_coords)
            if not proceed:
                # rollback last append to keep state consistent
                self.state.RelAP_MkD.pop()
                self.state.RelML_MkD.pop()
                self.state.RelDV_MkD.pop()
                self.state.RelAA_MkD.pop()
                return
            
            # Cache absolute device coords
            self.state.CoordX_MarkD.append(corrected[0])
            self.state.CoordY_MarkD.append(corrected[1])
            self.state.CoordZ_MarkD.append(corrected[2])
            self.state.CoordD_MarkD.append(corrected[3])

            # Clear input boxes (use "" not " ")
            for key in ["GoAP_box", "GoML_box", "GoDV_box", "GoAA_box"]:
                set_entry(self.widgets.get(key), "", key_name=key)


            new_entry = True
            
        # Case 2: define target from current position
        else:
            # If you still want "define by current position" in user-space,
            # you need to fetch device coords and map to AP/ML for storage.
            if messagebox.askquestion("Eat that question", "Define target by current position?", icon="warning") != "yes":
                return
            # self.fetch()
            
            # Read device absolute pos
            self.state.curr_pos = self.device.get_pos()
            curr = self.state.curr_pos
            zp = self.state.zero_pos

            x_rel = curr[0] - zp[0]
            y_rel = curr[1] - zp[1]
            dv = curr[2] - zp[2]
            aa = curr[3] - zp[3]

            # Convert device-relative XY -> user AP/ML based on rotation
            ap, ml = xy_to_apml(x_rel, y_rel, self.state.rotation_deg)
            # store user-relative (as floats)
            ap = float(ap)
            ml = float(ml)

            # Store relative in user coords (Option 1)
            self.state.RelAP_MkD.append(int(ap))
            self.state.RelML_MkD.append(int(ml))
            self.state.RelDV_MkD.append(int(dv))
            self.state.RelAA_MkD.append(int(aa))

            # Cache absolute device coords
            self.state.CoordX_MarkD.append(int(curr[0]))
            self.state.CoordY_MarkD.append(int(curr[1]))
            self.state.CoordZ_MarkD.append(int(curr[2]))
            self.state.CoordD_MarkD.append(int(curr[3]))
            
            new_entry = True

        if not new_entry:
            return
        
        # update color list
        n     = len(self.state.RelAP_MkD)
        BASE_COLORS = plt.get_cmap("tab20").colors
        color = BASE_COLORS[(n - 1) % len(BASE_COLORS)]
        self.state.RelColor_MkD.append(color)
        
        
        
        
        # Name bookkeeping
        name = get_str(self.widgets.get("NameMarD_box")) or f"Target{self.state.markD_idx + 1}"
        self.state.MarkD_names.append(name)
        
        # update figure
        dv_mix = (np.asarray(self.state.RelDV_MkD, float) +
          np.asarray(self.state.RelAA_MkD, float))
        markers = [{
            "name": "Target",
            "IDs": self.state.MarkD_names,
            "ap": self.state.RelAP_MkD,
            "ml": self.state.RelML_MkD,
            "dv": dv_mix,
            "colors": self.state.RelColor_MkD,  # permanent identity colors
            "legend": True,
            "label_numbers": True,
            "darken_by_dv": True,
            "darken_strength": 0.55,
            "max_legend": 40,
        }]
        update_fig(self.plot.ax, self.state.rotation_deg, markers=markers)
        self.plot.canvas.draw_idle()


        # Increment and rebuild the unified listbox from state
        self.state.markD_idx += 1
        self.refresh_targets_list()
        

    def markd_remove(self):
        lb = self.widgets.get("Targets_box")
        if lb is None or self.state.markD_idx <= 0:
            return
        
        sel = normalize_listbox_selection(lb.curselection())
        if sel is None:
            return
        if isinstance(sel, (tuple, list)):
            if not sel:
                return
            sel = sel[0]
        if isinstance(sel, str):
            sel = int(float(sel))
        else:
            sel = int(sel)
        
        if sel <= 0:
            return
        idx = sel - 1

        
        # Update state only
        self.state.MarkD_names.pop(idx)

        self.state.RelAP_MkD.pop(idx)
        self.state.RelML_MkD.pop(idx)
        self.state.RelDV_MkD.pop(idx)
        self.state.RelAA_MkD.pop(idx)

        self.state.CoordX_MarkD.pop(idx)
        self.state.CoordY_MarkD.pop(idx)
        self.state.CoordZ_MarkD.pop(idx)
        self.state.CoordD_MarkD.pop(idx)

        self.state.markD_idx -= 1

        # Rebuild UI from state (no need of delete the idx row here)
        self.refresh_targets_list()
        self.fetch()
        




    def go(self):
        # print("here: controllers/nav/def go 0")
        if not self.state.Zeroed:
            messagebox.showwarning("Error", "Zero basis first")
            return

        self.fetch()
        
        # read USER speed or set default
        speed = get_int(self.widgets.get("Speed_box"), default=2000)
        if get_str(self.widgets.get("Speed_box")) == "":
            set_entry(self.widgets.get("Speed_box"), "2000")
        
        goAP = get_str(self.widgets.get("GoAP_box"), "GoAP_box")
        goML = get_str(self.widgets.get("GoML_box"), "GoML_box")
        goDV = get_str(self.widgets.get("GoDV_box"), "GoDV_box")
        goAA = get_str(self.widgets.get("GoAA_box"), "GoAA_box")
        
        # print("GoAP_box widget:", self.widgets.get("GoAP_box"))
        # print("GoML_box widget:", self.widgets.get("GoML_box"))
        
        # Case 1: user typed AP/ML

        if goAP or goML:
            if not goAP or not goML:
                # print("here: controllers/nav/def go go boxes filled")
                messagebox.showwarning("Error", "Enter both AP & ML entries!")
                return

            if not goDV or not goAA:
                if messagebox.askquestion("Eat that question", "Move DV and A∠ to zero?", icon="warning") != "yes":
                    return
                goDV, goAA = "0", "0"
            
            try:
                ap = get_float(self.widgets.get("GoAP_box"), key_name="GoAP_box")
                ml = get_float(self.widgets.get("GoML_box"), key_name="GoML_box")
                
                # DV and A∠ can stay int (device uses ints)
                dv = get_int(self.widgets.get("GoDV_box"), default=0)
                aa = get_int(self.widgets.get("GoAA_box"), default=0)

            except ValueError:
                messagebox.showwarning("Invalid input", f"AP/ML/DV/A∠ must be integers.\nGot: AP={goAP!r}, ML={goML!r}, DV={goDV!r}, A∠={goAA!r}")
                return
            
            # else:
            #     rel = [int(goAP), int(goML), int(goDV), int(goAA)]
            
            # mapping AP/ML -> device XY rel
            x_rel, y_rel = apml_to_xy(ap, ml, self.state.rotation_deg)
            x_rel = int(round(x_rel))
            y_rel = int(round(y_rel))
            
            # Build device absolute target
            abs_target = [
                self.state.zero_pos[0] + x_rel,
                self.state.zero_pos[1] + y_rel,
                self.state.zero_pos[2] + int(round(dv)),
                self.state.zero_pos[3] + int(round(aa)),
                ]
            
            proceed, corrected = evaluate_new_coordinates(abs_target)
            if not proceed:
                return
            
            go_routine(self.device, self.state.curr_pos, corrected, speed, fetch_callback=self.fetch)
            
        # Case 2: use selected target from listbox
        else:
            # print("here: controllers/nav/def go markdown selected")
            idx = self.widgets["Targets_box"].curselection()
            if idx is None or idx <= 0:
                messagebox.showwarning("Error", "Select a target row (not the header) or enter coordinates")
                return
            
            state_idx = idx - 1 # header offset
            if state_idx >= self.state.markD_idx:
                messagebox.showwarning("Error", "Invalid selection")
                return
            
            target = [self.state.CoordX_MarkD[state_idx], self.state.CoordY_MarkD[state_idx], 0, 0]
            go_routine(self.device, self.state.curr_pos, target, speed, fetch_callback=self.fetch)

        # Clear input boxes (optional)
        for key in ["GoAP_box", "GoML_box", "GoDV_box", "GoAA_box"]:
            set_entry(self.widgets.get(key), "", key_name=key)
            
            

    def _format_target_row(self, idx: int) -> str:
        """
        Build ONE row string for the unified Targets_box list.

        Keeps relative (AP/ML/DV/A∠) and absolute (X/Y/Z/D) separated in the string.
        #=name | AP    ML    DV    A∠    || X Y Z D"
        """
        n = idx + 1
        name = self.state.MarkD_names[idx] if idx < len(self.state.MarkD_names) else f"Target{n}"

        # Relative (user/anatomical)
        ap = self.state.RelAP_MkD[idx]
        ml = self.state.RelML_MkD[idx]
        dv = self.state.RelDV_MkD[idx]
        aa = self.state.RelAA_MkD[idx]

        # Absolute (device)
        x = round(self.state.CoordX_MarkD[idx],1 )
        y = round(self.state.CoordY_MarkD[idx],1 )
        z = round(self.state.CoordZ_MarkD[idx],1 )
        d = round(self.state.CoordD_MarkD[idx],1 )


        return (
            f"{n}={name} | "
            f"AP:{ap}     ML:{ml}     DV:{dv}     A∠:{aa}     ||  "
            f"X:{x}  Y:{y}  Z:{z}  D:{d}"
        )

    def _clear_listbox(self, lb):
        """Best-effort clear for CTkListbox across versions."""
        if lb is None:
           return
       
       # many listbox implementations expect "0.0" or "end" or a range
        # Try common "delete all" patterns first
        for args in [("0.0", "end"), (0, "end"), ("0.0",), (0,)]:
            try:
                lb.delete(*args)
                # if it worked, we're done
                return
            except Exception:
                pass

        # Fallback: repeatedly delete the first item by trying known index formats
        while True:
            deleted = False
            for first in ("0.0", 0):
                try:
                    lb.delete(first)
                    deleted = True
                    break
                except Exception:
                    pass
            if not deleted:
                break

    # def _clear_listbox(self, lb):
    #     """Best-effort clear for CTkListbox."""
    #     if lb is None:
    #         return
    #     while True:
    #         try:
    #             lb.delete(0)
    #         except Exception:
    #             break


    # -------- NEW public method (#1/#3) --------
    def refresh_targets_list(self):
        """
        Clears and rebuilds the unified Targets_box from state.
        """
        lb = self.widgets.get("Targets_box")
        if lb is None:
            return

        self._clear_listbox(lb)

        # Header row (optional)
        lb.insert("0.0", "#=name | AP ML DV A∠ || X Y Z D")
        #=name | AP    ML    DV    A∠    || X Y Z D"

        for i in range(self.state.markD_idx):
            lb.insert(f"{i+1}.0", self._format_target_row(i))
            
    def _parse_int_field(self, key: str, label: str, default=None):
        s = get_str(self.widgets.get(key), key)
        if s == "" and default is not None:
            return default
        try:
            return int(s)
        except ValueError:
            messagebox.showwarning("Invalid input", f"{label} must be an integer. Got: {repr(s)}")
            raise

    def clear_go_entries(self):
        """Clear AP/ML/DV/A∠ input boxes manually."""
        for key in ["GoAP_box", "GoML_box", "GoDV_box", "GoAA_box"]:
            set_entry(self.widgets.get(key), "", key_name=key)


    def load_selected_target_into_go_boxes(self, state_idx: int):
        """
        Load *relative user-space* (AP/ML/DV/A∠) into the Go* boxes.
        state_idx: index into state arrays (header already accounted for)
        """

        if state_idx < 0:
            return
        # to protect Tk app from array-length mismatch
        needed = [self.state.RelAP_MkD, self.state.RelML_MkD, self.state.RelDV_MkD, self.state.RelAA_MkD]
        if any(state_idx >= len(arr) for arr in needed):
            print(f"[WARN] target arrays not aligned: state_idx={state_idx}, lens={[len(a) for a in needed]}, markD_idx={self.state.markD_idx}")
            return

        
        ap = self.state.RelAP_MkD[state_idx]
        ml = self.state.RelML_MkD[state_idx]
        dv = self.state.RelDV_MkD[state_idx]
        aa = self.state.RelAA_MkD[state_idx]
        
        set_entry(self.widgets.get("GoAP_box"), str(ap), key_name="GoAP_box")
        set_entry(self.widgets.get("GoML_box"), str(ml), key_name="GoML_box")
        set_entry(self.widgets.get("GoDV_box"), str(dv), key_name="GoDV_box")
        set_entry(self.widgets.get("GoAA_box"), str(aa), key_name="GoAA_box")
