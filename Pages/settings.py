import customtkinter as ctk
from Pages.sign_in import hash_password
from db_conn import get_connection

TEXT_DARK = "#222222"
MAROON = "#6A0032"


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master, fg_color="#FFFFFF")
        self.user_id = user_id

        # ================== TITLE ==================
        ctk.CTkLabel(
            self,
            text="Settings",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT_DARK
        ).pack(anchor="w", padx=30, pady=(20, 4))

        ctk.CTkLabel(
            self,
            text="Manage your account",
            font=ctk.CTkFont(size=13),
            text_color="#777777"
        ).pack(anchor="w", padx=30, pady=(0, 20))

        # ================== CONTENT ==================
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        self.profile_card = self._build_profile_card(content)
        self.profile_card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        self.security_card = self._build_security_card(content)
        self.security_card.grid(row=0, column=1, sticky="nsew")

        self._load_user()

    # ======================================================
    # FLOATING TOAST
    # ======================================================
    def show_toast(self, message, success=True):
        bg = "#E6F4EA" if success else "#FDECEA"
        fg = "#1E7F43" if success else "#B00020"
        icon = "✔ " if success else "❌ "

        toast = ctk.CTkLabel(
            self,
            text=icon + message,
            fg_color=bg,
            text_color=fg,
            corner_radius=10,
            padx=18,
            pady=10,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        toast.place(relx=0.98, rely=0.05, anchor="ne")
        self.after(3000, toast.destroy)

    # ======================================================
    # PROFILE CARD
    # ======================================================
    def _build_profile_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color="#F8F8F8", corner_radius=14)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text="Profile",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 2))

        ctk.CTkLabel(
            card, text="Update your personal details",
            font=ctk.CTkFont(size=12),
            text_color="#777777"
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 12))

        self.first_name = self._entry(card, "First Name", 2)
        self.last_name = self._entry(card, "Last Name", 4)
        self.email = self._entry(card, "Email", 6)

        ctk.CTkButton(
            card,
            text="Save Profile",
            width=160,
            height=36,
            fg_color=MAROON,
            hover_color="#4C0025",
            command=self.update_profile
        ).grid(row=8, column=0, padx=20, pady=(16, 20), sticky="w")

        return card

    # ======================================================
    # SECURITY CARD
    # ======================================================
    def _build_security_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color="#F8F8F8", corner_radius=14)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card, text="Security",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(16, 2))

        ctk.CTkLabel(
            card, text="Update your password",
            font=ctk.CTkFont(size=12),
            text_color="#777777"
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 12))

        self.current_pw = self._entry(card, "Current Password", 2, password=True)
        self.new_pw = self._entry(card, "New Password", 4, password=True)
        self.confirm_pw = self._entry(card, "Confirm New Password", 6, password=True)

        ctk.CTkButton(
            card,
            text="Change Password",
            width=220,
            height=36,
            fg_color=MAROON,
            hover_color="#4C0025",
            command=self.change_password
        ).grid(row=8, column=0, padx=20, pady=(16, 20), sticky="w")

        return card

    # ======================================================
    # ENTRY WITH SHOW / HIDE PASSWORD
    # ======================================================
    def _entry(self, parent, label, row, password=False):
        ctk.CTkLabel(
            parent, text=label,
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=row, column=0, sticky="w", padx=20)

        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=row + 1, column=0, sticky="we", padx=20, pady=(4, 10))
        container.grid_columnconfigure(0, weight=1)

        entry = ctk.CTkEntry(
            container,
            height=34,
            show="*" if password else ""
        )
        entry.grid(row=0, column=0, sticky="we")

        if password:
            toggle = ctk.CTkButton(
                container,
                text="👁",
                width=36,
                height=34,
                fg_color="#E0E0E0",
                text_color="#333333",
                hover_color="#CFCFCF",
                command=lambda e=entry: self._toggle_password(e)
            )
            toggle.grid(row=0, column=1, padx=(6, 0))

        return entry

    def _toggle_password(self, entry):
        entry.configure(show="" if entry.cget("show") == "*" else "*")

    # ======================================================
    # DATA OPERATIONS
    # ======================================================
    def _load_user(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT first_name, last_name, email FROM users WHERE id=?",
            (self.user_id,)
        )
        row = c.fetchone()
        conn.close()

        if row:
            self.first_name.insert(0, row[0])
            self.last_name.insert(0, row[1])
            self.email.insert(0, row[2])

    def update_profile(self):
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
            UPDATE users
            SET first_name=?, last_name=?, email=?
            WHERE id=?
        """, (
            self.first_name.get().strip(),
            self.last_name.get().strip(),
            self.email.get().strip(),
            self.user_id
        ))
        conn.commit()
        conn.close()

        self.show_toast("Profile updated successfully")

    def change_password(self):
        current = self.current_pw.get().strip()
        new = self.new_pw.get().strip()
        confirm = self.confirm_pw.get().strip()

        if not current or not new or not confirm:
            self.show_toast("All password fields are required", success=False)
            return

        if new != confirm:
            self.show_toast("Passwords do not match", success=False)
            return

        try:
            conn = get_connection()
            c = conn.cursor()

            c.execute(
                "SELECT password FROM users WHERE id=?",
                (self.user_id,)
            )
            row = c.fetchone()

            if not row:
                conn.close()
                self.show_toast("User not found", success=False)
                return

            stored_pw = row[0]

            # ✅ hash the typed current password
            typed_hash = hash_password(current)

            # ✅ allow legacy plaintext OR hashed comparison
            if stored_pw != current and stored_pw != typed_hash:
                conn.close()
                self.show_toast("Current password is incorrect", success=False)
                return

            # ✅ store NEW password as hash
            new_hash = hash_password(new)

            c.execute(
                "UPDATE users SET password=? WHERE id=?",
                (new_hash, self.user_id)
            )
            conn.commit()
            conn.close()

            # Clear fields
            self.current_pw.delete(0, "end")
            self.new_pw.delete(0, "end")
            self.confirm_pw.delete(0, "end")

            self.show_toast("Password updated successfully")

        except Exception as e:
            self.show_toast(f"Error: {e}", success=False)

            