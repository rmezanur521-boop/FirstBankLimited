import customtkinter as ctk
from models.account     import AccountModel
from models.transaction import TransactionModel
from utils.helpers import format_currency, format_datetime
from views.shared.widgets import stat_card

BLUE  = "#1A73E8"; WHITE = "#FFFFFF"; GRAY = "#F0F4FA"; DARK = "#1E2A3A"
GREEN = "#2E7D32"; ORANGE = "#E65100"; BORDER = "#DDE3EC"; RED = "#D32F2F"


class CustomerDashboard(ctk.CTkFrame):

    def __init__(self, parent, user, navigate_fn):
        super().__init__(parent, fg_color=GRAY, corner_radius=0)
        self.user        = user
        self.navigate_fn = navigate_fn
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(
            top,
            text=f"Welcome, {self.user['full_name']} 👋",
            font=("Arial", 20, "bold"), text_color=DARK
        ).pack(side="left", padx=24, pady=16)

        body = ctk.CTkScrollableFrame(self, fg_color=GRAY)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        accounts = AccountModel.get_by_customer(self.user["id"])
        total_balance = sum(float(a["balance"]) for a in accounts)

        # Get total deposit/withdraw
        all_txns = []
        for acc in accounts:
            all_txns += TransactionModel.get_by_account(acc["id"], limit=500)

        total_deposit  = sum(
            float(t["amount"]) for t in all_txns
            if t["transaction_type"] == "deposit"
        )
        total_withdraw = sum(
            float(t["amount"]) for t in all_txns
            if t["transaction_type"] == "withdraw"
        )

        # ── Stat cards ─────────────────────────────────────
        row1 = ctk.CTkFrame(body, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 16))
        for title, value, icon, color in [
            ("Total Balance",   format_currency(total_balance),  "💰", BLUE),
            ("Total Deposited", format_currency(total_deposit),  "📥", GREEN),
            ("Total Withdrawn", format_currency(total_withdraw), "📤", ORANGE),
            ("Total Accounts",  len(accounts),                   "🏦", "#6A1B9A"),
        ]:
            card = stat_card(row1, title, value, icon, color)
            card.pack(side="left", fill="both", expand=True, padx=6)

        # ── Account cards ──────────────────────────────────
        ctk.CTkLabel(
            body, text="🏦 My Accounts",
            font=("Arial", 15, "bold"), text_color=DARK
        ).pack(anchor="w", pady=(8, 6))

        if not accounts:
            ctk.CTkLabel(
                body, text="No accounts found.",
                font=("Arial", 13), text_color="#7A8BA0"
            ).pack(anchor="w")
        else:
            acc_row = ctk.CTkFrame(body, fg_color="transparent")
            acc_row.pack(fill="x", pady=(0, 16))
            for acc in accounts:
                ac = ctk.CTkFrame(
                    acc_row, fg_color=WHITE, corner_radius=12,
                    border_width=1, border_color=BORDER
                )
                ac.pack(side="left", fill="both",
                        expand=True, padx=6, pady=4)
                ctk.CTkLabel(
                    ac, text=acc["account_number"],
                    font=("Arial", 13, "bold"), text_color=DARK
                ).pack(anchor="w", padx=14, pady=(14, 2))
                ctk.CTkLabel(
                    ac, text=acc["account_type"],
                    font=("Arial", 11), text_color="#7A8BA0"
                ).pack(anchor="w", padx=14)
                ctk.CTkLabel(
                    ac, text=format_currency(acc["balance"]),
                    font=("Arial", 20, "bold"), text_color=BLUE
                ).pack(anchor="w", padx=14, pady=(4, 14))

        # ── Quick actions ──────────────────────────────────
        ctk.CTkLabel(
            body, text="⚡ Quick Actions",
            font=("Arial", 15, "bold"), text_color=DARK
        ).pack(anchor="w", pady=(8, 6))

        qf = ctk.CTkFrame(body, fg_color="transparent")
        qf.pack(fill="x", pady=(0, 16))
        for label, key, color in [
            ("💸 Send Money",    "fund_transfer",  BLUE),
            ("📜 Transactions",  "txn_history",    GREEN),
            ("📋 Apply for Loan","loans",          ORANGE),
        ]:
            ctk.CTkButton(
                qf, text=label, width=180, height=46,
                fg_color=color, font=("Arial", 13, "bold"),
                corner_radius=10,
                command=lambda k=key: self.navigate_fn(k)
            ).pack(side="left", padx=6)

        # ── Last 5 transactions ────────────────────────────
        ctk.CTkLabel(
            body, text="🕐 Last 5 Transactions",
            font=("Arial", 15, "bold"), text_color=DARK
        ).pack(anchor="w", pady=(8, 6))

        recent = TransactionModel.get_last_5_by_customer(self.user["id"])
        table  = ctk.CTkFrame(body, fg_color=WHITE, corner_radius=10,
                               border_width=1, border_color=BORDER)
        table.pack(fill="x", pady=(0, 20))

        headers = ["Ref", "Type", "Amount", "Net Amount", "Date"]
        widths  = [180, 150, 130, 130, 200]
        hrow    = ctk.CTkFrame(table, fg_color="#EEF2F7", corner_radius=0)
        hrow.pack(fill="x")
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                hrow, text=h, font=("Arial", 12, "bold"),
                text_color=DARK, width=w, anchor="w"
            ).pack(side="left", padx=10, pady=8)

        if not recent:
            ctk.CTkLabel(
                table, text="No transactions yet.",
                font=("Arial", 12), text_color="#7A8BA0"
            ).pack(pady=16)
        else:
            for i, t in enumerate(recent):
                bg  = WHITE if i % 2 == 0 else "#F8FAFD"
                drow = ctk.CTkFrame(table, fg_color=bg, corner_radius=0)
                drow.pack(fill="x")
                ttype = t["transaction_type"]
                color = GREEN if "deposit" in ttype else RED
                for val, w in zip([
                    t["transaction_ref"],
                    ttype.replace("_"," ").title(),
                    format_currency(t["amount"]),
                    format_currency(t["net_amount"]),
                    format_datetime(t["created_at"])
                ], widths):
                    ctk.CTkLabel(
                        drow, text=str(val), font=("Arial", 11),
                        text_color=color if val == format_currency(t["amount"]) else DARK,
                        width=w, anchor="w"
                    ).pack(side="left", padx=10, pady=6)