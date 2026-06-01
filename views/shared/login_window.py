import customtkinter as ctk
from controllers.auth_controller import login, setup_default_admin

BLUE   = "#1A73E8"
WHITE  = "#FFFFFF"
GRAY   = "#F5F7FA"
DARK   = "#1E2A3A"
BORDER = "#DDE3EC"
RED    = "#D32F2F"


class LoginWindow(ctk.CTk):

    def __init__(self):
        super().__init__()
        setup_default_admin()
        self.title("First Bank Limited — Login")
        self.geometry("960x600")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self._build_ui()
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 960) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"960x600+{x}+{y}")

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Left panel ───────────────────────────────────────
        left = ctk.CTkFrame(self, fg_color=BLUE, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_rowconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(
            left, text="🏦", font=("Arial", 64),
            text_color=WHITE
        ).grid(row=0, column=0, pady=(60, 0))

        ctk.CTkLabel(
            left, text="First Bank Limited",
            font=("Arial", 22, "bold"), text_color=WHITE
        ).grid(row=1, column=0, padx=30)

        ctk.CTkLabel(
            left,
            text="Secure • Reliable • Trusted\nYour Financial Partner",
            font=("Arial", 13), text_color="#C8DCFF",
            justify="center"
        ).grid(row=2, column=0, padx=30, pady=(0, 60))

        # ── Right panel ──────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")

        # Tab switcher
        tab_frame = ctk.CTkFrame(right, fg_color="#F0F4FA", corner_radius=0)
        tab_frame.pack(fill="x")

        self._active_tab = ctk.StringVar(value="login")

        self.btn_login = ctk.CTkButton(
            tab_frame, text="Sign In",
            font=("Arial", 13, "bold"), height=44,
            fg_color=WHITE, text_color=BLUE,
            hover_color="#EEF2F7", corner_radius=0,
            command=lambda: self._switch_tab("login")
        )
        self.btn_login.pack(side="left", fill="x", expand=True)

        self.btn_register = ctk.CTkButton(
            tab_frame, text="Register",
            font=("Arial", 13, "bold"), height=44,
            fg_color="#F0F4FA", text_color="#7A8BA0",
            hover_color="#EEF2F7", corner_radius=0,
            command=lambda: self._switch_tab("register")
        )
        self.btn_register.pack(side="left", fill="x", expand=True)

        # Panels container
        self.panels = ctk.CTkFrame(right, fg_color=WHITE, corner_radius=0)
        self.panels.pack(fill="both", expand=True)

        self._login_panel    = self._build_login_panel(self.panels)
        self._register_panel = self._build_register_panel(self.panels)

        self._switch_tab("login")

    def _switch_tab(self, tab):
        self._active_tab.set(tab)
        if tab == "login":
            self._register_panel.pack_forget()
            self._login_panel.pack(fill="both", expand=True)
            self.btn_login.configure(fg_color=WHITE, text_color=BLUE)
            self.btn_register.configure(fg_color="#F0F4FA", text_color="#7A8BA0")
        else:
            self._login_panel.pack_forget()
            self._register_panel.pack(fill="both", expand=True)
            self.btn_register.configure(fg_color=WHITE, text_color=BLUE)
            self.btn_login.configure(fg_color="#F0F4FA", text_color="#7A8BA0")

    # ── LOGIN PANEL ──────────────────────────────────────────
    def _build_login_panel(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=0)

        ctk.CTkLabel(
            frame, text="Welcome Back",
            font=("Arial", 24, "bold"), text_color=DARK
        ).pack(anchor="w", padx=44, pady=(36, 2))

        ctk.CTkLabel(
            frame, text="Sign in to your account",
            font=("Arial", 13), text_color="#7A8BA0"
        ).pack(anchor="w", padx=44, pady=(0, 16))

        # Role selector
        ctk.CTkLabel(
            frame, text="Login As",
            font=("Arial", 12, "bold"), text_color=DARK
        ).pack(anchor="w", padx=44, pady=(0, 4))

        self.role_var = ctk.StringVar(value="customer")
        rf = ctk.CTkFrame(frame, fg_color="transparent")
        rf.pack(anchor="w", padx=44, pady=(0, 12))
        for label, val in [("Customer", "customer"),
                            ("Employee", "employee"),
                            ("Admin",    "admin")]:
            ctk.CTkRadioButton(
                rf, text=label,
                variable=self.role_var, value=val,
                font=("Arial", 12), text_color=DARK
            ).pack(side="left", padx=10)

        ctk.CTkLabel(
            frame, text="Username",
            font=("Arial", 12, "bold"), text_color=DARK
        ).pack(anchor="w", padx=44, pady=(0, 4))
        self.username_entry = ctk.CTkEntry(
            frame, placeholder_text="Enter username",
            height=40, font=("Arial", 13)
        )
        self.username_entry.pack(fill="x", padx=44, pady=(0, 10))

        ctk.CTkLabel(
            frame, text="Password",
            font=("Arial", 12, "bold"), text_color=DARK
        ).pack(anchor="w", padx=44, pady=(0, 4))
        self.password_entry = ctk.CTkEntry(
            frame, placeholder_text="Enter password",
            show="*", height=40, font=("Arial", 13)
        )
        self.password_entry.pack(fill="x", padx=44, pady=(0, 6))

        self.login_error = ctk.CTkLabel(
            frame, text="", font=("Arial", 12), text_color=RED
        )
        self.login_error.pack(anchor="w", padx=44)

        ctk.CTkButton(
            frame, text="Sign In", height=42,
            font=("Arial", 14, "bold"),
            fg_color=BLUE, hover_color="#1558B0",
            command=self._on_login
        ).pack(fill="x", padx=44, pady=(8, 0))

        self.password_entry.bind("<Return>", lambda e: self._on_login())
        self.username_entry.bind("<Return>", lambda e: self._on_login())

        return frame

    # ── REGISTER PANEL ───────────────────────────────────────
    def _build_register_panel(self, parent):
        frame = ctk.CTkScrollableFrame(
            parent, fg_color=WHITE, corner_radius=0
        )

        ctk.CTkLabel(
            frame, text="Create Account",
            font=("Arial", 22, "bold"), text_color=DARK
        ).pack(anchor="w", padx=44, pady=(24, 2))
        ctk.CTkLabel(
            frame, text="Register as a new customer",
            font=("Arial", 13), text_color="#7A8BA0"
        ).pack(anchor="w", padx=44, pady=(0, 16))

        def lbl(t):
            ctk.CTkLabel(
                frame, text=t,
                font=("Arial", 12, "bold"), text_color=DARK
            ).pack(anchor="w", padx=44, pady=(6, 2))

        def ent(placeholder="", show=""):
            e = ctk.CTkEntry(
                frame, placeholder_text=placeholder,
                height=38, font=("Arial", 13), show=show
            )
            e.pack(fill="x", padx=44, pady=(0, 2))
            return e

        lbl("Full Name *");        self.r_name   = ent("Full name")
        lbl("Username *");         self.r_user   = ent("Choose a username")
        lbl("Password *");         self.r_pass   = ent("Min 8 chars, 1 uppercase, 1 digit", "*")
        lbl("Confirm Password *"); self.r_cpass  = ent("Re-enter password", "*")
        lbl("Phone Number *");     self.r_phone  = ent("01XXXXXXXXX")
        lbl("Email");              self.r_email  = ent("email@example.com")
        lbl("Father's Name");      self.r_father = ent("Father's name")
        lbl("Mother's Name");      self.r_mother = ent("Mother's name")
        lbl("Address");            self.r_addr   = ent("Full address")

        self.reg_error = ctk.CTkLabel(
            frame, text="", font=("Arial", 12),
            text_color=RED, wraplength=340
        )
        self.reg_error.pack(anchor="w", padx=44, pady=(4, 0))

        ctk.CTkButton(
            frame, text="✅ Create Account", height=42,
            font=("Arial", 14, "bold"),
            fg_color=BLUE, hover_color="#1558B0",
            command=self._on_register
        ).pack(fill="x", padx=44, pady=(10, 24))

        return frame

    # ── HANDLERS ─────────────────────────────────────────────
    def _on_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role     = self.role_var.get()
        self.login_error.configure(text="")

        if not username or not password:
            self.login_error.configure(text="Please fill in all fields.")
            return

        user = login(username, password, role)
        if not user:
            self.login_error.configure(
                text="Invalid credentials or account inactive."
            )
            return

        self.withdraw()
        self._open_panel(user)

    def _on_register(self):
        from utils.helpers import validate_phone, validate_password
        from controllers.customer_controller import register_customer

        self.reg_error.configure(text="")

        name   = self.r_name.get().strip()
        uname  = self.r_user.get().strip()
        pw     = self.r_pass.get().strip()
        cpw    = self.r_cpass.get().strip()
        phone  = self.r_phone.get().strip()
        email  = self.r_email.get().strip() or None
        father = self.r_father.get().strip() or None
        mother = self.r_mother.get().strip() or None
        addr   = self.r_addr.get().strip()   or None

        if not name or not uname or not pw or not phone:
            self.reg_error.configure(
                text="Name, username, password and phone are required."
            )
            return
        if pw != cpw:
            self.reg_error.configure(text="Passwords do not match.")
            return
        if not validate_password(pw):
            self.reg_error.configure(
                text="Password must be 8+ chars with 1 uppercase & 1 digit."
            )
            return
        if not validate_phone(phone):
            self.reg_error.configure(
                text="Invalid phone number (e.g. 01XXXXXXXXX)."
            )
            return

        try:
            cust_id = register_customer(
                {
                    "full_name"  : name,
                    "username"   : uname,
                    "password"   : pw,
                    "phone"      : phone,
                    "email"      : email,
                    "father_name": father,
                    "mother_name": mother,
                    "address"    : addr,
                },
                photo_src=None,
                doc_src=None,
                created_by_admin=None,
                created_by_employee=None
            )
            # Clear fields
            for e in [self.r_name, self.r_user, self.r_pass,
                      self.r_cpass, self.r_phone, self.r_email,
                      self.r_father, self.r_mother, self.r_addr]:
                e.delete(0, "end")

            self.reg_error.configure(
                text=f"✅ Account created! You can now sign in.",
                text_color="#2E7D32"
            )
            self._switch_tab("login")
        except Exception as e:
            self.reg_error.configure(text=f"Error: {e}")

    def _open_panel(self, user):
        role = user["role"]
        if role == "admin":
            from views.admin.main_window import AdminMainWindow
            AdminMainWindow(user, self)
        elif role == "employee":
            from views.employee.main_window import EmployeeMainWindow
            EmployeeMainWindow(user, self)
        else:
            from views.customer.main_window import CustomerMainWindow
            CustomerMainWindow(user, self)