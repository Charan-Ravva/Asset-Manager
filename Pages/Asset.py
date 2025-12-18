import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox

from db_conn import get_connection

TEXT_DARK = "#222222"
CARD_BG = "#F5F5F5"


class AssetsPage(ctk.CTkFrame):
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
            text="Assets",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_DARK,
        ).pack(side="left")

        ctk.CTkLabel(
            top_bar,
            text=" • Manage SAC equipment inventory",
            font=ctk.CTkFont(size=13),
            text_color="#777777",
        ).pack(side="left", padx=(6, 0))

        ctk.CTkButton(
            top_bar,
            text="+ Add Asset",
            width=120,
            height=34,
            fg_color="#6A0032",
            hover_color="#4C0025",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.open_add_asset_dialog,
        ).pack(side="right", padx=(0, 8))

        ctk.CTkButton(
            top_bar,
            text="Delete Selected",
            width=150,
            height=34,
            fg_color="#CC0000",
            hover_color="#A30000",
            text_color="white",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.delete_selected_assets,
        ).pack(side="right", padx=(0, 12))

        # ---------- MAIN TABLE ----------
        main_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        tree_container = ttk.Frame(main_frame)
        tree_container.pack(fill="both", expand=True)

        # ---------- TREEVIEW STYLE ----------
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Assets.Treeview",
            background=CARD_BG,
            fieldbackground=CARD_BG,
            foreground=TEXT_DARK,
            font=("Inter", 12),
            rowheight=36,
            borderwidth=0,
            relief="flat",
        )
        style.configure(
            "Assets.Treeview.Heading",
            background="#EEEEEE",
            foreground="#444444",
            font=("Inter", 11, "bold"),
            relief="solid",
            borderwidth=1,
        )

        # ---------- LOAD CHECKBOX IMAGES ----------
        self.img_unchecked, self.img_checked = self._load_checkbox_images()

        # Columns (checkbox is #0)
        self.columns = (
            "asset_name",
            "asset_tag",
            "status",
            "location",
            "category",
            "edit",
        )

        self.tree = ttk.Treeview(
            tree_container,
            columns=self.columns,
            show="tree headings",
            style="Assets.Treeview",
            selectmode="none",
        )

        # Checkbox column (#0)
        self.tree.heading("#0", image=self.img_unchecked, anchor="center")
        self.tree.column("#0", width=44, minwidth=44, stretch=False, anchor="center")

        # Headings
        self.tree.heading("asset_name", text="Asset Name")
        self.tree.heading("asset_tag", text="Asset Tag ID")
        self.tree.heading("status", text="Status")
        self.tree.heading("location", text="Location")
        self.tree.heading("category", text="Category")
        self.tree.heading("edit", text="Edit")

        self.tree.column("asset_name", width=220, anchor="center")
        self.tree.column("asset_tag", width=120, anchor="center")
        self.tree.column("status", width=100, anchor="center")
        self.tree.column("location", width=150, anchor="center")
        self.tree.column("category", width=180, anchor="center")
        self.tree.column("edit", width=60, anchor="center")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        # IMPORTANT: use ButtonPress + X-coordinate detection
        self.tree.bind("<ButtonPress-1>", self._on_tree_click)

        self.info_label = ctk.CTkLabel(
            self,
            text="0 asset(s) in inventory.",
            text_color="#777777",
            font=ctk.CTkFont(size=11),
        )
        self.info_label.pack(anchor="w", padx=20, pady=(6, 0))

        self.load_assets()

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

    # ---------- LOAD ASSETS ----------
    def load_assets(self):
        self.tree.delete(*self.tree.get_children())
        self.checked_rows.clear()
        self.header_checked = False
        self.tree.heading("#0", image=self.img_unchecked)

        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id, asset_name, asset_tag_id, status, location, category
            FROM assets
            ORDER BY asset_name
        """)
        rows = c.fetchall()
        conn.close()

        self.info_label.configure(text=f"{len(rows)} asset(s) in inventory.")

        for r in rows:
            asset_id, name, tag, status, location, category = r
            self.tree.insert(
                "",
                "end",
                iid=str(asset_id),
                image=self.img_unchecked,
                values=(name, tag, status, location, category, "✏️"),
            )

    # ---------- CHECKBOX HANDLING (ROBUST) ----------
    def _on_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        row_id = self.tree.identify_row(event.y)

        checkbox_width = self.tree.column("#0", "width")

        # Header checkbox
        if region == "heading" and event.x < checkbox_width:
            self._toggle_header_checkbox()
            return "break"

        # Row checkbox
        if row_id and region in ("tree", "cell") and event.x < checkbox_width:
            self._toggle_row_checkbox(row_id)
            return "break"

        # Edit column (last column)
        column = self.tree.identify_column(event.x)
        if row_id and column == "#6":
            self.open_edit_asset_dialog(int(row_id))
            return "break"

    def _toggle_row_checkbox(self, row_id):
        if row_id in self.checked_rows:
            self.tree.item(row_id, image=self.img_unchecked)
            self.checked_rows.remove(row_id)
        else:
            self.tree.item(row_id, image=self.img_checked)
            self.checked_rows.add(row_id)

        all_ids = list(self.tree.get_children())
        self.tree.heading(
            "#0",
            image=self.img_checked if all_ids and len(self.checked_rows) == len(all_ids)
            else self.img_unchecked,
        )

    def _toggle_header_checkbox(self):
        self.header_checked = not self.header_checked
        img = self.img_checked if self.header_checked else self.img_unchecked
        self.tree.heading("#0", image=img)

        self.checked_rows.clear()
        for iid in self.tree.get_children():
            self.tree.item(iid, image=img)
            if self.header_checked:
                self.checked_rows.add(iid)

    # ---------- DELETE ----------
    def delete_selected_assets(self):
        if not self.checked_rows:
            messagebox.showerror("No Selection", "Select at least one asset.")
            return

        if not messagebox.askyesno(
            "Delete Assets",
            f"Delete {len(self.checked_rows)} selected asset(s)?"
        ):
            return

        conn = get_connection()
        c = conn.cursor()
        placeholders = ",".join("?" for _ in self.checked_rows)
        c.execute(
            f"DELETE FROM assets WHERE id IN ({placeholders})",
            list(self.checked_rows),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Deleted", "Selected asset(s) deleted.")
        self.load_assets()


    # ---------- Add Asset dialog ----------
    def open_add_asset_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Asset")
        dialog.geometry("460x520")
        dialog.resizable(False, False)
        dialog.grab_set()  # make modal

        self._center_window(dialog, 460, 520)

        title = ctk.CTkLabel(
            dialog,
            text="Add New Asset",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(15, 10))

        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        def add_labeled_entry(row, label_text, placeholder=None):
            lbl = ctk.CTkLabel(
                form_frame,
                text=label_text,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            lbl.grid(row=row, column=0, sticky="w", pady=(8, 0))

            entry = ctk.CTkEntry(
                form_frame,
                width=340,
                height=32,
                placeholder_text=placeholder
            )
            entry.grid(row=row + 1, column=0, columnspan=2,
                       sticky="we", pady=(2, 0))
            return entry

        # Asset Name
        name_entry = add_labeled_entry(0, "Asset Name")

        # Asset Tag ID
        tag_entry = add_labeled_entry(2, "Asset Tag ID", "e.g. SAC-00123")

        # Status
        status_label = ctk.CTkLabel(
            form_frame,
            text="Status",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        status_label.grid(row=4, column=0, sticky="w", pady=(8, 0))

        status_combo = ctk.CTkComboBox(
            form_frame,
            width=340,
            height=32,
            values=["Available", "Checked Out", "Maintenance", "Broken", "Retired"]
        )
        status_combo.set("Available")
        status_combo.grid(row=5, column=0, columnspan=2,
                          sticky="we", pady=(2, 0))

        # Location
        loc_entry = add_labeled_entry(
            6, "Location", "e.g. Equipment Room, Court 2..."
        )

        # Category
        cat_label = ctk.CTkLabel(
            form_frame,
            text="Category",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        cat_label.grid(row=8, column=0, sticky="w", pady=(8, 0))

        default_categories = [
            "Basketball", "Volleyball", "Badminton",
            "Yoga", "Fitness", "Racquet Sports", "Equipment Checkout"
        ]

        category_combo = ctk.CTkComboBox(
            form_frame,
            width=260,
            height=32,
            values=default_categories
        )
        category_combo.grid(row=9, column=0, sticky="w", pady=(2, 0))
        category_combo.set("")

        def on_add_category():
            dlg = ctk.CTkInputDialog(
                title="Add Category",
                text="Enter new category name:"
            )
            new_cat = dlg.get_input()
            if new_cat:
                vals = list(category_combo.cget("values"))
                if new_cat not in vals:
                    vals.append(new_cat)
                    category_combo.configure(values=vals)
                category_combo.set(new_cat)

        add_cat_btn = ctk.CTkButton(
            form_frame,
            text="+ Add",
            width=70,
            height=32,
            fg_color="#6A0032",
            hover_color="#4C0025",
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=on_add_category
        )
        add_cat_btn.grid(row=9, column=1, sticky="e",
                         padx=(8, 0), pady=(2, 0))

        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=0)

        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(0, 15))

        def on_cancel():
            dialog.destroy()

        def on_save():
            name = name_entry.get().strip()
            tag = tag_entry.get().strip()
            status_val = status_combo.get().strip() or "Available"
            location = loc_entry.get().strip()
            category = category_combo.get().strip()

            if not name:
                messagebox.showerror("Error", "Asset name is required.")
                return
            if not tag:
                messagebox.showerror("Error", "Asset Tag ID is required.")
                return

            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute("""
                    INSERT INTO assets (asset_name, asset_tag_id, status, location, category)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, tag, status_val, location, category))
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Asset added successfully.")
                dialog.destroy()
                self.load_assets()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add asset.\n\n{e}")

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=100,
            fg_color="#CCCCCC",
            hover_color="#AAAAAA",
            text_color="#333333",
            command=on_cancel
        )
        cancel_btn.pack(side="left", padx=10)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save",
            width=100,
            fg_color="#6A0032",
            hover_color="#4C0025",
            text_color="white",
            command=on_save
        )
        save_btn.pack(side="left", padx=10)

    # ---------- EDIT EXISTING ASSET (used by pencil column) ----------
    def open_edit_asset_dialog(self, asset_id: int):
        # Fetch current values
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT asset_name, asset_tag_id, status, location, category
                FROM assets
                WHERE id = ?
            """, (asset_id,))
            row = c.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load asset.\n\n{e}")
            return

        if not row:
            messagebox.showerror("Error", "Asset not found.")
            return

        current_name, current_tag, current_status, current_location, current_category = row

        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Asset")
        dialog.geometry("460x520")
        dialog.resizable(False, False)
        dialog.grab_set()
        self._center_window(dialog, 460, 520)

        title = ctk.CTkLabel(
            dialog,
            text="Edit Asset",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(15, 10))

        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        def add_labeled_entry(row, label_text, initial="", placeholder=None):
            lbl = ctk.CTkLabel(
                form_frame,
                text=label_text,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            lbl.grid(row=row, column=0, sticky="w", pady=(8, 0))

            entry = ctk.CTkEntry(
                form_frame,
                width=340,
                height=32,
                placeholder_text=placeholder
            )
            if initial:
                entry.insert(0, initial)
            entry.grid(row=row + 1, column=0, columnspan=2,
                       sticky="we", pady=(2, 0))
            return entry

        name_entry = add_labeled_entry(0, "Asset Name", current_name)
        tag_entry = add_labeled_entry(2, "Asset Tag ID", current_tag, "e.g. SAC-00123")

        status_label = ctk.CTkLabel(
            form_frame,
            text="Status",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        status_label.grid(row=4, column=0, sticky="w", pady=(8, 0))

        status_values = ["Available", "Checked Out", "Maintenance", "Broken", "Retired"]
        status_combo = ctk.CTkComboBox(
            form_frame,
            width=340,
            height=32,
            values=status_values
        )
        status_combo.set(current_status if current_status in status_values else "Available")
        status_combo.grid(row=5, column=0, columnspan=2,
                          sticky="we", pady=(2, 0))

        loc_entry = add_labeled_entry(
            6, "Location", current_location
        )

        cat_label = ctk.CTkLabel(
            form_frame,
            text="Category",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        cat_label.grid(row=8, column=0, sticky="w", pady=(8, 0))

        default_categories = [
             "Fitness",  "Equipment Checkout"
        ]
        if current_category and current_category not in default_categories:
            default_categories.append(current_category)

        category_combo = ctk.CTkComboBox(
            form_frame,
            width=260,
            height=32,
            values=default_categories
        )
        category_combo.grid(row=9, column=0, sticky="w", pady=(2, 0))
        category_combo.set(current_category or "")

        def on_add_category():
            dlg = ctk.CTkInputDialog(
                title="Add Category",
                text="Enter new category name:"
            )
            new_cat = dlg.get_input()
            if new_cat:
                vals = list(category_combo.cget("values"))
                if new_cat not in vals:
                    vals.append(new_cat)
                    category_combo.configure(values=vals)
                category_combo.set(new_cat)

        add_cat_btn = ctk.CTkButton(
            form_frame,
            text="+ Add",
            width=70,
            height=32,
            fg_color="#6A0032",
            hover_color="#4C0025",
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=on_add_category
        )
        add_cat_btn.grid(row=9, column=1, sticky="e",
                         padx=(8, 0), pady=(2, 0))

        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=0)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(0, 15))

        def on_cancel():
            dialog.destroy()

        def on_save():
            name = name_entry.get().strip()
            tag = tag_entry.get().strip()
            status_val = status_combo.get().strip() or "Available"
            location = loc_entry.get().strip()
            category = category_combo.get().strip()

            if not name:
                messagebox.showerror("Error", "Asset name is required.")
                return
            if not tag:
                messagebox.showerror("Error", "Asset Tag ID is required.")
                return

            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute("""
                    UPDATE assets
                    SET asset_name = ?, asset_tag_id = ?, status = ?, location = ?, category = ?
                    WHERE id = ?
                """, (name, tag, status_val, location, category, asset_id))
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Asset updated successfully.")
                dialog.destroy()
                self.load_assets()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update asset.\n\n{e}")

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            width=100,
            fg_color="#CCCCCC",
            hover_color="#AAAAAA",
            text_color="#333333",
            command=on_cancel
        )
        cancel_btn.pack(side="left", padx=10)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Changes",
            width=130,
            fg_color="#6A0032",
            hover_color="#4C0025",
            text_color="white",
            command=on_save
        )
        save_btn.pack(side="left", padx=10)



    # ---------- Helper: get selected asset IDs ----------
    def get_selected_asset_ids(self):
        selected_ids = []
        for iid in self.tree.get_children():
            vals = self.tree.item(iid, "values")
            if vals and vals[0] == "☑":
                selected_ids.append(int(iid))
        return selected_ids

    # ---------- Helper: center Toplevel ----------
    def _center_window(self, window, width, height):
        try:
            window.update_idletasks()
            x = window.winfo_screenwidth() // 2 - width // 2
            y = window.winfo_screenheight() // 2 - height // 2
            window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass
