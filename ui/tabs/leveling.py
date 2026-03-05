# ui/tabs/leveling.py
import customtkinter as cmtk
from ui.theme import THEME

def build_leveling_tab(tab, widgets, lvl_ctrl, stop_callback):
    cmtk.CTkButton(tab, text="Left", command=lvl_ctrl.left_level, width=70,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=50,y=35)

    cmtk.CTkButton(tab, text="Right", command=lvl_ctrl.right_level, width=70,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=140,y=35)

    cmtk.CTkButton(tab, text="Anterior", command=lvl_ctrl.ant_level, width=50,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=50,y=120)

    cmtk.CTkButton(tab, text="Posterior", command=lvl_ctrl.pos_level, width=50,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=140,y=120)

    widgets["LeftRoll_label"] = cmtk.CTkEntry(tab, placeholder_text="L:    ", width=60, height=5,
                                             font=("Verdana",10,"bold"),
                                             fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                                             placeholder_text_color=THEME.TXT_WHITE)
    widgets["LeftRoll_label"].place(x=50,y=70)

    widgets["RightRoll_label"] = cmtk.CTkEntry(tab, placeholder_text="R:    ", width=60, height=5,
                                              font=("Verdana",10,"bold"),
                                              fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                                              placeholder_text_color=THEME.TXT_WHITE)
    widgets["RightRoll_label"].place(x=140,y=70)

    widgets["RollOff_label"] = cmtk.CTkEntry(tab, placeholder_text="Roll Offset:      ", width=200, height=5,
                                            font=("Verdana",10,"bold"),
                                            fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                                            placeholder_text_color=THEME.TXT_WHITE)
    widgets["RollOff_label"].place(x=50,y=100)

    widgets["AntPitch_label"] = cmtk.CTkEntry(tab, placeholder_text="A:    ", width=60, height=5,
                                             font=("Verdana",10,"bold"),
                                             fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                                             placeholder_text_color=THEME.TXT_WHITE)
    widgets["AntPitch_label"].place(x=50,y=155)

    widgets["PosPitch_label"] = cmtk.CTkEntry(tab, placeholder_text="P:    ", width=60, height=5,
                                             font=("Verdana",10,"bold"),
                                             fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                                             placeholder_text_color=THEME.TXT_WHITE)
    widgets["PosPitch_label"].place(x=140,y=155)

    widgets["PitchOff_label"] = cmtk.CTkEntry(tab, placeholder_text="Pitch Offset:      ", width=200, height=5,
                                             font=("Verdana",10,"bold"),
                                             fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                                             placeholder_text_color=THEME.TXT_WHITE)
    widgets["PitchOff_label"].place(x=50,y=185)

    widgets["GoLR_box"] = cmtk.CTkEntry(tab, placeholder_text=" ", width=80, font=("Verdana",10,"bold"),#LR for left/right, to avoid duplicity with GoML_box
                                       fg_color=THEME.ENTRY_BG, text_color=THEME.TXT_BLUE,
                                       placeholder_text_color=THEME.TXT_BLUE, corner_radius=3)
    widgets["GoLR_box"].place(x=280,y=55)

    widgets["GoFB_box"] = cmtk.CTkEntry(tab, placeholder_text=" ", width=80, font=("Verdana",10,"bold"), #FB for front/Back, to avoid duplicity with GoAP_box
                                       fg_color=THEME.ENTRY_BG, text_color=THEME.TXT_BLUE,
                                       placeholder_text_color=THEME.TXT_BLUE, corner_radius=3)
    widgets["GoFB_box"].place(x=280,y=135)

    cmtk.CTkEntry(tab, placeholder_text="Go", width=22, height=5,
                 font=("Verdana",10,"bold"),
                 fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                 placeholder_text_color=THEME.TXT_WHITE).place(x=250,y=60)

    cmtk.CTkEntry(tab, placeholder_text="Go", width=22, height=5,
                 font=("Verdana",10,"bold"),
                 fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                 placeholder_text_color=THEME.TXT_WHITE).place(x=250,y=140)

    cmtk.CTkButton(tab, text="to the right", command=lvl_ctrl.go_right, width=10,
                   font=("Verdana",10,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=370,y=40)

    cmtk.CTkButton(tab, text="to the left", command=lvl_ctrl.go_left, width=12,
                   font=("Verdana",10,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=370,y=70)

    cmtk.CTkButton(tab, text="anterior", command=lvl_ctrl.go_anterior, width=10,
                   font=("Verdana",10,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=370,y=115)

    cmtk.CTkButton(tab, text="posterior", command=lvl_ctrl.go_posterior, width=12,
                   font=("Verdana",10,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=370,y=145)

    cmtk.CTkButton(tab, text="STOP", command=stop_callback, width=12,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_DANGER, hover_color=THEME.BTN_DANGER_HOVER, corner_radius=5).place(x=412,y=0)
    
    widgets["Mapping_label"] = cmtk.CTkEntry(tab, placeholder_text="Mapping:",
                                             width=220,
                                             font=("Verdana", 10, "bold"),
                                             fg_color     = THEME.PANEL_BG,          # or your background
                                             border_color = THEME.PANEL_BG,
                                             text_color   = THEME.TXT_BLUE,
                                             placeholder_text_color = THEME.TXT_BLUE,
                                             corner_radius= 3,
                                             )
    widgets["Mapping_label"].place(x=330, y=185)  # pick coordinates you like
    
    widgets["SpeedLevel_box"] = cmtk.CTkEntry(tab,
                                              placeholder_text ="2000",
                                              width            = 50, 
                                              font       = ("Verdana",8,"bold"),
                                              fg_color   = THEME.ENTRY_BG, 
                                              text_color = THEME.TXT_BLUE,
                                              placeholder_text_color = THEME.TXT_BLUE, 
                                              corner_radius = 3)
    widgets["SpeedLevel_box"].place(x=280,y=185)
    
    widgets["SpeedLevel_label"] = cmtk.CTkLabel(tab,
                               text = "Speed (μm/s)",
                               width   = 52,height = 5,
                               font    = ("Verdana",6,"bold"),
                               fg_color      = THEME.PANEL_BG,
                               text_color =  THEME.TXT_WHITE)
    widgets["SpeedLevel_label"].place(x=280,y=175)

