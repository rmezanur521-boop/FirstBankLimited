import customtkinter as ctk
from models.transaction import TransactionModel
from utils.helpers import format_currency, format_datetime

BLUE  = "#1A73E8"; WHITE = "#FFFFFF"; GRAY = "#F0F4FA"; DARK = "#1E2A3A"
BORDER = "#DDE3EC"


class TransactionsView(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, fg_color=GRAY, corner_radius=0)
        self.user = user
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(
            top, text="All Transactions",
            font=("Arial", 20, "bold"), text_color=DARK
        ).pack(side="left", padx=24, pady=16)
        ctk.CTkButton(
            top, text="🔄 Refresh", width=100, fg_color=BLUE,
            command=self._load
        ).pack(side="right", padx=24, pady=16)

        self.table_frame = ctk.CTkScrollableFrame(
            self, fg_color=WHITE, corner_radius=10,
            border_width=1, border_color=BORDER
        )
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=16)
        self._load()

    def _load(self):
        for w in self.table_frame.winfo_children():
            w.destroy()
        txns = TransactionModel.get_all(limit=300)

        headers = ["Ref", "Type", "From A/C", "To A/C",
                   "Amount", "Fee", "Net", "Status", "Date"]
        widths  = [150, 120, 130, 130, 110, 80, 110, 90, 160]

        hrow = ctk.CTkFrame(self.table_frame,
                             fg_color="#EEF2F7", corner_radius=0)
        hrow.pack(fill="x")
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                hrow, text=h, font=("Arial", 12, "bold"),
                text_color=DARK, width=w, anchor="w"
            ).pack(side="left", padx=6, pady=8)

        if not txns:
            ctk.CTkLabel(
                self.table_frame, text="No transactions found.",
                font=("Arial", 13), text_color="#7A8BA0"
            ).pack(pady=30)
            return

        for i, t in enumerate(txns):
            bg = WHITE if i % 2 == 0 else "#F8FAFD"
            row = ctk.CTkFrame(self.table_frame, fg_color=bg, corner_radius=0)
            row.pack(fill="x")
            vals = [
                t["transaction_ref"],
                t["transaction_type"].replace("_", " ").title(),
                t["from_acc"] or "—", t["to_acc"] or "—",
                format_currency(t["amount"]),
                format_currency(t["fee_amount"]),
                format_currency(t["net_amount"]),
                t["status"].upper(),
                format_datetime(t["created_at"])
            ]
            for val, w in zip(vals, widths):
                ctk.CTkLabel(
                    row, text=str(val), font=("Arial", 11),
                    text_color=DARK, width=w, anchor="w"
                ).pack(side="left", padx=6, pady=6)