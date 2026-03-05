# ui/tabs/navigation.py
import customtkinter as cmtk
from CTkListbox import CTkListbox
from ui.theme import THEME

def build_navigation_tab(tab, widgets, nav_ctrl, stop_callback):
    cmtk.CTkButton(tab, text="Reset", command=nav_ctrl.connect, width=12,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=0,y=0)

    cmtk.CTkButton(tab, text="Calibrate", command=nav_ctrl.calibrate, width=12,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=60,y=0)

    cmtk.CTkButton(tab, text="Center", command=nav_ctrl.center, width=12,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=140,y=0)

    cmtk.CTkButton(tab, text="Zero", command=nav_ctrl.zero_basis, width=12,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=205,y=0)

    cmtk.CTkButton(tab, text="Scape", command=nav_ctrl.scape, width=12,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_WARNING, hover_color=THEME.BTN_WARNING_HOVER, corner_radius=5).place(x=357,y=0)

    cmtk.CTkButton(tab, text="STOP", command=stop_callback, width=12,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_DANGER, hover_color=THEME.BTN_DANGER_HOVER, corner_radius=5).place(x=412,y=0)

    cmtk.CTkButton(tab, text="Fetch", command=nav_ctrl.fetch, width=12,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=80,y=35)

    # Current fields
    widgets["Xfield_box"] = cmtk.CTkEntry(tab, placeholder_text="AP=", width=80, font=("Verdana",10,"bold"),
                                         fg_color=THEME.ENTRY_BG, text_color=THEME.TXT_BLUE,
                                         placeholder_text_color=THEME.TXT_BLUE, corner_radius=3)
    widgets["Xfield_box"].place(x=140,y=35)

    widgets["Yfield_box"] = cmtk.CTkEntry(tab, placeholder_text="ML=", width=80, font=("Verdana",10,"bold"),
                                         fg_color=THEME.ENTRY_BG, text_color=THEME.TXT_BLUE,
                                         placeholder_text_color=THEME.TXT_BLUE, corner_radius=3)
    widgets["Yfield_box"].place(x=220,y=35)

    widgets["Zfield_box"] = cmtk.CTkEntry(tab, placeholder_text="DV=", width=80, font=("Verdana",10,"bold"),
                                         fg_color=THEME.ENTRY_BG, text_color=THEME.TXT_BLUE,
                                         placeholder_text_color=THEME.TXT_BLUE, corner_radius=3)
    widgets["Zfield_box"].place(x=300,y=35)

    widgets["Dfield_box"] = cmtk.CTkEntry(tab, placeholder_text="A∠=", width=80, font=("Verdana",10,"bold"),
                                         fg_color=THEME.ENTRY_BG, text_color=THEME.TXT_BLUE,
                                         placeholder_text_color=THEME.TXT_BLUE, corner_radius=3)
    widgets["Dfield_box"].place(x=380,y=35)
    
    
    # Toggle User/Device
    cmtk.CTkButton(
        tab,
        text="Toggle to Device",
        command=nav_ctrl.toggle_display_mode,
        width=12,
        font=("Verdana", 10, "bold"),
        fg_color=THEME.BTN_PRIMARY,
        hover_color=THEME.BTN_PRIMARY_HOVER,
        corner_radius=5,
    ).place(x=250, y=0)

    # Target name
    widgets["NameMarD_box"] = cmtk.CTkEntry(tab, placeholder_text=" ", width=50, height=8, font=("Verdana",10,"bold"),
                                           fg_color=THEME.ENTRY_BG, text_color=THEME.TXT_BLUE,
                                           placeholder_text_color=THEME.TXT_BLUE, corner_radius=3)
    widgets["NameMarD_box"].place(x=0,y=70)

    cmtk.CTkButton(tab, text="+", command=nav_ctrl.markd_add, width=10, height=8,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=0,y=95)

    cmtk.CTkButton(tab, text="-", command=nav_ctrl.markd_remove, width=20, height=8,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=30,y=95)
    
    widgets["Targets_box"] = CTkListbox(tab, command=nav_ctrl.selection_markd, width=80, font=("Verdana",8,"bold"),
                                        fg_color=THEME.ENTRY_BG, 
                                        text_color=THEME.TXT_WHITE,
                                        hover_color=THEME.BTN_PRIMARY_HOVER,
                                        scrollbar_button_color=THEME.SCROLLBAR_BTN,
                                        corner_radius=3)
    widgets["Targets_box"].insert("0.0", "#=name | AP       ML      DV       A∠        || X Y Z D")
    widgets["Targets_box"].place(x=60, y=70, relwidth=0.9, relheight=0.5)

    # lb = widgets["Targets_box"]
    # try:
    #     lb.bind("<Button-1>", lambda e: lb.focus_set())
    # except Exception:
    #     pass
    # lb.bind("<Up>", nav_ctrl.targets_key_up)
    # lb.bind("<Down>", nav_ctrl.targets_key_down)
    # lb.bind("<Return>", nav_ctrl.targets_key_enter)
    # lb.bind("<KP_Enter>", nav_ctrl.targets_key_enter)
    # lb.bind("<Delete>", nav_ctrl.targets_key_delete)
    # lb.bind("<BackSpace>", nav_ctrl.targets_key_delete)
    # lb.bind("<Escape>", nav_ctrl.targets_key_escape)



    cmtk.CTkButton(tab, text="Go", command=nav_ctrl.go, width=50,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=60,y=185)

    for key, x in [("GoAP_box",120), ("GoML_box",200), ("GoDV_box",280), ("GoAA_box",360)]:
        widgets[key] = cmtk.CTkEntry(tab, placeholder_text=" ", width=80, font=("Verdana",10,"bold"),
                                     fg_color=THEME.ENTRY_BG, text_color=THEME.TXT_BLUE,
                                     placeholder_text_color=THEME.TXT_BLUE, corner_radius=3)
        widgets[key].place(x=x, y=185)

    widgets["Speed_box"] = cmtk.CTkEntry(tab, placeholder_text="2000", width=50, font=("Verdana",10,"bold"),
                                        fg_color=THEME.ENTRY_BG, text_color=THEME.TXT_BLUE,
                                        placeholder_text_color=THEME.TXT_BLUE, corner_radius=3)
    widgets["Speed_box"].place(x=0,y=185)
    
    widgets["Speed_label"] = cmtk.CTkLabel(tab,
                               text = "Speed (μm/s)",
                               width   = 52,height = 5,
                               font    = ("Verdana",6,"bold"),
                               fg_color      = THEME.PANEL_BG,
                               text_color =  THEME.TXT_WHITE)
    widgets["Speed_label"].place(x=0,y=175)
    
    widgets["values_sign"] = cmtk.CTkLabel(tab,
                               text = "*Values are μm",
                               width   = 52,height = 5,
                               font    = ("Verdana",6,"bold"),
                               fg_color      = THEME.PANEL_BG,
                               text_color =  THEME.TXT_WHITE)
    widgets["values_sign"].place(x=0,y=35)
    
    


    cmtk.CTkButton(master=tab, text="x", command=nav_ctrl.clear_go_entries, width=10,
                   font=("Verdana", 10, "bold"), fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5,
                   ).place(x=440, y=185)   # adjust coordinates as needed

