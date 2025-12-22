# pages/sign_up.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

HEADER_BG = "#6A0032"       # maroon
BUTTON_BG = "#6A0032"

from db_conn import get_connection


class SignUpPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white")

        self.master = master

        # ---------- TOP HEADER BAR ----------
        header = ctk.CTkFrame(
            self,
            fg_color=HEADER_BG,
            height=56,          # slightly shorter header
            corner_radius=0,
        )
        header.pack(fill="x", side="top")

        title_label = ctk.CTkLabel(
            header,
            text="Create An Account",
            text_color="white",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.place(relx=0.5, rely=0.5, anchor="center")

        # ---------- CENTERED CONTENT AREA ----------
        content = ctk.CTkFrame(self, fg_color="white")
        content.pack(fill="both", expand=True)

        # use pack instead of place -> lets layout shrink/grow naturally
        inner = ctk.CTkFrame(content, fg_color="white")
        inner.pack(pady=(40, 20))   # was y=80; move everything up

        inner.grid_columnconfigure(0, weight=1)

        LABEL_FONT = ctk.CTkFont(size=14, weight="bold")
        ENTRY_FONT = ctk.CTkFont(size=14)

        def add_labeled_entry(row, label_text, show: str = ""):
            lbl = ctk.CTkLabel(
                inner,
                text=label_text,
                font=LABEL_FONT,
                text_color="black",
                anchor="w",
            )
            lbl.grid(row=row * 2, column=0, sticky="w", pady=(0, 2))

            entry = ctk.CTkEntry(
                inner,
                width=420,
                height=36,
                font=ENTRY_FONT,
                show=show,
                corner_radius=6,
                fg_color="white",
                border_color="#808080",
                border_width=1,
            )
            entry.grid(row=row * 2 + 1, column=0, sticky="we", pady=(0, 10))
            return entry

        # ---------- FIELDS ----------
        self.first_name_entry = add_labeled_entry(0, "First Name")
        self.last_name_entry = add_labeled_entry(1, "Last Name")
        self.email_entry = add_labeled_entry(2, "Email")
        self.password_entry = add_labeled_entry(3, "Password", show="•")
        self.confirm_password_entry = add_labeled_entry(4, "Confirm Password", show="•")

        # ---------- SHOW PASSWORD ----------
        self.show_password_var = tk.IntVar()

        def toggle_password():
            if self.show_password_var.get() == 1:
                self.password_entry.configure(show="")
                self.confirm_password_entry.configure(show="")
            else:
                self.password_entry.configure(show="•")
                self.confirm_password_entry.configure(show="•")

        show_password_checkbox = ctk.CTkCheckBox(
            inner,
            text="Show Password",
            variable=self.show_password_var,
            command=toggle_password,
            text_color="black",
            font=ctk.CTkFont(size=12),
            checkbox_width=18,
            checkbox_height=18,
        )
        show_password_checkbox.grid(
            row=10, column=0, sticky="w", pady=(4, 10)
        )

        # ---------- SIGN UP BUTTON ----------
        sign_up_button = ctk.CTkButton(
            inner,
            text="Sign Up",
            width=160,
            height=40,
            fg_color=BUTTON_BG,
            hover_color="#4C0025",
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=8,
            command=self.handle_sign_up,
        )
        sign_up_button.grid(
            row=11, column=0, pady=(0, 6)
        )

        # ---------- "ALREADY HAVE AN ACCOUNT?" ----------
        bottom_frame = ctk.CTkFrame(inner, fg_color="white")
        bottom_frame.grid(row=12, column=0, pady=(0, 0))

        already_label = ctk.CTkLabel(
            bottom_frame,
            text="Already have an account?",
            text_color="black",
            font=ctk.CTkFont(size=13),
        )
        already_label.pack(side="left")

        def on_sign_in_click(event=None):
            if hasattr(master, "show_sign_in"):
                master.show_sign_in()

        sign_in_label = ctk.CTkLabel(
            bottom_frame,
            text=" Sign In",
            text_color=HEADER_BG,
            font=ctk.CTkFont(size=13, weight="bold"),
            cursor="hand2",
        )
        sign_in_label.pack(side="left")
        sign_in_label.bind("<Button-1>", on_sign_in_click)

    # ---------- Helper: Password validation ----------
    def is_valid_password(self, pw: str) -> bool:
        if len(pw) < 8:
            return False
        has_upper = any(ch.isupper() for ch in pw)
        has_lower = any(ch.islower() for ch in pw)
        has_digit = any(ch.isdigit() for ch in pw)
        return has_upper and has_lower and has_digit

    # ---------- Main sign-up logic ----------
    def handle_sign_up(self):
        first = self.first_name_entry.get().strip()
        last = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip().lower()
        pw = self.password_entry.get().strip()
        confirm = self.confirm_password_entry.get().strip()

        if not all([first, last, email, pw, confirm]):
            messagebox.showerror("Error", "All fields are required.")
            return

        if pw != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        if not self.is_valid_password(pw):
            messagebox.showerror(
                "Weak Password",
                "Password must be at least 8 characters long and include:\n"
                "- At least 1 uppercase letter\n"
                "- At least 1 lowercase letter\n"
                "- At least 1 number"
            )
            return

        conn = get_connection()
        c = conn.cursor()
        try:
            c.execute(
                """
                INSERT INTO users (first_name, last_name, email, password, role)
                VALUES (?, ?, ?, ?, 'staff')
                """,
                (first, last, email, pw),
            )
            conn.commit()

            messagebox.showinfo(
                "Success",
                "Account created successfully!\nPlease sign in to continue.",
            )

            if hasattr(self.master, "show_sign_in"):
                self.master.show_sign_in()

        except Exception as e:
            messagebox.showerror(
                "Error",
                "Could not create account.\n"
                "The email may already be in use.\n\n"
                f"Details: {e}"
            )
        finally:
            conn.close()
