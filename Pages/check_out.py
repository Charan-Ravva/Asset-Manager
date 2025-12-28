import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from utils.path_helper import resource_path


from datetime import datetime
from zoneinfo import ZoneInfo

def michigan_now():
    return datetime.now(ZoneInfo("America/Detroit")).strftime("%Y-%m-%d %H:%M:%S")
    
from db_conn import get_connection

TEXT_DARK = "#222222"
CARD_BG = "#F5F5F5"


class CheckOutPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#FFFFFF")

        # header checkbox state ("select all")
        self.header_checked = False
        # track which asset rows are checked (store iids as strings)
        self.checked_rows = set()

        # ---------- Top bar ----------
        top_bar = ctk.CTkFrame(self, fg_color="#FFFFFF")
        top_bar.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            top_bar,
            text="Check Out",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title_label.pack(side="left")

        subtitle_label = ctk.CTkLabel(
            top_bar,
            text="  •  Issue equipment to students",
            text_color="#777777",
            font=ctk.CTkFont(size=13),
        )
        subtitle_label.pack(side="left", pady=(6, 0))

        # ---------- Filters ----------
        filter_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        filter_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search by asset name or tag...",
            width=260,
            height=32,
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search_changed)

        self.status_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Available only", "All statuses"],
            width=150,
            height=32,
            command=self._on_status_changed,
        )
        self.status_filter.set("Available only")
        self.status_filter.pack(side="left")

        # ---------- Main split (left table + right details) ----------
        main_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # GRID inside main_frame so left & right get fixed proportions
        main_frame.grid_columnconfigure(0, weight=1)                 # table expands
        main_frame.grid_columnconfigure(1, weight=0, minsize=240)    # student panel narrower
        main_frame.grid_rowconfigure(0, weight=1)

        # ----- Left: assets table -----
        left_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tree_container = ttk.Frame(left_frame)
        tree_container.pack(fill="both", expand=True)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Checkout.Treeview",
            background=CARD_BG,
            fieldbackground=CARD_BG,
            foreground=TEXT_DARK,
            font=("Inter", 12),
            rowheight=36,
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "Checkout.Treeview.Heading",
            background="#EEEEEE",
            foreground="#444444",
            font=("Inter", 11, "bold"),
            relief="raised",
            borderwidth=1,
        )

        # Data columns (checkbox lives in tree column #0)
        self.columns = ("name", "tag", "location", "category", "status")

        # ---- load and SCALE checkbox icons ----
        self.img_unchecked, self.img_checked = self._load_checkbox_images()

        self.tree = ttk.Treeview(
            tree_container,
            columns=self.columns,
            show="tree headings",
            height=14,
            style="Checkout.Treeview",
        )

        # Tree / checkbox column
        self.tree.heading(
            "#0",
            image=self.img_unchecked,
             anchor="center"
            )
        self.tree.column("#0", width=45, anchor="center", stretch=False)

        # Headings for data columns
        self.tree.heading("name", text="Asset Name")
        self.tree.heading("tag", text="Asset Tag ID")
        self.tree.heading("location", text="Location")
        self.tree.heading("category", text="Category")
        self.tree.heading("status", text="Status")

        for col in self.columns:
            width = 120
            if col == "name":
                width = 180
            self.tree.column(col, width=width, anchor="center")

        vb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vb.grid(row=0, column=1, sticky="ns")
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.tree.bind("<Button-1>", self._on_tree_click)

        self.info_label = ctk.CTkLabel(
            left_frame,
            text="Select asset(s) to check out.",
            text_color="#777777",
            font=ctk.CTkFont(size=11),
            anchor="w",
            justify="left",
        )
        self.info_label.pack(anchor="w", pady=(6, 0))

        # ----- Right: student details (card with border) -----
        right_outer = ctk.CTkFrame(
            main_frame,
            fg_color="#FFFFFF",
            width=240
        )
        right_outer.grid(row=0, column=1, sticky="ns", padx=(10, 0), pady=2)
        # keep the panel at this width (so fields don't get squashed)
        right_outer.grid_propagate(False)

        right_frame = ctk.CTkFrame(
            right_outer,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color="#D0D0D0",
        )
        right_frame.pack(fill="y", padx=2, pady=2)

        header = ctk.CTkLabel(
            right_frame,
            text="Student Details",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_DARK,
        )
        header.pack(anchor="w", padx=12, pady=(12, 4))

        self.student_name_entry = ctk.CTkEntry(
            right_frame,
            width=220,
            height=32,
            placeholder_text="Student Name *",
        )
        self.student_name_entry.pack(padx=12, pady=(4, 6))
        self.student_name_entry.bind("<KeyRelease>", self._autocomplete_student)
        self.student_name_entry.bind("<FocusOut>", self._hide_suggestions)

        self.student_id_entry = ctk.CTkEntry(
            right_frame,
            width=220,
            height=32,
            placeholder_text="Student ID *",
        )
        self.student_id_entry.pack(padx=12, pady=(4, 6))

        # These two fields are still shown in the UI,
        # but they are no longer stored in the DB.
        self.phone_entry = ctk.CTkEntry(
            right_frame,
            width=220,
            height=32,
            placeholder_text="Phone Number (optional)",
        )
        self.phone_entry.pack(padx=12, pady=(4, 6))

        notes_label = ctk.CTkLabel(
            right_frame,
            text="Notes",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT_DARK,
        )
        notes_label.pack(anchor="w", padx=12, pady=(8, 0))

        self.notes_entry = ctk.CTkTextbox(
            right_frame,
            width=220,
            height=80,
            border_width=1,
            border_color="#D0D0D0",
            corner_radius=8,
        )
        self.notes_entry.pack(padx=12, pady=(4, 12))

        checkout_btn = ctk.CTkButton(
            right_frame,
            text="Confirm Check Out",
            width=220,
            height=36,
            fg_color="#6A0032",
            hover_color="#4C0025",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.confirm_checkout,
        )
        checkout_btn.pack(padx=12, pady=(8, 16))

        # initial data
        self.load_assets()
        self.load_known_students()

    # ---------- helper to load & scale checkbox icons ----------
    def _load_checkbox_images(self):
        """Load checkbox PNGs and shrink them if they are large."""
        unchecked_orig = tk.PhotoImage(
            file=resource_path("Images/unchecked.png")
        )
        checked_orig = tk.PhotoImage(
            file=resource_path("Images/checkbox.png")
        )

        max_size = 22  # target max width/height in pixels

        def scale(img):
            w, h = img.width(), img.height()
            if w <= max_size and h <= max_size:
                return img
            factor = max(int(w / max_size), int(h / max_size), 1)
            return img.subsample(factor, factor)

        img_unchecked = scale(unchecked_orig)
        img_checked = scale(checked_orig)

        return img_unchecked, img_checked

    # ---------- Filter helpers ----------
    def _filter_assets(self):
        query = self.search_entry.get().strip()
        available_only = (self.status_filter.get() == "Available only")
        self.load_assets(query=query, available_only=available_only)

    def _on_search_changed(self, event=None):
        self._filter_assets()

    def _on_status_changed(self, value):
        self._filter_assets()

    # ---------- Load assets ----------
    def load_assets(self, query: str = "", available_only: bool = True):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.header_checked = False
        self.checked_rows.clear()
        self.tree.heading("#0", image=self.img_unchecked, text="")

        try:
            conn = get_connection()
            c = conn.cursor()

            sql = """
                SELECT id, asset_name, asset_tag_id, location, category, status
                FROM assets
            """
            params = []
            where_clauses = []

            if available_only:
                where_clauses.append("status = 'Available'")
            if query:
                where_clauses.append("(asset_name LIKE ? OR asset_tag_id LIKE ?)")
                q = f"%{query}%"
                params.extend([q, q])

            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

            sql += " ORDER BY asset_name"

            c.execute(sql, params)
            rows = c.fetchall()
            conn.close()

            if not rows:
                self.info_label.configure(text="No matching assets found.")
            else:
                self.info_label.configure(
                    text=f"{len(rows)} asset(s) available to check out."
                )

            for r in rows:
                asset_id, name, tag, location, category, status = r
                iid = str(asset_id)
                self.tree.insert(
                    "",
                    "end",
                    iid=iid,
                    text="",
                    image=self.img_unchecked,
                    values=(name, tag, location, category, status),
                )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load assets.\n\n{e}")

    # ---------- Student autocomplete ----------
    def load_known_students(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT DISTINCT student_name
                FROM checkout
                WHERE student_name IS NOT NULL AND TRIM(student_name) <> ''
                ORDER BY student_name COLLATE NOCASE
            """)
            self.known_students = [row[0] for row in c.fetchall()]
            conn.close()
        except Exception as e:
            print("Failed to load student names:", e)
            self.known_students = []

    def _on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        column = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)

        if region == "heading" and column == "#0":
            self._toggle_header_checkbox()
            return

        if row_id and column == "#0" and region in ("tree", "cell"):
            self._toggle_row_checkbox(row_id)

    def _toggle_row_checkbox(self, row_id: str):
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


    def _set_row_checked(self, row_id: str, checked: bool):
        if checked:
            self.tree.item(row_id, image=self.img_checked)
            self.checked_rows.add(row_id)
        else:
            self.tree.item(row_id, image=self.img_unchecked)
            self.checked_rows.discard(row_id)

    def _toggle_header_checkbox(self):
        self.header_checked = not self.header_checked

        header_img = (
        self.img_checked if self.header_checked else self.img_unchecked
    )

        self.tree.heading("#0", image=header_img)

        for iid in self.tree.get_children():
         self._set_row_checked(iid, self.header_checked)


    # ----- autocomplete helpers -----
    def _autocomplete_student(self, event=None):
        text = self.student_name_entry.get().strip().lower()
        self._hide_suggestions()
        if not text:
            return
        matches = [n for n in self.known_students if text in n.lower()]
        if not matches:
            return
        self.student_name_entry.update_idletasks()
        x = self.student_name_entry.winfo_x()
        y = (
            self.student_name_entry.winfo_y()
            + self.student_name_entry.winfo_height()
            + 2
        )
        self.suggestion_frame = ctk.CTkFrame(
            self.student_name_entry.master,
            fg_color="#FFFFFF",
            corner_radius=6,
            border_width=1,
            border_color="#CCCCCC",
        )
        self.suggestion_frame.place(x=x, y=y)

        self.suggestion_listbox = tk.Listbox(
            self.suggestion_frame,
            height=min(5, len(matches)),
            width=28,
            bg="white",
            fg="#222222",
            borderwidth=0,
            highlightthickness=0,
            selectbackground="#6A0032",
            activestyle="none",
        )
        self.suggestion_listbox.pack(fill="both", expand=True)

        for m in matches:
            self.suggestion_listbox.insert("end", m)

        self.suggestion_listbox.bind("<<ListboxSelect>>", self._select_autocomplete)
        self.suggestion_listbox.bind("<Double-Button-1>", self._select_autocomplete)

    def _hide_suggestions(self, event=None):
        if getattr(self, "suggestion_frame", None) is not None:
            self.suggestion_frame.destroy()
            self.suggestion_frame = None
            self.suggestion_listbox = None

    def _select_autocomplete(self, event=None):
        if not getattr(self, "suggestion_listbox", None):
            return
        selection = self.suggestion_listbox.curselection()
        if not selection:
            return
        name = self.suggestion_listbox.get(selection[0])
        self.student_name_entry.delete(0, "end")
        self.student_name_entry.insert(0, name)
        self._hide_suggestions()
        self._autofill_student_details(name)

    def _autofill_student_details(self, name: str):
        """Fill only the student ID from the most recent checkout."""
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT student_id
                FROM checkout
                WHERE student_name = ?
                ORDER BY checkout_time DESC
                LIMIT 1
            """, (name,))
            row = c.fetchone()
            conn.close()
        except Exception as e:
            print("Failed to fetch student details:", e)
            row = None

        # Clear existing values
        self.student_id_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.notes_entry.delete("1.0", "end")

        if row:
            student_id = row[0]
            if student_id:
                self.student_id_entry.insert(0, student_id)

    # ---------- Confirm checkout ----------
    def get_selected_asset_ids(self):
        return [int(iid) for iid in self.checked_rows]

    def confirm_checkout(self):
        asset_ids = self.get_selected_asset_ids()
        student_name = self.student_name_entry.get().strip()
        student_id = self.student_id_entry.get().strip()
        # phone & notes kept local only (not stored in DB)
        # phone = self.phone_entry.get().strip()
        # notes = self.notes_entry.get("1.0", "end").strip()

        if not asset_ids:
            messagebox.showerror("Error", "Select at least one asset to check out.")
            return
        if not student_name or not student_id:
            messagebox.showerror(
                "Error",
                "Student Name and Student ID are required."
            )
            return

        try:
            conn = get_connection()
            c = conn.cursor()
            
            for aid in asset_ids:
                checkout_time = michigan_now()

                # We only insert fields that actually exist in the checkout table.
                c.execute(
                    """
                    INSERT INTO checkout (
                        asset_id, student_name, student_id, checkout_time, status
                    )
                    VALUES (?, ?, ?, ?, 'Checked Out')
                    """,
                    (aid, student_name, student_id, checkout_time),
                )

                c.execute(
                    "UPDATE assets SET status = 'Checked Out' WHERE id = ?",
                    (aid,),
                )

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Asset(s) checked out successfully.")
            self.load_assets()
            self.load_known_students()

            self.student_name_entry.delete(0, "end")
            self.student_id_entry.delete(0, "end")
            self.phone_entry.delete(0, "end")
            self.notes_entry.delete("1.0", "end")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to check out.\n\n{e}")
