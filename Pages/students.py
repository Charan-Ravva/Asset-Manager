# Pages/students.py
import customtkinter as ctk
from tkinter import ttk, messagebox

from datetime import datetime
from zoneinfo import ZoneInfo

def michigan_now():
    return datetime.now(ZoneInfo("America/Detroit")).strftime("%Y-%m-%d %H:%M:%S")

def to_michigan(ts: str | None):
    if not ts:
        return "-"
    return ts  # already Michigan time



from db_conn import get_connection

CARD_BG = "#F5F5F5"
TEXT_DARK = "#222222"


class StudentsPage(ctk.CTkFrame):
    def __init__(self, master):
        """
        master = the right-side content_frame from DashboardPage

        This page shows student checkout HISTORY using checkout + assets:

        Columns:
        - Student Name
        - Student ID
        - Asset Tag ID
        - Checkout Time
        - Return Time (checkin_time, may be NULL)
        - Status (Checked Out / Returned)
        """
        super().__init__(master, fg_color="#FFFFFF")

        # ---------- Top bar ----------
        top_bar = ctk.CTkFrame(self, fg_color="#FFFFFF")
        top_bar.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            top_bar,
            text="Student Checkout History",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(side="left")

        subtitle_label = ctk.CTkLabel(
            top_bar,
            text="  •  All checkouts by students (past and current)",
            text_color="#777777",
            font=ctk.CTkFont(size=13)
        )
        subtitle_label.pack(side="left", pady=(6, 0))

        # Search bar
        self.search_entry = ctk.CTkEntry(
            top_bar,
            placeholder_text="Search by student, ID, or tag...",
            width=260,
            height=32,
        )
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        # ---------- Table container ----------
        table_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill="both", expand=True)

        # ---------- Treeview styling ----------
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Students.Treeview",
            background=CARD_BG,
            fieldbackground=CARD_BG,
            foreground=TEXT_DARK,
            rowheight=26,
            borderwidth=1,
            relief="solid"
        )
        style.configure(
            "Students.Treeview.Heading",
            background="#EEEEEE",
            foreground="#444444",
            relief="raised",
            borderwidth=1,
            font=("Inter", 12, "bold")
        )
        style.map(
            "Students.Treeview",
            background=[("selected", "#D6E4FF")],
            foreground=[("selected", "#000000")]
        )

        # Columns: Student | Student ID | Asset Tag ID | Checkout Time | Return Time | Status
        columns = (
            "student_name",
            "student_id",
            "asset_tag",
            "checkout_time",
            "return_time",
            "status",
        )

        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=12,
            style="Students.Treeview"
        )

        # ----- Headings -----
        self.tree.heading("student_name", text="Student")
        self.tree.heading("student_id", text="Student ID")
        self.tree.heading("asset_tag", text="Asset Tag ID")
        self.tree.heading("checkout_time", text="Checkout Time")
        self.tree.heading("return_time", text="Return Time")
        self.tree.heading("status", text="Status")

        # ----- Column sizes / alignment -----
        self.tree.column("student_name", width=200, anchor="center")
        self.tree.column("student_id", width=110, anchor="center")
        self.tree.column("asset_tag", width=110, anchor="center")
        self.tree.column("checkout_time", width=170, anchor="center")
        self.tree.column("return_time", width=170, anchor="center")
        self.tree.column("status", width=90, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(
            tree_container,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        # Info label below table
        self.info_label = ctk.CTkLabel(
            table_frame,
            text="No history yet.",
            text_color="#777777",
            font=ctk.CTkFont(size=11),
            anchor="w",
            justify="left"
        )
        self.info_label.pack(anchor="w", pady=(6, 0))

        # Load initial data
        self.load_students()

    # ---------- Search handler ----------
    def _on_search_changed(self, event=None):
        query = self.search_entry.get().strip()
        self.load_students(query=query)

    # ---------- Load data from DB ----------
    def load_students(self, query: str = ""):
        """
        Loads checkout history with student + asset details:

        | Student | Student ID | Asset Tag ID | Checkout Time | Return Time | Status |
        from:
        - checkout (student_name, student_id, checkout_time, checkin_time, status)
        - assets (asset_tag_id)
        """
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            conn = get_connection()
            c = conn.cursor()

            sql = """
                SELECT
                    COALESCE(NULLIF(TRIM(co.student_name), ''), 'Unknown') AS s_name,
                    COALESCE(NULLIF(TRIM(co.student_id), ''), '-') AS s_id,
                    COALESCE(NULLIF(TRIM(a.asset_tag_id), ''), '-') AS tag_id,
                    co.checkout_time,
                    co.checkin_time,
                    co.status
                FROM checkout AS co
                JOIN assets AS a
                    ON co.asset_id = a.id
                WHERE 1=1
            """
            params = []

            if query:
                sql += """
                    AND (
                        co.student_name LIKE ?
                        OR co.student_id LIKE ?
                        OR a.asset_tag_id LIKE ?
                    )
                """
                q = f"%{query}%"
                params.extend([q, q, q])

            sql += """
                ORDER BY co.checkout_time DESC
            """

            c.execute(sql, params)
            rows = c.fetchall()
            conn.close()

            if not rows:
                if query:
                    self.info_label.configure(
                        text="No records matched your search."
                    )
                else:
                    self.info_label.configure(
                        text="No student checkouts yet. History will appear here after check-outs."
                    )
            else:
                self.info_label.configure(
                    text=f"{len(rows)} record(s) found."
                )

            for r in rows:
                s_name, s_id, tag_id, checkout_time, return_time, status = r

                # Display "-" if return_time is NULL
                checkout_time = to_michigan(checkout_time)
                display_return = to_michigan(return_time)


                self.tree.insert(
                    "",
                    "end",
                    values=(
                        s_name,
                        s_id,
                        tag_id,
                        checkout_time,
                        display_return,
                        status,
                    )
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load student history.\n\n{e}")
