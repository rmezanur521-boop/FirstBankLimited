import customtkinter as ctk
from models.loan import LoanModel
from controllers.loan_controller import approve_loan, reject_loan
from views.shared.widgets import show_message, confirm_dialog
from utils.helpers import format_currency, format_datetime

BLUE   = "#1A73E8"
WHITE  = "#FFFFFF"
GRAY   = "#F0F4FA"
DARK   = "#1E2A3A"
GREEN  = "#2E7D32"
RED    = "#D32F2F"
ORANGE = "#E65100"
BORDER = "#DDE3EC"


class LoanManagement(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, fg_color=GRAY, corner_radius=0)
        self.user            = user
        self._current_filter = "pending"
        self._filter_btns    = {}
        self._build()

    def _build(self):
        # ── Top bar ───────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(
            top, text="Loan Management",
            font=("Arial", 20, "bold"), text_color=DARK
        ).pack(side="left", padx=24, pady=16)
        ctk.CTkButton(
            top, text="🔄 Refresh", width=100,
            fg_color=BLUE, font=("Arial", 12),
            command=lambda: self._load(self._current_filter)
        ).pack(side="right", padx=24, pady=16)

        # ── Filter buttons ────────────────────────────────────
        filter_bar = ctk.CTkFrame(
            self, fg_color=WHITE, corner_radius=0, height=52
        )
        filter_bar.pack(fill="x")
        filter_bar.pack_propagate(False)

        for label, val in [
            ("⏳ Pending",  "pending"),
            ("✅ Active",   "active"),
            ("👍 Approved", "approved"),
            ("❌ Rejected", "rejected"),
            ("📋 All",      "all"),
        ]:
            is_default = (val == "pending")
            btn = ctk.CTkButton(
                filter_bar, text=label,
                width=110, height=34,
                font=("Arial", 12, "bold"),
                corner_radius=6,
                fg_color=BLUE      if is_default else "#EEF2F7",
                text_color=WHITE   if is_default else DARK,
                hover_color="#1558B0" if is_default else "#DDE3EC",
                command=lambda v=val: self._on_filter_click(v)
            )
            btn.pack(side="left", padx=5, pady=9)
            self._filter_btns[val] = btn

        # ── Summary strip ─────────────────────────────────────
        summary_bar = ctk.CTkFrame(
            self, fg_color="#EEF2F7", corner_radius=0, height=36
        )
        summary_bar.pack(fill="x")
        summary_bar.pack_propagate(False)
        self.summary_label = ctk.CTkLabel(
            summary_bar, text="",
            font=("Arial", 12), text_color=DARK
        )
        self.summary_label.pack(side="left", padx=20, pady=6)

        # ── Table area ────────────────────────────────────────
        self.table_frame = ctk.CTkScrollableFrame(
            self, fg_color=WHITE, corner_radius=10,
            border_width=1, border_color=BORDER
        )
        self.table_frame.pack(
            fill="both", expand=True, padx=20, pady=12
        )

        # Load pending on startup
        self._load("pending")

    # ── Filter click ──────────────────────────────────────────
    def _on_filter_click(self, val):
        for key, btn in self._filter_btns.items():
            if key == val:
                btn.configure(
                    fg_color=BLUE, text_color=WHITE,
                    hover_color="#1558B0"
                )
            else:
                btn.configure(
                    fg_color="#EEF2F7", text_color=DARK,
                    hover_color="#DDE3EC"
                )
        self._current_filter = val
        self._load(val)

    # ── Load loans ────────────────────────────────────────────
    def _load(self, status=None):
        for w in self.table_frame.winfo_children():
            w.destroy()

        query_status = None if status == "all" else status
        loans        = LoanModel.get_all(status=query_status)

        total = sum(float(ln["loan_amount"]) for ln in loans)
        self.summary_label.configure(
            text=f"  {len(loans)} loan(s) found   |   "
                 f"Total Amount: {format_currency(total)}"
        )

        if not loans:
            ctk.CTkLabel(
                self.table_frame,
                text="📭  No loan applications found.",
                font=("Arial", 14), text_color="#7A8BA0"
            ).pack(expand=True, pady=80)
            return

        self._render_table(loans)

    # ── Render table ──────────────────────────────────────────
    def _render_table(self, loans):
        headers = [
            "Loan Ref", "Customer", "Account",
            "Amount", "Rate", "Tenure",
            "EMI", "Outstanding", "Status",
            "Applied On", "Actions"
        ]
        widths = [140, 150, 130, 110, 60, 70, 110, 120, 100, 140, 180]

        # Header row
        hrow = ctk.CTkFrame(
            self.table_frame, fg_color="#EEF2F7", corner_radius=0
        )
        hrow.pack(fill="x")
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                hrow, text=h,
                font=("Arial", 11, "bold"), text_color=DARK,
                width=w, anchor="w"
            ).pack(side="left", padx=5, pady=8)

        # Data rows
        for i, ln in enumerate(loans):
            bg = WHITE if i % 2 == 0 else "#F8FAFD"
            row = ctk.CTkFrame(
                self.table_frame, fg_color=bg, corner_radius=0
            )
            row.pack(fill="x")

            status_colors = {
                "pending" : ORANGE,
                "approved": GREEN,
                "active"  : BLUE,
                "rejected": RED,
                "closed"  : "#7A8BA0"
            }
            sc = status_colors.get(ln["status"], DARK)

            # Data cells
            vals = [
                ln["loan_ref"],
                ln["customer_name"],
                ln["account_number"],
                format_currency(ln["loan_amount"]),
                f"{ln['interest_rate']}%",
                f"{ln['tenure_months']}m",
                format_currency(ln["emi_amount"]),
                format_currency(ln["outstanding_amount"]),
            ]
            for val, w in zip(vals, widths[:8]):
                ctk.CTkLabel(
                    row, text=str(val),
                    font=("Arial", 11), text_color=DARK,
                    width=w, anchor="w"
                ).pack(side="left", padx=5, pady=7)

            # Status badge
            ctk.CTkLabel(
                row,
                text=f"  {ln['status'].upper()}  ",
                font=("Arial", 10, "bold"),
                text_color=WHITE,
                fg_color=sc,
                corner_radius=6,
                width=widths[8],
                anchor="center"
            ).pack(side="left", padx=5, pady=7)

            # Applied on
            ctk.CTkLabel(
                row,
                text=format_datetime(ln["applied_at"]),
                font=("Arial", 11), text_color=DARK,
                width=widths[9], anchor="w"
            ).pack(side="left", padx=5, pady=7)

            # Actions
            act = ctk.CTkFrame(row, fg_color="transparent")
            act.pack(side="left", padx=6, pady=4)

            if ln["status"] == "pending":
                ctk.CTkButton(
                    act, text="✅ Approve",
                    width=86, height=30,
                    fg_color=GREEN, hover_color="#1B5E20",
                    font=("Arial", 11, "bold"), corner_radius=6,
                    command=lambda lid=ln["id"]: self._approve(lid)
                ).pack(side="left", padx=2)

                ctk.CTkButton(
                    act, text="❌ Reject",
                    width=78, height=30,
                    fg_color=RED, hover_color="#B71C1C",
                    font=("Arial", 11, "bold"), corner_radius=6,
                    command=lambda lid=ln["id"]: self._reject(lid)
                ).pack(side="left", padx=2)

            elif ln["status"] in ("active", "approved"):
                ctk.CTkButton(
                    act, text="📄 Details",
                    width=80, height=30,
                    fg_color=BLUE, hover_color="#1558B0",
                    font=("Arial", 11), corner_radius=6,
                    command=lambda lid=ln["id"]: self._view_detail(lid)
                ).pack(side="left", padx=2)

            else:
                ctk.CTkLabel(
                    act, text="—",
                    font=("Arial", 12), text_color="#AAAAAA"
                ).pack(side="left", padx=10)

    # ── Approve ───────────────────────────────────────────────
    def _approve(self, loan_id):
        loan = LoanModel.get_by_id(loan_id)
        if not loan:
            show_message(self, "Loan record not found.", "error")
            return

        msg = (
            f"Approve this loan?\n\n"
            f"  Customer   : {loan['customer_name']}\n"
            f"  Ref        : {loan['loan_ref']}\n"
            f"  Amount     : {format_currency(loan['loan_amount'])}\n"
            f"  Interest   : {loan['interest_rate']}% p.a.\n"
            f"  Tenure     : {loan['tenure_months']} months\n"
            f"  Monthly EMI: {format_currency(loan['emi_amount'])}\n\n"
            f"Amount will be credited to the customer's account immediately."
        )
        if not confirm_dialog(self, msg):
            return

        try:
            approve_loan(loan_id, self.user["id"])
            show_message(
                self,
                f"✅ Loan approved successfully!\n\n"
                f"{format_currency(loan['loan_amount'])} credited to "
                f"account {loan['account_number']}.",
                "success"
            )
            self._load(self._current_filter)
        except Exception as e:
            show_message(self, f"Approval failed: {e}", "error")

    # ── Reject ────────────────────────────────────────────────
    def _reject(self, loan_id):
        loan = LoanModel.get_by_id(loan_id)
        if not loan:
            show_message(self, "Loan record not found.", "error")
            return
        _RejectDialog(
            self, loan, self.user,
            on_done=lambda: self._load(self._current_filter)
        )

    # ── View detail ───────────────────────────────────────────
    def _view_detail(self, loan_id):
        loan = LoanModel.get_by_id(loan_id)
        if not loan:
            show_message(self, "Loan record not found.", "error")
            return
        _LoanDetailPopup(self, loan)


# ── Reject Dialog ─────────────────────────────────────────────
class _RejectDialog(ctk.CTkToplevel):

    def __init__(self, parent, loan, user, on_done=None):
        super().__init__(parent)
        self.loan    = loan
        self.user    = user
        self.on_done = on_done
        self.title("Reject Loan")
        self.geometry("460x320")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text="❌  Reject Loan Application",
            font=("Arial", 16, "bold"), text_color=DARK
        ).pack(pady=(24, 4))

        ctk.CTkLabel(
            self,
            text=f"{self.loan['customer_name']}  —  "
                 f"{format_currency(self.loan['loan_amount'])}",
            font=("Arial", 13), text_color="#7A8BA0"
        ).pack(pady=(0, 12))

        ctk.CTkLabel(
            self, text="Reason for Rejection *",
            font=("Arial", 12, "bold"), text_color=DARK
        ).pack(anchor="w", padx=28)

        self.reason_box = ctk.CTkTextbox(
            self, height=90, font=("Arial", 13)
        )
        self.reason_box.pack(padx=28, fill="x", pady=8)

        ctk.CTkButton(
            self, text="❌  Confirm Rejection",
            fg_color=RED, hover_color="#B71C1C",
            font=("Arial", 13, "bold"),
            height=42, command=self._confirm
        ).pack(padx=28, fill="x", pady=(4, 6))

        ctk.CTkButton(
            self, text="Cancel",
            fg_color="#7A8BA0",
            font=("Arial", 12),
            height=36, command=self.destroy
        ).pack(padx=28, fill="x")

    def _confirm(self):
        reason = self.reason_box.get("1.0", "end").strip()
        if not reason:
            show_message(self, "Please provide a rejection reason.", "error")
            return
        try:
            reject_loan(self.loan["id"], self.user["id"], reason)
            show_message(self, "Loan application rejected.", "info")
            self.destroy()
            if self.on_done:
                self.on_done()
        except Exception as e:
            show_message(self, f"Error: {e}", "error")


# ── Loan Detail Popup ─────────────────────────────────────────
class _LoanDetailPopup(ctk.CTkToplevel):

    def __init__(self, parent, loan):
        super().__init__(parent)
        self.loan = loan
        self.title(f"Loan Detail — {loan['loan_ref']}")
        self.geometry("500x520")
        self.resizable(False, True)
        self.grab_set()
        self._build()

    def _build(self):
        ln = self.loan
        sc = {
            "pending": ORANGE, "approved": GREEN,
            "active" : BLUE,   "rejected": RED,
            "closed" : "#7A8BA0"
        }.get(ln["status"], DARK)

        banner = ctk.CTkFrame(self, fg_color=sc, corner_radius=0)
        banner.pack(fill="x")
        ctk.CTkLabel(
            banner,
            text=f"  {ln['loan_ref']}   —   {ln['status'].upper()}",
            font=("Arial", 15, "bold"), text_color=WHITE
        ).pack(side="left", padx=20, pady=12)

        scroll = ctk.CTkScrollableFrame(self, fg_color=WHITE)
        scroll.pack(fill="both", expand=True, padx=20, pady=16)

        fields = [
            ("Customer",         ln["customer_name"]),
            ("Account No.",      ln["account_number"]),
            ("Loan Amount",      format_currency(ln["loan_amount"])),
            ("Interest Rate",    f"{ln['interest_rate']}% per annum"),
            ("Tenure",           f"{ln['tenure_months']} months"),
            ("Monthly EMI",      format_currency(ln["emi_amount"])),
            ("Total Payable",    format_currency(ln["total_payable"])),
            ("Amount Paid",      format_currency(ln["amount_paid"])),
            ("Outstanding",      format_currency(ln["outstanding_amount"])),
            ("Purpose",          ln.get("purpose") or "—"),
            ("Applied On",       format_datetime(ln["applied_at"])),
            ("Rejection Reason", ln.get("rejection_reason") or "—"),
        ]
        for i, (k, v) in enumerate(fields):
            bg = WHITE if i % 2 == 0 else "#F8FAFD"
            row = ctk.CTkFrame(scroll, fg_color=bg, corner_radius=0)
            row.pack(fill="x")
            ctk.CTkLabel(
                row, text=k,
                font=("Arial", 12, "bold"), text_color="#7A8BA0",
                width=160, anchor="w"
            ).pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(
                row, text=str(v),
                font=("Arial", 12), text_color=DARK,
                anchor="w", wraplength=280
            ).pack(side="left", padx=12, pady=8)

        ctk.CTkButton(
            self, text="Close", width=120,
            fg_color="#7A8BA0", command=self.destroy
        ).pack(pady=(0, 16))