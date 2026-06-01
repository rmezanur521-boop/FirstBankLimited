import customtkinter as ctk
from tkinter import filedialog
from models.account  import AccountModel
from models.customer import CustomerModel
from controllers.account_controller import open_account, deposit, withdraw
from views.shared.widgets import show_message, confirm_dialog, primary_button
from utils.helpers import format_currency, format_datetime

BLUE   = "#1A73E8"
WHITE  = "#FFFFFF"
GRAY   = "#F0F4FA"
DARK   = "#1E2A3A"
BORDER = "#DDE3EC"
RED    = "#D32F2F"
GREEN  = "#2E7D32"
ORANGE = "#E65100"


class AccountManagement(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, fg_color=GRAY, corner_radius=0)
        self.user = user
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(
            top, text="Account Management",
            font=("Arial", 20, "bold"), text_color=DARK
        ).pack(side="left", padx=24, pady=16)
        primary_button(
            top, "➕ Open Account", self._open_account_form, 160
        ).pack(side="right", padx=24, pady=14)

        # Search bar
        sf = ctk.CTkFrame(self, fg_color=WHITE,
                           corner_radius=0, height=52)
        sf.pack(fill="x")
        sf.pack_propagate(False)
        self.search_var = ctk.StringVar()
        ctk.CTkEntry(
            sf, textvariable=self.search_var,
            placeholder_text="🔍  Search by account number or customer name…",
            width=400, height=36, font=("Arial", 13)
        ).pack(side="left", padx=20, pady=8)
        ctk.CTkButton(
            sf, text="Search", width=90, height=36,
            fg_color=BLUE, command=self._search
        ).pack(side="left", pady=8)
        ctk.CTkButton(
            sf, text="Clear", width=80, height=36,
            fg_color="#7A8BA0", command=self._load_all
        ).pack(side="left", padx=6, pady=8)

        self.table_frame = ctk.CTkScrollableFrame(
            self, fg_color=WHITE, corner_radius=10,
            border_width=1, border_color=BORDER
        )
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=16)
        self._load_all()

    def _load_all(self):
        self.search_var.set("")
        accounts = AccountModel.get_all()
        self._render_table(accounts)

    def _search(self):
        kw = self.search_var.get().strip().lower()
        accounts = AccountModel.get_all()
        filtered = [
            a for a in accounts
            if kw in a["account_number"].lower()
            or kw in a["customer_name"].lower()
        ]
        self._render_table(filtered)

    def _render_table(self, accounts):
        for w in self.table_frame.winfo_children():
            w.destroy()

        headers = ["A/C Number", "Customer", "Type",
                   "Balance", "Status", "Opened", "Actions"]
        widths  = [150, 180, 120, 120, 80, 140, 220]

        hrow = ctk.CTkFrame(self.table_frame,
                             fg_color="#EEF2F7", corner_radius=0)
        hrow.pack(fill="x")
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                hrow, text=h, font=("Arial", 12, "bold"),
                text_color=DARK, width=w, anchor="w"
            ).pack(side="left", padx=6, pady=8)

        if not accounts:
            ctk.CTkLabel(
                self.table_frame, text="No accounts found.",
                font=("Arial", 13), text_color="#7A8BA0"
            ).pack(pady=30)
            return

        for i, a in enumerate(accounts):
            bg = WHITE if i % 2 == 0 else "#F8FAFD"
            row = ctk.CTkFrame(self.table_frame,
                                fg_color=bg, corner_radius=0)
            row.pack(fill="x")
            vals = [
                a["account_number"], a["customer_name"],
                a["account_type"], format_currency(a["balance"]),
                a["status"].upper(), format_datetime(a["opened_at"])
            ]
            for val, w in zip(vals, widths[:-1]):
                ctk.CTkLabel(
                    row, text=str(val),
                    font=("Arial", 11), text_color=DARK,
                    width=w, anchor="w"
                ).pack(side="left", padx=6, pady=6)

            # ── Action buttons (fixed) ────────────────────────
            act = ctk.CTkFrame(row, fg_color="transparent")
            act.pack(side="left", padx=4)

            ctk.CTkButton(
                act, text="Deposit", width=66, height=28,
                fg_color=GREEN, font=("Arial", 11),
                command=lambda aid=a["id"]: self._deposit_popup(aid)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                act, text="Withdraw", width=72, height=28,
                fg_color=ORANGE, font=("Arial", 11),
                command=lambda aid=a["id"]: self._withdraw_popup(aid)
            ).pack(side="left", padx=2)

            freeze_label = "Unfreeze" if a["status"] == "frozen" else "Freeze"
            ctk.CTkButton(
                act, text=freeze_label, width=68, height=28,
                fg_color="#455A64", font=("Arial", 11),
                command=lambda aid=a["id"], s=a["status"]: self._toggle_freeze(aid, s)
            ).pack(side="left", padx=2)

    def _open_account_form(self):
        _OpenAccountForm(self, self.user, on_save=self._load_all)

    def _deposit_popup(self, account_id):
        _TxnPopup(self, account_id, "Deposit", self.user,
                   on_done=self._load_all)

    def _withdraw_popup(self, account_id):
        _TxnPopup(self, account_id, "Withdraw", self.user,
                   on_done=self._load_all)

    def _toggle_freeze(self, account_id, current_status):
        new_status = "active" if current_status == "frozen" else "frozen"
        action     = "unfreeze" if current_status == "frozen" else "freeze"
        if confirm_dialog(self, f"Are you sure you want to {action} this account?"):
            AccountModel.update_status(account_id, new_status)
            show_message(self, f"Account {action}d.", "success")
            self._load_all()


# ── Open Account Form ─────────────────────────────────────────
class _OpenAccountForm(ctk.CTkToplevel):

    def __init__(self, parent, user, on_save=None):
        super().__init__(parent)
        self.user      = user
        self.on_save   = on_save
        self.photo_src = None
        self.doc_src   = None
        self.title("Open New Account")
        self.geometry("580x640")
        self.resizable(False, True)
        self.grab_set()
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(
            scroll, text="Open New Bank Account",
            font=("Arial", 18, "bold"), text_color=DARK
        ).pack(anchor="w", pady=(0, 16))

        def lbl(t):
            ctk.CTkLabel(
                scroll, text=t,
                font=("Arial", 12, "bold"), text_color=DARK, anchor="w"
            ).pack(fill="x", pady=(10, 2))

        # ── Customer ID ───────────────────────────────────────
        lbl("Customer ID *")
        id_row = ctk.CTkFrame(scroll, fg_color="transparent")
        id_row.pack(fill="x", pady=(0, 2))
        self.e_custid = ctk.CTkEntry(
            id_row, height=38, font=("Arial", 13),
            placeholder_text="Enter Customer ID"
        )
        self.e_custid.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(
            id_row, text="🔍 Lookup", width=90, height=38,
            fg_color="#455A64", command=self._lookup_customer
        ).pack(side="left")

        self.cust_info_label = ctk.CTkLabel(
            scroll, text="", font=("Arial", 12),
            text_color="#2E7D32", anchor="w"
        )
        self.cust_info_label.pack(fill="x", pady=(2, 4))

        # ── Account Type ──────────────────────────────────────
        lbl("Account Type *")
        types          = AccountModel.get_account_types()
        self.type_map  = {t["type_name"]: t["id"] for t in types}
        self.type_var  = ctk.StringVar(
            value=types[0]["type_name"] if types else "Savings"
        )
        ctk.CTkOptionMenu(
            scroll, variable=self.type_var,
            values=[t["type_name"] for t in types],
            height=38, font=("Arial", 13)
        ).pack(fill="x", pady=(0, 2))

        # ── Initial Deposit ───────────────────────────────────
        lbl("Initial Deposit Amount (৳) *")
        self.e_balance = ctk.CTkEntry(
            scroll, height=38, font=("Arial", 13),
            placeholder_text="Minimum deposit e.g. 500"
        )
        self.e_balance.pack(fill="x")

        # ── Passport Photo ────────────────────────────────────
        lbl("Passport Size Photo (optional)")
        pf = ctk.CTkFrame(scroll, fg_color="transparent")
        pf.pack(fill="x", pady=(0, 2))
        self.photo_lbl = ctk.CTkLabel(
            pf, text="No file selected",
            font=("Arial", 11), text_color="#7A8BA0"
        )
        self.photo_lbl.pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            pf, text="Browse", width=90, height=32,
            command=self._browse_photo
        ).pack(side="left")

        # ── ID Document ───────────────────────────────────────
        lbl("ID Document — NID / Passport / Birth Certificate (optional)")
        df = ctk.CTkFrame(scroll, fg_color="transparent")
        df.pack(fill="x", pady=(0, 2))
        self.doc_lbl = ctk.CTkLabel(
            df, text="No file selected",
            font=("Arial", 11), text_color="#7A8BA0"
        )
        self.doc_lbl.pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            df, text="Browse", width=90, height=32,
            command=self._browse_doc
        ).pack(side="left")

        # ── Submit ────────────────────────────────────────────
        ctk.CTkButton(
            scroll, text="✅ Open Account",
            fg_color=BLUE, font=("Arial", 13, "bold"),
            height=44, command=self._save
        ).pack(fill="x", pady=(20, 8))

    def _lookup_customer(self):
        try:
            cust_id = int(self.e_custid.get().strip())
        except ValueError:
            self.cust_info_label.configure(
                text="❌ Enter a valid numeric Customer ID.",
                text_color=RED
            )
            return
        cust = CustomerModel.get_by_id(cust_id)
        if not cust:
            self.cust_info_label.configure(
                text="❌ No customer found with this ID.",
                text_color=RED
            )
        else:
            self.cust_info_label.configure(
                text=f"✅  {cust['full_name']}  |  {cust['phone']}",
                text_color="#2E7D32"
            )

    def _browse_photo(self):
        path = filedialog.askopenfilename(
            title="Select Passport Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if path:
            self.photo_src = path
            self.photo_lbl.configure(text=path.split("/")[-1])

    def _browse_doc(self):
        path = filedialog.askopenfilename(
            title="Select ID Document",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"),
                       ("PDF files", "*.pdf")]
        )
        if path:
            self.doc_src = path
            self.doc_lbl.configure(text=path.split("/")[-1])

    def _save(self):
        # Validate customer ID
        try:
            cust_id = int(self.e_custid.get().strip())
        except ValueError:
            show_message(self, "Please enter a valid Customer ID.", "error")
            return

        # Validate amount
        try:
            balance = float(self.e_balance.get().strip())
        except ValueError:
            show_message(self, "Please enter a valid deposit amount.", "error")
            return

        if balance < 0:
            show_message(self, "Initial deposit cannot be negative.", "error")
            return

        # Verify customer exists
        cust = CustomerModel.get_by_id(cust_id)
        if not cust:
            show_message(self, "Customer not found. Please verify the ID.", "error")
            return

        # Save documents if provided
        if self.photo_src:
            try:
                from utils.image_handler import save_photo
                cust["photo_path"] = save_photo(self.photo_src, cust_id)
                CustomerModel.update(cust_id, cust)
            except Exception:
                pass  # Non-critical

        if self.doc_src:
            try:
                from utils.image_handler import save_document
                cust["id_document_path"] = save_document(self.doc_src, cust_id)
                CustomerModel.update(cust_id, cust)
            except Exception:
                pass  # Non-critical

        # Get account type ID
        type_id = self.type_map.get(self.type_var.get(), 1)

        try:
            result = open_account(
                cust_id, type_id, balance,
                created_by_admin=self.user["id"]
            )
            show_message(
                self,
                f"Account opened successfully!\n\n"
                f"Customer  : {cust['full_name']}\n"
                f"Account No: {result['account_number']}\n"
                f"Type      : {self.type_var.get()}\n"
                f"Balance   : {format_currency(balance)}",
                "success"
            )
            self.destroy()
            if self.on_save:
                self.on_save()
        except Exception as e:
            show_message(self, f"Failed to open account: {e}", "error")


# ── Deposit / Withdraw Popup ──────────────────────────────────
class _TxnPopup(ctk.CTkToplevel):

    def __init__(self, parent, account_id, txn_type, user, on_done=None):
        super().__init__(parent)
        self.account_id = account_id
        self.txn_type   = txn_type
        self.user       = user
        self.on_done    = on_done
        self.title(txn_type)
        self.geometry("420x280")
        self.resizable(False, False)
        self.grab_set()
        self._build()

    def _build(self):
        acc = AccountModel.get_by_id(self.account_id)
        ctk.CTkLabel(
            self,
            text=f"{self.txn_type}",
            font=("Arial", 18, "bold"), text_color=DARK
        ).pack(pady=(24, 2))

        ctk.CTkLabel(
            self,
            text=f"Account: {acc['account_number']}  |  "
                 f"Balance: {format_currency(acc['balance'])}",
            font=("Arial", 12), text_color="#7A8BA0"
        ).pack(pady=(0, 16))

        ctk.CTkLabel(
            self, text="Amount (৳)",
            font=("Arial", 13, "bold"), text_color=DARK
        ).pack()
        self.e_amount = ctk.CTkEntry(
            self, height=42, font=("Arial", 15),
            placeholder_text="Enter amount"
        )
        self.e_amount.pack(padx=40, fill="x", pady=8)

        btn_color = GREEN if self.txn_type == "Deposit" else ORANGE
        ctk.CTkButton(
            self,
            text=f"✅ Confirm {self.txn_type}",
            fg_color=btn_color,
            font=("Arial", 13, "bold"), height=42,
            command=self._confirm
        ).pack(padx=40, fill="x", pady=(4, 0))

    def _confirm(self):
        try:
            amount = float(self.e_amount.get().strip())
        except ValueError:
            show_message(self, "Please enter a valid amount.", "error")
            return
        if amount <= 0:
            show_message(self, "Amount must be greater than zero.", "error")
            return
        try:
            if self.txn_type == "Deposit":
                deposit(self.account_id, amount, "admin", self.user["id"])
            else:
                withdraw(self.account_id, amount, "admin", self.user["id"])
            show_message(
                self, f"{self.txn_type} of {format_currency(amount)} successful!", "success"
            )
            self.destroy()
            if self.on_done:
                self.on_done()
        except Exception as e:
            show_message(self, f"Error: {e}", "error")