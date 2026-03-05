# core/ui_helpers.py
def set_entry(entry, text, *, key_name: str = "", overwrite: bool = True):
    """
    Safely set a CTkEntry/Tk Entry text.

    - Casts text to str (prevents <class 'str'> surprises)
    - Optionally doesn't overwrite if user already typed something
    - Prints a warning if entry is missing
    """
    if entry is None:
        if key_name:
            print(f"[WARN] set_entry: missing widget for key '{key_name}'")
        return

    if text is None:
        text = ""

    # If someone accidentally passes a type (e.g. str), make it obvious
    if isinstance(text, type):
        print(f"[WARN] set_entry: got a type for '{key_name}': {text}. Did you pass str instead of a string?")
        text = str(text)  # will become "<class 'str'>", but now you get a warning

    # Don't nuke user input unless told
    if not overwrite:
        try:
            if entry.get().strip():
                return
        except Exception:
            pass

    try:
        entry.delete(0, "end")
        entry.insert(0, str(text))
    except Exception as e:
        print(f"[WARN] set_entry failed for '{key_name}': {e}")
# def set_entry(entry, text: str):
#     if entry is None:
#         return
#     entry.delete(0, "end")
#     entry.insert(0, text)
    
def get_str(entry, key_name: str = "") -> str:
    if entry is None:
        if key_name:
            print(f"[WARN] get_str: missing widget for key '{key_name}'")
        return ""
    s = entry.get()
    if s is None:
        return ""
    s = str(s).strip()

    if s == "<class 'str'>":
        print(f"[WARN] get_str: '{key_name}' contains the literal \"<class 'str'>\". Something is inserting the type 'str' into this Entry.")
        # treat as empty to avoid int() crash
        return ""

    return s

# def get_str(entry, key_name: str = "") -> str:
#     if entry is None:
#         print(f"[WARN] Entry widget missing for key: {key_name}")
#         return
#     entry.delete(0, "end")
#     # entry.insert(0, str(text))
#     return entry.get().strip()

# def get_str(entry) -> str:
#     if entry is None:
#         return ""
#     return entry.get().strip()

def get_int(entry, default: int = 0) -> int:
    s = get_str(entry)
    if not s:
        return default
    try:
        return int(s)
    except ValueError:
        return default

def get_float(entry, default: float = 0.0, key_name: str = "") -> float:
    try:
        return float(entry.get())
    except (ValueError, AttributeError):
        if key_name:
            print(f"[WARNING] Invalid float in {key_name}. Using default={default}")
        return default

    
def normalize_listbox_selection(sel):
    """
    Normalize CTkListbox/Tk listbox selection return into an int index or None.
    Handles: None, int, '1', '1.0', (1,), [1], etc.
    """
    if sel is None:
        return None
    if isinstance(sel, (tuple, list)):
        if not sel:
            return None
        sel = sel[0]
    if isinstance(sel, str):
        try:
            return int(float(sel))
        except Exception:
            return None
    try:
        return int(sel)
    except Exception:
        return None

