import customtkinter as ctk
from tkinter import filedialog
from config.database import Database
from utils.image_handler import save_logo
from views.shared.widgets import show_message

BLUE  = "#1A73E8"; WHITE = "#FFFFFF"; GRAY = "#F0F4FA"; DARK = "#1E2A3A"
BORDER = "#DDE3EC"


class AdminSettings(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, fg_color=GRAY, corner_radius=0)
        self.user     = user
        self.logo_src = None
        self._settings = self._load_settings()
        self._build()

    def _load_settings(self):
        with Database() as db:
            db.execute(
                "SELECT bank_name, bank_address, bank_phone, bank_email, "
                "logo_path, transfer_fee_same_customer, "
                "transfer_fee_other_customer, default_loan_interest_rate "
                "FROM bank_settings LIMIT 1"
            )
            row = db.fetchone()
            if row:
                return {
                    "bank_name"   : row[0], "bank_address": row[1],
                    "bank_phone"  : row[2], "bank_email"  : row[3],
                    "logo_path"   : row[4],
                    "fee_same"    : row[5], "fee_other"   : row[6],
                    "loan_rate"   : row[7]
                }
        return {}

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(
            top, text="Settings",
            font=("Arial", 20, "bold"), text_color=DARK
        ).pack(side="left", padx=24, pady=16)

        body = ctk.CTkScrollableFrame(self, fg_color=GRAY)
        body.pack(fill="both", expand=True, padx=24, pady=16)
        s = self._settings

        def section(t):
            ctk.CTkLabel(
                body, text=t, font=("Arial", 15, "bold"), text_color=DARK
            ).pack(anchor="w", pady=(16, 6))

        def card():
            f = ctk.CTkFrame(body, fg_color=WHITE, corner_radius=10,
                              border_width=1, border_color=BORDER)
            f.pack(fill="x", pady=4)
            return f

        def row_entry(parent, label, value=""):
            rf = ctk.CTkFrame(parent, fg_color="transparent")
            rf.pack(fill="x", padx=16, pady=6)
            ctk.CTkLabel(
                rf, text=label, font=("Arial", 12, "bold"),
                text_color=DARK, width=200, anchor="w"
            ).pack(side="left")
            e = ctk.CTkEntry(rf, height=36, font=("Arial", 13), width=320)
            e.insert(0, str(value or ""))
            e.pack(side="left")
            return e

        # ── Bank Profile ─────────────────────────────────────
        section("🏦 Bank Profile")
        c1 = card()
        self.e_bname  = row_entry(c1, "Bank Name",    s.get("bank_name",""))
        self.e_baddr  = row_entry(c1, "Address",      s.get("bank_address",""))
        self.e_bphone = row_entry(c1, "Phone",        s.get("bank_phone",""))
        self.e_bemail = row_entry(c1, "Email",        s.get("bank_email",""))

        # Logo
        logo_row = ctk.CTkFrame(c1, fg_color="transparent")
        logo_row.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(
            logo_row, text="Logo", font=("Arial", 12, "bold"),
            text_color=DARK, width=200, anchor="w"
        ).pack(side="left")
        self.logo_label = ctk.CTkLabel(
            logo_row,
            text=s.get("logo_path","No logo") or "No logo set",
            font=("Arial", 11), text_color="#7A8BA0"
        )
        self.logo_label.pack(side="left", padx=(0,10))
        ctk.CTkButton(
            logo_row, text="Browse", width=100, height=32,
            command=self._browse_logo
        ).pack(side="left")

        # ── Fee Settings ─────────────────────────────────────
        section("💸 Transfer Fee Settings")
        c2 = card()
        self.e_fee_same  = row_entry(
            c2, "Fee % (Own→Own A/C)",       s.get("fee_same", 0)
        )
        self.e_fee_other = row_entry(
            c2, "Fee % (Own→Other Customer)", s.get("fee_other", 1.5)
        )

        # ── Loan Settings ─────────────────────────────────────
        section("📋 Loan Settings")
        c3 = card()
        self.e_loan_rate = row_entry(
            c3, "Default Interest Rate %", s.get("loan_rate", 10.0)
        )

        # Save button
        ctk.CTkButton(
            body, text="💾 Save All Settings",
            fg_color=BLUE, font=("Arial", 14, "bold"),
            height=46, command=self._save
        ).pack(fill="x", pady=20)

    def _browse_logo(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if path:
            self.logo_src = path
            self.logo_label.configure(text=path.split("/")[-1])

    def _save(self):
        try:
            fee_same  = float(self.e_fee_same.get().strip())
            fee_other = float(self.e_fee_other.get().strip())
            loan_rate = float(self.e_loan_rate.get().strip())
        except ValueError:
            show_message(self, "Fee and rate must be numbers.", "error")
            return

        logo_path = None
        if self.logo_src:
            logo_path = save_logo(self.logo_src)

        with Database() as db:
            if logo_path:
                db.execute(
                    """UPDATE bank_settings SET
                       bank_name=%s, bank_address=%s, bank_phone=%s,
                       bank_email=%s, logo_path=%s,
                       transfer_fee_same_customer=%s,
                       transfer_fee_other_customer=%s,
                       default_loan_interest_rate=%s,
                       updated_at=CURRENT_TIMESTAMP, updated_by=%s""",
                    (
                        self.e_bname.get().strip(),
                        self.e_baddr.get().strip(),
                        self.e_bphone.get().strip(),
                        self.e_bemail.get().strip(),
                        logo_path, fee_same, fee_other,
                        loan_rate, self.user["id"]
                    )
                )
            else:
                db.execute(
                    """UPDATE bank_settings SET
                       bank_name=%s, bank_address=%s, bank_phone=%s,
                       bank_email=%s,
                       transfer_fee_same_customer=%s,
                       transfer_fee_other_customer=%s,
                       default_loan_interest_rate=%s,
                       updated_at=CURRENT_TIMESTAMP, updated_by=%s""",
                    (
                        self.e_bname.get().strip(),
                        self.e_baddr.get().strip(),
                        self.e_bphone.get().strip(),
                        self.e_bemail.get().strip(),
                        fee_same, fee_other,
                        loan_rate, self.user["id"]
                    )
                )
        show_message(self, "Settings saved successfully!", "success")