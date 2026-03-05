# ARCHITECTURE

## High-level layout
- `main.py`
  - wires app together
  - creates root, tabs, widgets dict
  - constructs controllers and injects dependencies
  - starts mainloop

- `core/`
  - `state.py`: AppState (single source of truth)
  - `device.py`: Sensapex device wrapper (UMP)
  - `math_utils.py`: mapping functions + movement routines + bounds validation
  - `ui_helpers.py`: safe UI getter/setter helpers, selection normalization

- `ui/`
  - `theme.py`: centralized colors and styling constants
  - `figure3d.py`: matplotlib plot creation + `update_fig(ax, rotation_deg)`
  - `ui/tabs/`
    - `navigation.py`: build navigation widgets and connect callbacks
    - `leveling.py`: build leveling widgets and connect callbacks
    - `implantation.py`: build implantation widgets and connect callbacks

- `controllers/`
  - `navigation.py`: targets list, add/remove, go, fetch display, selection behavior
  - `leveling.py`: step moves (AP/ML), leveling offsets, mapping label updates
  - `implantation.py`: DV zero, implant/explant routines, tracking
  - `common.py`: global actions and orchestration (rotate, stop, plot updates)

## Dependency rules
- UI tab builders (`ui/tabs/*`) should only:
  - construct widgets
  - register them into `widgets` dict
  - bind callbacks to controller methods
  - NEVER contain device logic or math logic

- Controllers should:
  - read/write `AppState`
  - call device methods through `core/device.py`
  - call mapping via `core/math_utils.py`
  - update UI via `core/ui_helpers.py` (set_entry/get_*)

- `CommonController` orchestrates cross-controller refresh:
  - on rotate: updates state.rotation_deg, plot, target caches, then tells:
    - `nav_ctrl.refresh_targets_list()`
    - `nav_ctrl.fetch()`
    - `lvl_ctrl.update_mapping_label()`

## Data flow
1) User interacts with UI widget
2) UI triggers a controller callback
3) Controller:
   - validates inputs (get_str/get_int/get_float)
   - updates state arrays and/or calls device movement
   - updates widgets using set_entry / refresh_targets_list
4) Plot/UI refresh occurs if needed

## Rotation contract
All conversions between user-space and device-space must use:
- `apml_to_xy(ap, ml, rotation_deg)`
- `xy_to_apml(x, y, rotation_deg)`

No controller should call legacy rotation paths.
