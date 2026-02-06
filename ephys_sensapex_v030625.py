import customtkinter as cmtk
import tkinter as tk
from tkinter import messagebox, PhotoImage
from sensapex import UMP
from CTkListbox import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from starter_fun import show_Stop_btn


###################################
# GLOBAL VARIABLES
ump          = UMP.get_ump()           # connect to UMP
dev_ids      = ump.list_devices()  # Find list of devices
manipulator  = ump.get_device(dev_ids[0]) # Connect to available device
curr_pos     = manipulator.get_pos()
zero_pos     = [0, 0, 0, 0]
markD_idx    = 0
log_idx      = 1
MarkDList    = ["#=name"]
MarkDList_X  = ["X     "]
MarkDList_Y  = ["Y     "]
MarkDList_Z  = ["Z     "]
MarkDList_D  = ["D     "]

selected_MarkD = []
CoordX_MarkD = []
CoordY_MarkD = []
CoordZ_MarkD = []
CoordD_MarkD = []
new_target   = [0, 0, 0, 0]

rotation_deg = 0;

CoordX_RelMkD = []
CoordY_RelMkD = []
CoordZ_RelMkD = []
CoordD_RelMkD = []

Zeroed       = 0
ZeroedX      = []
ZeroedY      = []
ZeroedZ      = []
ZeroedD      = []

DVzeroed     = 0
DVzero_pos   = [0, 0]
DVzeroedZ    = []
DVzeroedD    = []

MarkD_names  = []
left_set     = 0
right_set    = 0
ant_set      = 0
pos_set      = 0
left_level   = []
right_level  = []
ant_level    = []
pos_level    = []

Space_orientation = 0
# Zcheck_var = tk.StringVar("on")
# Dcheck_var = tk.StringVar("on")

###################################
# INITIALIZE ROOT OBJECT
cmtk.set_appearance_mode("Dark")  # Modes: system (default), light, dark
cmtk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

cmtk.set_widget_scaling(2.3)  # widget dimensions and text size
cmtk.set_window_scaling(1.3)  # window geometry dimensions


root = cmtk.CTk()  # create CTk window like you do with the Tk window
root.title("Sensapex User Interface")
root.resizable(True, True)
root.geometry("1400x600")


###################################
###################################
###################################

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# FUNCTIONS
def connect_fun():
    global manipulator
    ump = UMP.get_ump()           # connect to UMP
    dev_ids = ump.list_devices()  # Find list of devices
    manipulator = ump.get_device(dev_ids[0])
    Fetch_fun()                   # print current coords.
    # # uptdate log
    # new_str = "Device {} connected".format(str(dev_ids[0]))
    # log_callback(new_str) # update log
    
    #end
    
def calib_fun():
    # log_callback("Calibrating...  ") # uptdate log
    
    # calibrate
    manipulator.calibrate_zero_position()
        
    #end
def center_fun():
    # log_callback("Centering...  ") # uptdate log
    manipulator.goto_pos([10000,10000,0,0], speed=1000)
    print("Centering")
    #while(manipulator.is_busy()):
    #   print("Centering")
    Fetch_fun()                   # update current coords.
        
    #end


def Zero_fun():
    global zero_pos, curr_pos, markD_idx, CoordX_MarkD, CoordY_MarkD,  CoordZ_MarkD,  CoordD_MarkD, MarkD_names
    global Zeroed, zero_pos, CoordX_RelMkD, CoordY_RelMkD, CoordZ_RelMkD, CoordD_RelMkD
    Fetch_fun()
    print("Zero_fun")
    zero_pos = curr_pos
    
    Xfield_box.delete(0,"end")
    Xfield_box.insert(0,"X= " + "0.0")
    Yfield_box.delete(0,"end")
    Yfield_box.insert(0,"Y= " +"0.0")
    Zfield_box.delete(0,"end")
    Zfield_box.insert(0,"Z= " + "0.0")
    Dfield_box.delete(0,"end")
    Dfield_box.insert(0,"D= " + "0.0")
    
    if Zeroed==1:
        CoordX_MarkD   = [zero_pos[0] + x for x in CoordX_RelMkD]
        CoordY_MarkD   = [zero_pos[1] + x for x in CoordY_RelMkD]
        CoordZ_MarkD   = [zero_pos[2] + x for x in CoordZ_RelMkD]
        CoordD_MarkD   = [zero_pos[3] + x for x in CoordD_RelMkD]
    else:
        Zeroed   = 1
     
    # end

def Comply_rotation(input_coords):
    global rotation_deg, CoordX_MarkD, CoordY_MarkD,  CoordZ_MarkD,  CoordD_MarkD
    print("Comply_rotation fun")
    
    """
     Given the initial coordinates (X, Y, Z, D), computes the change of basis to ML, AP, DV, D,
     applies the rotation, and returns the new (X, Y, Z, D) coordinates after the rotation.
    """
    # Step 1: Translate from global (X, Y, Z, D) to local (ML, AP, DV, D)
     
    local_coords = np.array(input_coords)
    
    # Step 2: Apply the rotation matrix to the local coordinates
    """
    Returns a 4x4 rotation matrix for the specified angle in degrees
    for rotations about the Z-axis (affecting LR, FB, UD, D).
    """
    radians = np.deg2rad(rotation_deg)
    cos_theta = np.cos(radians)
    sin_theta = np.sin(radians)
    
    # Rotation matrix for a 2D rotation in the XY-plane, extended for 4D coordinates
    rotation_matrix = np.array([[cos_theta, -sin_theta, 0, 0],
                                [sin_theta,  cos_theta, 0, 0],
                                [        0,          0, 1, 0],
                                [        0,          0, 0, 1]])
    # Step 3: Translate back to global (X, Y, Z, D)

    new_local_coords  = np.dot(rotation_matrix, local_coords)
    
    # convert to int 
    new_global_coords = [int(x) for x in new_local_coords]
    #print(f"new coords. =  {new_global_coords}")
    return new_global_coords
    #end

def Scape_fun():
    manipulator.goto_pos(curr_pos, speed=1000)
    curr_pos[2] = 0
    curr_pos[3] = 0
    
    while(manipulator.is_busy()):
        print("Scaping")
    # log_callback("Scape finalized") # update log 
    #end
    
def Stop_fun():
    manipulator.stop()
    manipulator.stop()
    manipulator.stop()
    print("'Stop' button pressed")
    #end
    
def Fetch_fun():
    global curr_pos, Zeroed, zero_pos
    curr_pos = manipulator.get_pos()
    if Zeroed==1:
        Xstr = str(round(curr_pos[0] - zero_pos[0],1))
        Ystr = str(round(curr_pos[1] - zero_pos[1],1))
        Zstr = str(round(curr_pos[2] - zero_pos[2],1))
        Dstr = str(round(curr_pos[3] - zero_pos[3],1))
    else:
        Xstr = str(round(curr_pos[0],1))
        Ystr = str(round(curr_pos[1],1))
        Zstr = str(round(curr_pos[2],1))
        Dstr = str(round(curr_pos[3],1))
    
    Xfield_box.delete(0,"end")
    Xfield_box.insert(0,"X= " + Xstr)
    Yfield_box.delete(0,"end")
    Yfield_box.insert(0,"Y= " + Ystr)
    Zfield_box.delete(0,"end")
    Zfield_box.insert(0,"Z= " + Zstr)
    Dfield_box.delete(0,"end")
    Dfield_box.insert(0,"D= " + Dstr)
    
    # log_callback("Current position updated") # uptdate log
    
    #end

def Selection_MarkD_fun(selected_option):
    selected_markD = ListMarD_box.curselection()

    ListMarDX_box.activate(selected_markD)           # Highlight the item
    ListMarDY_box.activate(selected_markD)
    ListMarDZ_box.activate(selected_markD)
    ListMarDD_box.activate(selected_markD)


def MarkD_fun():
    global markD_idx, CoordX_MarkD, CoordY_MarkD, CoordZ_MarkD, CoordD_MarkD, MarkD_names, new_target
    global Zeroed, zero_pos, CoordX_RelMkD, CoordY_RelMkD, CoordZ_RelMkD, CoordD_RelMkD, rotation_deg
    
    new_entry = False
    proceed_Q = False
    
    if Zeroed:
        # if  selected_markD is None:
        if len(GoX_box.get())>0 or len(GoY_box.get())>0: # prioritizes the X and Y entries
            if len(GoX_box.get())==0 or len(GoY_box.get())==0:
                messagebox.showwarning("Warning", "Enter both X, Y entries!")
                return None
            elif len(GoZ_box.get())==0 or len(GoD_box.get())==0:
                result = messagebox.askquestion("Eat that question", "Fill Z and D with zeros?", icon='warning')
                print(result)
                if result == 'yes':
                    new_target[0] = int(GoX_box.get())
                    new_target[1] = int(GoY_box.get())
                    new_target[2] = 0
                    new_target[3] = 0
                else:
                    return None
            else:
                new_target[0] = int(GoX_box.get())
                new_target[1] = int(GoY_box.get())
                new_target[2] = int(GoZ_box.get())
                new_target[3] = int(GoD_box.get())
                
            # rotate relative coordinates according to manipulator perspective
            true_coords = Comply_rotation(new_target)
            
            # transform relative coordinates into absulute coordinates with rotation
            new_markD   = [x + y for x, y in zip(zero_pos, true_coords)]
            
            # evaluate if new absolute coordinates are in manipulator's range
            proceed_Q, corrected_coords = evaluate_new_coordinates(new_markD)
            
            if proceed_Q:
                CoordX_MarkD.append(corrected_coords[0]) # CoordX_MarkD.append(true_coords[0])
                CoordY_MarkD.append(corrected_coords[1])
                CoordZ_MarkD.append(corrected_coords[2])
                CoordD_MarkD.append(corrected_coords[3])
                
                CoordX_RelMkD.append(new_target[0])
                CoordY_RelMkD.append(new_target[1])
                CoordZ_RelMkD.append(new_target[2])
                CoordD_RelMkD.append(new_target[3])
                
                Xstr = str(new_target[0])
                Ystr = str(new_target[1])
                Zstr = str(new_target[2])
                Dstr = str(new_target[3])
                
                GoX_box.delete(0,"end")
                GoY_box.delete(0,"end")
                GoZ_box.delete(0,"end")
                GoD_box.delete(0,"end")
                
                new_entry = True
            else:
                # abort
                return None
            
        else:                    # enter current position as new target
            result = messagebox.askquestion("Eat that question", "Do you want to define target by current position?", icon='warning')
            if result == 'yes':
                print("Defining target by current position")
                Fetch_fun()                   # update current coords.
                CoordX_MarkD.append(curr_pos[0])
                CoordY_MarkD.append(curr_pos[1])
                CoordZ_MarkD.append(curr_pos[2])
                CoordD_MarkD.append(curr_pos[3])
                
                CoordX_RelMkD.append(curr_pos[0])
                CoordY_RelMkD.append(curr_pos[1])
                CoordZ_RelMkD.append(curr_pos[2])
                CoordD_RelMkD.append(curr_pos[3])
                
                Xstr = str(round(curr_pos[0]-zero_pos[0],1))
                Ystr = str(round(curr_pos[1]-zero_pos[1],1))
                Zstr = str(round(curr_pos[2]-zero_pos[2],1))
                Dstr = str(round(curr_pos[3]-zero_pos[3],1))
                
                new_entry = True
                
            else:
                return None
        
        
        if new_entry:
            curr_name = NameMarD_box.get()
            #NEW PRINT
            new_str = "{}={}".format(str(markD_idx+1),
                                          curr_name)
            ListMarD_box.insert(str(markD_idx)+".0",new_str)
            MarkD_names.append(curr_name)
            
            #X COORD
            ListMarDX_box.insert(str(markD_idx)+".0",Xstr)
            #Y COORD
            ListMarDY_box.insert(str(markD_idx)+".0",Ystr)
            #Z COORD
            ListMarDZ_box.insert(str(markD_idx)+".0",Zstr)
            #D COORD
            ListMarDD_box.insert(str(markD_idx)+".0",Dstr)
            markD_idx += 1
            
            # update_fig()
    else:  # if Zeroed:
        messagebox.showwarning("Stop right there", "Zero basis first")
        return None
            
        
    # print(CoordX_MarkD[-1])
    # print( CoordY_MarkD[-1])
    # print(CoordZ_MarkD[-1]+CoordD_MarkD[-1])
    # marplot = np.array([CoordX_MarkD[-1],CoordY_MarkD[-1], CoordZ_MarkD[-1]+CoordD_MarkD[-1]])
    # ax.plot(marplot[0],marplot[1],marplot[2], marker='o', zdir='z', label='Markers', color='m')
    
    # #end
    
def MarkDRemv_fun():
    global markD_idx, CoordX_MarkD, CoordY_MarkD, CoordZ_MarkD, CoordD_MarkD, MarkD_names
    global Zeroed, CoordX_RelMkD, CoordY_RelMkD, CoordZ_RelMkD, CoordD_RelMkD
    Fetch_fun()                   # update current coords.
    markD_idx -= 1
    
    del_indx = ListMarD_box.curselection()
    ListMarD_box.delete(del_indx)
    ListMarDX_box.delete(del_indx)
    ListMarDY_box.delete(del_indx)
    ListMarDZ_box.delete(del_indx)
    ListMarDD_box.delete(del_indx)
    del MarkD_names[del_indx]
    del CoordX_MarkD[del_indx]
    del CoordY_MarkD[del_indx]
    del CoordZ_MarkD[del_indx]
    del CoordD_MarkD[del_indx]
    
    del CoordX_RelMkD[del_indx]
    del CoordY_RelMkD[del_indx]
    del CoordZ_RelMkD[del_indx]
    del CoordD_RelMkD[del_indx]
    
    # end

def Go_fun():
    global CoordX_MarkD, CoordY_MarkD, CoordZ_MarkD, CoordD_MarkD
    global Zeroed, zero_pos
    
    if Zeroed:
        Fetch_fun()                   # update current coords.
        selected_markD = ListMarD_box.curselection()
        # print(type(selected_markD))
        speed_entry    = Speed_box.get()
        if len(speed_entry)==0:
            speed_entry = 2000
        speed_entry = int(speed_entry)
        
        
        # if  selected_markD is None:
        if len(GoX_box.get())>0 or len(GoY_box.get())>0: # prioritizes the X and Y entries
            if len(GoX_box.get())==0 or len(GoY_box.get())==0:
                messagebox.showwarning("Error", "Enter both X, Y entries!")
                return None
            elif len(GoZ_box.get())==0 or len(GoD_box.get())==0:
                result = messagebox.askquestion("Eat that question", "Move Z and D to zero?", icon='warning')
                if result == 'yes':
                    moveX = int(GoX_box.get())
                    moveY = int(GoY_box.get())
                    moveZ = 0
                    moveD = 0
                else:
                    return None
            else:
                moveX = int(GoX_box.get())
                moveY = int(GoY_box.get())
                moveZ = int(GoZ_box.get())
                moveD = int(GoD_box.get())
                
                
            target_pos   = [moveX, moveY, moveZ, moveD]
            
            # rotate relative coordinates according to manipulator perspective
            true_coords = Comply_rotation(target_pos)
            
            # transform relative coordinates into absulute coordinates with rotation
            new_target_pos   = [x + y for x, y in zip(zero_pos, true_coords)]
            
            proceed_Q, corrected_coords = evaluate_new_coordinates(new_target_pos)
            
            if proceed_Q:
                # Go routine
                Go_routine(curr_pos, corrected_coords, speed_entry)
            else:
                # abort
                return None
            
        else:                # Second in importance are the target selections
            if  selected_markD is None:
                messagebox.showwarning("Stop right there","Error: select a target or enter X,Y,Z,D coordinates")
                return None
            else:
                target_pos = [CoordX_MarkD[selected_markD], CoordY_MarkD[selected_markD],
                              0,0]
                # Go routine
                Go_routine(curr_pos, target_pos, speed_entry)
                '''
                original_pos = curr_pos
                target_pos = [CoordX_MarkD[selected_markD], CoordY_MarkD[selected_markD],
                              0,0]
                
                curr_pos1 = curr_pos
                curr_pos1[2] = 0
                curr_pos1[3] = 0
                manipulator.goto_pos(curr_pos1, speed=speed_entry)
                # print("Scaping")
                while(manipulator.is_busy()):
                        print("Scaping")
                
                manipulator.goto_pos(target_pos, speed=speed_entry)
                # print("Moving")
                while(manipulator.is_busy()):
                        print("Moving")
                
                target_pos[2] = original_pos[2]-500
                target_pos[3] = original_pos[3]-500
                manipulator.goto_pos(target_pos, speed=100)
                # print(target_pos)
                while(manipulator.is_busy()):
                        print("descending")
                print(target_pos)
                # log_callback("Target reached") # update log
                '''
            
        GoX_box.delete(0,"end")
        GoY_box.delete(0,"end")
        GoZ_box.delete(0,"end")
        GoD_box.delete(0,"end")
        Fetch_fun()                   # update current coords.
    else:  # if Zeroed:
        messagebox.showwarning("Error", "Zero basis first")
        return None
    
    #end

def Go_routine(curr_pos, target_pos, speed_entry):
    print(f"go target : {target_pos} (abs. units):")
    # messagebox.showwarning("Warning", "Moving to target!")
    original_pos = curr_pos
    curr_pos1    = curr_pos
    curr_pos1[2] = 0
    curr_pos1[3] = 0
    
    manipulator.goto_pos(curr_pos1, speed=speed_entry)
    #while(manipulator.is_busy()):
    #        print("Scaping")
    
    curr_pos2    = target_pos
    curr_pos2[2] = 0
    curr_pos2[3] = 0
    manipulator.goto_pos(curr_pos2,speed=speed_entry)
    #while(manipulator.is_busy()):
    #        print("Moving")
    
    target_pos[2] = 500 #original_pos[2]-500
    target_pos[3] = 500 #original_pos[3]-500
    manipulator.goto_pos(target_pos, speed=250)
    # print(target_pos)
    #while(manipulator.is_busy()):
    #        print("descending")
    #print(target_pos)
    #print("Go routine")
    # messagebox.destroy()
    Fetch_fun()                   # update current coords.
    
def evaluate_new_coordinates(input_coords):
    manipulator_axes = ['x','y','z','d']
    result           = []

    # physical stage limits
    lower_bound = 0
    upper_bound = 20000
    out_of_range_values = []
    comply_range_values = []
    for index, value in enumerate(input_coords):
        if lower_bound <= value <= upper_bound:
            proceed_Q = True
            comply_range_values.append(value)
        else:
            out_of_range_values.append((manipulator_axes[index], value))
            corrected_value = max(lower_bound, min(value, upper_bound))
            comply_range_values.append(corrected_value)

    result_string = "\n".join(f"{item[0]}: {item[1]}" for item in out_of_range_values)
    result_string = f"Following targets are out of micromanipulator's range.\n{result_string}\nContinue?\n\
        If 'Yes' target will truncate at stages' limits"
    
    if len(out_of_range_values)>0:
        result = messagebox.askquestion("Eat that question", result_string,
        type=messagebox.YESNO, default=messagebox.NO)
    
    if result == 'yes':
        proceed_Q = True        
    elif result == 'no':
        proceed_Q = False
        
    return proceed_Q, comply_range_values
    
def LeftLevel_fun():
    global curr_pos, left_set, right_set, left_level, right_level
    curr_pos   = manipulator.get_pos()
    left_level = curr_pos[2]+curr_pos[3]
    left_set   = 1
    if right_set:
        new_str = "L:" + str(round(left_level,2))
        LeftRoll_label.delete(0,"end")
        LeftRoll_label.insert(0,new_str)
        new_str = " R:" + str(round(right_level,2))
        RightRoll_label.delete(0,"end")
        RightRoll_label.insert(0,new_str)
        
        offset = left_level-right_level
        if offset>0:
            new_str = "Left is below by " + str(abs(round(offset,2)))
        else:
            new_str = "Left is above by " + str(abs(round(offset,2)))
        RollOff_label.delete(0,"end")
        RollOff_label.insert(0,new_str)
    else:
        new_str = "L:" + str(round(left_level,2))
        LeftRoll_label.delete(0,"end")
        LeftRoll_label.insert(0,new_str)
    
    

def RightLevel_fun():
    global curr_pos, left_set, right_set, left_level, right_level
    curr_pos   = manipulator.get_pos()
    right_level = curr_pos[2]+curr_pos[3]
    right_set   = 1
    if left_set:
        new_str = "L:" + str(round(left_level,1))
        LeftRoll_label.delete(0,"end")
        LeftRoll_label.insert(0,new_str)
        new_str = " R:" + str(round(right_level,1))
        RightRoll_label.delete(0,"end")
        RightRoll_label.insert(0,new_str)
        
        offset = left_level-right_level
        if offset>0:
            new_str = "Left is below by " + str(abs(round(offset,1)))
        else:
            new_str = "Left is above by " + str(abs(round(offset,1)))
        RollOff_label.delete(0,"end")
        RollOff_label.insert(0,new_str)
    else:
        new_str = " R:" + str(round(right_level,1))
        RightRoll_label.delete(0,"end")
        RightRoll_label.insert(0,new_str)

def AntLevel_fun():
    global curr_pos, ant_set, pos_set, ant_level, pos_level
    curr_pos   = manipulator.get_pos()
    ant_level = curr_pos[2]+curr_pos[3]
    ant_set   = 1
    if pos_set:
        new_str = "A:" + str(round(ant_level,1))
        AntPitch_label.delete(0,"end")
        AntPitch_label.insert(0,new_str)
        new_str = " P:" + str(round(pos_level,1))
        PosPitch_label.delete(0,"end")
        PosPitch_label.insert(0,new_str)
        
        offset = ant_level-pos_level
        if offset>0:
            new_str = "Ant. is below by " + str(abs(round(offset,1)))
        else:
            new_str = "Ant. is above by " + str(abs(round(offset,1)))
        PitchOff_label.delete(0,"end")
        PitchOff_label.insert(0,new_str)
    else:
        new_str = "A:" + str(round(ant_level,1))
        AntPitch_label.delete(0,"end")
        AntPitch_label.insert(0,new_str)

def PosLevel_fun():
    global curr_pos, ant_set, pos_set, ant_level, pos_level
    curr_pos   = manipulator.get_pos()
    pos_level = curr_pos[2]+curr_pos[3]
    pos_set   = 1
    if ant_set:
        new_str = "A:" + str(round(ant_level,1))
        AntPitch_label.delete(0,"end")
        AntPitch_label.insert(0,new_str)
        new_str = " P:" + str(round(pos_level,1))
        PosPitch_label.delete(0,"end")
        PosPitch_label.insert(0,new_str)
        
        offset = ant_level-pos_level
        if offset>0:
            new_str = "Ant. is below by " + str(abs(round(offset,1)))
        else:
            new_str = "Ant. is above by " + str(abs(round(offset,1)))
        PitchOff_label.delete(0,"end")
        PitchOff_label.insert(0,new_str)
    else:
        new_str = "A:    " + " P:" + str(round(pos_level,1))
        PosPitch_label.delete(0,"end")
        PosPitch_label.insert(0,new_str)
        
def ZeroDV_fun():
    global curr_pos, DVzero_pos, DVzeroed
    
    Fetch_fun()
    print(curr_pos)
    DVzero_pos[0]    = curr_pos[2]
    DVzero_pos[1]    = curr_pos[3]
    DVzeroed         = 1
    DV_level         = DVzero_pos[0] + DVzero_pos[1]
    # DV_level[0]   = curr_pos[2] # copy Z
    # DV_level[1]   = curr_pos[3] # copy D
    
    #    reset DV tracker
    new_str    = str(abs(round(DV_level,1)))
    RawImplant_label.delete(0,"end")
    RawImplant_label.insert(0,new_str)
    
    new_str    = "0.0"
    ZroImplant_label.delete(0,"end")
    ZroImplant_label.insert(0,new_str)
    

def DVlevel_disp():
    global curr_pos, DVzero_pos, DVzeroed
    Fetch_fun()
    
    
    DV_level = curr_pos[2] + curr_pos[3]
    new_str    = str(abs(round(DV_level,1)))
    RawImplant_label.delete(0,"end")
    RawImplant_label.insert(0,new_str)
    
    
    DV_level = curr_pos[2]-DVzero_pos[0] + curr_pos[3]-DVzero_pos[1]
    new_str    = str(round(DV_level,1))
    ZroImplant_label.delete(0,"end")
    ZroImplant_label.insert(0,new_str)
    
def FetchDV_fun():
    print("FetchDV_fun")
    if DVzeroed:
        DVlevel_disp()
    else:
        ZeroDV_fun()    

def Implant_fun():
    print("Implant_fun")
    global curr_pos, DVzero_pos, DVzeroed
    Fetch_fun()  
    
    speed_entry    = SpeedImplant_box.get()
    if len(speed_entry)==0:
        speed_entry = 50 
    speed_entry = int(speed_entry)
    
    
    ZMove = ZImplant_checkbox.get()
    DMove = DImplant_checkbox.get()
    
    Zdiff = int(ZImplant_box.get())
    Ddiff = int(DImplant_box.get())
    
    if ZMove == 'on':
        target_pos    = curr_pos
        target_pos[2] = curr_pos[2] + Zdiff
        manipulator.goto_pos(target_pos,speed=speed_entry)
        DVlevel_disp()
        DV_level = curr_pos[2]-DVzero_pos[0] + Zdiff
        new_str    = str(round(DV_level,1))
        ZTrack_label.delete(0,"end")
        ZTrack_label.insert(0,new_str)
    
    if DMove == 'on':
        target_pos    = curr_pos
        target_pos[3] = curr_pos[3] + Ddiff
        manipulator.goto_pos(target_pos,speed=speed_entry)
        DVlevel_disp()
        DV_level = curr_pos[3]-DVzero_pos[1] + Ddiff
        new_str    = str(round(DV_level,1))
        DTrack_label.delete(0,"end")
        DTrack_label.insert(0,new_str)
    
    
    while(manipulator.is_busy()):
            # print("Implanting")
            DVlevel_disp()
            
def Explant_fun():
    print("Explant_fun")
    global curr_pos, DVzero_pos, DVzeroed
    Fetch_fun()  
    
    speed_entry    = SpeedImplant_box.get()
    if len(speed_entry)==0:
        speed_entry = 50 
    speed_entry = int(speed_entry)
    
    
    ZMove = ZImplant_checkbox.get()
    DMove = DImplant_checkbox.get()
    
    Zdiff = int(ZImplant_box.get())
    Ddiff = int(DImplant_box.get())
    
    if ZMove == 'on':
        target_pos    = curr_pos
        target_pos[2] = curr_pos[2] - Zdiff
        manipulator.goto_pos(target_pos, speed=speed_entry)
        DVlevel_disp()
        DV_level = curr_pos[2]-DVzero_pos[0] - Zdiff 
        new_str    = str(round(DV_level,1))
        ZTrack_label.delete(0,"end")
        ZTrack_label.insert(0,new_str)
    
    if DMove == 'on':
        target_pos    = curr_pos
        target_pos[3] = curr_pos[3] - Ddiff
        manipulator.goto_pos(target_pos, speed=speed_entry)
        DVlevel_disp()
        DV_level = curr_pos[3]-DVzero_pos[1] - Ddiff
        new_str    = str(round(DV_level,1))
        DTrack_label.delete(0,"end")
        DTrack_label.insert(0,new_str)
    
    while(manipulator.is_busy()):
            # print("Implanting")
            DVlevel_disp()
    
def Zcheck_fun():
    print('Zcheck_fun')
    
    DMove = DImplant_checkbox.get()
    if DMove == 'on':
        DImplant_checkbox.toggle()
        
def Dcheck_fun():
    print('Dcheck_fun')
    
    ZMove = ZImplant_checkbox.get()
    if ZMove == 'on':
        ZImplant_checkbox.toggle()
    
def GoR_fun():
    print("GoR_fun")
    global curr_pos
    Fetch_fun()

    Movediff = int(GoLR_box.get())
    
    target_pos    = curr_pos
    target_pos[1] = curr_pos[1] - Movediff
    manipulator.goto_pos(target_pos, speed=2000)
    
def GoL_fun():
    print("GoL_fun")
    global curr_pos
    Fetch_fun()

    Movediff = int(GoLR_box.get())
    
    target_pos    = curr_pos
    target_pos[1] = curr_pos[1] + Movediff
    manipulator.goto_pos(target_pos, speed=2000)

def GoA_fun():
    print("GoA_fun")
    global curr_pos
    Fetch_fun()

    Movediff = int(GoAP_box.get())
    
    target_pos    = curr_pos
    target_pos[0] = curr_pos[0] - Movediff
    manipulator.goto_pos(target_pos, speed=2000)
    
def GoP_fun():
    print("GoP_fun")
    global curr_pos
    Fetch_fun()

    Movediff = int(GoAP_box.get())
    
    target_pos    = curr_pos
    target_pos[0] = curr_pos[0] + Movediff
    manipulator.goto_pos(target_pos, speed=2000)
    
def update_fig():
    global fig, ax, markD_idx
    # global CoordX_MarkD, CoordY_MarkD, CoordZ_MarkD, CoordD_MarkD
    # global Zeroed, zero_pos #CoordX_ZroMkD, CoordY_ZroMkD, CoordZ_ZroMkD, CoordD_ZroMkD
    global x1,x2,y1,y2,z1,z2,z3,rotation_deg
    print('Update FIG')
    ax.clear()
    
    # Plot anatomy axes
    x1 = np.array([0,100])
    x2 = np.array([0,0])
    y1 = np.array([0,0])
    y2 = np.array([0,100])
    z1 = np.array([0,0,0])
    z2 = np.array([0,0,0])
    z3 = np.array([0,0,100])
    
    
    angle_radians = np.radians(rotation_deg)
    rot_matrix = np.array([[np.cos(angle_radians), -np.sin(angle_radians)],
                           [np.sin(angle_radians),  np.cos(angle_radians)]])
    
    new_x = np.vstack((x1,x2))
    new_y = np.vstack((y1,y2))
    
    rotated_x  = np.dot(rot_matrix, new_x)
    rotated_y  = np.dot(rot_matrix, new_y)
   
    ax.plot(rotated_x[0,:], rotated_x[1,:], zs=0, marker='v', zdir='z', label='Markers', color='b')
    ax.plot(rotated_y[0,:], rotated_y[1,:], zs=0, marker='v', zdir='z', label='Markers', color='r')
    ax.plot(z1, z2, z3,   marker='v', zdir='z', label='Markers', color='g')
    
    ax.text(rotated_x[0,0], rotated_x[1,0], 0, 'AP', color='white',
            bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
    ax.text(rotated_y[0,0], rotated_y[1,0], 0, 'ML', color='white',
            bbox={'facecolor': 'blue', 'alpha': 0.5, 'pad': 10})
    ax.text(0, 0, 110, 'DV', color='white',
            bbox={'facecolor': 'green', 'alpha': 0.5, 'pad': 10})
    
    # plot manipulator axis
    Mx1 = np.array([-200, 50])
    Mx2 = np.array([100,100])
    My1 = np.array([0,   0])
    My2 = np.array([150, 50])
    Mz1 = np.array([  0,   0,  0])
    Mz2 = np.array([100, 100, 100])
    Mz3 = np.array([1000,1000,500])

    ax.plot(Mx1, Mx2, zs=500, marker='v', zdir='z', label='Markers', color='w')
    ax.plot(My1, My2, zs=500, marker='v', zdir='z', label='Markers', color='w')
    ax.plot(Mz1, Mz2, Mz3,   marker='v', zdir='z', label='Markers', color='w')


    ax.text(60, 100, 500, 'X', color='white')
    ax.text( 0,  40, 500, 'Y', color='white')
    ax.text( 0, 100, 1020, 'Z/D', color='white')
    
    
    # ax.set_xlim(-700, 700)
    # ax.set_ylim(-100, 2000)
    # ax.set_zlim(-100, 1200)
    ax.view_init(elev=20., azim=-35, roll=0)

    ax.axis("off")
    
    
    
    
    
    
    
    
    
    
    
    
    
    '''
    print(markD_idx)
    # re-size origin rows
    if markD_idx>1:
        Xrange = np.array([min(CoordX_MarkD), max(CoordX_MarkD)])
        Yrange = np.array([min(CoordY_MarkD), max(CoordY_MarkD)])
        Zrange = np.array([min(CoordZ_MarkD), max(CoordZ_MarkD)])
        Drange = np.array([min(CoordD_MarkD), max(CoordD_MarkD)])
    elif markD_idx==1:
        Xrange = np.array([0, CoordX_MarkD[0]])
        Yrange = np.array([0, CoordY_MarkD[0]])
        Zrange = np.array([0, CoordZ_MarkD[0]])
        Drange = np.array([0, CoordD_MarkD[0]])
    
    x1 = np.array([0,(max(Xrange)-min(Xrange))/2])
    x2 = np.array([0,0])
    y1 = np.array([0,0])
    y2 = np.array([0,(max(Yrange)-min(Yrange))/2])
    z1 = np.array([0,0,0])
    z2 = np.array([0,0,0])
    z3 = np.array([0,0,(max(Zrange)+max(Drange))-(min(Zrange)+min(Drange))/2])
    
    ax.plot(x1, x2, zs=0, marker='v', zdir='z', label='Markers', color='m')
    ax.plot(y1, y2, zs=0, marker='v', zdir='z', label='Markers', color='y')
    ax.plot(z1, z2, z3,   marker='v', zdir='z', label='Markers', color='c')
    
    for ii in range(markD_idx):
        marker = np.array([CoordX_MarkD[ii], CoordY_MarkD[ii], CoordZ_MarkD[ii]+CoordD_MarkD[ii]])
        ax.plot(marker[0],marker[1],marker[2],'d')
    if (Xrange[1]-Xrange[0])!=0:
        ax.set_xlim(np.array(Xrange))
    if (Yrange[1]-Yrange[0])!=0:
        ax.set_ylim(np.array(Yrange))
    if ((Zrange[1]+Drange[1])-(Zrange[0]+Drange[0]))!=0:   
        ax.set_zlim(np.array([Zrange[0]+Drange[0],
                         Zrange[1]+Drange[1]]))
    
    # ax.plot(markers[0],markers[1],markers[2],'d')
    # markers = np.array([1000.0,2990.8,04068.0])
    # ax.plot(markers[0],markers[1],markers[2],'d')
    '''

def rotate_space():
    global fig, ax, markD_idx, Space_orientation
    global CoordX_MarkD, CoordY_MarkD, CoordZ_MarkD, CoordD_MarkD
    global Zeroed, zero_pos, rotation_deg
    
    print("rotate_space fun")
    
    
    # '#0050a0'  x
    # '#a01800'  y
    
    
        
    
    Space_orientation+=1
    if Space_orientation>3:
        Space_orientation = 0
    
    print(Space_orientation)
    if Space_orientation==0 or Space_orientation==2:
        XWheel.configure(fg_color = '#0050a0', text = 'ML')
        YWheel.configure(fg_color = '#a01800', text = 'AP')
        
        
    elif Space_orientation==1 or Space_orientation==3:
        XWheel.configure(fg_color = '#a01800', text = 'AP')
        YWheel.configure(fg_color = '#0050a0', text = 'ML')
    
    # rotate basis 90 degrees
    rotation_deg += 90
    if rotation_deg>=360:
        rotation_deg = 0
    
    # update anatomy axis in figure
    update_fig()
    
        
    """
    Re-write relative and absolute target coordinates to comply with current rotation
    """
    # eliminate old absolute target coordinates
    while len(CoordX_MarkD)>0:
        del CoordX_MarkD[0]
        del CoordY_MarkD[0]
        del CoordZ_MarkD[0]
        del CoordD_MarkD[0]
        
    for x in range(markD_idx):
        # rotate relative coordinates according to manipulator perspective
        old_basis_coord = [CoordX_RelMkD[x], CoordY_RelMkD[x], CoordZ_RelMkD[x], CoordD_RelMkD[x]]
        new_basis_coord = Comply_rotation(old_basis_coord)
        
        CoordX_RelMkD[x] = new_basis_coord[0]
        CoordY_RelMkD[x] = new_basis_coord[1]
        CoordZ_RelMkD[x] = new_basis_coord[2]
        CoordD_RelMkD[x] = new_basis_coord[3]
        
        # transform relative coordinates into new absolute coordinates based on new basis
        new_markD   = [z + y for z, y in zip(zero_pos, new_basis_coord)]
        CoordX_MarkD.append(new_markD[0])
        CoordY_MarkD.append(new_markD[1])
        CoordZ_MarkD.append(new_markD[2])
        CoordD_MarkD.append(new_markD[3])
        
    print(f"Current XY basis rotation = {rotation_deg}")
    # end
    
    
            
###################################
###################################
###################################

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# MENU TABS
tabview = cmtk.CTkTabview(master=root,
                          width    = 500, height = 280,
                          fg_color = '#29334a',
                          segmented_button_selected_color       =  '#00a091',
                          segmented_button_selected_hover_color = '#007a6f')
tabview.place(x = 5, y = 5)

tabview.add("Navigation")
tabview.add("Leveling")
tabview.add("Implantation")
tabview.add("Routing")
tabview.set("Navigation")  # set currently visible tab

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ~~~~~~~~ ROOT ELEMENTS
Quit_btn = cmtk.CTkButton(master  = root,
                          text    ='Quit',
                          command = root.destroy,
                          width   = 8,
                          font    = ("Verdana",12,"bold"),
                          fg_color      = '#00a091',
                          hover_color   = '#007a6f',
                          corner_radius = 5)
Quit_btn.place(x = 5, y = 300)

#          Wheel control

XWheel = cmtk.CTkButton(master  = root,
                              text    ='ML',
                              width   = 1,
                              font    = ("Verdana",12,"bold"),
                              fg_color      = '#0050a0',
                              corner_radius = 50)
XWheel.place(x = 530, y = 220)

YWheel = cmtk.CTkButton(master  = root,
                              text    ='AP',
                              width   = 1,
                              font    = ("Verdana",12,"bold"),
                              fg_color      = '#a01800',
                              corner_radius = 50)
YWheel.place(x = 570, y = 190)

ZWheel = cmtk.CTkButton(master  = root,
                              text    ='DV(Z)',
                              width   = 1,
                              font    = ("Verdana",12,"bold"),
                              fg_color      = '#48a000',
                              corner_radius = 50)
ZWheel.place(x = 610, y = 220)

DWheel = cmtk.CTkButton(master  = root,
                              text    ='DV(D)',
                              width   = 1,
                              font    = ("Verdana",12,"bold"),
                              fg_color      = '#48a000',
                              corner_radius = 50)
DWheel.place(x = 570, y = 260)

rotateSpace_left = cmtk.CTkButton(master  = root,
                              text    ='Rot. 90 deg.', # 90°
                              command = rotate_space,
                              width   = 5,
                              font    = ("Verdana",12,"bold"),
                              fg_color     = '#00a091',
                              hover_color   = '#007a6f',
                              corner_radius = 5)
rotateSpace_left.place(x = 615, y = 270)

###################################
# FIGURE
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('k')
fig.set_size_inches(4,4)
# Plot anatomy axes
x1 = np.array([0,100])
x2 = np.array([0,0])
y1 = np.array([0,0])
y2 = np.array([0,100])
z1 = np.array([0,0,0])
z2 = np.array([0,0,0])
z3 = np.array([0,0,100])
ax.plot(x1, x2, zs=0, marker='v', zdir='z', label='Markers', color='b')
ax.plot(y1, y2, zs=0, marker='v', zdir='z', label='Markers', color='r')
ax.plot(z1, z2, z3,   marker='v', zdir='z', label='Markers', color='g')


ax.text(0, 110, 0, 'AP', color='white',
        bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
ax.text(110, 0, 0, 'ML', color='white',
        bbox={'facecolor': 'blue', 'alpha': 0.5, 'pad': 10})
ax.text(0, 0, 110, 'DV', color='white',
        bbox={'facecolor': 'green', 'alpha': 0.5, 'pad': 10})

# plot micromanipulator axes
Mx1 = np.array([-200, 50])
Mx2 = np.array([100,100])
My1 = np.array([0,   0])
My2 = np.array([150, 50])
Mz1 = np.array([  0,   0,  0])
Mz2 = np.array([100, 100, 100])
Mz3 = np.array([1000,1000,500])

ax.plot(Mx1, Mx2, zs=500, marker='v', zdir='z', label='Markers', color='w')
ax.plot(My1, My2, zs=500, marker='v', zdir='z', label='Markers', color='w')
ax.plot(Mz1, Mz2, Mz3,   marker='v', zdir='z', label='Markers', color='w')


ax.text(60, 100, 500, 'X', color='white')
ax.text( 0,  40, 500, 'Y', color='white')
ax.text( 0, 100, 1020, 'Z/D', color='white')

# # plot rotation direction
# x_rot_values = np.array([100,200])
# y_rot_values = np.sin(x_rot_values) + 100 * x_rot_values
# ax.plot(x_rot_values, y_rot_values, zs=0, marker='v', zdir='z', label='Markers', color='w')


# ax.set_xlim(-700, 700)
# ax.set_ylim(-100, 2000)
# ax.set_zlim(-100, 1200)

# Customize the view angle so it's easier to see that the scatter points lie
# on the plane y=0
ax.view_init(elev=20., azim=-35, roll=0)

ax.axis("off")
fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)

# plt.show()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().place(x = 950, y = 0, relx=0.15, rely=0.15) 






# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ~~~~~~~~ NAVIGATION TAB
#          Connect
Connect_btn = cmtk.CTkButton(master  = tabview.tab("Navigation"),
                              text    ='Reset',
                              command = connect_fun,
                              width   = 12,
                              font    = ("Verdana",12,"bold"),
                              fg_color      = '#00a091',
                              hover_color   = '#007a6f',
                              corner_radius = 5)
Connect_btn.place(x = 0, y = 0)
#          Calibrate
Calib_btn = cmtk.CTkButton(master  = tabview.tab("Navigation"),
                            text    ='Calibrate',
                            command = calib_fun,
                            width   = 12,
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
Calib_btn.place(x = 60, y = 0)
#          Center
Center_btn = cmtk.CTkButton(master  = tabview.tab("Navigation"),
                            text    ='Center',
                            command = center_fun,
                            width   = 12,
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
Center_btn.place(x = 140, y = 0)
#          Zero
Zero_btn = cmtk.CTkButton(master  = tabview.tab("Navigation"),
                            text    ='Zero',
                            command = Zero_fun,
                            width   = 12,
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
Zero_btn.place(x = 205, y = 0)


#          Scape
Scape1_bnt = cmtk.CTkButton(master  = tabview.tab("Navigation"),
                            text    ='Scape',
                            command = Scape_fun,
                            width   = 12,
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#eb9602',
                            hover_color   = '#c47e04',
                            corner_radius = 5)
Scape1_bnt.place(x = 357, y = 0)
#          Stop
Stop1_bnt = cmtk.CTkButton(master  = tabview.tab("Navigation"),
                            text    ='STOP',
                            command = Stop_fun,
                            width   = 12,
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#eb0202',
                            hover_color   = '#a30303',
                            corner_radius = 5)
Stop1_bnt.place(x = 412, y = 0)
#          Fetch
Fetch_bnt = cmtk.CTkButton(master  = tabview.tab("Navigation"),
                            text    ='Fetch',
                            command = Fetch_fun,
                            width   = 12,
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
Fetch_bnt.place(x = 80, y = 35)
# X field
Xfield_box = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = "X= " + str(round(curr_pos[0],1)),
                           width   = 80,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
Xfield_box.place(x = 140, y = 35)
# Y field
Yfield_box = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = "Y= " + str(round(curr_pos[1],1)),
                           width   = 80,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
Yfield_box.place(x = 220, y = 35)
# Z field
Zfield_box = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = "Z= " + str(round(curr_pos[2],1)),
                           width   = 80,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
Zfield_box.place(x = 300, y = 35)
# D field
Dfield_box = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = "D= " + str(round(curr_pos[3],1)),
                           width   = 80,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
Dfield_box.place(x = 380, y = 35)

# Markdown label and name entry
NameMarD_label1 = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = "Target",
                           width   = 52,height = 5,
                           font    = ("Verdana",8,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
NameMarD_label1.place(x = 0, y = 37)
NameMarD_label2 = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = "name",
                           width   = 50,height = 5,
                           font    = ("Verdana",8,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
NameMarD_label2.place(x = 0, y = 50)                                  
NameMarD_box = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = " ",
                           width   = 50, height = 8,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
NameMarD_box.place(x = 0, y = 70)

# Add and remove markdowns
MarkD_btn = cmtk.CTkButton(master  = tabview.tab("Navigation"),
                            text    ='+',
                            command = MarkD_fun,
                            width   = 10, height = 8,
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
MarkD_btn.place(x = 10, y = 95)
MarkDRmv_btn = cmtk.CTkButton(master  = tabview.tab("Navigation"),
                            text    ='-',
                            command = MarkDRemv_fun,
                            width   = 18, height = 8,
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
MarkDRmv_btn.place(x = 10, y = 120)

## Markdown name,X,Y,Z,D coord. lists
ListMarD_box = CTkListbox(master  = tabview.tab("Navigation"),
                          command = Selection_MarkD_fun,
                              width   = 80,
                              font    = ("Verdana",8,"bold"),
                              fg_color      = '#87c9a8',
                              text_color    = '#026afa',
                              scrollbar_button_color = '#ffffff',
                              corner_radius = 3)
ListMarD_box.insert("0.0", MarkDList[0])
ListMarD_box.place(x = 60, y = 70, relwidth=0.2,  relheight=0.5)

ListMarDX_box = CTkListbox(master  = tabview.tab("Navigation"),
                              width   = 80,
                              font    = ("Verdana",8,"bold"),
                              fg_color      = '#87c9a8',
                              text_color    = '#026afa',
                              scrollbar_button_color = '#ffffff',
                              hover_color            = '#87c9a8',
                              corner_radius = 3)
ListMarDX_box.insert("0.0", MarkDList_X[0])
ListMarDX_box.place(x = 140, y = 70, relwidth=0.2,  relheight=0.5)

ListMarDY_box = CTkListbox(master  = tabview.tab("Navigation"),
                              width   = 80,
                              font    = ("Verdana",8,"bold"),
                              fg_color      = '#87c9a8',
                              text_color    = '#026afa',
                              scrollbar_button_color = '#ffffff',
                              hover_color            = '#87c9a8',
                              corner_radius = 3)
ListMarDY_box.insert("0.0", MarkDList_Y[0])
ListMarDY_box.place(x = 220, y = 70, relwidth=0.2,  relheight=0.5)

ListMarDZ_box = CTkListbox(master  = tabview.tab("Navigation"),
                              width   = 80,
                              font    = ("Verdana",8,"bold"),
                              fg_color      = '#87c9a8',
                              text_color    = '#026afa',
                              scrollbar_button_color = '#ffffff',
                              hover_color            = '#87c9a8',
                              corner_radius = 3)
ListMarDZ_box.insert("0.0", MarkDList_Z[0])
ListMarDZ_box.place(x = 300, y = 70, relwidth=0.2,  relheight=0.5)

ListMarDD_box = CTkListbox(master  = tabview.tab("Navigation"),
                              width   = 70,
                              font    = ("Verdana",8,"bold"),
                              fg_color      = '#87c9a8',
                              text_color    = '#026afa',
                              scrollbar_button_color = '#ffffff',
                              hover_color            = '#87c9a8',
                              corner_radius = 3)
ListMarDD_box.insert("0.0", MarkDList_D[0])
ListMarDD_box.place(x = 380, y = 70, relwidth=0.17,  relheight=0.5)

#          Go
Go_bnt = cmtk.CTkButton(master  = tabview.tab("Navigation"),
                            text    ='Go',
                            command = Go_fun,
                            width   = 50, 
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
Go_bnt.place(x = 80, y = 185)

# GO X,YZ and D
GoX_box = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = " ",
                           width   = 80,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
GoX_box.place(x = 140, y = 185)

GoY_box = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = " ",
                           width   = 80,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
GoY_box.place(x = 220, y = 185)

GoZ_box = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = " ",
                           width   = 80,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
GoZ_box.place(x = 300, y = 185)

GoD_box = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = " ",
                           width   = 80,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
GoD_box.place(x = 380, y = 185)

# Speed label and entry
NameMarD_label1 = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = "Speed",
                           width   = 52,height = 5,
                           font    = ("Verdana",8,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
NameMarD_label1.place(x = 0, y = 157)
NameMarD_label1 = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = "(um/s)",
                           width   = 52,height = 5,
                           font    = ("Verdana",8,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
NameMarD_label1.place(x = 0, y = 170)

Speed_box = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
                           placeholder_text = "2000",
                           width   = 50,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
Speed_box.place(x = 0, y = 185)

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ~~~~~~~~ LEVELING TAB
#          Left level button
LeftLevel_btn = cmtk.CTkButton(master  = tabview.tab("Leveling"),
                            text    ='Left',
                            command = LeftLevel_fun,
                            width   = 70, 
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
LeftLevel_btn.place(x = 50, y = 35)

#          Right level button
RightLevel_btn = cmtk.CTkButton(master  = tabview.tab("Leveling"),
                            text    ='Right',
                            command = RightLevel_fun,
                            width   = 70, 
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
RightLevel_btn.place(x = 140, y = 35)

#          Anterior level button
AntLevel_btn = cmtk.CTkButton(master  = tabview.tab("Leveling"),
                            text    ='Anterior',
                            command = AntLevel_fun,
                            width   = 50, 
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
AntLevel_btn.place(x = 50, y = 120)



#          Posterior level button
PosLevel_btn = cmtk.CTkButton(master  = tabview.tab("Leveling"),
                            text    ='Posterior',
                            command = PosLevel_fun,
                            width   = 50, 
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
PosLevel_btn.place(x = 140, y = 120)

#          Left/Right/Roll label
LeftRoll_label = cmtk.CTkEntry(master  = tabview.tab("Leveling"),
                           placeholder_text = "L:    ",
                           width   = 60,height = 5,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
LeftRoll_label.place(x = 50, y = 70)

RightRoll_label = cmtk.CTkEntry(master  = tabview.tab("Leveling"),
                           placeholder_text = "R:    ",
                           width   = 60,height = 5,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
RightRoll_label.place(x = 140, y = 70)

RollOff_label = cmtk.CTkEntry(master  = tabview.tab("Leveling"),
                           placeholder_text = "Roll Offset:      ",
                           width   = 200,height = 5,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
RollOff_label.place(x = 50, y = 100)

#          Anterior/Posterior/Pitch label
AntPitch_label = cmtk.CTkEntry(master  = tabview.tab("Leveling"),
                           placeholder_text = "A:    ",
                           width   = 60,height = 5,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
AntPitch_label.place(x = 50, y = 155)

PosPitch_label = cmtk.CTkEntry(master  = tabview.tab("Leveling"),
                           placeholder_text = "P:    ",
                           width   = 60,height = 5,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
PosPitch_label.place(x = 140, y = 155)

PitchOff_label = cmtk.CTkEntry(master  = tabview.tab("Leveling"),
                           placeholder_text = "Pitch Offset:      ",
                           width   = 200,height = 5,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
PitchOff_label.place(x = 50, y = 185)

#           Go Left/Right Entry
GoLR_box = cmtk.CTkEntry(master  = tabview.tab("Leveling"),
                           placeholder_text = " ",
                           width   = 80,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
GoLR_box.place(x = 280, y = 55)

#           Go Anterior/Posterior Entry
GoAP_box = cmtk.CTkEntry(master  = tabview.tab("Leveling"),
                           placeholder_text = " ",
                           width   = 80,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
GoAP_box.place(x = 280, y = 135)

GOLR_label = cmtk.CTkEntry(master  = tabview.tab("Leveling"),
                           placeholder_text = "Go",
                           width   = 22,height = 5,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
GOLR_label.place(x = 250, y = 60)
GOAP_label = cmtk.CTkEntry(master  = tabview.tab("Leveling"),
                           placeholder_text = "Go",
                           width   = 22,height = 5,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
GOAP_label.place(x = 250, y = 140)

#           Go Left/Right buttons
GoR_bnt = cmtk.CTkButton(master  = tabview.tab("Leveling"),
                            text    ='to the right',
                            command = GoR_fun,
                            width   = 10,
                            font    = ("Verdana",10,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
GoR_bnt.place(x = 370, y = 40)
GoL_bnt = cmtk.CTkButton(master  = tabview.tab("Leveling"),
                            text    ='to the left',
                            command = GoL_fun,
                            width   = 12,
                            font    = ("Verdana",10,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
GoL_bnt.place(x = 370, y = 70)

#           Go Anterior/Posterior buttons
GoA_bnt = cmtk.CTkButton(master  = tabview.tab("Leveling"),
                            text    ='anterior',
                            command = GoA_fun,
                            width   = 10,
                            font    = ("Verdana",10,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
GoA_bnt.place(x = 370, y = 115)
GoP_bnt = cmtk.CTkButton(master  = tabview.tab("Leveling"),
                            text    ='posterior',
                            command = GoP_fun,
                            width   = 12,
                            font    = ("Verdana",10,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
GoP_bnt.place(x = 370, y = 145)


Stop2_bnt = cmtk.CTkButton(master  = tabview.tab("Leveling"),
                            text    ='STOP',
                            command = Stop_fun,
                            width   = 12,
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#eb0202',
                            hover_color   = '#a30303',
                            corner_radius = 5)
Stop2_bnt.place(x = 412, y = 0)

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# ~~~~~~~~ IMPLANTATION TAB
#            Raw and Zeored labels
Implantation_label1 = cmtk.CTkEntry(master  = tabview.tab("Implantation"),
                            placeholder_text = "Raw",
                            width   = 52,height = 5,
                            font    = ("Verdana",8,"bold"),
                            fg_color      = '#29334a',
                            border_color  = '#29334a',
                            placeholder_text_color =  '#ffffff')
Implantation_label1.place(x = 140, y = 0)
Implantation_label1 = cmtk.CTkEntry(master  = tabview.tab("Implantation"),
                            placeholder_text = "Zeroed",
                            width   = 52,height = 5,
                            font    = ("Verdana",8,"bold"),
                            fg_color      = '#29334a',
                            border_color  = '#29334a',
                            placeholder_text_color =  '#ffffff')
Implantation_label1.place(x = 200, y = 0)
#          Fetch
FetchImplant_bnt = cmtk.CTkButton(master  = tabview.tab("Implantation"),
                            text    ='Fetch',
                            command = FetchDV_fun,
                            width   = 50, 
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
FetchImplant_bnt.place(x = 5, y = 10)

#          Zero implant entry and button
ZroImplant_bnt = cmtk.CTkButton(master  = tabview.tab("Implantation"),
                            text    ='Zero DV',
                            command = ZeroDV_fun,
                            width   = 50,
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#00a091',
                            hover_color   = '#007a6f',
                            corner_radius = 5)
ZroImplant_bnt.place(x = 60, y = 10)

RawImplant_label = cmtk.CTkEntry(master  = tabview.tab("Implantation"),
                           placeholder_text = "  0",
                           width   = 200, height = 3,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
RawImplant_label.place(x = 140, y = 15)
ZroImplant_label = cmtk.CTkEntry(master  = tabview.tab("Implantation"),
                           placeholder_text = "  0",
                           width   = 200,height = 3,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
ZroImplant_label.place(x = 200, y = 15)

#          Implant/Explant buttons
Implant_bnt = cmtk.CTkButton(master  = tabview.tab("Implantation"),
                            text    ='Implant',
                            command = Implant_fun,
                            width   = 50, 
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#eb9602',
                            hover_color   = '#c47e04',
                            corner_radius = 5)
Implant_bnt.place(x = 60, y = 60)
Explant_bnt = cmtk.CTkButton(master  = tabview.tab("Implantation"),
                            text    ='Explant',
                            command = Explant_fun,
                            width   = 50, 
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#eb9602',
                            hover_color   = '#c47e04',
                            corner_radius = 5)
Explant_bnt.place(x = 300, y = 60)

#          Z/D entries

# ZImplant_label = cmtk.CTkEntry(master  = tabview.tab("Implantation"),
#                            placeholder_text = "Z",
#                            width   = 52,height = 5,
#                            font    = ("Verdana",8,"bold"),
#                            fg_color      = '#29334a',
#                            border_color  = '#29334a',
#                            placeholder_text_color =  '#ffffff')
# ZImplant_label.place(x = 180, y = 40)
ZImplant_checkbox = cmtk.CTkCheckBox(tabview.tab("Implantation"),
                                     text = "Z",
                                     command = Zcheck_fun,
                                     width   = 52, height = 5,
                                     checkbox_width = 20, checkbox_height = 20,
                                     border_width = 2,
                                     font    = ("Verdana",12,"bold"),
                                     fg_color      = '#29334a',
                                     border_color  = '#ffffff',
                                     onvalue="on", offvalue="off")
ZImplant_checkbox.place(x = 170, y = 35)

# DImplant_label = cmtk.CTkEntry(master  = tabview.tab("Implantation"),
#                            placeholder_text = "D",
#                            width   = 52,height = 5,
#                            font    = ("Verdana",8,"bold"),
#                            fg_color      = '#29334a',
#                            border_color  = '#29334a',
#                            placeholder_text_color =  '#ffffff')
# DImplant_label.place(x = 260, y = 40)
DImplant_checkbox = cmtk.CTkCheckBox(tabview.tab("Implantation"),
                                     text = "D",
                                     command = Dcheck_fun,
                                     width   = 52, height = 5,
                                     checkbox_width = 20, checkbox_height = 20,
                                     border_width = 2,
                                     font    = ("Verdana",12,"bold"),
                                     fg_color      = '#29334a',
                                     border_color  = '#ffffff',
                                     onvalue="on", offvalue="off")
DImplant_checkbox.place(x = 240, y = 35)

ZImplant_box = cmtk.CTkEntry(master  = tabview.tab("Implantation"),
                           placeholder_text = "0",
                           width   = 50,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
ZImplant_box.place(x = 160, y = 60)
DImplant_box = cmtk.CTkEntry(master  = tabview.tab("Implantation"),
                           placeholder_text = "0",
                           width   = 50,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
DImplant_box.place(x = 240, y = 60)


#           Speed label and entry
SpeedImplant_label1 = cmtk.CTkEntry(master  = tabview.tab("Implantation"),
                           placeholder_text = "Speed",
                           width   = 52,height = 5,
                           font    = ("Verdana",8,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
SpeedImplant_label1.place(x = 60, y = 100)
SpeedImplant_label2 = cmtk.CTkEntry(master  = tabview.tab("Implantation"),
                           placeholder_text = "(um/s)",
                           width   = 52,height = 5,
                           font    = ("Verdana",8,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
SpeedImplant_label2.place(x = 60, y = 113)

SpeedImplant_box = cmtk.CTkEntry(master  = tabview.tab("Implantation"),
                           placeholder_text = "50",
                           width   = 50,
                           font    = ("Verdana",10,"bold"),
                           fg_color      = '#87c9a8',
                           text_color    = '#026afa',
                           placeholder_text_color =  '#026afa',
                           corner_radius = 3)
SpeedImplant_box.place(x = 60, y = 131)

#          Z/D trajectory tracks


ZTrack_label = cmtk.CTkEntry(master  = tabview.tab("Implantation"),
                           placeholder_text = " 0",
                           width   = 52,height = 5,
                           font    = ("Verdana",12,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
ZTrack_label.place(x = 178, y = 100)
DTrack_label = cmtk.CTkEntry(master  = tabview.tab("Implantation"),
                           placeholder_text = " 0",
                           width   = 52,height = 5,
                           font    = ("Verdana",12,"bold"),
                           fg_color      = '#29334a',
                           border_color  = '#29334a',
                           placeholder_text_color =  '#ffffff')
DTrack_label.place(x = 260, y = 100)

#         Stop
Stop3_bnt = cmtk.CTkButton(master  = tabview.tab("Implantation"),
                            text    ='STOP',
                            command = Stop_fun,
                            width   = 12,
                            font    = ("Verdana",12,"bold"),
                            fg_color      = '#eb0202',
                            hover_color   = '#a30303',
                            corner_radius = 5)
Stop3_bnt.place(x = 412, y = 0)


# Speed_box = cmtk.CTkEntry(master  = tabview.tab("Navigation"),
#                            placeholder_text = "1000",
#                            width   = 50,
#                            font    = ("Verdana",10,"bold"),
#                            fg_color      = '#87c9a8',
#                            text_color    = '#026afa',
#                            placeholder_text_color =  '#026afa',
#                            corner_radius = 3)
# Speed_box.place(x = 0, y = 185)





root.mainloop()






