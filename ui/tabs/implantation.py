# ui/tabs/implantation.py
import customtkinter as cmtk
from ui.theme import THEME

def build_implantation_tab(tab, widgets, imp_ctrl, stop_callback):
    cmtk.CTkEntry(tab, placeholder_text="Raw", width=52, height=5,
                 font=("Verdana",8,"bold"),
                 fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                 placeholder_text_color=THEME.TXT_WHITE).place(x=140,y=0)

    cmtk.CTkEntry(tab, placeholder_text="Zeroed", width=52, height=5,
                 font=("Verdana",8,"bold"),
                 fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                 placeholder_text_color=THEME.TXT_WHITE).place(x=200,y=0)

    cmtk.CTkButton(tab, text="Fetch", command=imp_ctrl.fetch_dv, width=50,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=5,y=10)

    cmtk.CTkButton(tab, text="Zero DV", command=imp_ctrl.zero_dv, width=50,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5).place(x=60,y=10)

    widgets["RawImplant_label"] = cmtk.CTkEntry(tab, placeholder_text="  0", width=200, height=3,
                                              font=("Verdana",10,"bold"),
                                              fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                                              placeholder_text_color=THEME.TXT_WHITE)
    widgets["RawImplant_label"].place(x=140,y=15)

    widgets["ZroImplant_label"] = cmtk.CTkEntry(tab, placeholder_text="  0", width=200, height=3,
                                              font=("Verdana",10,"bold"),
                                              fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                                              placeholder_text_color=THEME.TXT_WHITE)
    widgets["ZroImplant_label"].place(x=200,y=15)

    cmtk.CTkButton(tab, text="Implant", command=imp_ctrl.implant, width=50,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_WARNING, hover_color=THEME.BTN_WARNING_HOVER, corner_radius=5).place(x=60,y=60)

    cmtk.CTkButton(tab, text="Explant", command=imp_ctrl.explant, width=50,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_WARNING, hover_color=THEME.BTN_WARNING_HOVER, corner_radius=5).place(x=300,y=60)

    widgets["ZImplant_checkbox"] = cmtk.CTkCheckBox(
        tab, text="Z", command=imp_ctrl.zcheck_fun, width=52, height=5,
        checkbox_width=20, checkbox_height=20, border_width=2,
        font=("Verdana",12,"bold"),
        fg_color=THEME.PANEL_BG, border_color=THEME.TXT_WHITE,
        onvalue="on", offvalue="off"
    )
    widgets["ZImplant_checkbox"].place(x=170,y=35)

    widgets["DImplant_checkbox"] = cmtk.CTkCheckBox(
        tab, text="D", command=imp_ctrl.dcheck_fun, width=52, height=5,
        checkbox_width=20, checkbox_height=20, border_width=2,
        font=("Verdana",12,"bold"),
        fg_color=THEME.PANEL_BG, border_color=THEME.TXT_WHITE,
        onvalue="on", offvalue="off"
    )
    widgets["DImplant_checkbox"].place(x=240,y=35)

    widgets["ZImplant_box"] = cmtk.CTkEntry(tab, placeholder_text="0", width=50, font=("Verdana",10,"bold"),
                                          fg_color=THEME.ENTRY_BG, text_color=THEME.TXT_BLUE,
                                          placeholder_text_color=THEME.TXT_BLUE, corner_radius=3)
    widgets["ZImplant_box"].place(x=160,y=60)

    widgets["DImplant_box"] = cmtk.CTkEntry(tab, placeholder_text="0", width=50, font=("Verdana",10,"bold"),
                                          fg_color=THEME.ENTRY_BG, text_color=THEME.TXT_BLUE,
                                          placeholder_text_color=THEME.TXT_BLUE, corner_radius=3)
    widgets["DImplant_box"].place(x=240,y=60)

    cmtk.CTkEntry(tab, placeholder_text="Speed", width=52, height=5,
                 font=("Verdana",8,"bold"),
                 fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                 placeholder_text_color=THEME.TXT_WHITE).place(x=60,y=100)

    cmtk.CTkEntry(tab, placeholder_text="(μm/s)",
                 width=52, height=5,
                 font=("Verdana",8,"bold"),
                 fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                 placeholder_text_color=THEME.TXT_WHITE).place(x=60,y=113)

    widgets["SpeedImplant_box"] = cmtk.CTkEntry(tab, placeholder_text="50", width=50, font=("Verdana",10,"bold"),
                                              fg_color=THEME.ENTRY_BG, text_color=THEME.TXT_BLUE,
                                              placeholder_text_color=THEME.TXT_BLUE, corner_radius=3)
    widgets["SpeedImplant_box"].place(x=60,y=131)

    widgets["ZTrack_label"] = cmtk.CTkEntry(tab, placeholder_text=" 0", width=52, height=5,
                                           font=("Verdana",12,"bold"),
                                           fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                                           placeholder_text_color=THEME.TXT_WHITE)
    widgets["ZTrack_label"].place(x=178,y=100)

    widgets["DTrack_label"] = cmtk.CTkEntry(tab, placeholder_text=" 0", width=52, height=5,
                                           font=("Verdana",12,"bold"),
                                           fg_color=THEME.PANEL_BG, border_color=THEME.PANEL_BG,
                                           placeholder_text_color=THEME.TXT_WHITE)
    widgets["DTrack_label"].place(x=260,y=100)

    cmtk.CTkButton(tab, text="STOP", command=stop_callback, width=12,
                   font=("Verdana",12,"bold"),
                   fg_color=THEME.BTN_DANGER, hover_color=THEME.BTN_DANGER_HOVER, corner_radius=5).place(x=412,y=0)
