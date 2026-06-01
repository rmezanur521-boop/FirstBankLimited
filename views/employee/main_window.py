import customtkinter as ctk

BLUE    = "#1A73E8"; WHITE = "#FFFFFF"
SIDEBAR = "#1E2A3A"; HOVER = "#2D3F55"
ACTIVE  = "#1A73E8"; TEXT_S = "#A8BDD0"


class EmployeeMainWindow(ctk.CTkToplevel):

    MENU = [
        ("🏠", "Dashboard",    "dashboard"),
        ("👥", "Customers",    "customers"),
        ("🏦", "Accounts",     "accounts"),
        ("💸", "Transactions", "transactions"),
    ]

    def __init__(self, user, login_win):
        super().__init__()
        self.user      = user
        self.login_win = login_win
        self.title("First Bank Limited — Employee Panel")
        self.geometry("1280x740")
        self.minsize(1100, 680)
        ctk.set_appearance_mode("light")
        self._btn_refs = {}
        self._build()
        self._center()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.navigate("dashboard")

    def _center(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 1280) // 2
        y = (self.winfo_screenheight() - 740)  // 2
        self.geometry(f"1280x740+{x}+{y}")

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(
            self, fg_color=SIDEBAR, width=220, corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(len(self.MENU) + 2, weight=1)

        logo_frame = ctk.CTkFrame(
            self.sidebar, fg_color="#151E2B", corner_radius=0
        )
        logo_frame.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            logo_frame, text="🏦 First Bank",
            font=("Arial", 16, "bold"), text_color=WHITE
        ).pack(pady=16, padx=16)

        for i, (icon, label, key) in enumerate(self.MENU, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}  {label}", anchor="w",
                fg_color="transparent", hover_color=HOVER,
                text_color=TEXT_S, font=("Arial", 13),
                height=44, corner_radius=8,
                command=lambda k=key: self.navigate(k)
            )
            btn.grid(row=i, column=0, padx=10, pady=2, sticky="ew")
            self._btn_refs[key] = btn

        ctk.CTkLabel(
            self.sidebar,
            text=f"👤 {self.user['full_name']}\nEmployee",
            font=("Arial", 11), text_color=TEXT_S, justify="left"
        ).grid(row=len(self.MENU) + 2, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkButton(
            self.sidebar, text="  🚪  Logout",
            anchor="w", fg_color="transparent",
            hover_color="#3D1515", text_color="#FF6B6B",
            font=("Arial", 13), height=44, corner_radius=8,
            command=self._on_close
        ).grid(row=len(self.MENU) + 3, column=0,
               padx=10, pady=(0, 16), sticky="ew")

        self.content = ctk.CTkFrame(
            self, fg_color="#F0F4FA", corner_radius=0
        )
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def navigate(self, page_key):
        for key, btn in self._btn_refs.items():
            btn.configure(
                fg_color=ACTIVE if key == page_key else "transparent",
                text_color=WHITE if key == page_key else TEXT_S
            )
        for w in self.content.winfo_children():
            w.destroy()
        if page_key == "dashboard":
            from views.employee.dashboard import EmployeeDashboard
            EmployeeDashboard(self.content, self.user).pack(fill="both", expand=True)
        elif page_key == "customers":
            from views.admin.customer_management import CustomerManagement
            CustomerManagement(self.content, self.user).pack(fill="both", expand=True)
        elif page_key == "accounts":
            from views.admin.account_management import AccountManagement
            AccountManagement(self.content, self.user).pack(fill="both", expand=True)
        elif page_key == "transactions":
            from views.admin.transactions import TransactionsView
            TransactionsView(self.content, self.user).pack(fill="both", expand=True)

    def _on_close(self):
        self.destroy()
        self.login_win.deiconify()