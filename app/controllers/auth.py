from typing import Optional, Tuple
from app.database import Database


def login(db: Database, user_type: str, username: str, password: str) -> Optional[Tuple]:
    if user_type == "admin":
        rec = db.get_admin(username)
        if rec and rec[1] == password:
            return ("admin", {"username": rec[0]})
        return None
    else:
        rec = db.get_student_by_username(username)
        if rec and rec[7] == password:
            # map to dict for convenience
            return (
                "student",
                {
                    "id": rec[0],
                    "name": rec[1],
                    "age": rec[2],
                    "class": rec[3],
                    "contact": rec[4],
                    "email": rec[5],
                    "username": rec[6],
                    "batch": rec[8],
                    "parent_contact": rec[9],
                    "student_contact": rec[10],
                },
            )
        return None
