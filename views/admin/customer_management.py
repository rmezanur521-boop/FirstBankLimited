import customtkinter as ctk
from tkinter import filedialog
from models.customer    import CustomerModel
from controllers.customer_controller import (
    register_customer, update_customer, get_customer_full_profile
)
from views.shared.widgets import (
    show_message, confirm_dialog, primary_button, danger_button
)
from utils.helpers import format_currency, format_datetime

BLUE  = "#1A73E8"
WHITE = "#FFFFFF"
GRAY  = "#F0F4FA"
DARK  = "#1E2A3A"
BORDER= "#DDE3EC"
RED   = "#D32F2F"


class CustomerManagement(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, fg_color=GRAY, corner_radius=0)
        self.user = user
        self._build()

    def _build(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(
            top, text="Customer Management",
            font=("Arial", 20, "bold"), text_color=DARK
        ).pack(side="left", padx=24, pady=16)
        primary_button(top, "➕ Add Customer",
                       self._open_add_form, width=160).pack(
            side="right", padx=24, pady=14)

        # Search bar
        sf = ctk.CTkFrame(self, fg_color=WHITE,
                           corner_radius=0, height=52)
        sf.pack(fill="x")
        sf.pack_propagate(False)
        self.search_var = ctk.StringVar()
        ctk.CTkEntry(
            sf, textvariable=self.search_var,
            placeholder_text="🔍  Search by name, phone or username…",
            width=380, height=36, font=("Arial", 13)
        ).pack(side="left", padx=20, pady=8)
        ctk.CTkButton(
            sf, text="Search", width=90, height=36,
            fg_color=BLUE, command=self._search
        ).pack(side="left", pady=8)
        ctk.CTkButton(
            sf, text="Clear", width=80, height=36,
            fg_color="#7A8BA0", command=self._load_all
        ).pack(side="left", padx=6, pady=8)

        # Table area
        self.table_frame = ctk.CTkScrollableFrame(
            self, fg_color=WHITE, corner_radius=10,
            border_width=1, border_color=BORDER
        )
        self.table_frame.pack(fill="both", expand=True,
                               padx=20, pady=16)
        self._load_all()

    # ── Data loading ─────────────────────────────────────────
    def _load_all(self):
        self.search_var.set("")
        customers = CustomerModel.get_all()
        self._render_table(customers)

    def _search(self):
        kw = self.search_var.get().strip()
        if not kw:
            self._load_all()
            return
        from models.customer import CustomerModel as CM
        customers = CM.search(kw)
        self._render_table(customers)

    def _render_table(self, customers):
        for w in self.table_frame.winfo_children():
            w.destroy()

        headers = ["ID", "Full Name", "Username", "Phone",
                   "Accounts", "Status", "KYC", "Actions"]
        widths  = [50, 180, 130, 120, 80, 80, 60, 200]

        hrow = ctk.CTkFrame(self.table_frame,
                             fg_color="#EEF2F7", corner_radius=0)
        hrow.pack(fill="x")
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                hrow, text=h, font=("Arial", 12, "bold"),
                text_color=DARK, width=w, anchor="w"
            ).pack(side="left", padx=6, pady=8)

        if not customers:
            ctk.CTkLabel(
                self.table_frame,
                text="No customers found.",
                font=("Arial", 13), text_color="#7A8BA0"
            ).pack(pady=30)
            return

        for i, c in enumerate(customers):
            bg = WHITE if i % 2 == 0 else "#F8FAFD"
            row = ctk.CTkFrame(self.table_frame,
                                fg_color=bg, corner_radius=0)
            row.pack(fill="x")

            vals = [
                c["id"], c["full_name"], c["username"],
                c["phone"], c["account_count"],
                "Active" if c["is_active"] else "Inactive",
                "✅" if c["kyc_verified"] else "❌"
            ]
            for val, w in zip(vals, widths[:-1]):
                ctk.CTkLabel(
                    row, text=str(val),
                    font=("Arial", 11), text_color=DARK,
                    width=w, anchor="w"
                ).pack(side="left", padx=6, pady=6)

            # Action buttons
            act = ctk.CTkFrame(row, fg_color="transparent")
            act.pack(side="left", padx=4)
            ctk.CTkButton(
                act, text="View", width=56, height=28,
                fg_color=BLUE, font=("Arial", 11),
                command=lambda cid=c["id"]: self._view_customer(cid)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                act, text="Edit", width=52, height=28,
                fg_color="#388E3C", font=("Arial", 11),
                command=lambda cid=c["id"]: self._edit_customer(cid)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                act, text="Del", width=46, height=28,
                fg_color=RED, font=("Arial", 11),
                command=lambda cid=c["id"]: self._delete_customer(cid)
            ).pack(side="left", padx=2)

    # ── Actions ──────────────────────────────────────────────
    def _view_customer(self, cust_id):
        profile = get_customer_full_profile(cust_id)
        if not profile:
            show_message(self, "Customer not found.", "error")
            return
        _CustomerDetailPopup(self, profile)

    def _open_add_form(self):
        _CustomerForm(self, self.user, on_save=self._load_all)

    def _edit_customer(self, cust_id):
        cust = CustomerModel.get_by_id(cust_id)
        if not cust:
            show_message(self, "Not found.", "error")
            return
        _CustomerForm(self, self.user,
                      customer=cust, on_save=self._load_all)

    def _delete_customer(self, cust_id):
        if confirm_dialog(self, "Are you sure you want to delete this customer?\n"
                                "All related accounts will also be deleted."):
            try:
                CustomerModel.delete(cust_id)
                show_message(self, "Customer deleted.", "success")
                self._load_all()
            except Exception as e:
                show_message(self, f"Error: {e}", "error")


# ── Customer Form Popup ───────────────────────────────────────
class _CustomerForm(ctk.CTkToplevel):

    def __init__(self, parent, user, customer=None, on_save=None):
        super().__init__(parent)
        self.user      = user
        self.customer  = customer
        self.on_save   = on_save
        self.photo_src = None
        self.doc_src   = None
        self.is_edit   = customer is not None
        self.title("Edit Customer" if self.is_edit else "Add New Customer")
        self.geometry("680x700")
        self.resizable(False, True)
        self.grab_set()
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        def lbl(t):
            ctk.CTkLabel(
                scroll, text=t, font=("Arial", 12, "bold"),
                text_color=DARK, anchor="w"
            ).pack(fill="x", pady=(8, 2))

        def entry(var=None, placeholder="", show=""):
            e = ctk.CTkEntry(
                scroll, height=38, font=("Arial", 13),
                placeholder_text=placeholder, show=show
            )
            e.pack(fill="x")
            if var and self.customer:
                val = self.customer.get(var, "") or ""
                e.insert(0, str(val))
            return e

        lbl("Full Name *")
        self.e_name = entry("full_name", "Full name")

        lbl("Username *")
        self.e_user = entry("username", "Username")
        if self.is_edit:
            self.e_user.configure(state="disabled")

        if not self.is_edit:
            lbl("Password *")
            self.e_pass = entry(placeholder="Min 8 chars, 1 uppercase, 1 digit",
                                 show="*")

        lbl("Father's Name")
        self.e_father = entry("father_name", "Father's name")

        lbl("Mother's Name")
        self.e_mother = entry("mother_name", "Mother's name")

        lbl("Date of Birth (YYYY-MM-DD)")
        self.e_dob = entry("date_of_birth", "e.g. 1990-01-15")

        lbl("Gender")
        self.gender_var = ctk.StringVar(
            value=self.customer.get("gender", "Male") if self.is_edit else "Male"
        )
        gf = ctk.CTkFrame(scroll, fg_color="transparent")
        gf.pack(fill="x", pady=2)
        for g in ["Male", "Female", "Other"]:
            ctk.CTkRadioButton(
                gf, text=g, variable=self.gender_var, value=g
            ).pack(side="left", padx=8)

        lbl("Phone *")
        self.e_phone = entry("phone", "01XXXXXXXXX")

        lbl("Email")
        self.e_email = entry("email", "email@example.com")

        lbl("Address")
        self.e_address = entry("address", "Full address")

        lbl("City")
        self.e_city = entry("city", "City")

        lbl("ID Type")
        self.id_type_var = ctk.StringVar(
            value=self.customer.get("id_type", "NID") if self.is_edit else "NID"
        )
        idf = ctk.CTkFrame(scroll, fg_color="transparent")
        idf.pack(fill="x", pady=2)
        for t in ["NID", "Passport", "Birth Certificate"]:
            ctk.CTkRadioButton(
                idf, text=t, variable=self.id_type_var, value=t
            ).pack(side="left", padx=8)

        lbl("ID Number")
        self.e_idnum = entry("id_number", "ID number")

        # KYC verified (admin only toggle)
        self.kyc_var = ctk.BooleanVar(
            value=self.customer.get("kyc_verified", False) if self.is_edit else False
        )
        ctk.CTkCheckBox(
            scroll, text="KYC Verified",
            variable=self.kyc_var,
            font=("Arial", 12)
        ).pack(anchor="w", pady=6)

        self.active_var = ctk.BooleanVar(
            value=self.customer.get("is_active", True) if self.is_edit else True
        )
        ctk.CTkCheckBox(
            scroll, text="Active",
            variable=self.active_var,
            font=("Arial", 12)
        ).pack(anchor="w", pady=2)

        # Photo upload
        lbl("Passport Size Photo")
        pf = ctk.CTkFrame(scroll, fg_color="transparent")
        pf.pack(fill="x", pady=2)
        self.photo_label = ctk.CTkLabel(
            pf, text="No file selected",
            font=("Arial", 11), text_color="#7A8BA0"
        )
        self.photo_label.pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            pf, text="Browse Photo", width=120, height=32,
            command=self._browse_photo
        ).pack(side="left")

        # Document upload
        lbl("ID Document (NID / Passport / Birth Cert) *")
        df = ctk.CTkFrame(scroll, fg_color="transparent")
        df.pack(fill="x", pady=2)
        self.doc_label = ctk.CTkLabel(
            df, text="No file selected",
            font=("Arial", 11), text_color="#7A8BA0"
        )
        self.doc_label.pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            df, text="Browse Document", width=140, height=32,
            command=self._browse_doc
        ).pack(side="left")

        # Save button
        ctk.CTkButton(
            scroll, text="💾 Save Customer",
            fg_color=BLUE, font=("Arial", 13, "bold"),
            height=42, command=self._save
        ).pack(fill="x", pady=16)

    def _browse_photo(self):
        path = filedialog.askopenfilename(
            title="Select Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if path:
            self.photo_src = path
            self.photo_label.configure(text=path.split("/")[-1])

    def _browse_doc(self):
        path = filedialog.askopenfilename(
            title="Select ID Document",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"),
                       ("PDF files", "*.pdf")]
        )
        if path:
            self.doc_src = path
            self.doc_label.configure(text=path.split("/")[-1])

    def _save(self):
        from utils.helpers import validate_phone, validate_password
        name  = self.e_name.get().strip()
        phone = self.e_phone.get().strip()

        if not name or not phone:
            show_message(self, "Name and phone are required.", "error")
            return
        if not validate_phone(phone):
            show_message(self, "Invalid phone number (01XXXXXXXXX).", "error")
            return
        if not self.is_edit and not self.doc_src:
            show_message(self, "ID document is required.", "error")
            return

        data = {
            "full_name"  : name,
            "username"   : self.e_user.get().strip(),
            "father_name": self.e_father.get().strip(),
            "mother_name": self.e_mother.get().strip(),
            "date_of_birth": self.e_dob.get().strip() or None,
            "gender"     : self.gender_var.get(),
            "phone"      : phone,
            "email"      : self.e_email.get().strip() or None,
            "address"    : self.e_address.get().strip(),
            "city"       : self.e_city.get().strip(),
            "id_type"    : self.id_type_var.get(),
            "id_number"  : self.e_idnum.get().strip(),
            "kyc_verified": self.kyc_var.get(),
            "is_active"  : self.active_var.get()
        }

        try:
            if self.is_edit:
                update_customer(
                    self.customer["id"], data,
                    self.photo_src, self.doc_src
                )
                show_message(self, "Customer updated.", "success")
            else:
                pw = self.e_pass.get().strip()
                if not validate_password(pw):
                    show_message(
                        self,
                        "Password must be 8+ chars with 1 uppercase & 1 digit.",
                        "error"
                    )
                    return
                data["password"] = pw
                register_customer(
                    data,
                    photo_src=self.photo_src,
                    doc_src=self.doc_src,
                    created_by_admin=self.user["id"]
                )
                show_message(self, "Customer created successfully.", "success")
            self.destroy()
            if self.on_save:
                self.on_save()
        except Exception as e:
            show_message(self, f"Error: {e}", "error")


# ── Customer Detail Popup ─────────────────────────────────────
class _CustomerDetailPopup(ctk.CTkToplevel):

    def __init__(self, parent, profile):
        super().__init__(parent)
        self.profile = profile
        self.title(f"Customer — {profile['full_name']}")
        self.geometry("760x640")
        self.grab_set()
        self._build()

    def _build(self):
        nb = ctk.CTkTabview(self, fg_color="white")
        nb.pack(fill="both", expand=True, padx=16, pady=16)

        # Tab 1: Profile
        t1 = nb.add("👤 Profile")
        p  = self.profile
        fields = [
            ("Full Name",    p["full_name"]),
            ("Username",     p["username"]),
            ("Father Name",  p.get("father_name", "—")),
            ("Mother Name",  p.get("mother_name", "—")),
            ("DOB",          str(p.get("date_of_birth","—"))),
            ("Gender",       p.get("gender","—")),
            ("Phone",        p["phone"]),
            ("Email",        p.get("email","—")),
            ("Address",      p.get("address","—")),
            ("ID Type",      p.get("id_type","—")),
            ("ID Number",    p.get("id_number","—")),
            ("KYC Verified", "Yes" if p.get("kyc_verified") else "No"),
            ("Status",       "Active" if p.get("is_active") else "Inactive"),
            ("Created At",   format_datetime(p.get("created_at"))),
        ]
        sf = ctk.CTkScrollableFrame(t1, fg_color="white")
        sf.pack(fill="both", expand=True)
        for i, (k, v) in enumerate(fields):
            bg = WHITE if i % 2 == 0 else "#F8FAFD"
            row = ctk.CTkFrame(sf, fg_color=bg, corner_radius=0)
            row.pack(fill="x")
            ctk.CTkLabel(
                row, text=k, font=("Arial", 12, "bold"),
                text_color=DARK, width=160, anchor="w"
            ).pack(side="left", padx=12, pady=6)
            ctk.CTkLabel(
                row, text=str(v), font=("Arial", 12),
                text_color=DARK, anchor="w"
            ).pack(side="left", padx=12, pady=6)

        # Tab 2: Accounts
        t2 = nb.add("🏦 Accounts")
        af = ctk.CTkScrollableFrame(t2, fg_color="white")
        af.pack(fill="both", expand=True)
        for acc in p.get("accounts", []):
            card = ctk.CTkFrame(af, fg_color="#F0F4FA",
                                 corner_radius=8, border_width=1,
                                 border_color=BORDER)
            card.pack(fill="x", padx=10, pady=6)
            ctk.CTkLabel(
                card,
                text=f"  {acc['account_number']}  |  {acc['account_type']}  "
                     f"|  Balance: {format_currency(acc['balance'])}  "
                     f"|  {acc['status'].upper()}",
                font=("Arial", 12), text_color=DARK
            ).pack(anchor="w", padx=10, pady=10)

        # Tab 3: Transactions
        t3 = nb.add("💸 Recent Txns")
        tf = ctk.CTkScrollableFrame(t3, fg_color="white")
        tf.pack(fill="both", expand=True)
        for tx in p.get("recent_txns", []):
            ctk.CTkLabel(
                tf,
                text=f"  {tx['transaction_ref']}  |  "
                     f"{tx['transaction_type']}  |  "
                     f"{format_currency(tx['amount'])}  |  "
                     f"{format_datetime(tx['created_at'])}",
                font=("Arial", 11), text_color=DARK
            ).pack(anchor="w", padx=10, pady=4)