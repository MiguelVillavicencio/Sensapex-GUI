# core/math_utils.py
import numpy as np
from tkinter import messagebox
import math
from typing import Tuple

def comply_rotation(input_coords, rotation_deg: int):
    local_coords = np.array(input_coords)

    radians = np.deg2rad(rotation_deg)
    cos_theta = np.cos(radians)
    sin_theta = np.sin(radians)

    rotation_matrix = np.array([
        [cos_theta, -sin_theta, 0, 0],
        [sin_theta,  cos_theta, 0, 0],
        [0,          0,         1, 0],
        [0,          0,         0, 1],
    ])

    new_local_coords = np.dot(rotation_matrix, local_coords)
    return [int(x) for x in new_local_coords]

def evaluate_new_coordinates(input_coords):
    manipulator_axes = ["x", "y", "z", "d"]
    lower_bound = 0
    upper_bound = 20000

    out_of_range = []
    corrected = []
    for i, value in enumerate(input_coords):
        if lower_bound <= value <= upper_bound:
            corrected.append(value)
        else:
            out_of_range.append((manipulator_axes[i], value))
            corrected.append(max(lower_bound, min(value, upper_bound)))

    if out_of_range:
        result_string = "\n".join(f"{axis}: {val}" for axis, val in out_of_range)
        msg = (
            "Following targets are out of micromanipulator's range.\n"
            f"{result_string}\n"
            "Continue?\n"
            "If 'Yes' target will truncate at stages' limits"
        )
        answer = messagebox.askquestion("Out of range", msg, type=messagebox.YESNO, default=messagebox.NO)
        return (answer == "yes"), corrected

    return True, corrected

def go_routine(device, curr_pos, target_pos, speed_entry: int, fetch_callback=None):
    curr_pos1 = list(curr_pos)
    curr_pos1[2] = 0
    curr_pos1[3] = 0
    device.goto(curr_pos1, speed=speed_entry)

    curr_pos2 = list(target_pos)
    curr_pos2[2] = 0
    curr_pos2[3] = 0
    device.goto(curr_pos2, speed=speed_entry)

    final_pos = list(target_pos)
    final_pos[2] = 500
    final_pos[3] = 500
    device.goto(final_pos, speed=250)

    if fetch_callback:
        fetch_callback()

# def xy_to_apml(x: int, y: int, rotation_deg: int):
#     """Map device XY into anatomical AP/ML for DISPLAY/USER space."""
#     r = rotation_deg % 360
#     if r in (0, 180):
#         return x, y
#     # r in (90, 270)
#     return y, x

# def apml_to_xy(ap: int, ml: int, rotation_deg: int):
#     """Map anatomical AP/ML into device XY for EXECUTION space."""
#     r = rotation_deg % 360
#     if r in (0, 180):
#         return ap, ml
#     # r in (90, 270)
#     return ml, ap

def apml_to_xy(ap: float, ml: float, rotation_deg: float) -> Tuple[float, float]:
    """
    USER (AP, ML) -> DEVICE (X, Y)
    Convention:
      - rot=0: AP->+X, ML->+Y
      - positive rotation rotates USER axes counterclockwise relative to DEVICE
      v_dev = R(theta) * v_user
    """
    theta = math.radians(rotation_deg % 360)
    c = math.cos(theta)
    s = math.sin(theta)

    x = c * ap - s * ml
    y = s * ap + c * ml
    return x, y


def xy_to_apml(x: float, y: float, rotation_deg: float) -> Tuple[float, float]:
    """
    DEVICE (X, Y) -> USER (AP, ML)
    This is the inverse transform of apml_to_xy, using R(-theta)=R(theta)^T.
    v_user = R(-theta) * v_dev
    """
    theta = math.radians(rotation_deg % 360)
    c = math.cos(theta)
    s = math.sin(theta)

    ap =  c * x + s * y
    ml = -s * x + c * y
    return ap, ml
