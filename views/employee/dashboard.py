import customtkinter as ctk
from models.customer    import CustomerModel
from models.account     import AccountModel
from models.transaction import TransactionModel
from utils.helpers import format_currency, format_datetime
from views.shared.widgets import stat_card

BLUE  = "#1A73E8"; WHITE = "#FFFFFF"; GRAY = "#F0F4FA"; DARK = "#1E2A3A"
GREEN = "#2E7D32"; ORANGE = "#E65100"; BORDER = "#DDE3EC"


class EmployeeDashboard(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, fg_color=GRAY, corner_radius=0)
        self.user = user
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

        # Stats
        row1 = ctk.CTkFrame(body, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 16))

        total_customers = len(CustomerModel.get_all())
        total_accounts  = len(AccountModel.get_all())
        txns = TransactionModel.get_all(limit=1000)
        today_txns = [
            t for t in txns
            if str(t["created_at"])[:10] == __import__("datetime").date.today().isoformat()
        ]

        for title, value, icon, color in [
            ("Total Customers", total_customers, "👥", BLUE),
            ("Total Accounts",  total_accounts,  "🏦", GREEN),
            ("Today Txns",      len(today_txns), "📈", ORANGE),
        ]:
            card = stat_card(row1, title, value, icon, color)
            card.pack(side="left", fill="both", expand=True, padx=6)

        # Recent transactions
        ctk.CTkLabel(
            body, text="🕐 Recent Transactions",
            font=("Arial", 15, "bold"), text_color=DARK
        ).pack(anchor="w", pady=(8, 6))

        table = ctk.CTkFrame(body, fg_color=WHITE, corner_radius=10,
                              border_width=1, border_color=BORDER)
        table.pack(fill="x")
        headers = ["Ref", "Type", "Amount", "Fee", "Status", "Date"]
        widths  = [160, 140, 120, 90, 90, 180]
        hrow = ctk.CTkFrame(table, fg_color="#EEF2F7", corner_radius=0)
        hrow.pack(fill="x")
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                hrow, text=h, font=("Arial", 12, "bold"),
                text_color=DARK, width=w, anchor="w"
            ).pack(side="left", padx=8, pady=8)

        for i, t in enumerate(txns[:15]):
            bg = WHITE if i % 2 == 0 else "#F8FAFD"
            drow = ctk.CTkFrame(table, fg_color=bg, corner_radius=0)
            drow.pack(fill="x")
            for val, w in zip([
                t["transaction_ref"],
                t["transaction_type"].replace("_"," ").title(),
                format_currency(t["amount"]),
                format_currency(t["fee_amount"]),
                t["status"].upper(),
                format_datetime(t["created_at"])
            ], widths):
                ctk.CTkLabel(
                    drow, text=str(val), font=("Arial", 11),
                    text_color=DARK, width=w, anchor="w"
                ).pack(side="left", padx=8, pady=6)