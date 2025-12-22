import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox

from Pages.students import to_michigan
from db_conn import get_connection

from datetime import datetime
from zoneinfo import ZoneInfo

def michigan_now():
    return datetime.now(ZoneInfo("America/Detroit")).strftime("%Y-%m-%d %H:%M:%S")


TEXT_DARK = "#222222"
CARD_BG = "#F5F5F5"


class CheckInPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#FFFFFF")

        # checkbox state
        self.header_checked = False
        self.checked_rows = set()

        # ---------- TOP BAR ----------
        top_bar = ctk.CTkFrame(self, fg_color="#FFFFFF")
        top_bar.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            top_bar,
            text="Check In",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_DARK,
        ).pack(side="left")

        ctk.CTkLabel(
            top_bar,
            text=" • Return equipment to inventory",
            font=ctk.CTkFont(size=13),
            text_color="#777777",
        ).pack(side="left", padx=(6, 0))

        # ---------- SEARCH + BUTTON ----------
        action_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        action_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            action_frame,
            placeholder_text="Search by asset or student...",
            width=260,
            height=32,
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        ctk.CTkButton(
            action_frame,
            text="Confirm Check In",
            width=160,
            height=36,
            fg_color="#6A0032",
            hover_color="#4C0025",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.confirm_checkin,
        ).pack(side="right")

        # ---------- MAIN TABLE ----------
        main_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")

        # Treeview style
        style.configure(
            "CheckIn.Treeview",
            background=CARD_BG,
            fieldbackground=CARD_BG,
            foreground=TEXT_DARK,
            font=("Inter", 12),
            rowheight=38,
            borderwidth=0,
            relief="flat",
        )
        style.configure(
            "CheckIn.Treeview.Heading",
            background="#EEEEEE",
            foreground="#444444",
            font=("Inter", 11, "bold"),
            relief="solid",
            borderwidth=1,
        )
        style.map(
            "CheckIn.Treeview",
            background=[("selected", "#4E6B85")],
            foreground=[("selected", "white")],
        )

        # ---------- LOAD CHECKBOX IMAGES (SAME AS CHECK OUT) ----------
        self.img_unchecked, self.img_checked = self._load_checkbox_images()

        # Columns (checkbox is #0)
        self.columns = (
            "asset_name",
            "asset_tag",
            "student_name",
            "student_id",
            "checkout_time",
        )

        self.tree = ttk.Treeview(
            tree_container,
            columns=self.columns,
            show="tree headings",
            style="CheckIn.Treeview",
            selectmode="none",   # prevents checkbox shift
        )

        # Checkbox column
        self.tree.heading("#0", image=self.img_unchecked, anchor="center")
        self.tree.column(
            "#0",
            width=45,
            minwidth=44,
            stretch=False,
            anchor="center",
        )

        # Headings
        self.tree.heading("asset_name", text="Asset Name")
        self.tree.heading("asset_tag", text="Tag ID")
        self.tree.heading("student_name", text="Student Name")
        self.tree.heading("student_id", text="Student ID")
        self.tree.heading("checkout_time", text="Checked Out At")

        self.tree.column("asset_name", width=180, anchor="center")
        self.tree.column("asset_tag", width=100, anchor="center")
        self.tree.column("student_name", width=180, anchor="center")
        self.tree.column("student_id", width=120, anchor="center")
        self.tree.column("checkout_time", width=180, anchor="center")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.tree.bind("<ButtonRelease-1>", self._on_tree_click)

        # ---------- INFO ----------
        self.info_label = ctk.CTkLabel(
            self,
            text="0 asset(s) currently checked out.",
            text_color="#777777",
            font=ctk.CTkFont(size=11),
        )
        self.info_label.pack(anchor="w", padx=20, pady=(6, 0))

        self.load_checked_out_items()

    # ---------- IMAGE LOADER ----------
    def _load_checkbox_images(self):
        unchecked = tk.PhotoImage(file="Images/unchecked.png")
        checked = tk.PhotoImage(file="Images/checkbox.png")

        max_size = 22

        def scale(img):
            w, h = img.width(), img.height()
            if w <= max_size and h <= max_size:
                return img
            factor = max(int(w / max_size), int(h / max_size), 1)
            return img.subsample(factor, factor)

        return scale(unchecked), scale(checked)

    # ---------- SEARCH ----------
    def _on_search_changed(self, event=None):
        self.load_checked_out_items(self.search_entry.get().strip())

    # ---------- LOAD DATA ----------
    def load_checked_out_items(self, query=""):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.header_checked = False
        self.checked_rows.clear()
        self.tree.heading("#0", image=self.img_unchecked)

        conn = get_connection()
        c = conn.cursor()

        sql = """
            SELECT co.id, a.asset_name, a.asset_tag_id,
                   co.student_name, co.student_id, co.checkout_time
            FROM checkout co
            JOIN assets a ON co.asset_id = a.id
            WHERE co.status = 'Checked Out'
        """

        params = []
        if query:
            sql += """ AND (
                a.asset_name LIKE ? OR
                a.asset_tag_id LIKE ? OR
                co.student_name LIKE ? OR
                co.student_id LIKE ?
            )"""
            q = f"%{query}%"
            params.extend([q, q, q, q])

        sql += " ORDER BY co.checkout_time DESC"
        c.execute(sql, params)
        rows = c.fetchall()
        conn.close()

        self.info_label.configure(text=f"{len(rows)} asset(s) currently checked out.")

        for r in rows:
            checkout_id, asset, tag, sname, sid, time = r
            self.tree.insert(
                "",
                "end",
                iid=str(checkout_id),
                text="",
                image=self.img_unchecked,
                values=(asset, tag, sname, sid, to_michigan(time)),
            )

    # ---------- CHECKBOX HANDLING ----------
    def _on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        column = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)

    # Header checkbox
        if region == "heading" and column == "#0":
            self._toggle_header_checkbox()
            return "break"

    # Row checkbox
        if region in ("tree", "cell") and column == "#0" and row_id:
            self._toggle_row_checkbox(row_id)
            return "break"
 

    def _toggle_row_checkbox(self, row_id):
        if row_id in self.checked_rows:
            self._set_row_checked(row_id, False)
        else:
            self._set_row_checked(row_id, True)

        all_ids = list(self.tree.get_children())
        if all_ids and all(rid in self.checked_rows for rid in all_ids):
            self.header_checked = True
            self.tree.heading("#0", image=self.img_checked)
        else:
            self.header_checked = False
            self.tree.heading("#0", image=self.img_unchecked)

    def _set_row_checked(self, row_id, checked):
        if checked:
            self.tree.item(row_id, image=self.img_checked)
            self.checked_rows.add(row_id)
        else:
            self.tree.item(row_id, image=self.img_unchecked)
            self.checked_rows.discard(row_id)

    def _toggle_header_checkbox(self):
        self.header_checked = not self.header_checked
        header_img = self.img_checked if self.header_checked else self.img_unchecked
        self.tree.heading("#0", image=header_img)

        for iid in self.tree.get_children():
            self._set_row_checked(iid, self.header_checked)

    # ---------- CONFIRM ----------
    def confirm_checkin(self):
        if not self.checked_rows:
            messagebox.showerror("Error", "Select asset(s) to check in.")
            return

        conn = get_connection()
        c = conn.cursor()

        for cid in self.checked_rows:
            c.execute("SELECT asset_id FROM checkout WHERE id=?", (cid,))
            asset_id = c.fetchone()[0]

            c.execute("UPDATE assets SET status='Available' WHERE id=?", (asset_id,))
            checkin_time = michigan_now()

            c.execute(
            """
            UPDATE checkout
            SET status='Returned', checkin_time=?
            WHERE id=?
            """,
            (checkin_time, cid),
        )


        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Asset(s) checked in successfully.")
        self.load_checked_out_items()
