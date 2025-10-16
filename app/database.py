import os
import sqlite3
from typing import Optional, List, Tuple, Any, Dict

DB_PATH = os.path.join("data", "app.db")


class Database:
    def __init__(self, path: str = DB_PATH):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def connect(self):
        return sqlite3.connect(self.path)

    def _column_exists(self, cur, table: str, column: str) -> bool:
        cur.execute(f"PRAGMA table_info({table})")
        return any(row[1] == column for row in cur.fetchall())

    def init_db(self):
        with self.connect() as con:
            cur = con.cursor()
            # core tables
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS Admin (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS Students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    age INTEGER,
                    class TEXT,
                    contact TEXT,
                    email TEXT,
                    username TEXT UNIQUE,
                    password TEXT,
                    batch TEXT,
                    parent_contact TEXT DEFAULT '' NOT NULL,
                    student_contact TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS Batches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    subject TEXT,
                    time TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS Attendance (
                    student_id INTEGER,
                    date TEXT,
                    status TEXT,
                    PRIMARY KEY (student_id, date)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS Fees (
                    student_id INTEGER PRIMARY KEY,
                    amount_paid REAL DEFAULT 0,
                    pending_amount REAL DEFAULT 0,
                    last_payment_date TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS Performance (
                    student_id INTEGER,
                    subject TEXT,
                    marks REAL,
                    date TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS Messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_text TEXT,
                    date_sent TEXT,
                    sender_type TEXT,
                    recipient TEXT
                )
                """
            )

            # Teachers
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS Teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    subjects TEXT,
                    availability TEXT
                )
                """
            )
            # Timetable
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS Timetable (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch TEXT,
                    day TEXT,
                    time_slot TEXT,
                    subject TEXT,
                    teacher_id INTEGER
                )
                """
            )
            # Homework (assigned per batch)
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS Homework (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch TEXT,
                    title TEXT,
                    due_date TEXT,
                    description TEXT,
                    posted_at TEXT,
                    is_optional INTEGER DEFAULT 0
                )
                """
            )

            # Migrations for existing DBs
            try:
                if not self._column_exists(cur, "Students", "parent_contact"):
                    cur.execute("ALTER TABLE Students ADD COLUMN parent_contact TEXT DEFAULT '' NOT NULL")
                if not self._column_exists(cur, "Students", "student_contact"):
                    cur.execute("ALTER TABLE Students ADD COLUMN student_contact TEXT")
            except Exception:
                pass
            try:
                if not self._column_exists(cur, "Batches", "time"):
                    cur.execute("ALTER TABLE Batches ADD COLUMN time TEXT")
            except Exception:
                pass

            # default admin
            cur.execute("INSERT OR IGNORE INTO Admin(username, password) VALUES(?, ?)", ("admin", "admin1"))
            con.commit()

    # --- Admin / Student Auth ---
    def get_admin(self, username: str) -> Optional[Tuple]:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT username, password FROM Admin WHERE username=?", (username,))
            return cur.fetchone()

    def get_student_by_username(self, username: str) -> Optional[Tuple]:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                SELECT id, name, age, class, contact, email, username, password, batch, parent_contact, student_contact
                FROM Students WHERE username=?
                """,
                (username,),
            )
            return cur.fetchone()

    def get_student_by_id(self, sid: int) -> Optional[Tuple]:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                SELECT id, name, age, class, contact, email, username, batch, parent_contact, student_contact
                FROM Students WHERE id=?
                """,
                (sid,),
            )
            return cur.fetchone()

    def search_students_by_id_prefix(self, prefix: str) -> List[Tuple]:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                SELECT id, name, class, username, batch
                FROM Students
                WHERE CAST(id AS TEXT) LIKE ?
                ORDER BY id
                """,
                (f"{prefix}%",),
            )
            return cur.fetchall()

    # --- Students ---
    def add_student(self, data: Dict[str, Any]) -> int:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO Students(name, age, class, contact, email, username, password, batch, parent_contact, student_contact)
                VALUES(?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    data.get("name"), data.get("age"), data.get("class"),
                    data.get("contact"), data.get("email"), data.get("username"),
                    data.get("password"), data.get("batch"), data.get("parent_contact", ""),
                    data.get("student_contact"),
                ),
            )
            sid = cur.lastrowid
            # Ensure fees row exists
            cur.execute(
                "INSERT OR IGNORE INTO Fees(student_id, amount_paid, pending_amount, last_payment_date) VALUES(?,?,?,?)",
                (sid, 0, 0, None),
            )
            con.commit()
            return sid

    def update_student(self, sid: int, data: Dict[str, Any]):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                UPDATE Students SET name=?, age=?, class=?, contact=?, email=?, username=?, password=?, batch=?, parent_contact=?, student_contact=?
                WHERE id=?
                """,
                (
                    data.get("name"), data.get("age"), data.get("class"), data.get("contact"),
                    data.get("email"), data.get("username"), data.get("password"), data.get("batch"),
                    data.get("parent_contact", ""), data.get("student_contact"), sid,
                ),
            )
            con.commit()

    def delete_student(self, sid: int):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("DELETE FROM Students WHERE id=?", (sid,))
            cur.execute("DELETE FROM Fees WHERE student_id=?", (sid,))
            cur.execute("DELETE FROM Attendance WHERE student_id=?", (sid,))
            cur.execute("DELETE FROM Performance WHERE student_id=?", (sid,))
            con.commit()

    def list_students(self, search: str = "") -> List[Tuple]:
        with self.connect() as con:
            cur = con.cursor()
            if search:
                like = f"%{search}%"
                cur.execute(
                    """
                    SELECT id, name, age, class, contact, email, username, batch, parent_contact, student_contact
                    FROM Students
                    WHERE name LIKE ? OR class LIKE ? OR batch LIKE ?
                    ORDER BY name
                    """,
                    (like, like, like),
                )
            else:
                cur.execute(
                    "SELECT id, name, age, class, contact, email, username, batch, parent_contact, student_contact FROM Students ORDER BY name"
                )
            return cur.fetchall()

    def list_students_full_order(self, search: str = "") -> List[Tuple]:
        """Return rows ordered as: id, username, password, name, age, class, contact, email, batch, parent_contact, student_contact"""
        with self.connect() as con:
            cur = con.cursor()
            if search:
                like = f"%{search}%"
                cur.execute(
                    """
                    SELECT id, username, password, name, age, class, contact, email, batch, parent_contact, student_contact
                    FROM Students
                    WHERE username LIKE ? OR name LIKE ? OR class LIKE ? OR batch LIKE ?
                    ORDER BY name
                    """,
                    (like, like, like, like),
                )
            else:
                cur.execute(
                    "SELECT id, username, password, name, age, class, contact, email, batch, parent_contact, student_contact FROM Students ORDER BY name"
                )
            return cur.fetchall()

    # --- Batches ---
    def upsert_batch(self, name: str, subject: str = "", time: str = ""):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO Batches(name, subject, time)
                VALUES(?,?,?)
                ON CONFLICT(name) DO UPDATE SET subject=excluded.subject, time=excluded.time
                """,
                (name, subject, time),
            )
            con.commit()

    def delete_batch(self, name: str):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("DELETE FROM Batches WHERE name=?", (name,))
            con.commit()

    def list_batches(self) -> List[Tuple]:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT name, subject, time FROM Batches ORDER BY name")
            return cur.fetchall()

    # --- Attendance ---
    def mark_attendance(self, student_id: int, date: str, status: str):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                "INSERT OR REPLACE INTO Attendance(student_id, date, status) VALUES(?,?,?)",
                (student_id, date, status),
            )
            con.commit()

    def get_attendance(self, student_id: int) -> List[Tuple]:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT date, status FROM Attendance WHERE student_id=? ORDER BY date DESC",
                (student_id,),
            )
            return cur.fetchall()

    def attendance_percentage(self, student_id: Optional[int] = None) -> float:
        with self.connect() as con:
            cur = con.cursor()
            if student_id is None:
                cur.execute("SELECT COUNT(*) FROM Attendance")
                total = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM Attendance WHERE status='Present'")
                present = cur.fetchone()[0]
            else:
                cur.execute("SELECT COUNT(*) FROM Attendance WHERE student_id=?", (student_id,))
                total = cur.fetchone()[0]
                cur.execute(
                    "SELECT COUNT(*) FROM Attendance WHERE student_id=? AND status='Present'",
                    (student_id,),
                )
                present = cur.fetchone()[0]
            return round((present / total) * 100, 2) if total else 0.0

    # --- Fees ---
    def record_payment(self, student_id: int, amount_paid: float, pending_amount: float, date: str):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                """
                INSERT INTO Fees(student_id, amount_paid, pending_amount, last_payment_date)
                VALUES(?,?,?,?)
                ON CONFLICT(student_id) DO UPDATE SET
                    amount_paid=excluded.amount_paid,
                    pending_amount=excluded.pending_amount,
                    last_payment_date=excluded.last_payment_date
                """,
                (student_id, amount_paid, pending_amount, date),
            )
            con.commit()

    def get_fees(self, student_id: Optional[int] = None):
        with self.connect() as con:
            cur = con.cursor()
            if student_id is None:
                cur.execute("SELECT SUM(amount_paid) FROM Fees")
                total = cur.fetchone()[0] or 0
                return total
            else:
                cur.execute(
                    "SELECT amount_paid, pending_amount, last_payment_date FROM Fees WHERE student_id=?",
                    (student_id,),
                )
                return cur.fetchone()

    # --- Teachers ---
    def add_teacher(self, name: str, subjects: str = "", availability: str = "") -> int:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO Teachers(name, subjects, availability) VALUES(?,?,?)", (name, subjects, availability))
            con.commit()
            return cur.lastrowid

    def list_teachers(self):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id, name, subjects, availability FROM Teachers ORDER BY name")
            return cur.fetchall()

    def delete_teacher(self, tid: int):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("DELETE FROM Teachers WHERE id=?", (tid,))
            con.commit()

    # --- Timetable ---
    def upsert_timetable_entry(self, batch: str, day: str, time_slot: str, subject: str, teacher_id: int = None):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO Timetable(batch, day, time_slot, subject, teacher_id) VALUES(?,?,?,?,?)",
                (batch, day, time_slot, subject, teacher_id),
            )
            con.commit()

    def delete_timetable_entry(self, entry_id: int):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("DELETE FROM Timetable WHERE id=?", (entry_id,))
            con.commit()

    def clear_timetable_for_batch(self, batch: str):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("DELETE FROM Timetable WHERE batch=?", (batch,))
            con.commit()

    def list_timetable(self, batch: str = None):
        with self.connect() as con:
            cur = con.cursor()
            if batch:
                cur.execute("SELECT id, batch, day, time_slot, subject, teacher_id FROM Timetable WHERE batch=? ORDER BY day, time_slot", (batch,))
            else:
                cur.execute("SELECT id, batch, day, time_slot, subject, teacher_id FROM Timetable ORDER BY batch, day, time_slot")
            return cur.fetchall()

    def next_classes_for(self, batch: str, limit: int = 5):
        import datetime as _dt
        days_order = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        today_idx = _dt.datetime.today().weekday()  # 0=Mon
        all_rows = self.list_timetable(batch)
        # Simple ordering by day index then time_slot lexicographically
        def day_idx(d):
            d3 = d[:3].title()
            return days_order.index(d3) if d3 in days_order else 7
        all_rows.sort(key=lambda r: (day_idx(r[2]), r[3]))
        return all_rows[:limit]

    # --- Homework ---
    def list_homework_for(self, batch: str):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute("SELECT id, title, due_date, description, posted_at, is_optional FROM Homework WHERE batch=? ORDER BY due_date", (batch,))
            return cur.fetchall()

    # --- Messages ---
    def send_message(self, text: str, date: str, sender_type: str, recipient: str = "all"):
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO Messages(message_text, date_sent, sender_type, recipient) VALUES(?,?,?,?)",
                (text, date, sender_type, recipient),
            )
            con.commit()

    def list_messages_for(self, recipient: str) -> List[Tuple]:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT message_text, date_sent, sender_type FROM Messages WHERE recipient=? OR recipient='all' ORDER BY date_sent DESC",
                (recipient,),
            )
            return cur.fetchall()

    def list_all_messages(self) -> List[Tuple]:
        with self.connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT message_text, date_sent, sender_type, recipient FROM Messages ORDER BY date_sent DESC"
            )
            return cur.fetchall()
