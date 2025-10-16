import customtkinter as ctk

DARK_COLORS = {
    "bg1": "#0b0b0d",
    "bg2": "#141419",
    "panel": "#101015",
    "gold": "#FFD700",
    "gold_dim": "#C9A400",
    "white": "#FFFFFF",
    "muted": "#A0A0A0",
}

LIGHT_COLORS = {
    "bg1": "#f6f6f8",
    "bg2": "#ffffff",
    "panel": "#ffffff",
    "gold": "#C9A400",
    "gold_dim": "#9f8700",
    "white": "#000000",
    "muted": "#555555",
}

# Mutable palette used by the UI; toggled via set_mode()
COLORS = DARK_COLORS.copy()
CURRENT_MODE = "dark"

APP_INFO = {
    "title": "Arora Teacher – Tuition Management System",
    "version": "1.0.0",
}

FONTS = {
    "h1": ("Segoe UI", 24, "bold"),
    "h2": ("Segoe UI", 18, "bold"),
    "body": ("Segoe UI", 12),
}

def set_mode(mode: str = "dark"):
    """Switch between light/dark modes.
    Updates the global COLORS palette and CTk appearance mode.
    """
    global CURRENT_MODE, COLORS
    mode = mode.lower()
    if mode == CURRENT_MODE:
        return
    if mode == "light":
        COLORS.clear(); COLORS.update(LIGHT_COLORS)
        ctk.set_appearance_mode("light")
        CURRENT_MODE = "light"
    else:
        COLORS.clear(); COLORS.update(DARK_COLORS)
        ctk.set_appearance_mode("dark")
        CURRENT_MODE = "dark"
