import customtkinter as ctk
from models.account import AccountModel
from controllers.account_controller import transfer
from utils.fee_calculator import calculate_fee
from views.shared.widgets import show_message, confirm_dialog
from utils.helpers import format_currency

BLUE  = "#1A73E8"; WHITE = "#FFFFFF"; GRAY = "#F0F4FA"; DARK = "#1E2A3A"
GREEN = "#2E7D32"; ORANGE = "#E65100"; BORDER = "#DDE3EC"; RED = "#D32F2F"


class FundTransfer(ctk.CTkFrame):

    def __init__(self, parent, user, navigate_fn=None):
        super().__init__(parent, fg_color=GRAY, corner_radius=0)
        self.user        = user
        self.navigate_fn = navigate_fn
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(
            top, text="Fund Transfer",
            font=("Arial", 20, "bold"), text_color=DARK
        ).pack(side="left", padx=24, pady=16)

        body = ctk.CTkScrollableFrame(self, fg_color=GRAY)
        body.pack(fill="both", expand=True, padx=40, pady=20)

        # Transfer type selector
        ctk.CTkLabel(
            body, text="Transfer Type",
            font=("Arial", 14, "bold"), text_color=DARK
        ).pack(anchor="w", pady=(0, 6))

        self.transfer_type = ctk.StringVar(value="own")
        tf = ctk.CTkFrame(body, fg_color="transparent")
        tf.pack(anchor="w", pady=(0, 16))
        ctk.CTkRadioButton(
            tf, text="Transfer to My Own Account  (No fee)",
            variable=self.transfer_type, value="own",
            font=("Arial", 13), text_color=DARK,
            command=self._on_type_change
        ).pack(side="left", padx=(0, 20))
        ctk.CTkRadioButton(
            tf, text="Transfer to Another Customer  (Fee applies)",
            variable=self.transfer_type, value="other",
            font=("Arial", 13), text_color=DARK,
            command=self._on_type_change
        ).pack(side="left")

        # Form card
        form = ctk.CTkFrame(
            body, fg_color=WHITE, corner_radius=12,
            border_width=1, border_color=BORDER
        )
        form.pack(fill="x", pady=8)
        form.grid_columnconfigure((0, 1), weight=1)

        def lbl(parent, text, row, col, colspan=1):
            ctk.CTkLabel(
                parent, text=text, font=("Arial", 12, "bold"),
                text_color=DARK, anchor="w"
            ).grid(row=row, column=col, columnspan=colspan,
                   padx=20, pady=(12, 2), sticky="w")

        # From account
        lbl(form, "From Account *", 0, 0)
        my_accounts = AccountModel.get_by_customer(self.user["id"])
        active_accounts = [a for a in my_accounts if a["status"] == "active"]
        self.from_options = {
            f"{a['account_number']} ({a['account_type']}) — "
            f"{format_currency(a['balance'])}": a
            for a in active_accounts
        }
        self.from_var = ctk.StringVar(
            value=list(self.from_options.keys())[0]
            if self.from_options else ""
        )
        ctk.CTkOptionMenu(
            form, variable=self.from_var,
            values=list(self.from_options.keys()),
            height=38, font=("Arial", 12), width=380,
            command=self._update_fee_preview
        ).grid(row=1, column=0, padx=20, pady=4, sticky="w")

        # To account
        lbl(form, "To Account Number *", 0, 1)
        self.to_entry = ctk.CTkEntry(
            form, height=38, font=("Arial", 13),
            placeholder_text="Enter account number", width=280
        )
        self.to_entry.grid(row=1, column=1, padx=20, pady=4, sticky="w")

        # To account name display (for verification)
        self.to_name_label = ctk.CTkLabel(
            form, text="", font=("Arial", 12), text_color=GREEN
        )
        self.to_name_label.grid(row=2, column=1, padx=20, sticky="w")

        ctk.CTkButton(
            form, text="🔍 Verify Account", width=140, height=32,
            fg_color="#455A64", font=("Arial", 12),
            command=self._verify_account
        ).grid(row=3, column=1, padx=20, pady=4, sticky="w")

        # Amount
        lbl(form, "Amount (৳) *", 4, 0)
        self.amount_entry = ctk.CTkEntry(
            form, height=38, font=("Arial", 13),
            placeholder_text="Enter amount", width=280
        )
        self.amount_entry.grid(row=5, column=0, padx=20, pady=4, sticky="w")
        self.amount_entry.bind("<KeyRelease>", lambda e: self._update_fee_preview())

        # Fee preview panel
        self.fee_frame = ctk.CTkFrame(
            form, fg_color="#F0F4FA", corner_radius=8
        )
        self.fee_frame.grid(row=6, column=0, columnspan=2,
                             padx=20, pady=12, sticky="ew")
        self.fee_labels = {}
        for i, key in enumerate(["Amount", "Fee %", "Fee", "You Pay", "Recipient Gets"]):
            ctk.CTkLabel(
                self.fee_frame, text=key,
                font=("Arial", 11), text_color="#7A8BA0"
            ).grid(row=0, column=i, padx=12, pady=6)
            lv = ctk.CTkLabel(
                self.fee_frame, text="—",
                font=("Arial", 13, "bold"), text_color=DARK
            )
            lv.grid(row=1, column=i, padx=12, pady=(0, 8))
            self.fee_labels[key] = lv

        # Submit
        ctk.CTkButton(
            form, text="✅ Confirm Transfer",
            fg_color=BLUE, font=("Arial", 14, "bold"),
            height=46, command=self._confirm_transfer
        ).grid(row=7, column=0, columnspan=2,
               padx=20, pady=16, sticky="ew")

        self._to_account_data = None

    def _on_type_change(self):
        self.to_name_label.configure(text="")
        self._to_account_data = None
        self._update_fee_preview()

    def _verify_account(self):
        acc_no   = self.to_entry.get().strip()
        to_acc   = AccountModel.get_by_account_number(acc_no)
        if not to_acc:
            self.to_name_label.configure(
                text="❌ Account not found.", text_color=RED
            )
            self._to_account_data = None
            return
        if to_acc["status"] != "active":
            self.to_name_label.configure(
                text="❌ Account is not active.", text_color=RED
            )
            self._to_account_data = None
            return
        self._to_account_data = to_acc
        self.to_name_label.configure(
            text=f"✅ {to_acc['customer_name']}", text_color=GREEN
        )
        self._update_fee_preview()

    def _update_fee_preview(self, *args):
        try:
            amount = float(self.amount_entry.get().strip())
        except ValueError:
            for lv in self.fee_labels.values():
                lv.configure(text="—")
            return

        from_acc_data = self.from_options.get(self.from_var.get())
        if not from_acc_data or not self._to_account_data:
            is_same = (self.transfer_type.get() == "own")
        else:
            is_same = (from_acc_data["id"] != self._to_account_data["id"] and
                       self.transfer_type.get() == "own")

        fee_info = calculate_fee(amount, self.transfer_type.get() == "own")
        self.fee_labels["Amount"].configure(
            text=format_currency(fee_info["amount"])
        )
        self.fee_labels["Fee %"].configure(
            text=f"{fee_info['fee_percentage']}%"
        )
        self.fee_labels["Fee"].configure(
            text=format_currency(fee_info["fee_amount"])
        )
        self.fee_labels["You Pay"].configure(
            text=format_currency(fee_info["amount"]),
            text_color=RED
        )
        self.fee_labels["Recipient Gets"].configure(
            text=format_currency(fee_info["net_amount"]),
            text_color=GREEN
        )

    def _confirm_transfer(self):
        from_acc_data = self.from_options.get(self.from_var.get())
        if not from_acc_data:
            show_message(self, "Please select a source account.", "error")
            return
        if not self._to_account_data:
            show_message(self, "Please verify the destination account.", "error")
            return
        try:
            amount = float(self.amount_entry.get().strip())
        except ValueError:
            show_message(self, "Invalid amount.", "error")
            return
        if amount <= 0:
            show_message(self, "Amount must be positive.", "error")
            return

        fee_info = calculate_fee(amount, self.transfer_type.get() == "own")

        msg = (
            f"Transfer Summary:\n\n"
            f"  From : {from_acc_data['account_number']}\n"
            f"  To   : {self._to_account_data['account_number']}\n"
            f"         ({self._to_account_data['customer_name']})\n"
            f"  Amount  : {format_currency(amount)}\n"
            f"  Fee     : {format_currency(fee_info['fee_amount'])} "
            f"({fee_info['fee_percentage']}%)\n"
            f"  Recipient gets: {format_currency(fee_info['net_amount'])}\n\n"
            f"Confirm this transfer?"
        )
        if not confirm_dialog(self, msg):
            return

        try:
            result = transfer(
                from_acc_data["id"],
                self._to_account_data["id"],
                amount, "customer", self.user["id"]
            )
            show_message(
                self,
                f"Transfer successful!\nRef: {result['transaction_ref']}",
                "success"
            )
            # Reset
            self.amount_entry.delete(0, "end")
            self.to_entry.delete(0, "end")
            self.to_name_label.configure(text="")
            self._to_account_data = None
            for lv in self.fee_labels.values():
                lv.configure(text="—", text_color=DARK)
        except Exception as e:
            show_message(self, f"Transfer failed: {e}", "error")