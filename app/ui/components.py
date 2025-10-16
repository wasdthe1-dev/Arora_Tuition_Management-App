import customtkinter as ctk
from tkinter import ttk
from app.config import COLORS, FONTS


class GoldButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["gold"],
            hover_color=COLORS["gold_dim"],
            text_color=COLORS["bg1"],
            corner_radius=10,
            **kwargs,
        )


class Card(ctk.CTkFrame):
    def __init__(self, master, title: str, value: str, **kwargs):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=12, **kwargs)
        self.title = ctk.CTkLabel(self, text=title, font=FONTS["h2"], text_color=COLORS["gold"]).pack(
            anchor="w", padx=12, pady=(12, 2)
        )
        self.value = ctk.CTkLabel(
            self, text=value, font=("Segoe UI", 20, "bold"), text_color=COLORS["white"]
        ).pack(anchor="w", padx=12, pady=(0, 12))


def style_treeview(tv: ttk.Treeview):
    style = ttk.Style(tv)
    style.configure(
        "Treeview",
        background=COLORS["bg2"],
        fieldbackground=COLORS["bg2"],
        foreground=COLORS["white"],
        rowheight=28,
    )
    style.map(
        "Treeview",
        background=[("selected", COLORS["gold"])],
        foreground=[("selected", COLORS["bg1"])],
    )


class PanelSwitcher(ctk.CTkFrame):
    """Animated panel switcher that slides new content in.

    Usage:
        switcher = PanelSwitcher(parent)
        switcher.set(widget)  # shows first
        switcher.transition_to(next_widget, direction=1)
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["bg1"], **kwargs)
        self.current = None

    def set(self, widget: ctk.CTkFrame):
        if self.current is not None:
            self.current.place_forget()
        self.current = widget
        self.current.place(relx=0, rely=0, relwidth=1, relheight=1)

    def transition_to(self, widget: ctk.CTkFrame, direction: int = 1, steps: int = 24, interval_ms: int = 10):
        # If navigating to the same widget, do nothing
        if widget is self.current:
            return
        if self.current is None:
            self.set(widget)
            return
        # place new just outside view
        start_x = 1.0 if direction > 0 else -1.0
        widget.place(relx=start_x, rely=0, relwidth=1, relheight=1)

        def ease_in_out_quad(t: float) -> float:
            return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t

        def animate(step=0):
            t = step / steps
            prog = ease_in_out_quad(t)
            offset = start_x * (1 - prog)
            widget.place(relx=offset, rely=0, relwidth=1, relheight=1)
            if direction > 0:
                self.current.place(relx=offset - 1.0, rely=0, relwidth=1, relheight=1)
            else:
                self.current.place(relx=offset + 1.0, rely=0, relwidth=1, relheight=1)
            if step < steps:
                self.after(interval_ms, lambda: animate(step + 1))
            else:
                self.current.place_forget()
                self.current = widget

        animate()
