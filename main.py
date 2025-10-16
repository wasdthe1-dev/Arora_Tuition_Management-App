import os
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
from ttkthemes import ThemedStyle

from app.database import Database
from app.ui.splash import SplashScreen
from app.ui.login import LoginFrame
from app.ui.admin_dashboard import AdminApp
from app.ui.student_dashboard import StudentApp
from app.config import COLORS, APP_INFO


class AppController:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.root = ctk.CTk()
        self.root.title(APP_INFO["title"]) 

        try:
            self.root.state("zoomed") 
        except Exception:
            pass
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.root.resizable(True, True)


        self.style = ThemedStyle(self.root)
        self._apply_ttk_theme("dark")


        self.db = Database()
        self.db.init_db()


        self.status_bar = ctk.CTkLabel(self.root, text="", text_color=COLORS["gold"], anchor="e")
        self.status_bar.pack(side="bottom", fill="x", padx=6, pady=4)
        self._tick_clock()

        self.current_frame = None
        self.show_splash()

    def _apply_ttk_theme(self, mode: str):
        try:
            if mode == "light":
                self.style.set_theme("arc")
            else:
                self.style.set_theme("equilux")
        except Exception:
            pass

    def _tick_clock(self):
        import datetime
        now = datetime.datetime.now().strftime("%a, %d %b %Y  %I:%M:%S %p")
        self.status_bar.configure(text=f"{APP_INFO['title']}  •  {now}")
        self.root.after(1000, self._tick_clock)

    def show_splash(self):
        splash = SplashScreen(self.root, title=APP_INFO["title"])
        def load():

            for _ in range(80):
                self.root.after(0, splash.step)
                import time; time.sleep(0.02)
            self.root.after(0, splash.destroy)
            self.root.after(50, self.show_login)
        threading.Thread(target=load, daemon=True).start()

    def clear_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def show_login(self):
        self.clear_frame()
        self.current_frame = LoginFrame(self.root, self.db, on_login=self._on_login, on_exit=self.root.destroy)
        self.current_frame.pack(fill="both", expand=True)

    def _on_login(self, user_type: str, user_record: dict):
        self.clear_frame()
        if user_type == "admin":
            self.current_frame = AdminApp(self.root, self.db, on_logout=self.show_login, on_theme_change=self._on_theme_change)
        else:
            self.current_frame = StudentApp(self.root, self.db, user_record, on_logout=self.show_login)
        self.current_frame.pack(fill="both", expand=True)

    def _on_theme_change(self, mode: str):

        self._apply_ttk_theme(mode)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("assets/icons", exist_ok=True)
    AppController().run()
