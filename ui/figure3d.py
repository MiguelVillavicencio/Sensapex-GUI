# ui/figure3d.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pathlib import Path
from matplotlib.lines import Line2D

class PlotHandle:
    def __init__(self, fig, ax, canvas):
        self.fig = fig
        self.ax = ax
        self.canvas = canvas
        
# ----------------------------
# Brain wire data (cached)
# ----------------------------
_BRAIN_GRID_CACHE = None

def _load_brain_grid() -> np.ndarray:
    """
    Loads brainGridData.npy (Nx3):
      col0 = AP, col1 = DV, col2 = ML
    Rows of [0,0,0] are treated as polyline separators (breaks).
    """
    global _BRAIN_GRID_CACHE
    if _BRAIN_GRID_CACHE is not None:
        return _BRAIN_GRID_CACHE

    candidates = [
        Path(__file__).with_name("brainGridData.npy"),  # ui/brainGridData.npy
        Path("brainGridData.npy"),                      # cwd fallback
    ]
    for p in candidates:
        if p.exists():
            _BRAIN_GRID_CACHE = np.load(p)
            return _BRAIN_GRID_CACHE

    print("[WARNING] brainGridData.npy not found. Brain wireframe will not be drawn.")
    _BRAIN_GRID_CACHE = np.empty((0, 3), dtype=float)
    return _BRAIN_GRID_CACHE


def create_plot(master, rotation_deg: int):
    fig = plt.figure(figsize=(6, 6), dpi=100) # figsize (wide, height) is inches, not pixels
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor("k")
    ax.view_init(elev=45, azim=45, roll=0) # set the camera view (in deg)
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection="3d")
    # ax.set_facecolor("k")
    # # fig.set_size_inches(4, 4)
    # fig.set_size_inches(8, 4)

    update_fig(ax, rotation_deg)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)

    canvas = FigureCanvasTkAgg(fig, master=master)
    canvas.draw()
    return PlotHandle(fig, ax, canvas)

def update_fig(ax, rotation_deg: float, markers=None):
    ax.clear()
    ax.set_facecolor("k")
    
    current_elev = ax.elev
    current_azim = ax.azim
    current_dist = ax.dist

    # ---------------------------------------
    # Rotation (around DV axis): rotate AP/ML
    # ---------------------------------------
    angle = np.radians(rotation_deg % 360)
    rot = np.array([
        [np.cos(angle), -np.sin(angle)],
        [np.sin(angle),  np.cos(angle)]
    ])

    # ---------------------------------------
    # 1) Draw brain wireframe (WHITE), rotated
    # ---------------------------------------
    data = _load_brain_grid()
    if data.size:
        d = data.astype(float)
        # Center brain coords at bregma (AP, ML, DV)
        bregma = np.array([540.0, 570.0, 0.0], dtype=float)
        is_break = np.all(d == 0, axis=1)
        d[~is_break] = d[~is_break] - bregma
        
        # Break polylines at [0,0,0] rows
        breaks = np.where(is_break)[0]
        # breaks = np.where(np.all(d == 0, axis=1))[0]
        start = 0

        def plot_segment(seg: np.ndarray):
            if seg.shape[0] < 2:
                return
            ap = seg[:, 0]*-1  # reverse direction
            dv = seg[:, 2]     # 
            ml = seg[:, 1]     # 

            xy = rot @ np.vstack((ap, ml))  # rotate AP/ML
            ax.plot(
                xy[0, :],     # AP'
                xy[1, :],     # ML'
                dv,           # DV
                color="w",
                linewidth=0.5
            )

        for b in breaks:
            plot_segment(d[start:b])
            start = b + 1
        plot_segment(d[start:])

    # ----------------------------------------------------
    # 2) Draw manipulator axes (ALWAYS X/Y/Z, consistent)
    #
    #  GUI definitions:
    #   X = ML  -> +Y direction in this plot
    #   Y = AP  -> +X direction in this plot
    #   Z = DV  -> +Z direction in this plot
    # These arrows do NOT rotate; the brain rotates instead.
    # ----------------------------------------------------
    L =  660  # arrow length
    O = -660  # arrow origin

    # X = red, along +X
    ax.plot([O, L], [O, O], [O, O], marker="v", color="r")
    ax.text(L, O, O, "X", color="white",
            bbox={"facecolor": "red", "alpha": 0.5, "pad": 6})

    # Y = blue, along +Y
    ax.plot([O, O], [O, L],[O, O], marker="v", color="b")
    ax.text(O, L, O, "Y", color="white",
            bbox={"facecolor": "blue", "alpha": 0.5, "pad": 6})

    # Z (DV) = green, along +Z
    ax.plot([O, O], [O, O], [O, L], marker="v", color="g")
    ax.text(O, O, L, "Z", color="white",
            bbox={"facecolor": "green", "alpha": 0.25, "pad": 6})
    
    # ----------------------------------------------------
    # 3) Draw targets. Comply current rotation
    # ----------------------------------------------------
    if markers:
        legend_handles = []
        legend_labels = []
        
        for m in markers:
            ap = np.asarray(m.get("ap", []), dtype=float)/10 # ccf works @10um resolution
            ml = np.asarray(m.get("ml", []), dtype=float)/10
            dv = np.asarray(m.get("dv", []), dtype=float)/10

            n = min(len(ap), len(ml), len(dv))
            if n <= 0:
                continue
            ap, ml, dv = ap[:n], ml[:n], dv[:n]
            # xy = np.vstack((ap, ml))
        
            xy = rot @ np.vstack((ap, ml))  # rotate with space

            # per-target identity colors (RGBA list/array), or fallback
            base_colors = m.get("colors", None)
            if base_colors is None:
                base_colors = np.tile(np.array([1, 1, 0, 1.0]), (n, 1))  # yellow fallback
            colors = np.asarray(base_colors, dtype=float)
            if colors.ndim == 1:
                colors = np.tile(colors, (n, 1))
            colors = colors[:n]

            # auto-darken by DV for depth perception
            if m.get("darken_by_dv", True):
                colors = _darken_by_depth(colors, dv, strength=float(m.get("darken_strength", 0.55)))
                
            ax.scatter(
                xy[0, :], xy[1, :], dv,
                c=colors, s=100, depthshade=False
            )
            
            # target numbers on plot (1-based)
            if m.get("label_numbers", True):
                for i in range(n):
                    ax.text(
                        float(xy[0, i]), float(xy[1, i]), float(dv[i]),
                        str(i + 1),
                        color="yellow",
                        fontsize=12,
                        ha="center", va="center",
                    )

            # legend with target numbers (proxy handles)
            if m.get("legend", True):
                # keep legend readable: optionally limit count
                max_legend = int(m.get("max_legend", 30))
                k = min(n, max_legend)
                for i in range(k):
                    ids = m.get("IDs", [])
                    label_name = ids[i] if i < len(ids) else f"{i+1}"
                    legend_handles.append(
                        Line2D([0], [0], marker="o", linestyle="",
                               markerfacecolor=colors[i], markeredgecolor="none",
                               markersize=7)
                    )
                    legend_labels.append(f"{m.get('name','Target')} {i+1} | {label_name}")

        if legend_handles:
            ax.legend(
                legend_handles, legend_labels,
                loc="upper left",
                frameon=True,
                fontsize=8
            )

    # View / style
    ax.view_init(elev=current_elev, azim=current_azim, roll=0)
    ax.dist=current_dist
    ax.axis("off")
    ax.invert_zaxis() #
    
    
    
def _darken_by_depth(colors_rgba: np.ndarray, dv: np.ndarray, strength: float = 0.55):
    """
    Darken colors as DV increases (deeper -> darker). strength in [0..1].
    Returns new RGBA array.
    """
    cols = np.array(colors_rgba, dtype=float, copy=True)
    if cols.ndim == 1:
        cols = np.tile(cols, (len(dv), 1))
    if len(dv) == 0:
        return cols

    dv = np.asarray(dv, dtype=float)
    dmin, dmax = float(np.nanmin(dv)), float(np.nanmax(dv))
    if np.isclose(dmin, dmax):
        return cols

    # normalize 0..1 (shallow->0, deep->1)
    t = (dv - dmin) / (dmax - dmin)
    # scale factor: shallow ~1, deep ~(1-strength)
    s = 1.0 - strength * t

    cols[:, 0] *= s
    cols[:, 1] *= s
    cols[:, 2] *= s
    return cols

