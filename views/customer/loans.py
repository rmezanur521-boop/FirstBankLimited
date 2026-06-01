import customtkinter as ctk
from models.loan    import LoanModel
from models.account import AccountModel
from controllers.loan_controller import apply_for_loan, calculate_emi
from views.shared.widgets import show_message, confirm_dialog
from utils.helpers import format_currency, format_datetime

BLUE  = "#1A73E8"; WHITE = "#FFFFFF"; GRAY = "#F0F4FA"; DARK = "#1E2A3A"
GREEN = "#2E7D32"; ORANGE = "#E65100"; BORDER = "#DDE3EC"; RED = "#D32F2F"


class CustomerLoans(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, fg_color=GRAY, corner_radius=0)
        self.user = user
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(
            top, text="Loans & Investments",
            font=("Arial", 20, "bold"), text_color=DARK
        ).pack(side="left", padx=24, pady=16)
        ctk.CTkButton(
            top, text="➕ Apply for Loan", width=160, height=36,
            fg_color=BLUE, font=("Arial", 12, "bold"),
            command=self._open_loan_form
        ).pack(side="right", padx=24, pady=14)

        body = ctk.CTkScrollableFrame(self, fg_color=GRAY)
        body.pack(fill="both", expand=True, padx=20, pady=16)
        self._body = body
        self._load_loans(body)

    def _load_loans(self, body):
        for w in body.winfo_children():
            w.destroy()
        loans = LoanModel.get_by_customer(self.user["id"])

        if not loans:
            ctk.CTkLabel(
                body, text="No loan applications yet.",
                font=("Arial", 14), text_color="#7A8BA0"
            ).pack(pady=40)
            return

        for ln in loans:
            status_colors = {
                "pending"  : ORANGE, "approved": GREEN,
                "active"   : BLUE,   "rejected": RED, "closed": "#7A8BA0"
            }
            sc = status_colors.get(ln["status"], DARK)

            card = ctk.CTkFrame(
                body, fg_color=WHITE, corner_radius=12,
                border_width=1, border_color=BORDER
            )
            card.pack(fill="x", pady=8)

            # Header
            hf = ctk.CTkFrame(card, fg_color=sc, corner_radius=0)
            hf.pack(fill="x")
            ctk.CTkLabel(
                hf, text=f"  {ln['loan_ref']}",
                font=("Arial", 14, "bold"), text_color=WHITE
            ).pack(side="left", padx=16, pady=10)
            ctk.CTkLabel(
                hf, text=f"{ln['status'].upper()}  ",
                font=("Arial", 12, "bold"), text_color=WHITE
            ).pack(side="right", padx=16)

            # Details grid
            dg = ctk.CTkFrame(card, fg_color="transparent")
            dg.pack(fill="x", padx=16, pady=12)

            fields = [
                ("Loan Amount",     format_currency(ln["loan_amount"])),
                ("Interest Rate",   f"{ln['interest_rate']}% p.a."),
                ("Tenure",          f"{ln['tenure_months']} months"),
                ("Monthly EMI",     format_currency(ln["emi_amount"])),
                ("Total Payable",   format_currency(
                    float(ln["emi_amount"]) * int(ln["tenure_months"]))),
                ("Amount Paid",     format_currency(ln["amount_paid"])),
                ("Outstanding",     format_currency(ln["outstanding_amount"])),
                ("Account",         ln["account_number"]),
                ("Applied On",      format_datetime(ln["applied_at"])),
            ]
            for i, (k, v) in enumerate(fields):
                col = (i % 3) * 2
                row = i // 3
                ctk.CTkLabel(
                    dg, text=k, font=("Arial", 11),
                    text_color="#7A8BA0", anchor="w"
                ).grid(row=row*2, column=col, padx=12, pady=(6,0), sticky="w")
                ctk.CTkLabel(
                    dg, text=v, font=("Arial", 13, "bold"),
                    text_color=DARK, anchor="w"
                ).grid(row=row*2+1, column=col, padx=12, pady=(0,6), sticky="w")

    def _open_loan_form(self):
        _LoanApplicationForm(self, self.user, on_done=lambda: self._load_loans(self._body))


class _LoanApplicationForm(ctk.CTkToplevel):

    def __init__(self, parent, user, on_done=None):
        super().__init__(parent)
        self.user    = user
        self.on_done = on_done
        self.title("Loan Application")
        self.geometry("560x600")
        self.resizable(False, True)
        self.grab_set()
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(
            scroll, text="📋 New Loan Application",
            font=("Arial", 18, "bold"), text_color=DARK
        ).pack(anchor="w", pady=(0, 16))

        def lbl(t):
            ctk.CTkLabel(
                scroll, text=t, font=("Arial", 12, "bold"),
                text_color=DARK, anchor="w"
            ).pack(fill="x", pady=(8, 2))

        # Account selector
        lbl("Select Account *")
        accounts = AccountModel.get_by_customer(self.user["id"])
        active   = [a for a in accounts if a["status"] == "active"]
        self.acc_map = {
            f"{a['account_number']} — {format_currency(a['balance'])}": a["id"]
            for a in active
        }
        self.acc_var = ctk.StringVar(
            value=list(self.acc_map.keys())[0] if self.acc_map else ""
        )
        ctk.CTkOptionMenu(
            scroll, variable=self.acc_var,
            values=list(self.acc_map.keys()),
            height=38, font=("Arial", 13)
        ).pack(fill="x", pady=2)

        lbl("Loan Amount (৳) *")
        self.e_amount = ctk.CTkEntry(
            scroll, height=38, font=("Arial", 13),
            placeholder_text="e.g. 50000"
        )
        self.e_amount.pack(fill="x")

        lbl("Tenure (Months) *")
        self.e_tenure = ctk.CTkEntry(
            scroll, height=38, font=("Arial", 13),
            placeholder_text="e.g. 12, 24, 36"
        )
        self.e_tenure.pack(fill="x")

        lbl("Purpose")
        self.e_purpose = ctk.CTkTextbox(scroll, height=80, font=("Arial", 13))
        self.e_purpose.pack(fill="x")

        # EMI Preview
        ctk.CTkButton(
            scroll, text="📊 Calculate EMI Preview",
            fg_color="#455A64", font=("Arial", 12),
            height=36, command=self._calc_emi
        ).pack(fill="x", pady=8)

        self.emi_frame = ctk.CTkFrame(
            scroll, fg_color="#F0F4FA", corner_radius=8
        )
        self.emi_frame.pack(fill="x", pady=4)
        self.emi_labels = {}
        for i, key in enumerate(["EMI/Month", "Total Payable", "Total Interest"]):
            ctk.CTkLabel(
                self.emi_frame, text=key,
                font=("Arial", 11), text_color="#7A8BA0"
            ).grid(row=0, column=i, padx=16, pady=6)
            lv = ctk.CTkLabel(
                self.emi_frame, text="—",
                font=("Arial", 14, "bold"), text_color=DARK
            )
            lv.grid(row=1, column=i, padx=16, pady=(0, 8))
            self.emi_labels[key] = lv

        ctk.CTkButton(
            scroll, text="✅ Submit Application",
            fg_color=BLUE, font=("Arial", 13, "bold"),
            height=44, command=self._submit
        ).pack(fill="x", pady=12)

    def _calc_emi(self):
        try:
            amount = float(self.e_amount.get().strip())
            tenure = int(self.e_tenure.get().strip())
        except ValueError:
            show_message(self, "Enter valid amount and tenure.", "error")
            return
        from config.database import Database
        with Database() as db:
            db.execute("SELECT default_loan_interest_rate FROM bank_settings LIMIT 1")
            row  = db.fetchone()
            rate = float(row[0]) if row else 10.0
        try:
            calc = calculate_emi(amount, rate, tenure)
            self.emi_labels["EMI/Month"].configure(
                text=format_currency(calc["emi_amount"])
            )
            self.emi_labels["Total Payable"].configure(
                text=format_currency(calc["total_payable"])
            )
            self.emi_labels["Total Interest"].configure(
                text=format_currency(calc["interest_total"])
            )
        except Exception as e:
            show_message(self, str(e), "error")

    def _submit(self):
        if not self.acc_map:
            show_message(self, "No active accounts found.", "error")
            return
        try:
            amount = float(self.e_amount.get().strip())
            tenure = int(self.e_tenure.get().strip())
        except ValueError:
            show_message(self, "Invalid amount or tenure.", "error")
            return
        if amount <= 0 or tenure <= 0:
            show_message(self, "Amount and tenure must be positive.", "error")
            return

        purpose    = self.e_purpose.get("1.0", "end").strip()
        account_id = self.acc_map.get(self.acc_var.get())

        if not confirm_dialog(
            self,
            f"Submit loan application for {format_currency(amount)} "
            f"over {tenure} months?\n\n"
            "Your application will be reviewed by the bank."
        ):
            return
        try:
            result = apply_for_loan(
                self.user["id"], account_id,
                amount, tenure, purpose
            )
            show_message(
                self,
                f"Application submitted!\nRef: {result['loan_ref']}\n"
                "Status: Pending Review",
                "success"
            )
            self.destroy()
            if self.on_done:
                self.on_done()
        except Exception as e:
            show_message(self, f"Error: {e}", "error")