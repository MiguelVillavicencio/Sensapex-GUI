# TODO

## Must-fix (stability)
- [ ] Add `normalize_listbox_selection()` in `core/ui_helpers.py` and use it in:
  - `controllers/navigation.py`: `selection_markd()`, `markd_remove()`, and any key handlers that read selection.
- [ ] Add `get_float()` in `core/ui_helpers.py` and use it for AP/ML parsing in:
  - `controllers/navigation.py`: `go()`, `markd_add()`
  - optionally `controllers/leveling.py` if fractional step inputs are desired.
- [ ] In `controllers/navigation.py` `zero_basis()`: when recomputing absolute caches from RelAP/RelML, round to int:
  - `int(round(zp[0] + x_rel))`, `int(round(zp[1] + y_rel))`, etc.
- [ ] In `ui/tabs/navigation.py`: add keyboard bindings to `Targets_box`:
  - Up/Down to change selection
  - Enter to `go()`
  - Delete/Backspace to `markd_remove()`
  - Esc to clear Go entries
- [ ] Unhandled situation when 'Quit' bottom is hit
- [ ] Remove default for Go to finish Z & D in 500um

## UX improvements
- [ ] Show mapping label in Leveling tab with exact sign-aware mapping for 0/90/180/270:
  - `AP→+X, ML→+Y`, `AP→+Y, ML→−X`, etc. (already present; verify text).
- [ ] Add a small mapping “compass” label near Rotate button (optional).
- [ ] Improve target row formatting for alignment (fixed-width columns).
- [ ] Add a box next to the 'Rotate 90 d." bottom where user can input any degree (maybe, if it results to be useful at some point)
- [ ] Enable 'Implantation' tab
- [ ] Integrate atlas visualization


## Cleanups
- [ ] Remove or rename `comply_rotation()` to `legacy_comply_rotation()` (avoid accidental use).
- [ ] Remove legacy arrays from `AppState` once confirmed unused:
  - `CoordX_RelMkD`, `CoordY_RelMkD`, `CoordZ_RelMkD`, `CoordD_RelMkD`
- [ ] Confirm all controllers use `apml_to_xy()` / `xy_to_apml()` and not old rotation semantics.
- [ ] Move makers info from lists to dictionaries, along with other features (color, name, etc)

## Safety / QA
- [ ] Add a “debug mode” flag in state that enables verbose prints without editing code.
- [ ] Add guardrails around device movement:
  - always validate limits
  - always clamp only after user confirmation
- [ ] Add tests (even simple ones) for:
  - mapping at 0/90/180/270
  - invertibility: `xy_to_apml(*apml_to_xy(ap,ml)) ≈ (ap,ml)`

## CUSTOMIZATION
- [ ] add a "Settings" tab with contents:
	- Calibrate (move from Navigation)
	- Reset (move from Navigation)
	- Save settings: a JSON file saving current rotation, targets lists, etc that it's loaded automatically (NEW)

## PLOTTING
- [X] Plot brain and rotate X,Y,Z axes around it
- [X] Make plot bigger
- [ ] Apply update_figure() in all instances where lists of markers are manipulated
- [ ] Add plot-navigation buttons like zoom, pan, roll
