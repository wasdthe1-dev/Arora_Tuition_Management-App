import customtkinter as ctk
from app.config import COLORS, FONTS


class SplashScreen(ctk.CTkToplevel):
    def __init__(self, master, title: str):
        super().__init__(master)
        self.geometry("520x280")
        self.overrideredirect(True)
        self.configure(fg_color=COLORS["bg1"])
        self.attributes("-topmost", True)
        self.after(10, self._center)

        title_label = ctk.CTkLabel(self, text=title, font=("Segoe UI", 20, "bold"), text_color=COLORS["gold"])
        title_label.pack(pady=(60, 10))
        self.progress = ctk.CTkProgressBar(self, width=420)
        self.progress.set(0)
        self.progress.pack(pady=10)
        self.sub = ctk.CTkLabel(self, text="Loading", font=FONTS["body"], text_color=COLORS["muted"]) 
        self.sub.pack(pady=(4, 0))
        self._dots = 0
        self._animate_dots()

    def _center(self):
        self.update_idletasks()
        w, h = map(int, self.geometry().split('+')[0].split('x'))
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _animate_dots(self):
        self._dots = (self._dots + 1) % 4
        self.sub.configure(text="Loading" + "." * self._dots)
        self.after(300, self._animate_dots)

    def step(self):
        # ease-in progress
        val = self.progress.get()
        inc = 0.02 if val < 0.6 else 0.01
        self.progress.set(min(val + inc, 1.0))
