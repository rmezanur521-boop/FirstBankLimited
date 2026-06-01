import customtkinter as ctk
from models.admin   import AdminModel
from utils.helpers  import format_currency, format_datetime
from views.shared.widgets import stat_card

BLUE   = "#1A73E8"
WHITE  = "#FFFFFF"
GRAY   = "#F0F4FA"
DARK   = "#1E2A3A"
GREEN  = "#2E7D32"
ORANGE = "#E65100"
BORDER = "#DDE3EC"


class AdminDashboard(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, fg_color="#F0F4FA", corner_radius=0)
        self.user = user
        self._build()

    def _build(self):
        # ── Top bar ──────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="white",
                            corner_radius=0, height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(
            top, text="Dashboard",
            font=("Arial", 20, "bold"), text_color="#1E2A3A"
        ).pack(side="left", padx=24, pady=16)
        ctk.CTkButton(
            top, text="🔄 Refresh", width=100,
            fg_color=BLUE, font=("Arial", 12),
            command=self._refresh
        ).pack(side="right", padx=24, pady=16)

        # ── Scrollable body ───────────────────────────────────
        body = ctk.CTkScrollableFrame(self, fg_color="#F0F4FA")
        body.pack(fill="both", expand=True, padx=20, pady=16)
        self._body = body
        self._populate(body)

    def _refresh(self):
        for w in self._body.winfo_children():
            w.destroy()
        self._populate(self._body)

    def _populate(self, body):
        stats = AdminModel.get_dashboard_stats()

        ctk.CTkLabel(
            body, text="📊 Overview",
            font=("Arial", 15, "bold"), text_color=DARK
        ).pack(anchor="w", pady=(4, 8))

        # ── Stat cards row 1 ─────────────────────────────────
        row1 = ctk.CTkFrame(body, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 12))
        cards1 = [
            ("Total Customers",  stats["total_customers"],
             "👥", BLUE),
            ("Active Accounts",  stats["total_accounts"],
             "🏦", GREEN),
            ("Total Balance",
             format_currency(stats["total_balance"]),
             "💰", ORANGE),
            ("Pending Loans",    stats["pending_loans"],
             "📋", "#6A1B9A"),
        ]
        for title, value, icon, color in cards1:
            card = stat_card(row1, title, value, icon, color)
            card.pack(side="left", fill="both", expand=True, padx=6)

        # ── Stat cards row 2 ─────────────────────────────────
        row2 = ctk.CTkFrame(body, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 20))
        cards2 = [
            ("Today's Transactions",
             stats["today_txn_count"],  "📈", BLUE),
            ("Today's Amount",
             format_currency(stats["today_txn_amount"]), "💸", GREEN),
            ("Active Loans",
             stats["active_loans"], "✅", ORANGE),
            ("Total Disbursed",
             format_currency(stats["total_disbursed"]), "🏛️", "#C62828"),
        ]
        for title, value, icon, color in cards2:
            card = stat_card(row2, title, value, icon, color)
            card.pack(side="left", fill="both", expand=True, padx=6)

        # ── Recent Transactions ───────────────────────────────
        ctk.CTkLabel(
            body, text="🕐 Recent Transactions",
            font=("Arial", 15, "bold"), text_color=DARK
        ).pack(anchor="w", pady=(8, 6))

        from models.transaction import TransactionModel
        txns = TransactionModel.get_all(limit=10)

        table = ctk.CTkFrame(body, fg_color=WHITE,
                              corner_radius=10, border_width=1,
                              border_color="#DDE3EC")
        table.pack(fill="x", pady=(0, 20))

        headers = ["Ref", "Type", "From A/C", "To A/C",
                   "Amount", "Fee", "Date"]
        widths  = [150, 130, 130, 130, 110, 80, 160]

        hrow = ctk.CTkFrame(table, fg_color="#EEF2F7", corner_radius=0)
        hrow.pack(fill="x")
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                hrow, text=h, font=("Arial", 12, "bold"),
                text_color=DARK, width=w, anchor="w"
            ).pack(side="left", padx=8, pady=8)

        if not txns:
            ctk.CTkLabel(
                table, text="No transactions yet.",
                font=("Arial", 12), text_color="#7A8BA0"
            ).pack(pady=20)
        else:
            for i, t in enumerate(txns):
                bg = WHITE if i % 2 == 0 else "#F8FAFD"
                drow = ctk.CTkFrame(table, fg_color=bg, corner_radius=0)
                drow.pack(fill="x")
                vals = [
                    t["transaction_ref"],
                    t["transaction_type"].replace("_", " ").title(),
                    t["from_acc"] or "—",
                    t["to_acc"]   or "—",
                    format_currency(t["amount"]),
                    format_currency(t["fee_amount"]),
                    format_datetime(t["created_at"])
                ]
                for val, w in zip(vals, widths):
                    ctk.CTkLabel(
                        drow, text=str(val),
                        font=("Arial", 11), text_color=DARK,
                        width=w, anchor="w"
                    ).pack(side="left", padx=8, pady=6)