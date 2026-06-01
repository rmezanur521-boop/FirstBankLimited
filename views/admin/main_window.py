import customtkinter as ctk

BLUE    = "#1A73E8"
WHITE   = "#FFFFFF"
SIDEBAR = "#1E2A3A"
DARK    = "#1E2A3A"
HOVER   = "#2D3F55"
ACTIVE  = "#1A73E8"
TEXT_S  = "#A8BDD0"


class AdminMainWindow(ctk.CTkToplevel):

    MENU = [
        ("🏠", "Dashboard",    "dashboard"),
        ("👥", "Customers",    "customers"),
        ("🏦", "Accounts",     "accounts"),
        ("💸", "Transactions", "transactions"),
        ("📋", "Loans",        "loans"),
        ("👔", "Employees",    "employees"),
        ("⚙️",  "Settings",    "settings"),
    ]

    def __init__(self, user: dict, login_win):
        super().__init__()
        self.user         = user
        self.login_win    = login_win
        self._active_page = None
        self._btn_refs    = {}

        self.title("First Bank Limited — Admin Panel")
        self.geometry("1280x740")
        self.minsize(1100, 680)
        ctk.set_appearance_mode("light")

        self._build()
        self._center()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Navigate AFTER mainloop starts via after()
        self.after(100, lambda: self.navigate("dashboard"))

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 1280) // 2
        y = (self.winfo_screenheight() - 740)  // 2
        self.geometry(f"1280x740+{x}+{y}")

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ───────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(
            self, fg_color=SIDEBAR, width=230, corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Logo
        logo_frame = ctk.CTkFrame(
            self.sidebar, fg_color="#151E2B", corner_radius=0
        )
        logo_frame.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            logo_frame, text="🏦  First Bank",
            font=("Arial", 17, "bold"), text_color=WHITE
        ).pack(pady=18, padx=16)

        # Nav items
        for i, (icon, label, key) in enumerate(self.MENU, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}   {label}",
                anchor="w",
                fg_color="transparent",
                hover_color=HOVER,
                text_color=TEXT_S,
                font=("Arial", 13),
                height=46,
                corner_radius=8,
                command=lambda k=key: self.navigate(k)
            )
            btn.grid(row=i, column=0, padx=10, pady=2, sticky="ew")
            self._btn_refs[key] = btn

        # Spacer
        self.sidebar.grid_rowconfigure(len(self.MENU) + 1, weight=1)

        # Admin info label
        ctk.CTkLabel(
            self.sidebar,
            text=f"👤  {self.user['full_name']}\nAdministrator",
            font=("Arial", 11), text_color=TEXT_S,
            justify="left"
        ).grid(
            row=len(self.MENU) + 2, column=0,
            padx=16, pady=(8, 4), sticky="w"
        )

        # Logout
        ctk.CTkButton(
            self.sidebar,
            text="  🚪   Logout",
            anchor="w",
            fg_color="transparent",
            hover_color="#3D1515",
            text_color="#FF6B6B",
            font=("Arial", 13),
            height=44,
            corner_radius=8,
            command=self._on_close
        ).grid(
            row=len(self.MENU) + 3, column=0,
            padx=10, pady=(0, 16), sticky="ew"
        )

        # ── Content area ──────────────────────────────────────
        self.content = ctk.CTkFrame(
            self, fg_color="#F0F4FA", corner_radius=0
        )
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    # ── Navigation ────────────────────────────────────────────
    def navigate(self, page_key: str):
        # Update sidebar button highlights
        for key, btn in self._btn_refs.items():
            if key == page_key:
                btn.configure(fg_color=ACTIVE, text_color=WHITE)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_S)

        # Destroy current content
        for widget in self.content.winfo_children():
            widget.destroy()

        self._active_page = page_key

        # Load the new page
        try:
            self._load_page(page_key)
        except Exception as e:
            self._show_error(f"Failed to load page '{page_key}':\n\n{e}")

    def _load_page(self, key: str):
        if key == "dashboard":
            from views.admin.dashboard import AdminDashboard
            page = AdminDashboard(self.content, self.user)

        elif key == "customers":
            from views.admin.customer_management import CustomerManagement
            page = CustomerManagement(self.content, self.user)

        elif key == "accounts":
            from views.admin.account_management import AccountManagement
            page = AccountManagement(self.content, self.user)

        elif key == "transactions":
            from views.admin.transactions import TransactionsView
            page = TransactionsView(self.content, self.user)

        elif key == "loans":
            from views.admin.loan_management import LoanManagement
            page = LoanManagement(self.content, self.user)

        elif key == "employees":
            from views.admin.employee_management import EmployeeManagement
            page = EmployeeManagement(self.content, self.user)

        elif key == "settings":
            from views.admin.settings import AdminSettings
            page = AdminSettings(self.content, self.user)

        else:
            self._show_error(f"Unknown page: '{key}'")
            return

        page.pack(fill="both", expand=True)

    def _show_error(self, message: str):
        """Show error message inside content area."""
        frame = ctk.CTkFrame(self.content, fg_color="#F0F4FA")
        frame.pack(fill="both", expand=True)
        ctk.CTkLabel(
            frame,
            text="⚠️  Page Load Error",
            font=("Arial", 18, "bold"),
            text_color="#D32F2F"
        ).pack(pady=(80, 12))
        ctk.CTkLabel(
            frame,
            text=message,
            font=("Arial", 13),
            text_color="#555555",
            wraplength=500,
            justify="center"
        ).pack(pady=(0, 20))
        ctk.CTkButton(
            frame,
            text="🔄 Retry",
            fg_color=BLUE,
            command=lambda: self.navigate(self._active_page)
        ).pack()

    def _on_close(self):
        self.destroy()
        self.login_win.deiconify()