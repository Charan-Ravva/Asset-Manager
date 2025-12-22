import customtkinter as ctk
from tkinter import ttk, messagebox
from db_conn import get_connection

TEXT_DARK = "#222222"
CARD_BG = "#F5F5F5"
PRIMARY = "#6A0032"


class StaffPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#FFFFFF")

        # ---------- TOP BAR ----------
        top_bar = ctk.CTkFrame(self, fg_color="#FFFFFF")
        top_bar.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            top_bar,
            text="Staff",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_DARK,
        ).pack(side="left")

        ctk.CTkLabel(
            top_bar,
            text=" • Manage staff accounts",
            font=ctk.CTkFont(size=13),
            text_color="#777777",
        ).pack(side="left", padx=(6, 0))

        ctk.CTkButton(
            top_bar,
            text="+ Add Staff",
            width=120,
            height=34,
            fg_color=PRIMARY,
            hover_color="#4C0025",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.open_add_staff_dialog,
        ).pack(side="right")

        # ---------- TABLE ----------
        main_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Staff.Treeview",
            background=CARD_BG,
            fieldbackground=CARD_BG,
            foreground=TEXT_DARK,
            font=("Inter", 12),
            rowheight=36,
        )
        style.configure(
            "Staff.Treeview.Heading",
            background="#EEEEEE",
            foreground="#444444",
            font=("Inter", 11, "bold"),
        )

        self.tree = ttk.Treeview(
            tree_container,
            columns=("name", "email", "role", "edit", "delete"),
            show="headings",
            style="Staff.Treeview",
            selectmode="none",
        )

        self.tree.heading("name", text="Name")
        self.tree.heading("email", text="Email")
        self.tree.heading("role", text="Role")
        self.tree.heading("edit", text="Edit")
        self.tree.heading("delete", text="Delete")

        self.tree.column("name", width=220, anchor="center")
        self.tree.column("email", width=260, anchor="center")
        self.tree.column("role", width=120, anchor="center")
        self.tree.column("edit", width=60, anchor="center")
        self.tree.column("delete", width=70, anchor="center")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.tree.bind("<ButtonPress-1>", self.on_tree_click)

        self.load_staff()

    # ---------- ADMIN COUNT ----------
    def admin_count(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
        count = c.fetchone()[0]
        conn.close()
        return count

    # ---------- LOAD STAFF ----------
    def load_staff(self):
        self.tree.delete(*self.tree.get_children())

        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id,
                   first_name || ' ' || last_name,
                   email,
                   role
            FROM users
            ORDER BY first_name
        """)
        rows = c.fetchall()
        conn.close()

        for uid, name, email, role in rows:
            self.tree.insert(
                "",
                "end",
                iid=str(uid),
                values=(name, email, role, "✏️", "🗑️"),
            )

    # ---------- TABLE CLICK ----------
    def on_tree_click(self, event):
        col = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)

        if not row_id:
            return

        user_id = int(row_id)

        if col == "#4":
            self.open_edit_staff_dialog(user_id)
        elif col == "#5":
            self.confirm_delete_staff(user_id)

    # ---------- POPUPS ----------
    def open_add_staff_dialog(self):
        self._staff_dialog()

    def open_edit_staff_dialog(self, user_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT first_name, last_name, email, role
            FROM users WHERE id=?
        """, (user_id,))
        row = c.fetchone()
        conn.close()

        if row:
            self._staff_dialog(user_id, *row)

    def _staff_dialog(self, user_id=None, first_name="", last_name="", email="", role="staff"):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Staff" if user_id else "Add Staff")
        dialog.geometry("400x420")
        dialog.resizable(False, False)
        dialog.grab_set()

        self._center_window(dialog, 400, 420)

        title = ctk.CTkLabel(
            dialog,
            text="Edit Staff" if user_id else "Add Staff",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(15, 10))

        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30)

        def add_entry(row, label, value=""):
            lbl = ctk.CTkLabel(form_frame, text=label, font=ctk.CTkFont(size=13, weight="bold"))
            lbl.grid(row=row, column=0, sticky="w", pady=(8, 0))
            ent = ctk.CTkEntry(form_frame, width=340, height=32)
            ent.grid(row=row + 1, column=0, sticky="we")
            ent.insert(0, value)
            return ent

        fn_entry = add_entry(0, "First Name", first_name)
        ln_entry = add_entry(2, "Last Name", last_name)
        email_entry = add_entry(4, "Email", email)

        ctk.CTkLabel(form_frame, text="Role", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=6, column=0, sticky="w", pady=(8, 0)
        )

        role_combo = ctk.CTkComboBox(
            form_frame,
            width=340,
            height=32,
            values=["admin", "staff"]
        )
        role_combo.set(role)
        role_combo.grid(row=7, column=0)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15)

        def on_save():
            fn = fn_entry.get().strip()
            ln = ln_entry.get().strip()
            em = email_entry.get().strip()
            rl = role_combo.get()

            if not fn or not ln or not em:
                messagebox.showerror("Error", "All fields are required.")
                return

            # 🚨 Prevent demoting last admin
            if user_id and role == "admin" and rl != "admin":
                if self.admin_count() <= 1:
                    messagebox.showerror(
                        "Not Allowed",
                        "You cannot demote the last admin account."
                    )
                    return

            conn = get_connection()
            c = conn.cursor()

            if user_id:
                c.execute("""
                    UPDATE users
                    SET first_name=?, last_name=?, email=?, role=?
                    WHERE id=?
                """, (fn, ln, em, rl, user_id))
            else:
                c.execute("""
                    INSERT INTO users (first_name, last_name, email, password, role)
                    VALUES (?, ?, ?, ?, ?)
                """, (fn, ln, em, "temp123", rl))

            conn.commit()
            conn.close()
            dialog.destroy()
            self.load_staff()

        ctk.CTkButton(
            btn_frame, text="Cancel", width=100,
            fg_color="#CCCCCC", hover_color="#AAAAAA",
            text_color="#333333", command=dialog.destroy
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="Save", width=100,
            fg_color=PRIMARY, hover_color="#4C0025",
            text_color="white", command=on_save
        ).pack(side="left", padx=10)

    # ---------- DELETE STAFF ----------
    def confirm_delete_staff(self, user_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT first_name, last_name, role FROM users WHERE id=?", (user_id,))
        row = c.fetchone()

        if not row:
            conn.close()
            return

        name = f"{row[0]} {row[1]}"
        role = row[2]

        # 🚨 Prevent deleting last admin
        if role == "admin" and self.admin_count() <= 1:
            messagebox.showerror(
                "Not Allowed",
                "You cannot delete the last admin account."
            )
            conn.close()
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete staff member:\n\n{name}?"
        ):
            conn.close()
            return

        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        self.load_staff()

    def _center_window(self, window, w, h):
        window.update_idletasks()
        x = window.winfo_screenwidth() // 2 - w // 2
        y = window.winfo_screenheight() // 2 - h // 2
        window.geometry(f"{w}x{h}+{x}+{y}")
