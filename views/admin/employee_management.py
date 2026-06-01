import customtkinter as ctk
from models.employee import EmployeeModel
from controllers.auth_controller import hash_password
from views.shared.widgets import show_message, confirm_dialog, primary_button
from utils.helpers import validate_phone, validate_password, format_datetime

BLUE  = "#1A73E8"; WHITE = "#FFFFFF"; GRAY = "#F0F4FA"; DARK = "#1E2A3A"
RED   = "#D32F2F"; GREEN = "#2E7D32"; BORDER = "#DDE3EC"


class EmployeeManagement(ctk.CTkFrame):

    def __init__(self, parent, user):
        super().__init__(parent, fg_color=GRAY, corner_radius=0)
        self.user = user
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=0, height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkLabel(
            top, text="Employee Management",
            font=("Arial", 20, "bold"), text_color=DARK
        ).pack(side="left", padx=24, pady=16)
        primary_button(
            top, "➕ Add Employee", self._add_emp, 160
        ).pack(side="right", padx=24, pady=14)

        self.table_frame = ctk.CTkScrollableFrame(
            self, fg_color=WHITE, corner_radius=10,
            border_width=1, border_color=BORDER
        )
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=16)
        self._load()

    def _load(self):
        for w in self.table_frame.winfo_children():
            w.destroy()
        employees = EmployeeModel.get_all()

        headers = ["ID", "Full Name", "Username", "Email",
                   "Phone", "Designation", "Status", "Created", "Actions"]
        widths  = [50, 160, 120, 180, 120, 140, 70, 140, 160]

        hrow = ctk.CTkFrame(self.table_frame,
                             fg_color="#EEF2F7", corner_radius=0)
        hrow.pack(fill="x")
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                hrow, text=h, font=("Arial", 12, "bold"),
                text_color=DARK, width=w, anchor="w"
            ).pack(side="left", padx=6, pady=8)

        if not employees:
            ctk.CTkLabel(
                self.table_frame, text="No employees found.",
                font=("Arial", 13), text_color="#7A8BA0"
            ).pack(pady=30)
            return

        for i, e in enumerate(employees):
            bg = WHITE if i % 2 == 0 else "#F8FAFD"
            row = ctk.CTkFrame(self.table_frame, fg_color=bg, corner_radius=0)
            row.pack(fill="x")
            vals = [
                e["id"], e["full_name"], e["username"],
                e["email"] or "—", e["phone"] or "—",
                e["designation"] or "—",
                "Active" if e["is_active"] else "Inactive",
                format_datetime(e["created_at"])
            ]
            for val, w in zip(vals, widths[:-1]):
                ctk.CTkLabel(
                    row, text=str(val), font=("Arial", 11),
                    text_color=DARK, width=w, anchor="w"
                ).pack(side="left", padx=6, pady=6)

            act = ctk.CTkFrame(row, fg_color="transparent")
            act.pack(side="left", padx=4)
            ctk.CTkButton(
                act, text="Edit", width=56, height=28,
                fg_color=GREEN, font=("Arial", 11),
                command=lambda eid=e["id"]: self._edit_emp(eid)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                act, text="Delete", width=60, height=28,
                fg_color=RED, font=("Arial", 11),
                command=lambda eid=e["id"]: self._delete_emp(eid)
            ).pack(side="left", padx=2)

    def _add_emp(self):
        _EmployeeForm(self, self.user, on_save=self._load)

    def _edit_emp(self, emp_id):
        emp = EmployeeModel.get_by_id(emp_id)
        if emp:
            _EmployeeForm(self, self.user, employee=emp, on_save=self._load)

    def _delete_emp(self, emp_id):
        if confirm_dialog(self, "Delete this employee account?"):
            try:
                EmployeeModel.delete(emp_id)
                show_message(self, "Employee deleted.", "success")
                self._load()
            except Exception as e:
                show_message(self, f"Error: {e}", "error")


class _EmployeeForm(ctk.CTkToplevel):

    def __init__(self, parent, user, employee=None, on_save=None):
        super().__init__(parent)
        self.user     = user
        self.employee = employee
        self.on_save  = on_save
        self.is_edit  = employee is not None
        self.title("Edit Employee" if self.is_edit else "Add Employee")
        self.geometry("520x560")
        self.resizable(False, True)
        self.grab_set()
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=24, pady=20)

        def lbl(t):
            ctk.CTkLabel(
                scroll, text=t, font=("Arial", 12, "bold"),
                text_color=DARK, anchor="w"
            ).pack(fill="x", pady=(8, 2))

        def entry(key=None, placeholder="", show=""):
            e = ctk.CTkEntry(
                scroll, height=38,
                font=("Arial", 13),
                placeholder_text=placeholder,
                show=show
            )
            e.pack(fill="x")
            if key and self.employee:
                val = self.employee.get(key, "") or ""
                e.insert(0, str(val))
            return e

        lbl("Full Name *");      self.e_name  = entry("full_name", "Full name")
        lbl("Username *");       self.e_user  = entry("username",  "Username")
        if self.is_edit:
            self.e_user.configure(state="disabled")
        if not self.is_edit:
            lbl("Password *");   self.e_pass  = entry(placeholder="Password", show="*")
        lbl("Email");            self.e_email = entry("email", "email@example.com")
        lbl("Phone *");          self.e_phone = entry("phone", "01XXXXXXXXX")
        lbl("Designation");      self.e_desig = entry("designation", "e.g. Teller")

        self.active_var = ctk.BooleanVar(
            value=self.employee.get("is_active", True) if self.is_edit else True
        )
        ctk.CTkCheckBox(
            scroll, text="Active", variable=self.active_var, font=("Arial", 12)
        ).pack(anchor="w", pady=8)

        ctk.CTkButton(
            scroll, text="💾 Save",
            fg_color=BLUE, font=("Arial", 13, "bold"),
            height=42, command=self._save
        ).pack(fill="x", pady=12)

    def _save(self):
        name  = self.e_name.get().strip()
        phone = self.e_phone.get().strip()
        if not name or not phone:
            show_message(self, "Name and phone required.", "error")
            return
        if not validate_phone(phone):
            show_message(self, "Invalid phone number.", "error")
            return
        try:
            if self.is_edit:
                EmployeeModel.update(
                    self.employee["id"], name,
                    self.e_email.get().strip(),
                    phone, self.e_desig.get().strip(),
                    self.active_var.get()
                )
                show_message(self, "Employee updated.", "success")
            else:
                pw = self.e_pass.get().strip()
                if not validate_password(pw):
                    show_message(
                        self,
                        "Password: 8+ chars, 1 uppercase, 1 digit.",
                        "error"
                    )
                    return
                EmployeeModel.create(
                    name, self.e_user.get().strip(),
                    hash_password(pw),
                    self.e_email.get().strip(), phone,
                    self.e_desig.get().strip(),
                    self.user["id"]
                )
                show_message(self, "Employee created.", "success")
            self.destroy()
            if self.on_save:
                self.on_save()
        except Exception as e:
            show_message(self, f"Error: {e}", "error")