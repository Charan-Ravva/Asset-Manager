# Pages/dashboard.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from db_conn import get_connection
from Pages.Asset import AssetsPage
from Pages.check_out import CheckOutPage
from Pages.check_in import CheckInPage
from Pages.students import StudentsPage 
from Pages.staff import StaffPage   
from Pages.settings import SettingsPage   



SIDEBAR_BG = "#6A0032"   # maroon
CARD_BG = "#F5F5F5"      # light grey
TEXT_DARK = "#222222"

# Column widths for the checked-out table (minimums; they will stretch)
COL_WIDTHS = [
    160,  # Asset Name
    80,   # Tag ID
    160,  # Student Name
    120,  # Student ID
    180   # Checked Out At
]


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, user_id, first_name, role):
        """
        master  = main App window
        user_id = logged in user's DB id
        first_name = for greeting
        role   = 'admin' or 'staff'
        """
        super().__init__(master, fg_color="white")
        self.nav_buttons = {}

        

        self.master = master
        self.user_id = user_id
        self.first_name = first_name
        self.role = role

        # will hold the scrollable list on the dashboard
        self.checked_out_list_frame = None

        # ---------- Layout: sidebar + content ----------
        self.columnconfigure(0, weight=0)   # sidebar
        self.columnconfigure(1, weight=1)   # main content
        self.rowconfigure(0, weight=1)

        SIDEBAR_WIDTH = 230

        # ---------- SIDEBAR ----------
        self.sidebar = ctk.CTkFrame(
            self,
            width=SIDEBAR_WIDTH,
            fg_color=SIDEBAR_BG,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        title_label = ctk.CTkLabel(
            self.sidebar,
            text="Asset Manager",
            justify="left",
            text_color="white",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(anchor="w", padx=20, pady=(20, 10))

        role_label = ctk.CTkLabel(
            self.sidebar,
            text=f"{role.upper()}",
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        role_label.pack(anchor="w", padx=20, pady=(0, 20))

        self.nav_buttons = {}

        def make_nav_button(text, command):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"    {text}",
                fg_color="transparent",
                hover_color="#4C0025",
                text_color="white",
                font=ctk.CTkFont(size=15, weight="bold"),
                anchor="w",
                corner_radius=0,
                height=40,
                command=command
            )
            btn.pack(fill="x", padx=0, pady=4)
            self.nav_buttons[text] = btn
            return btn

        make_nav_button("Dashboard", self.show_dashboard_view)
        make_nav_button("Check Out", self.show_checkout_page)
        make_nav_button("Check In", self.show_checkin_page)
        make_nav_button("Assets", self.show_assets_page)
        make_nav_button("History", self.show_students_page)

        if self.role == "admin":
            make_nav_button("Staff", self.show_staff_page)

        make_nav_button("Settings", self.show_settings_page)
 

        ctk.CTkLabel(self.sidebar, text="", fg_color=SIDEBAR_BG).pack(
            expand=True, fill="both"
        )

        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            fg_color="#FFFFFF",
            hover_color="#DDDDDD",
            text_color=SIDEBAR_BG,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=20,
            command=self.logout
        )
        logout_btn.pack(padx=20, pady=20, fill="x")

        # ---------- MAIN CONTENT AREA ----------
        self.content_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_propagate(True)

        self.current_view = None

        # Show dashboard by default
        self.show_dashboard_view()

    # ---------- UTIL ----------
    def clear_content(self):
        if self.current_view is not None:
            self.current_view.destroy()
            self.current_view = None
    
    # ---------- SIDEBAR HIGHLIGHT ----------
    def set_active_nav(self, page_name):
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(fg_color="#4C0025")   # active
            else:
                btn.configure(fg_color="transparent")

    # ---------- DASHBOARD VIEW ----------
    def show_dashboard_view(self):
        self.set_active_nav("Dashboard")
        self.clear_content()

        view = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF")
        view.pack(fill="both", expand=True, padx=20, pady=20)

        # Top bar
        top_bar = ctk.CTkFrame(view, fg_color="#FFFFFF")
        top_bar.pack(fill="x")

        ctk.CTkLabel(
            top_bar,
            text="Dashboard",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")

        ctk.CTkLabel(
            top_bar,
            text="  •  SAC asset overview",
            text_color="#777777",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", pady=(8, 0))

        ctk.CTkLabel(
            top_bar,
            text=f"Logged in as: {self.first_name}",
            text_color="#555555",
            font=ctk.CTkFont(size=14)
        ).pack(side="right")

        # Stats row
        stats_frame = ctk.CTkFrame(view, fg_color="#FFFFFF")
        stats_frame.pack(fill="x", pady=(20, 10))

        stats = self.get_summary_stats()

        def make_card(parent, title, value, extra, color):
            card = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12)
            card.pack(side="left", expand=True, fill="x", padx=8)

            ctk.CTkLabel(
                card, text=title, text_color="#555555",
                font=ctk.CTkFont(size=13, weight="bold")
            ).pack(anchor="w", padx=16, pady=(10, 0))

            ctk.CTkLabel(
                card, text=str(value), text_color=color,
                font=ctk.CTkFont(size=28, weight="bold")
            ).pack(anchor="w", padx=16, pady=(2, 0))

            ctk.CTkLabel(
                card, text=extra, text_color="#777777",
                font=ctk.CTkFont(size=12)
            ).pack(anchor="w", padx=16, pady=(0, 10))

        make_card(stats_frame, "Total Assets", stats["total_assets"],
                  "All items in inventory", "#1E88E5")
        make_card(stats_frame, "Checked Out", stats["checked_out"],
                  "Currently with students", "#D81B60")
        make_card(stats_frame, "Available", stats["available"],
                  "Ready to check out", "#43A047")
        make_card(stats_frame, "Staff Accounts", stats["total_users"],
                  "Admin + staff users", "#FB8C00")

        # Main panel
        main_panel = ctk.CTkFrame(view, fg_color="#FFFFFF")
        main_panel.pack(fill="both", expand=True, pady=(10, 0))

        ctk.CTkLabel(
            main_panel,
            text="Checked Out Assets",
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", pady=(5, 2))

        ctk.CTkLabel(
            main_panel,
            text="Live list of items currently with students.",
            text_color="#777777",
            font=ctk.CTkFont(size=13),
            justify="left"
        ).pack(anchor="w", pady=(0, 10))

        # Card container around the table
        table_card = ctk.CTkFrame(
            main_panel,
            fg_color="#F8F8FB",
            corner_radius=18
        )
        table_card.pack(fill="both", expand=True, pady=(0, 5))

        inner = ctk.CTkFrame(table_card, fg_color="#FFFFFF", corner_radius=16)
        inner.pack(fill="both", expand=True, padx=12, pady=12)

        self.checked_out_list_frame = ctk.CTkScrollableFrame(
            inner,
            fg_color="#FFFFFF"
        )
        self.checked_out_list_frame.pack(fill="both", expand=True)

        self.load_checked_out_assets()
        self.current_view = view

    # ---------- LOAD CHECKED-OUT TABLE ----------
    def load_checked_out_assets(self):
        """Show all currently checked-out assets using checkout + assets join."""
        # clear previous rows
        for w in self.checked_out_list_frame.winfo_children():
            w.destroy()

        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT a.asset_name,
                       a.asset_tag_id,
                       co.student_name,
                       co.student_id,
                       co.checkout_time
                FROM checkout AS co
                JOIN assets AS a ON co.asset_id = a.id
                WHERE co.status = 'Checked Out'
                ORDER BY co.checkout_time DESC
            """)
            rows = c.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load checked-out assets.\n\n{e}")
            rows = []

        if not rows:
            ctk.CTkLabel(
                self.checked_out_list_frame,
                text="No assets checked-out yet.",
                text_color="#0E7A52",
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(anchor="center", pady=16)
            return

        # HEADER
        header_frame = ctk.CTkFrame(
            self.checked_out_list_frame,
            fg_color="#ECECEC",
            corner_radius=8
        )
        header_frame.pack(fill="x", pady=(0, 0))

        headers = ["Asset Name", "Tag ID", "Student Name", "Student ID", "Checked Out At"]

        for col, (text, width) in enumerate(zip(headers, COL_WIDTHS)):
            # let each column stretch while keeping a minimum width
            header_frame.columnconfigure(col, minsize=width, weight=1)
            ctk.CTkLabel(
                header_frame,
                text=text,
                anchor="center",
                text_color="#333333",
                font=ctk.CTkFont(size=14, weight="bold")
            ).grid(row=0, column=col, padx=2, pady=10, sticky="nsew")

        # Dark separator under header
        ctk.CTkFrame(
            self.checked_out_list_frame,
            fg_color="#C7C7C7",
            height=1
        ).pack(fill="x")

        # ROWS
        for i, (asset_name, tag_id, student_name, student_id, checkout_time) in enumerate(rows):
            bg = "#FFFFFF" if i % 2 == 0 else "#F2F2F5"

            row = ctk.CTkFrame(
                self.checked_out_list_frame,
                fg_color=bg,
                corner_radius=6
            )
            row.pack(fill="x", pady=2)

            row_data = [asset_name, tag_id, student_name, student_id, checkout_time]

            for col, (text, width) in enumerate(zip(row_data, COL_WIDTHS)):
                # each column in the row also stretches to fill full width
                row.columnconfigure(col, minsize=width, weight=1)
                ctk.CTkLabel(
                    row,
                    text=str(text),
                    anchor="center",
                    text_color="#1A1A1A",
                    font=ctk.CTkFont(size=13)
                ).grid(row=0, column=col, padx=2, pady=10, sticky="nsew")

            # line after each row
            ctk.CTkFrame(
                self.checked_out_list_frame,
                fg_color="#D5D5D5",
                height=1
            ).pack(fill="x")

    # ---------- SUMMARY ----------
    def get_summary_stats(self):
        """Return basic statistics from DB."""
        stats = {
            "total_assets": 0,
            "checked_out": 0,
            "available": 0,
            "total_users": 0,
        }
        try:
            conn = get_connection()
            c = conn.cursor()

            c.execute("SELECT COUNT(*) FROM assets")
            stats["total_assets"] = c.fetchone()[0] or 0

            c.execute("SELECT COUNT(*) FROM assets WHERE status = 'Checked Out'")
            stats["checked_out"] = c.fetchone()[0] or 0

            c.execute("SELECT COUNT(*) FROM assets WHERE status = 'Available'")
            stats["available"] = c.fetchone()[0] or 0

            c.execute("SELECT COUNT(*) FROM users")
            stats["total_users"] = c.fetchone()[0] or 0

            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load dashboard stats.\n\n{e}")
        return stats

    # ---------- NAV PAGES ----------
    def show_assets_page(self):
        self.set_active_nav("Assets")
        self.clear_content()
        self.current_view = AssetsPage(self.content_frame)
        self.current_view.pack(fill="both", expand=True)

    def show_checkout_page(self):
        self.set_active_nav("Check Out")
        self.clear_content()
        self.current_view = CheckOutPage(self.content_frame)
        self.current_view.pack(fill="both", expand=True)

    def show_checkin_page(self):
        self.set_active_nav("Check In")
        self.clear_content()
        self.current_view = CheckInPage(self.content_frame)
        self.current_view.pack(fill="both", expand=True)

    def show_students_page(self):
        """Show the Students management page inside content_frame."""
        self.set_active_nav("History")
        self.clear_content()
        self.current_view = StudentsPage(self.content_frame)
        self.current_view.pack(fill="both", expand=True)
    
    def show_staff_page(self):
        self.set_active_nav("Staff")
        self.clear_content()
        self.current_view = StaffPage(self.content_frame)
        self.current_view.pack(fill="both", expand=True)

    def show_settings_page(self):
        self.set_active_nav("Settings")
        self.clear_content()
        self.current_view = SettingsPage(self.content_frame, self.user_id)
        self.current_view.pack(fill="both", expand=True)

    def show_placeholder(self, title, text):
        self.clear_content()
        view = ctk.CTkFrame(self.content_frame, fg_color="#FFFFFF")
        view.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            view,
            text=title,
            text_color=TEXT_DARK,
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            view,
            text=text,
            text_color="#555555",
            font=ctk.CTkFont(size=14),
            justify="left"
        ).pack(anchor="w", pady=(10, 0))

        self.current_view = view



    # ---------- LOGOUT ----------
    def logout(self):
        if messagebox.askyesno("Logout", "Do you want to log out?"):
            # 1. Reset resizable status
            self.master.resizable(True, True)
            
            # 2. Force the window back to a smaller size suitable for login
            # Replace 800x600 with your preferred Sign In dimensions
            self.master.geometry("800x600") 
            
            # 3. Clear and show sign in
            self.master.clear_page()
            self.master.show_sign_in()


