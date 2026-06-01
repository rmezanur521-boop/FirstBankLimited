import customtkinter as ctk
from models.account     import AccountModel
from models.transaction import TransactionModel
from utils.helpers import format_currency, format_datetime

BLUE  = "#1A73E8"; WHITE = "#FFFFFF"; GRAY = "#F0F4FA"; DARK = "#1E2A3A"
GREEN = "#2E7D32"; RED = "#D32F2F"; BORDER = "#DDE3EC"


class TransactionHistory(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, fg_color=GRAY, corner_radius=0)
        self.user = user
        self._all_txns = []
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(
            top, text="Transaction History",
            font=("Arial", 20, "bold"), text_color=DARK
        ).pack(side="left", padx=24, pady=16)

        # Filter bar
        fb = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=56)
        fb.pack(fill="x")
        fb.pack_propagate(False)

        ctk.CTkLabel(
            fb, text="From:", font=("Arial", 12), text_color=DARK
        ).pack(side="left", padx=(20, 4), pady=12)
        self.from_date = ctk.CTkEntry(
            fb, placeholder_text="YYYY-MM-DD",
            width=130, height=34, font=("Arial", 12)
        )
        self.from_date.pack(side="left", pady=12)

        ctk.CTkLabel(
            fb, text="To:", font=("Arial", 12), text_color=DARK
        ).pack(side="left", padx=(12, 4))
        self.to_date = ctk.CTkEntry(
            fb, placeholder_text="YYYY-MM-DD",
            width=130, height=34, font=("Arial", 12)
        )
        self.to_date.pack(side="left", pady=12)

        ctk.CTkLabel(
            fb, text="Amount:", font=("Arial", 12), text_color=DARK
        ).pack(side="left", padx=(12, 4))
        self.amt_filter = ctk.CTkEntry(
            fb, placeholder_text="exact amount",
            width=120, height=34, font=("Arial", 12)
        )
        self.amt_filter.pack(side="left", pady=12)

        ctk.CTkButton(
            fb, text="🔍 Search", width=90, height=34,
            fg_color=BLUE, command=self._search
        ).pack(side="left", padx=8, pady=12)
        ctk.CTkButton(
            fb, text="Clear", width=70, height=34,
            fg_color="#7A8BA0", command=self._load_all
        ).pack(side="left", pady=12)

        self.table_frame = ctk.CTkScrollableFrame(
            self, fg_color=WHITE, corner_radius=10,
            border_width=1, border_color=BORDER
        )
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=16)
        self._load_all()

    def _load_all(self):
        self.from_date.delete(0, "end")
        self.to_date.delete(0, "end")
        self.amt_filter.delete(0, "end")

        accounts = AccountModel.get_by_customer(self.user["id"])
        txns = []
        seen = set()
        for acc in accounts:
            for t in TransactionModel.get_by_account(acc["id"], limit=500):
                if t["id"] not in seen:
                    txns.append(t)
                    seen.add(t["id"])
        txns.sort(key=lambda x: x["created_at"], reverse=True)
        self._all_txns = txns
        self._render(txns)

    def _search(self):
        from_d  = self.from_date.get().strip() or None
        to_d    = self.to_date.get().strip()   or None
        amt_str = self.amt_filter.get().strip()
        amount  = float(amt_str) if amt_str else None

        accounts = AccountModel.get_by_customer(self.user["id"])
        txns = []
        seen = set()
        for acc in accounts:
            for t in TransactionModel.search_by_date_and_amount(
                acc["id"], from_d, to_d, amount
            ):
                if t["id"] not in seen:
                    txns.append(t)
                    seen.add(t["id"])
        txns.sort(key=lambda x: x["created_at"], reverse=True)
        self._render(txns)

    def _render(self, txns):
        for w in self.table_frame.winfo_children():
            w.destroy()

        headers = ["Ref", "Type", "Amount", "Fee", "Net Amount", "Status", "Date"]
        widths  = [180, 150, 120, 90, 120, 90, 180]

        hrow = ctk.CTkFrame(self.table_frame,
                             fg_color="#EEF2F7", corner_radius=0)
        hrow.pack(fill="x")
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                hrow, text=h, font=("Arial", 12, "bold"),
                text_color=DARK, width=w, anchor="w"
            ).pack(side="left", padx=8, pady=8)

        if not txns:
            ctk.CTkLabel(
                self.table_frame, text="No transactions found.",
                font=("Arial", 13), text_color="#7A8BA0"
            ).pack(pady=30)
            return

        for i, t in enumerate(txns):
            bg    = WHITE if i % 2 == 0 else "#F8FAFD"
            ttype = t["transaction_type"]
            is_cr = "deposit" in ttype or "transfer_other" in ttype
            acolor = GREEN if is_cr else RED
            row   = ctk.CTkFrame(self.table_frame, fg_color=bg, corner_radius=0)
            row.pack(fill="x")
            for val, w, col in zip([
                t["transaction_ref"],
                ttype.replace("_"," ").title(),
                format_currency(t["amount"]),
                format_currency(t["fee_amount"]),
                format_currency(t["net_amount"]),
                t.get("status","completed").upper(),
                format_datetime(t["created_at"])
            ], widths, range(len(widths))):
                color = acolor if col == 2 else DARK
                ctk.CTkLabel(
                    row, text=str(val), font=("Arial", 11),
                    text_color=color, width=w, anchor="w"
                ).pack(side="left", padx=8, pady=6)