"""Real Tkinter GUI smoke under Xvfb. Only operates in disposable HOME.

This checks that actual windows can be created, navigated and repainted. It
does not test hardware drivers, SDDM, Wayland or disk installation.
"""
import os
from pathlib import Path
import tempfile
import time


def smoke():
    with tempfile.TemporaryDirectory() as temp:
        os.environ["HOME"] = temp
        os.environ["XDG_CONFIG_HOME"] = str(Path(temp) / ".config")
        from aevonyr.onboarding import mark_completed
        mark_completed()  # Avoid pop-up while checking navigation.
        from aevonyr.ui import AevonyrDesktop
        root = AevonyrDesktop()
        root.geometry("1160x800")
        root.update_idletasks()
        pages = ("home", "apps", "files", "network", "updates", "phone",
                 "pulse", "system", "restore", "notes", "settings", "about")
        try:
            for page in pages:
                root.show(page)
                root.update()
                print(f"rendered: {page}", flush=True)
                if page == "pulse":
                    time.sleep(1.8)
                    root.update()
                    panels = root.body.winfo_children()
                    assert panels, "Pulse panel not created"
                    panel = panels[0]
                    assert panel._values["ram"].cget("text").endswith("%"), "Pulse RAM did not update"
                elif page == "apps":
                    # The listing is asynchronous; visual page still must render.
                    root.update()
            root.show_welcome()
            root.update()
            wizard = root._wizard
            assert wizard.winfo_exists()
            wizard._navigate(1)
            root.update()
            wizard._navigate(1)
            root.update()
            wizard.destroy()
            root.update()
            print("All Aevonyr 1.0 GUI smoke checks passed.", flush=True)
        finally:
            root.destroy()


if __name__ == "__main__":
    smoke()
