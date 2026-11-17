import win32gui
import win32con


def _enum_visible_windows():
    """Return a list of (hwnd, title) for visible, titled top-level windows."""
    windows = []

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd)
        if not title.strip():
            return
        rect = win32gui.GetClientRect(hwnd)
        if rect[2] == 0 or rect[3] == 0:
            return
        windows.append((hwnd, title))

    win32gui.EnumWindows(callback, None)
    return windows


def choose_window_interactively():
    """
    Print a numbered list of open windows and let the user pick one by index.
    Returns the chosen hwnd (int).
    """
    windows = _enum_visible_windows()
    if not windows:
        raise RuntimeError("No visible windows found.")

    print("\nOpen windows:")
    for i, (hwnd, title) in enumerate(windows):
        print(f"  [{i}] {title}")

    while True:
        choice = input("\nType the number of the window to target: ").strip()
        if choice.isdigit() and 0 <= int(choice) < len(windows):
            hwnd, title = windows[int(choice)]
            print(f"Selected: {title}")
            return hwnd
        print("Invalid choice, try again.")


def get_window_rect(hwnd):
    
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
   
    client_left_top = win32gui.ClientToScreen(hwnd, (left, top))
    client_right_bottom = win32gui.ClientToScreen(hwnd, (right, bottom))
    return (
        client_left_top[0],
        client_left_top[1],
        client_right_bottom[0],
        client_right_bottom[1],
    )


def is_window_valid(hwnd):
    return win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)


def bring_to_front(hwnd):
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass  
