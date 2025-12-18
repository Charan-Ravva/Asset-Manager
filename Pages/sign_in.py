# pages/sign_in.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from db_conn import get_connection

HEADER_BG = "#6A0032"
BUTTON_BG = "#6A0032"
BORDER_COLOR = "#E0E0E0"


def handle_login(self):
    email = self.email_entry.get().strip()
    pw = self.password_entry.get().strip()

    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, first_name, role FROM users WHERE email=? AND password=?",
        (email, pw)
    )
    user = c.fetchone()
    conn.close()
    return user


class SignInPage(ctk.CTkFrame):
    def __init__(self, master):
        # Transparent: NO WHITE BACKGROUND
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)

        # ---------- Center modal card ----------
        self.card = ctk.CTkFrame(
            self,
            width=520,
            height=420,
            fg_color="white",
            corner_radius=0,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # ---------- Header ----------
        header = ctk.CTkFrame(
            self.card,
            fg_color=HEADER_BG,
            height=72,
            corner_radius=0
        )
        header.pack(fill="x")

        title = ctk.CTkLabel(
            header,
            text="Sign In",
            text_color="white",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.place(relx=0.5, rely=0.5, anchor="center")

        # ---------- Form ----------
        form = ctk.CTkFrame(self.card, fg_color="white")
        form.pack(fill="both", expand=True, padx=40, pady=30)

        LABEL_FONT = ctk.CTkFont(size=15, weight="bold")

        def label(text):
            return ctk.CTkLabel(
                form,
                text=text,
                font=LABEL_FONT,
                text_color="#222222"
            )

        def entry(placeholder, show=None):
            return ctk.CTkEntry(
                form,
                height=42,
                placeholder_text=placeholder,
                show=show,
                corner_radius=8,
                border_width=1,
                border_color="#9A9A9A",
                fg_color="white",
                font=ctk.CTkFont(size=14),
            )

        # Email
        label("Email").pack(anchor="w")
        self.email_entry = entry("Email")
        self.email_entry.pack(fill="x", pady=(4, 18))

        # Password
        label("Password").pack(anchor="w")
        self.password_entry = entry("Password", show="•")
        self.password_entry.pack(fill="x", pady=(4, 10))

        # Show password
        self.show_pw = tk.BooleanVar()
        show_pw_cb = ctk.CTkCheckBox(
            form,
            text="Show Password",
            variable=self.show_pw,
            text_color=HEADER_BG,
            font=ctk.CTkFont(size=13, weight="bold"),
            checkbox_width=18,
            checkbox_height=18,
            command=self._toggle_password
        )
        show_pw_cb.pack(anchor="w", pady=(0, 24))

        # ---------- Actions ----------
        action_row = ctk.CTkFrame(form, fg_color="white")
        action_row.pack(fill="x")

        create_account = ctk.CTkLabel(
            action_row,
            text="Create An Account",
            text_color=HEADER_BG,
            font=ctk.CTkFont(size=14, weight="bold"),
            cursor="hand2"
        )
        create_account.pack(side="left")
        create_account.bind("<Button-1>", lambda e: self.master.show_sign_up())

        signin_btn = ctk.CTkButton(
            action_row,
            text="Sign In",
            width=160,
            height=44,
            fg_color=BUTTON_BG,
            hover_color="#4C0025",
            text_color="white",
            font=ctk.CTkFont(size=17, weight="bold"),
            command=self._sign_in
        )
        signin_btn.pack(side="right")

    # ---------- Helpers ----------
    def _toggle_password(self):
        self.password_entry.configure(
            show="" if self.show_pw.get() else "•"
        )

    def _sign_in(self):
        user = handle_login(self)
        if user:
            user_id, first_name, role = user
            self.master.show_dashboard(user_id, first_name, role)
        else:
            messagebox.showerror("Login Failed", "Invalid email or password")
