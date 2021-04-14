SAVED_ROOT = None


def center(window, root=None):
    global SAVED_ROOT
    if root is not None:
        SAVED_ROOT = root
    # add offset
    SAVED_ROOT.update_idletasks()
    win_x = SAVED_ROOT.winfo_screenwidth() // 2 - window.winfo_width() // 2

    win_y = SAVED_ROOT.winfo_screenheight() // 2 - window.winfo_height() // 2

    # set top level in new position
    window.geometry(f'+{win_x}+{win_y}')
