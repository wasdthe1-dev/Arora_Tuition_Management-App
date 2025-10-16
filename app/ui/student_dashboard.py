import customtkinter as ctk
from tkinter import ttk
from app.config import COLORS, FONTS
from app.ui.components import style_treeview


class StudentApp(ctk.CTkFrame):
    def __init__(self, master, db, user_record, on_logout):
        super().__init__(master, fg_color=COLORS["bg1"]) 
        self.db = db
        self.user = user_record
        self.on_logout = on_logout

        header = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text=f"Welcome, {self.user['name']}", font=FONTS["h2"], text_color=COLORS["gold"]).pack(side="left", padx=12, pady=8)
        # Logout bottom-left anchor
        footer = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=0)
        footer.pack(side="bottom", fill="x")
        ctk.CTkButton(footer, text="Logout", fg_color=COLORS["gold"], text_color=COLORS["bg1"], command=self.on_logout).pack(side="left", padx=12, pady=8)

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=12, pady=12)
        self.home = self.tabs.add("Home")
        self.timetable = self.tabs.add("Timetable")
        self.attendance = self.tabs.add("Attendance")
        self.fees = self.tabs.add("Fees")
        self.ann = self.tabs.add("Announcements")
        self.profile = self.tabs.add("Profile")

        # --- Home: Dynamic dashboard cards ---
        self._build_home()

        # Attendance
        cols = ("Date", "Status")
        tv = ttk.Treeview(self.attendance, columns=cols, show="headings")
        for c in cols:
            tv.heading(c, text=c)
            tv.column(c, width=160, anchor="w")
        tv.pack(fill="both", expand=True, padx=8, pady=8)
        style_treeview(tv)
        for d, s in self.db.get_attendance(self.user['id']):
            tv.insert('', 'end', values=(d, s))

        # Fees summary
        f = self.db.get_fees(self.user['id'])
        paid, pending, last = (f or (0, 0, None))
        ctk.CTkLabel(self.fees, text=f"Paid: ₹ {paid:.2f}\nPending: ₹ {pending:.2f}\nLast Payment: {last or '-'}",
                     font=FONTS["h2"], text_color=COLORS["gold"]).pack(pady=16)

        # Messages
        cols2 = ("Message", "Date", "Sender")
        tv2 = ttk.Treeview(self.ann, columns=cols2, show="headings")
        for c in cols2:
            tv2.heading(c, text=c)
            tv2.column(c, width=220, anchor="w")
        tv2.pack(fill="both", expand=True, padx=8, pady=8)
        style_treeview(tv2)
        for m, d, s in self.db.list_messages_for(self.user['username']):
            tv2.insert('', 'end', values=(m, d, s))

        # Profile + Change Password
        self._build_profile()

    def _build_home(self):
        grid = ctk.CTkFrame(self.home, fg_color=COLORS["bg1"]) 
        grid.pack(fill="both", expand=True, padx=12, pady=12)
        # Top metrics
        from app.ui.components import Card
        # Attendance %
        try:
            pct = self.db.attendance_percentage(self.user['id'])
        except Exception:
            pct = 0
        metrics = [
            ("Name", self.user['name']),
            ("Roll No", str(self.user['id'])),
            ("Class", self.user['class']),
            ("Attendance", f"{pct}%"),
        ]
        for i,(t,v) in enumerate(metrics):
            card = Card(grid, t, v)
            card.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")
        for i in range(len(metrics)):
            grid.grid_columnconfigure(i, weight=1)

        # Timetable preview / Upcoming classes
        tt_frame = ctk.CTkFrame(grid, fg_color=COLORS["panel"], corner_radius=12)
        tt_frame.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(tt_frame, text="Upcoming Classes", text_color=COLORS["gold"], font=FONTS["h2"]).pack(anchor="w", padx=12, pady=6)
        cols = ("Day","Time","Subject")
        tv = ttk.Treeview(tt_frame, columns=cols, show="headings", height=5)
        for c in cols:
            tv.heading(c, text=c); tv.column(c, width=120, anchor="w")
        tv.pack(fill="both", expand=True, padx=12, pady=8)
        style_treeview(tv)
        for _id,b,d,t,s,tid in (self.db.next_classes_for(self.user.get('batch','')) or []):
            tv.insert('', 'end', values=(d,t,s))

        # Announcements preview
        ann = ctk.CTkFrame(grid, fg_color=COLORS["panel"], corner_radius=12)
        ann.grid(row=1, column=2, columnspan=2, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(ann, text="Recent Announcements", text_color=COLORS["gold"], font=FONTS["h2"]).pack(anchor="w", padx=12, pady=6)
        cols2 = ("Message","Date")
        tv2 = ttk.Treeview(ann, columns=cols2, show="headings", height=5)
        for c in cols2:
            tv2.heading(c, text=c); tv2.column(c, width=220, anchor="w")
        tv2.pack(fill="both", expand=True, padx=12, pady=8)
        style_treeview(tv2)
        for m,d,_s in self.db.list_messages_for(self.user['username'])[:8]:
            tv2.insert('', 'end', values=(m,d))

        # Performance summary (average marks if any)
        perf = ctk.CTkFrame(grid, fg_color=COLORS["panel"], corner_radius=12)
        perf.grid(row=2, column=0, columnspan=4, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(perf, text="Performance Summary", text_color=COLORS["gold"], font=FONTS["h2"]).pack(anchor="w", padx=12, pady=6)
        try:
            marks = self.db.get_marks(self.user['id'])
            if marks:
                avg = sum(m for _sub,m,_d in marks)/len(marks)
                ctk.CTkLabel(perf, text=f"Average: {avg:.1f}", font=FONTS["h2"], text_color=COLORS["white"]).pack(anchor="w", padx=12, pady=6)
            else:
                ctk.CTkLabel(perf, text="No marks available", font=FONTS["body"], text_color=COLORS["muted"]).pack(anchor="w", padx=12, pady=6)
        except Exception:
            ctk.CTkLabel(perf, text="No marks available", font=FONTS["body"], text_color=COLORS["muted"]).pack(anchor="w", padx=12, pady=6)

        for i in range(4):
            grid.grid_columnconfigure(i, weight=1)

    def _build_profile(self):
        info = "\n".join([
            f"Name: {self.user['name']}",
            f"Class: {self.user['class']}",
            f"Batch: {self.user.get('batch','-')}",
            f"Contact: {self.user['contact']}",
            f"Parent Contact: {self.user.get('parent_contact','-')}",
            f"Student Contact: {self.user.get('student_contact','-')}",
            f"Email: {self.user['email']}",
            f"Username: {self.user['username']}",
        ])
        left = ctk.CTkFrame(self.profile, fg_color=COLORS["panel"], corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(left, text=info, font=FONTS["body"], text_color=COLORS["white"]).pack(pady=12, anchor="w", padx=12)

        right = ctk.CTkFrame(self.profile, fg_color=COLORS["panel"], corner_radius=12)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(right, text="Change Password", font=FONTS["h2"], text_color=COLORS["gold"]).pack(pady=(12,6))
        form = ctk.CTkFrame(right, fg_color="transparent")
        form.pack(pady=4)
        ctk.CTkLabel(form, text="Current:").grid(row=0, column=0, sticky="e")
        self.curr_pw = ctk.CTkEntry(form, show='*', width=200); self.curr_pw.grid(row=0, column=1, padx=6, pady=4)
        ctk.CTkLabel(form, text="New:").grid(row=1, column=0, sticky="e")
        self.new_pw = ctk.CTkEntry(form, show='*', width=200); self.new_pw.grid(row=1, column=1, padx=6, pady=4)
        ctk.CTkLabel(form, text="Confirm:").grid(row=2, column=0, sticky="e")
        self.new_pw2 = ctk.CTkEntry(form, show='*', width=200); self.new_pw2.grid(row=2, column=1, padx=6, pady=4)
        ctk.CTkButton(right, text="Update Password", command=self._change_password, fg_color=COLORS["gold"], text_color=COLORS["bg1"]).pack(pady=8)

    def _change_password(self):
        cur = self.curr_pw.get().strip(); new = self.new_pw.get().strip(); new2 = self.new_pw2.get().strip()
        if not cur or not new or new != new2:
            from tkinter import messagebox
            messagebox.showwarning("Password", "Please enter current password and matching new passwords")
            return
        # verify
        rec = self.db.get_student_by_username(self.user['username'])
        if not rec or rec[7] != cur:
            from tkinter import messagebox
            messagebox.showerror("Password", "Current password incorrect")
            return
        # update
        self.db.update_student(self.user['id'], {
            "name": self.user['name'],
            "age": self.user['age'],
            "class": self.user['class'],
            "contact": self.user['contact'],
            "email": self.user['email'],
            "username": self.user['username'],
            "password": new,
            "batch": self.user.get('batch',''),
            "parent_contact": self.user.get('parent_contact',''),
            "student_contact": self.user.get('student_contact'),
        })
        from tkinter import messagebox
        messagebox.showinfo("Password", "Password updated successfully")
