import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_NAME = "database.db"


# Database setup
def init_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT
    )
    """)

    # Check if date_added exists
    cursor.execute("PRAGMA table_info(records)")
    columns = [column[1] for column in cursor.fetchall()]

    if "date_added" not in columns:
        cursor.execute(
            "ALTER TABLE records ADD COLUMN date_added TEXT"
        )

    conn.commit()
    conn.close()


init_database()


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Tracker Database")
        self.geometry("800x500")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (InputPage, DatabasePage):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(InputPage)

    def show_frame(self, page):
        frame = self.frames[page]

        if page == DatabasePage:
            frame.load_data()

        frame.tkraise()


class InputPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(
            self,
            text="Tracker",
            font=("Arial", 20)
        ).pack(pady=20)

        tk.Label(self, text="Name").pack()

        self.name_entry = tk.Entry(self, width=40)
        self.name_entry.pack()

        tk.Label(
            self,
            text="Feedback"
        ).pack(pady=(10, 0))

        self.feedback_entry = tk.Entry(self, width=40)
        self.feedback_entry.pack()

        tk.Button(
            self,
            text="Track",
            command=self.save_record
        ).pack(pady=15)

        tk.Button(
            self,
            text="View Database",
            command=lambda: parent.show_frame(DatabasePage)
        ).pack()

    def save_record(self):
        name = self.name_entry.get().strip()
        feedback = self.feedback_entry.get().strip()

        if not name or not feedback:
            messagebox.showerror(
                "Error",
                "Please complete all fields."
            )
            return

        date_added = datetime.now().strftime(
            "%d/%m/%Y %H:%M"
        )

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO records
                (name, email, date_added)
                VALUES (?, ?, ?)
                """,
                (name, feedback, date_added)
            )

            conn.commit()
            conn.close()

            self.name_entry.delete(0, tk.END)
            self.feedback_entry.delete(0, tk.END)

            messagebox.showinfo(
                "Success",
                "Record saved successfully."
            )

        except Exception as e:
            messagebox.showerror(
                "Database Error",
                str(e)
            )


class DatabasePage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(
            self,
            text="Database Records",
            font=("Arial", 20)
        ).pack(pady=20)

        self.tree = ttk.Treeview(
            self,
            columns=(
                "Name",
                "Feedback",
                "Date"
            ),
            show="headings"
        )

        self.tree.heading("Name", text="Name")
        self.tree.heading("Feedback", text="Feedback")
        self.tree.heading("Date", text="Date Added")

        self.tree.column("Name", width=150)
        self.tree.column("Feedback", width=450)
        self.tree.column("Date", width=150)

        self.tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # Duplicate names will be highlighted red
        self.tree.tag_configure(
            "duplicate",
            background="#ff0000"
        )

        tk.Button(
            self,
            text="Back",
            command=lambda: parent.show_frame(InputPage)
        ).pack(pady=10)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    name,
                    email,
                    COALESCE(date_added, '')
                FROM records
                ORDER BY id DESC
            """)

            records = cursor.fetchall()
            conn.close()

            # Count occurrences of each name
            name_counts = {}

            for record in records:
                name = record[0].strip().lower()

                if name:
                    name_counts[name] = name_counts.get(name, 0) + 1

            # Insert rows and highlight duplicates
            for record in records:
                name = record[0].strip().lower()

                if name_counts.get(name, 0) > 1:
                    self.tree.insert(
                        "",
                        tk.END,
                        values=record,
                        tags=("duplicate",)
                    )
                else:
                    self.tree.insert(
                        "",
                        tk.END,
                        values=record
                    )

        except Exception as e:
            messagebox.showerror(
                "Database Error",
                str(e)
            )


if __name__ == "__main__":
    app = App()
    app.mainloop()