# main.py
import customtkinter as cmtk

from core.state import AppState
from core.device import SensapexDevice
from ui.theme import THEME
from ui.figure3d import create_plot
from ui.tabs.navigation import build_navigation_tab
from ui.tabs.leveling import build_leveling_tab
from ui.tabs.implantation import build_implantation_tab

from controllers.common import CommonController
from controllers.navigation import NavigationController
from controllers.leveling import LevelingController
from controllers.implantation import ImplantationController

def main():
    # CTk config
    cmtk.set_appearance_mode("Dark")
    cmtk.set_default_color_theme("blue")
    cmtk.set_widget_scaling(2.3)
    cmtk.set_window_scaling(1.3)

    # Core objects
    state = AppState()
    device = SensapexDevice()
    widgets = {}

    # Root
    root = cmtk.CTk()
    root.title("Sensapex User Interface")
    root.resizable(True, True)
    root.geometry("1400x700")

    # Tabview
    tabview = cmtk.CTkTabview(
        master=root, width=500, height=280,
        fg_color=THEME.PANEL_BG,
        segmented_button_selected_color=THEME.BTN_PRIMARY,
        segmented_button_selected_hover_color=THEME.BTN_PRIMARY_HOVER
    )
    tabview.place(x=5, y=1)
    tabview.add("Navigation")
    tabview.add("Leveling")
    tabview.add("Implantation")
    tabview.add("Atlas")
    tabview.add("Settings")
    tabview.set("Navigation")
    
    
    # Quit
    cmtk.CTkButton(
        master=root, text="Quit", command=root.destroy, width=8,
        font=("Verdana",12,"bold"),
        fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5
    ).place(x=5, y=300)

    # Wheels (UI only)
    x_shift = 540
    widgets["wheel_sign"] = cmtk.CTkLabel(root, text = "Wheel rotary control's \n current map",
                               width = 1, height = 1, font = ("Verdana",6,"italic"), text_color = THEME.TXT_WHITE)
    widgets["wheel_sign"].place(x=170+x_shift, y=285)
    widgets["x_sign"] = cmtk.CTkLabel(root, text = "x",
                               width = 1, font = ("Verdana",6,"italic"), text_color = THEME.TXT_WHITE)
    widgets["x_sign"].place(x=100+x_shift, y=325)
    widgets["XWheel"] = cmtk.CTkButton(root, text="AP", width=.5, font=("Verdana",8,"bold"),
                                      fg_color=THEME.AXIS_ML, corner_radius=30)
    widgets["XWheel"].place(x=80+x_shift, y=305)
    
    widgets["y_sign"] = cmtk.CTkLabel(root, text = "y",
                               width = 1, height = 1,  font = ("Verdana",6,"italic"), text_color = THEME.TXT_WHITE)
    widgets["y_sign"].place(x=140+x_shift, y=280)
    widgets["YWheel"] = cmtk.CTkButton(root, text="ML", width=.5, font=("Verdana",8,"bold"),
                                      fg_color=THEME.AXIS_AP, corner_radius=30)
    widgets["YWheel"].place(x=120+x_shift, y=290)
    
    widgets["z_sign"] = cmtk.CTkLabel(root, text = "z",
                               width = 1, font = ("Verdana",6,"italic"), text_color = THEME.TXT_WHITE)
    widgets["z_sign"].place(x=180+x_shift, y=325)
    widgets["ZWheel"] = cmtk.CTkButton(root, text="DV", width=.5, font=("Verdana",8,"bold"),
                                      fg_color=THEME.AXIS_DV, corner_radius=30)
    widgets["ZWheel"].place(x=160+x_shift, y=305)
    
    widgets["d_sign"] = cmtk.CTkLabel(root, text = "d",
                               width = 1, font = ("Verdana",6,"italic"), text_color = THEME.TXT_WHITE)
    widgets["d_sign"].place(x=140+x_shift, y=340)
    widgets["DWheel"] = cmtk.CTkButton(root, text="A∠", width=10, font=("Verdana",8,"bold"),
                                      fg_color=THEME.AXIS_DV, corner_radius=30)
    widgets["DWheel"].place(x=120+x_shift, y=320)

    # Figure
    plot = create_plot(root, rotation_deg=state.rotation_deg)
    # plot.canvas.get_tk_widget().pack(side="right")
    plot.canvas.get_tk_widget().place(relx=.65, rely=0)

    # Controllers
    nav_ctrl = NavigationController(state, device, widgets, plot)
    lvl_ctrl = LevelingController(state, device, widgets)
    imp_ctrl = ImplantationController(state, device, widgets, nav_controller=nav_ctrl)
    common_ctrl = CommonController(state, device, widgets, plot, nav_ctrl=nav_ctrl, lvl_ctrl=lvl_ctrl)

    # Rotate space button (wired to common controller)
    cmtk.CTkButton(
        master=root, text="Rot. 90 deg.", command=common_ctrl.rotate_space, width=4,
        font=("Verdana",10,"bold"),
        fg_color=THEME.BTN_PRIMARY, hover_color=THEME.BTN_PRIMARY_HOVER, corner_radius=5
    ).place(x=0+x_shift, y=305)

    # Build tabs (UI only)
    build_navigation_tab(tabview.tab("Navigation"), widgets, nav_ctrl, stop_callback=common_ctrl.stop)
    build_leveling_tab(tabview.tab("Leveling"), widgets, lvl_ctrl, stop_callback=common_ctrl.stop)
    build_implantation_tab(tabview.tab("Implantation"), widgets, imp_ctrl, stop_callback=common_ctrl.stop)
    
    # lvl_ctrl.update_mapping_label()
    # nav_ctrl.refresh_targets_list()
    # nav_ctrl.fetch() # triggers Error:   controllers/navigation/fetch() -> device/commons/get_pos()  'Manipulator not connected.'

    # Optional: connect at startup without crashing UI
    try:
        nav_ctrl.connect()
    except Exception as e:
        print(f"Startup connect failed: {e}")

    root.mainloop()

if __name__ == "__main__":
    main()
