"""Shared Bookish OS layout rules for desktop and tablet-sized windows.

Pure functions make responsiveness testable without a display server.
"""


def layout_for_width(width):
    """Return the layout profile for a window width in logical pixels."""
    if width < 1:
        raise ValueError("window width must be positive")
    if width < 900:
        return {"mode": "compact", "sidebar_width": 74, "label_navigation": False,
                "content_padding": 14}
    return {"mode": "desktop", "sidebar_width": 225, "label_navigation": True,
            "content_padding": 30}
