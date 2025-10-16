import customtkinter as ctk
from tkinter import messagebox
from app.config import COLORS, FONTS, set_mode, CURRENT_MODE
from app.controllers.auth import login as auth_login


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, db, on_login, on_exit):
        super().__init__(master, fg_color=COLORS["bg1"]) 
        self.db = db
        self.on_login = on_login
        self.on_exit = on_exit

        self.container = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=16)
        # start off-screen for slide-in animation
        self.container.place(relx=-0.6, rely=0.5, anchor="center", relwidth=0.5, relheight=0.6)

        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(12, 4))
        title = ctk.CTkLabel(header, text="Welcome", font=FONTS["h1"], text_color=COLORS["gold"]) 
        title.pack(side="left", padx=16)
        # Theme toggle
        theme = ctk.CTkSegmentedButton(header, values=["Light", "Dark"]) 
        theme.set("Dark" if CURRENT_MODE == "dark" else "Light")
        def _toggle(val):
            set_mode("light" if val.lower().startswith("light") else "dark")
        theme.configure(command=_toggle)
        theme.pack(side="right", padx=16)

        self.role = ctk.StringVar(value="admin")
        switcher = ctk.CTkSegmentedButton(self.container, values=["admin", "student"], variable=self.role,
                                          fg_color=COLORS["bg2"], selected_color=COLORS["gold"], selected_hover_color=COLORS["gold_dim"],
                                          unselected_color=COLORS["panel"], text_color=COLORS["white"]) 
        switcher.pack(pady=8)

        # Labeled inputs so text never disappears
        form = ctk.CTkFrame(self.container, fg_color="transparent")
        form.pack(pady=8)
        ctk.CTkLabel(form, text="Username:", text_color=COLORS["gold"]).grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.username = ctk.CTkEntry(form, width=280)
        self.username.grid(row=0, column=1, sticky="w", padx=6, pady=6)
        ctk.CTkLabel(form, text="Password:", text_color=COLORS["gold"]).grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.password = ctk.CTkEntry(form, show="*", width=280)
        self.password.grid(row=1, column=1, sticky="w", padx=6, pady=6)

        btn = ctk.CTkButton(self.container, text="Login", width=180, corner_radius=10, fg_color=COLORS["gold"],
                             hover_color=COLORS["gold_dim"], text_color=COLORS["bg1"], command=self._do_login)
        btn.pack(pady=12)

        exit_btn = ctk.CTkButton(self.container, text="Exit", width=120, corner_radius=10, fg_color="#333333",
                                  hover_color="#444444", command=self.on_exit)
        exit_btn.pack(pady=4)

        self._animate_in()

    def _animate_in(self):
        steps = 24
        def anim(step=0):
            t = step / steps
            # ease-out
            prog = 1 - (1 - t)*(1 - t)
            x = -0.6 + (1.1) * prog  # from -0.6 to 0.5
            self.container.place(relx=x, rely=0.5, anchor="center", relwidth=0.5, relheight=0.6)
            if step < steps:
                self.after(12, lambda: anim(step + 1))
        anim()

    def _do_login(self):
        user = self.username.get().strip()
        pwd = self.password.get().strip()
        if not user or not pwd:
            messagebox.showwarning("Login", "Please enter both username and password")
            return
        res = auth_login(self.db, self.role.get(), user, pwd)
        if res:
            utype, record = res
            self.on_login(utype, record)
        else:
            messagebox.showerror("Invalid", "Invalid username or password")
