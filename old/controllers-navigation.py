# controllers/navigation.py
from tkinter import messagebox
from core.ui_helpers import set_entry, get_int, get_str
from core.math_utils import evaluate_new_coordinates, go_routine, apml_to_xy, xy_to_apml, comply_rotation

class NavigationController:
    def __init__(self, state, device, widgets):
        self.state = state
        self.device = device
        self.widgets = widgets

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

        # if self.state.Zeroed:
        #     x = str(round(curr[0] - zero[0], 1))
        #     y = str(round(curr[1] - zero[1], 1))
        #     z = str(round(curr[2] - zero[2], 1))
        #     d = str(round(curr[3] - zero[3], 1))
        # else:
        #     x = str(round(curr[0], 1))
        #     y = str(round(curr[1], 1))
        #     z = str(round(curr[2], 1))
        #     d = str(round(curr[3], 1))
        
        if self.state.display_mode == "device":
            # Device view: X/Y/Z/D
            set_entry(self.widgets.get("Xfield_box"), f"X= {round(x,1)}")
            set_entry(self.widgets.get("Yfield_box"), f"Y= {round(y,1)}")
            set_entry(self.widgets.get("Zfield_box"), f"Z= {round(z,1)}")
            set_entry(self.widgets.get("Dfield_box"), f"D= {round(d,1)}")
            return
            # set_entry(self.widgets.get("Xfield_box"), f"X= {x}")
            # set_entry(self.widgets.get("Yfield_box"), f"Y= {y}")
            # set_entry(self.widgets.get("Zfield_box"), f"Z= {z}")
            # set_entry(self.widgets.get("Dfield_box"), f"D= {d}")
            # return
        
        # User view: AP/ML/DV/A∠
        p, ml = xy_to_apml(int(round(x)), int(round(y)), self.state.rotation_deg)
        set_entry(self.widgets.get("Xfield_box"), f"AP= {ap}")
        (self.widgets.get("Yfield_box"), f"ML= {ml}")
        set_entry(self.widgets.get("Zfield_box"), f"DV= {round(z,1)}")
        set_entry(self.widgets.get("Dfield_box"), f"A∠= {round(d,1)}")
    
        # ap, ml = xy_to_apml(x, y, self.state.rotation_deg)

        # set_entry(self.widgets.get("Xfield_box"), f"AP= {ap}")
        # set_entry(self.widgets.get("Yfield_box"), f"ML= {ml}")
        # set_entry(self.widgets.get("Zfield_box"), f"DV {z}")
        # set_entry(self.widgets.get("Dfield_box"), f"A∠= {d}")
        
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
            self.state.CoordX_MarkD = [zp[0] + x for x in self.state.CoordX_RelMkD]
            self.state.CoordY_MarkD = [zp[1] + x for x in self.state.CoordY_RelMkD]
            self.state.CoordZ_MarkD = [zp[2] + x for x in self.state.CoordZ_RelMkD]
            self.state.CoordD_MarkD = [zp[3] + x for x in self.state.CoordD_RelMkD]
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
        idx = lb.curselection()
        try:
            lb.activate(idx)
        except Exception:
            pass
        # idx = self.widgets["ListMarD_box"].curselection()
        # self.widgets["Targets_box"].activate(idx)
        # self.widgets["ListMarDY_box"].activate(idx)
        # self.widgets["ListMarDZ_box"].activate(idx)
        # self.widgets["ListMarDD_box"].activate(idx)

    def markd_add(self):
        # print("\n====== MARKD_ADD DEBUG ======")

        # expected = ["GoAP_box", "GoML_box", "GoDV_box", "GoAA_box"]

        # for key in expected:
        #     w = self.widgets.get(key)

        #     if w is None:
        #         print(f"{key:12} -> ❌ NOT FOUND in widgets dict")
        #         continue

        #     try:
        #         value = w.get()
        #         placeholder = w.cget("placeholder_text") if hasattr(w, "cget") else None
        #     except Exception as e:
        #         print(f"{key:12} -> ⚠️ get/cget failed: {e}")
        #         continue
            
        #     print(f"{key:12} -> id={id(w)}  get()={repr(value)}  placeholder={repr(placeholder)}")


        # print("Available widget keys:")
        # print(sorted(self.widgets.keys()))
        # print("=============================\n")

        # print("GoAP_box widget:", self.widgets.get("GoAP_box"))
        # print("GoML_box widget:", self.widgets.get("GoML_box"))
        
        
        if not self.state.Zeroed:
            messagebox.showwarning("Stop right there", "Zero basis first")
            return
        
        # ap = self._parse_int_field("GoAP_box", "AP")
        # ml = self._parse_int_field("GoML_box", "ML")
        # dv = self._parse_int_field("GoDV_box", "DV", default=0)
        # aa = self._parse_int_field("GoAA_box", "A∠", default=0)

        APs = get_str(self.widgets.get("GoAP_box"), "GoAP_box")
        MLs = get_str(self.widgets.get("GoML_box"), "GoML_box")
        DVs = get_str(self.widgets.get("GoDV_box"), "GoDV_box")
        AAs = get_str(self.widgets.get("GoAA_box"), "GoAA_box")
        new_entry = False
        # print("APs:", repr(APs), "MLs:", repr(MLs), "DVs:", repr(DVs), "AAs:", repr(AAs))

        if APs or MLs:
            if not APs or not MLs:
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

            # if not DVs or not AAs:
            #     if messagebox.askquestion("Eat that question", "Fill DV and A∠ with zeros?", icon="warning") != "yes":
            #         return
            #     ap = int(APs); ml = int(MLs); dv = 0; aa = 0
            # else:
            #     ap = int(APs); ml = int(MLs); dv = int(DVs); aa = int(AAs)
                
            self.state.RelAP_MkD.append(ap)
            self.state.RelML_MkD.append(ml)
            self.state.RelDV_MkD.append(dv)
            self.state.RelAA_MkD.append(aa)
            
            # Convert AP/ML -> device XY rel depending on rotation
            x_rel, y_rel = apml_to_xy(ap, ml, self.state.rotation_deg)
            
            # Convert to absolute device coords using zero_pos
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

            # self.state.CoordX_RelMkD.append(rel[0])
            # self.state.CoordY_RelMkD.append(rel[1])
            # self.state.CoordZ_RelMkD.append(rel[2])
            # self.state.CoordD_RelMkD.append(rel[3])

            # Xstr, Ystr, Zstr, Dstr = map(str, rel)

            for key in ["GoAP_box", "GoML_box", "GoDV_box", "GoAA_box"]:
                set_entry(self.widgets.get(key)," ", key_name=key)

                # set_entry(self.widgets.get(key), "")

            new_entry = True

        else:
            # If you still want "define by current position" in user-space,
            # you need to fetch device coords and map to AP/ML for storage.
            if messagebox.askquestion("Eat that question", "Define target by current position?", icon="warning") != "yes":
                return
            self.fetch()
            
            # take current device relative coords (as shown in device space)
            self.state.curr_pos = self.device.get_pos()
            curr = self.state.curr_pos
            zp = self.state.zero_pos

            x_rel = curr[0] - zp[0]
            y_rel = curr[1] - zp[1]
            dv = curr[2] - zp[2]
            aa = curr[3] - zp[3]

            ap, ml = xy_to_apml(int(x_rel), int(y_rel), self.state.rotation_deg)

            self.state.RelAP_MkD.append(ap)
            self.state.RelML_MkD.append(ml)
            self.state.RelDV_MkD.append(int(dv))
            self.state.RelAA_MkD.append(int(aa))

            self.state.CoordX_MarkD.append(int(curr[0]))
            self.state.CoordY_MarkD.append(int(curr[1]))
            self.state.CoordZ_MarkD.append(int(curr[2]))
            self.state.CoordD_MarkD.append(int(curr[3]))
            
            # cp = list(self.state.curr_pos)

            # self.state.CoordX_MarkD.append(cp[0])
            # self.state.CoordY_MarkD.append(cp[1])
            # self.state.CoordZ_MarkD.append(cp[2])
            # self.state.CoordD_MarkD.append(cp[3])

            # self.state.CoordX_RelMkD.append(cp[0])
            # self.state.CoordY_RelMkD.append(cp[1])
            # self.state.CoordZ_RelMkD.append(cp[2])
            # self.state.CoordD_RelMkD.append(cp[3])

            # Xstr = str(round(cp[0] - self.state.zero_pos[0], 1))
            # Ystr = str(round(cp[1] - self.state.zero_pos[1], 1))
            # Zstr = str(round(cp[2] - self.state.zero_pos[2], 1))
            # Dstr = str(round(cp[3] - self.state.zero_pos[3], 1))
            new_entry = True

        if not new_entry:
            return

        name = get_str(self.widgets.get("NameMarD_box")) or f"Target{self.state.markD_idx + 1}"
        self.state.MarkD_names.append(name)

        row = self.state.markD_idx
        self.widgets["Targets_box"].insert(f"{row}.0", self._format_target_row(row))
        # self.widgets["ListMarD_box"].insert(f"{row}.0", f"{row+1}={name}")
        # self.widgets["ListMarDX_box"].insert(f"{row}.0", Xstr)
        # self.widgets["ListMarDY_box"].insert(f"{row}.0", Ystr)
        # self.widgets["ListMarDZ_box"].insert(f"{row}.0", Zstr)
        # self.widgets["ListMarDD_box"].insert(f"{row}.0", Dstr)

        self.state.markD_idx += 1
        

    def markd_remove(self):
        lb = self.widgets.get("Targets_box")
        if lb is None or self.state.markD_idx <= 0:
            return
        
        sel = lb.curselection()
        if sel is None:
            return
        # idx = self.widgets["ListMarD_box"].curselection()
        # if idx is None:
        #     return
            
        # Because row 0 is header, actual target index is sel-1
        idx = sel - 1
        if idx < 0 or idx >= self.state.markD_idx:
            return
       # Remove state entries
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

        self.refresh_targets_list()
        self.fetch()
        
        # for key in ["ListMarD_box", "ListMarDX_box", "ListMarDY_box", "ListMarDZ_box", "ListMarDD_box"]:
        #     self.widgets[key].delete(idx)
        self.widgets["Targets_box"].delete(idx)

        # self.state.MarkD_names.pop(idx)
        # self.state.CoordX_MarkD.pop(idx)
        # self.state.CoordY_MarkD.pop(idx)
        # self.state.CoordZ_MarkD.pop(idx)
        # self.state.CoordD_MarkD.pop(idx)
        # self.state.CoordX_RelMkD.pop(idx)
        # self.state.CoordY_RelMkD.pop(idx)
        # self.state.CoordZ_RelMkD.pop(idx)
        # self.state.CoordD_RelMkD.pop(idx)

        # self.state.markD_idx -= 1
        # self.fetch()

    def go(self):
        print("here: controllers/nav/def go 0")
        if not self.state.Zeroed:
            messagebox.showwarning("Error", "Zero basis first")
            return

        self.fetch()
        speed = get_int(self.widgets.get("Speed_box"), default=2000)
        
        goAP = get_str(self.widgets.get("GoAP_box"), "GoAP_box")
        goML = get_str(self.widgets.get("GoML_box"), "GoML_box")
        goDV = get_str(self.widgets.get("GoDV_box"), "GoDV_box")
        goAA = get_str(self.widgets.get("GoAA_box"), "GoAA_box")
        
        print("GoAP_box widget:", self.widgets.get("GoAP_box"))
        print("GoML_box widget:", self.widgets.get("GoML_box"))

        if goAP or goML:
            if not goAP or not goML:
                print("here: controllers/nav/def go go boxes filled")
                messagebox.showwarning("Error", "Enter both AP & ML entries!")
                return

            if not goDV or not goAA:
                if messagebox.askquestion("Eat that question", "Move DV and A∠ to zero?", icon="warning") != "yes":
                    return
                rel = [int(goAP), int(goML), 0, 0]
            else:
                rel = [int(goAP), int(goML), int(goDV), int(goAA)]

            true_coords = comply_rotation(rel, self.state.rotation_deg)
            abs_target = [z + t for z, t in zip(self.state.zero_pos, true_coords)]
            proceed, corrected = evaluate_new_coordinates(abs_target)
            if not proceed:
                return

            go_routine(self.device, self.state.curr_pos, corrected, speed, fetch_callback=self.fetch)

        else:
            print("here: controllers/nav/def go markdown selected")
            idx = self.widgets["Targets_box"].curselection()
            if idx is None or idx <= 0:
                messagebox.showwarning("Error", "Select a target row (not the header) or enter coordinates")
                return
            
            state_idx = idx - 1
            if state_idx >= self.state.markD_idx:
                messagebox.showwarning("Error", "Invalid selection")
                return
            
            target = [self.state.CoordX_MarkD[state_idx], self.state.CoordY_MarkD[state_idx], 0, 0]
            go_routine(self.device, self.state.curr_pos, target, speed, fetch_callback=self.fetch)

        for key in ["GoAP_box", "GoML_box", "GoDV_box", "GoAA_box"]:
            set_entry(self.widgets.get(key), " ")
            
            

    def _format_target_row(self, idx: int) -> str:
        """
        Build ONE row string for the unified Targets_box list.

        Keeps relative (AP/ML/DV/A∠) and absolute (X/Y/Z/D) separated in the string.
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
            f"AP:{ap}  ML:{ml}  DV:{dv}  A∠:{aa}  ||  "
            f"X:{x}  Y:{y}  Z:{z}  D:{d}"
        )


    def _clear_listbox(self, lb):
        """Best-effort clear for CTkListbox."""
        if lb is None:
            return
        while True:
            try:
                lb.delete(0)
            except Exception:
                break


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
