import customtkinter as ctk
from models.account     import AccountModel
from models.transaction import TransactionModel
from utils.helpers import format_currency, format_datetime

BLUE  = "#1A73E8"; WHITE = "#FFFFFF"; GRAY = "#F0F4FA"; DARK = "#1E2A3A"
GREEN = "#2E7D32"; RED = "#D32F2F"; BORDER = "#DDE3EC"


class AccountDetails(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, fg_color=GRAY, corner_radius=0)
        self.user = user
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(
            top, text="Account Details",
            font=("Arial", 20, "bold"), text_color=DARK
        ).pack(side="left", padx=24, pady=16)

        accounts = AccountModel.get_by_customer(self.user["id"])
        if not accounts:
            ctk.CTkLabel(
                self, text="No accounts found.",
                font=("Arial", 14), text_color="#7A8BA0"
            ).pack(expand=True)
            return

        body = ctk.CTkScrollableFrame(self, fg_color=GRAY)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        for acc in accounts:
            # Account card
            card = ctk.CTkFrame(
                body, fg_color=WHITE, corner_radius=12,
                border_width=1, border_color=BORDER
            )
            card.pack(fill="x", pady=8)

            # Header row
            hf = ctk.CTkFrame(card, fg_color=BLUE, corner_radius=0)
            hf.pack(fill="x")
            ctk.CTkLabel(
                hf,
                text=f"  {acc['account_number']}  —  {acc['account_type']}",
                font=("Arial", 14, "bold"), text_color=WHITE
            ).pack(side="left", padx=16, pady=10)
            status_color = GREEN if acc["status"] == "active" else RED
            ctk.CTkLabel(
                hf, text=acc["status"].upper(),
                font=("Arial", 12, "bold"), text_color=WHITE
            ).pack(side="right", padx=16)

            # Balance
            bf = ctk.CTkFrame(card, fg_color="transparent")
            bf.pack(fill="x", padx=16, pady=12)
            ctk.CTkLabel(
                bf, text="Current Balance",
                font=("Arial", 12), text_color="#7A8BA0"
            ).pack(anchor="w")
            ctk.CTkLabel(
                bf, text=format_currency(acc["balance"]),
                font=("Arial", 28, "bold"), text_color=BLUE
            ).pack(anchor="w")

            # Recent transactions for this account
            ctk.CTkLabel(
                card, text="Recent Transactions",
                font=("Arial", 13, "bold"), text_color=DARK
            ).pack(anchor="w", padx=16, pady=(0, 6))

            txns = TransactionModel.get_by_account(acc["id"], limit=10)
            tf   = ctk.CTkFrame(card, fg_color="#F8FAFD", corner_radius=8)
            tf.pack(fill="x", padx=16, pady=(0, 12))

            headers = ["Ref", "Type", "Amount", "Fee", "Net", "Date"]
            widths  = [160, 140, 110, 90, 110, 180]
            hrow = ctk.CTkFrame(tf, fg_color="#EEF2F7", corner_radius=0)
            hrow.pack(fill="x")
            for h, w in zip(headers, widths):
                ctk.CTkLabel(
                    hrow, text=h, font=("Arial", 11, "bold"),
                    text_color=DARK, width=w, anchor="w"
                ).pack(side="left", padx=6, pady=6)

            if not txns:
                ctk.CTkLabel(
                    tf, text="No transactions.",
                    font=("Arial", 11), text_color="#7A8BA0"
                ).pack(pady=8)
            else:
                for i, t in enumerate(txns):
                    bg = WHITE if i % 2 == 0 else "#F0F4FA"
                    drow = ctk.CTkFrame(tf, fg_color=bg, corner_radius=0)
                    drow.pack(fill="x")
                    ttype   = t["transaction_type"]
                    is_credit = ("deposit" in ttype or
                                 t.get("to_acc") == acc["account_number"])
                    amt_color = GREEN if is_credit else RED
                    for val, w in zip([
                        t["transaction_ref"],
                        ttype.replace("_"," ").title(),
                        format_currency(t["amount"]),
                        format_currency(t["fee_amount"]),
                        format_currency(t["net_amount"]),
                        format_datetime(t["created_at"])
                    ], widths):
                        ctk.CTkLabel(
                            drow, text=str(val), font=("Arial", 11),
                            text_color=DARK, width=w, anchor="w"
                        ).pack(side="left", padx=6, pady=5)