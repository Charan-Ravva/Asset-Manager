# Pages/landing_page.py
import customtkinter as ctk

PRIMARY = "#6A0032"    # maroon
PRIMARY_DARK = "#4C0025"
ACCENT = "#FFC82E"
BG = "#F5F5F7"


class LandingPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG)

        # root expands with window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ---------- HERO CARD (expands like dashboard) ----------
        card = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=18,
            border_width=1,
            border_color="#E0E0E0",
        )
        card.grid(row=0, column=0, padx=24, pady=24, sticky="nsew")

        # card expands, with left/right sections
        card.grid_rowconfigure(0, weight=1)
        # slightly more weight on left so it stays visually balanced
        card.grid_columnconfigure(0, weight=3)
        card.grid_columnconfigure(1, weight=2)

        # ---------- LEFT: Brand + value ----------
        left = ctk.CTkFrame(card, fg_color=PRIMARY, corner_radius=16)
        left.grid(row=0, column=0, padx=18, pady=18, sticky="nsew")
        left.grid_columnconfigure(0, weight=1)
        # allow vertical stretch, but content is stacked from top
        for r in range(7):
            left.grid_rowconfigure(r, weight=0)
        left.grid_rowconfigure(7, weight=1)  # spacer row at bottom

        badge = ctk.CTkLabel(
            left,
            text="Asset Management System",
            text_color=ACCENT,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        badge.grid(row=0, column=0, sticky="w", padx=20, pady=(18, 4))

        title = ctk.CTkLabel(
            left,
            text="Asset Manager",
            text_color="white",
            font=ctk.CTkFont(size=26, weight="bold"),
            justify="left",
        )
        title.grid(row=1, column=0, sticky="w", padx=20)

        subtitle = ctk.CTkLabel(
            left,
            text=(
                "Simple, secure inventory management\n"
                "for equipment, tools, and shared resources."
            ),
            text_color="#F6F6F6",
            font=ctk.CTkFont(size=13),
            justify="left",
        )
        subtitle.grid(row=2, column=0, sticky="w", padx=20, pady=(8, 18))

        def bullet(text, row):
            lbl = ctk.CTkLabel(
                left,
                text=f"• {text}",
                text_color="#FCEFF5",
                font=ctk.CTkFont(size=12),
                justify="left",
            )
            lbl.grid(row=row, column=0, sticky="w", padx=22, pady=(2, 0))

        bullet("Real-time checkout & availability tracking", 3)
        bullet("Fast user lookup and transaction history", 4)
        bullet("Role-based access for admins & staff", 5)

        footer = ctk.CTkLabel(
            left,
            text="Designed for organizations that manage shared assets.",
            text_color="#F9DDEB",
            font=ctk.CTkFont(size=11, slant="italic"),
            justify="left",
        )
        footer.grid(row=6, column=0, sticky="w", padx=20, pady=(18, 20))

        # ---------- RIGHT: Actions (also expands) ----------
        right = ctk.CTkFrame(card, fg_color="white")
        right.grid(row=0, column=1, padx=(0, 18), pady=18, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        # top content, bottom spacer for nicer vertical feel
        for r in range(6):
            right.grid_rowconfigure(r, weight=0)
        right.grid_rowconfigure(6, weight=1)

        heading = ctk.CTkLabel(
            right,
            text="Welcome back 👋",
            text_color="#222222",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        heading.grid(row=0, column=0, sticky="w", padx=18, pady=(20, 4))

        subheading = ctk.CTkLabel(
            right,
            text="Sign in to manage assets or create a account.",
            text_color="#555555",
            font=ctk.CTkFont(size=12),
            justify="left",
            wraplength=320,
        )
        subheading.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 16))

        sign_in_btn = ctk.CTkButton(
            right,
            text="Sign In",
            width=220,
            height=40,
            fg_color=PRIMARY,
            hover_color=PRIMARY_DARK,
            text_color="white",
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=10,
            command=master.show_sign_in,
        )
        sign_in_btn.grid(row=2, column=0, padx=18, pady=(10, 8), sticky="w")

        create_btn = ctk.CTkButton(
            right,
            text="Create Account",
            width=220,
            height=38,
            fg_color="white",
            hover_color="#F3F3F3",
            border_width=1,
            border_color=PRIMARY,
            text_color=PRIMARY,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=10,
            command=master.show_sign_up,
        )
        create_btn.grid(row=3, column=0, padx=18, pady=(0, 10), sticky="w")

        hint = ctk.CTkLabel(
            right,
            text="Only authorized users may access this system.",
            text_color="#777777",
            font=ctk.CTkFont(size=11),
            wraplength=320,
            justify="left",
        )
        hint.grid(row=4, column=0, sticky="w", padx=18, pady=(8, 0))

        