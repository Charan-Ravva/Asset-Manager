# main.py
import customtkinter as ctk
from Pages.landing_page import LandingPage
from Pages.sign_in import SignInPage
from Pages.sign_up import SignUpPage
from Pages.dashboard import DashboardPage
from Pages.students import StudentsPage




class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.title("SAC Asset Manager")

        self.current_page = None

        # start on landing with medium window
        self.show_landing()

    # ------------ helper: center + resize ------------
    def center_window(self, w: int, h: int):
        """Resize and center the window on the screen."""
        self.update_idletasks()
        x = self.winfo_screenwidth() // 2 - w // 2
        y = self.winfo_screenheight() // 2 - h // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ------------ Page switching helpers ------------
    def clear_page(self):
        if self.current_page is not None:
            self.current_page.destroy()
            self.current_page = None

    def show_landing(self):
        self.clear_page()
        # medium window for landing
        self.resizable(True, True)
        self.center_window(900, 540)
        self.current_page = LandingPage(self)
        self.current_page.pack(fill="both", expand=True)

    def show_sign_in(self):
        self.clear_page()
        # slightly smaller width for sign in popup
        self.resizable(False, False)
        self.center_window(720, 560)
        self.current_page = SignInPage(self)
        self.current_page.pack(fill="both", expand=True)

    def show_sign_up(self):
        self.clear_page()
        # a bit wider/taller for the sign up form
        self.resizable(False, False)
        self.center_window(820, 640)
        self.current_page = SignUpPage(self)
        self.current_page.pack(fill="both", expand=True)

    # ------------ After login go to Dashboard ------------
    def show_dashboard(self, user_id, first_name, role):
        self.clear_page()
        # full-size app only for dashboard
        self.resizable(True, True)
        self.center_window(1100, 650)
        self.minsize(900, 500)
        self.current_page = DashboardPage(self, user_id, first_name, role)
        self.current_page.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
