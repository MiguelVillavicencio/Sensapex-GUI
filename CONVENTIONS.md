# CONVENTIONS

## Coordinate spaces
### Device space (hardware)
- Axes: `X, Y, Z, D`
- Units: microns (µm), integer commands to the device.

### User/anatomical space (UI)
- Axes: `AP, ML, DV, A∠`
- `DV` maps to Z (depth axis), `A∠` maps to D.
- UI may display floats for AP/ML when using true rotation.

## Rotation semantics (TRUE rotation with sign)
We use a true 2D rotation relationship between user XY-plane axes (AP/ML) and device axes (X/Y).

Let θ = `rotation_deg` in degrees.

USER → DEVICE:
- `[X, Y]^T = R(θ) [AP, ML]^T`
- `X = cosθ·AP − sinθ·ML`
- `Y = sinθ·AP + cosθ·ML`

DEVICE → USER:
- `[AP, ML]^T = R(−θ) [X, Y]^T`
- `AP = cosθ·X + sinθ·Y`
- `ML = −sinθ·X + cosθ·Y`

Special cases (90° steps):
- 0°:   `AP→+X`, `ML→+Y`
- 90°:  `AP→+Y`, `ML→−X`
- 180°: `AP→−X`, `ML→−Y`
- 270°: `AP→−Y`, `ML→+X`

## Target storage model (Option 1)
### Stored canonical targets (USER-space, relative to zero)
We store targets as:
- `RelAP_MkD[i], RelML_MkD[i], RelDV_MkD[i], RelAA_MkD[i]`

These are the authoritative values for a target.

### Cached absolute device targets
We also cache absolute device coordinates for convenience/display:
- `CoordX_MarkD[i], CoordY_MarkD[i], CoordZ_MarkD[i], CoordD_MarkD[i]`

These must be recomputed from Rel* whenever:
- rotation changes
- zero basis changes

## Zero basis
- `zero_pos` is a device-space absolute position.
- When `Zeroed == 1`, user-space values are interpreted relative to zero basis.

## UI Display mode
- `display_mode = "user"`: show AP/ML/DV/A∠
- `display_mode = "device"`: show X/Y/Z/D

## Step buttons (Leveling tab)
- Right/Left buttons modify **ML** in user space.
- Anterior/Posterior buttons modify **AP** in user space.
- Deltas are mapped to device XY using `apml_to_xy(d_ap, d_ml, rotation_deg)`.

## Listbox indexing
- `Targets_box` row 0 is header.
- For a selected row `idx` in the widget, the corresponding target index is `idx - 1`.
- Always normalize selection using `normalize_listbox_selection()`.
