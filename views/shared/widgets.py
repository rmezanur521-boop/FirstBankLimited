import customtkinter as ctk

BLUE   = "#1A73E8"
WHITE  = "#FFFFFF"
GRAY   = "#F5F7FA"
DARK   = "#1E2A3A"
BORDER = "#DDE3EC"
GREEN  = "#2E7D32"
RED    = "#D32F2F"
ORANGE = "#E65100"


def stat_card(parent, title, value, icon="", color=BLUE):
    card = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=12,
                         border_width=1, border_color=BORDER)
    ctk.CTkLabel(
        card, text=f"{icon}  {title}",
        font=("Arial", 12), text_color="#7A8BA0"
    ).pack(anchor="w", padx=16, pady=(16, 4))
    ctk.CTkLabel(
        card, text=str(value),
        font=("Arial", 22, "bold"), text_color=color
    ).pack(anchor="w", padx=16, pady=(0, 16))
    return card


def section_title(parent, text):
    ctk.CTkLabel(
        parent, text=text,
        font=("Arial", 16, "bold"), text_color=DARK
    ).pack(anchor="w", padx=20, pady=(20, 8))


def primary_button(parent, text, command, width=140, color=BLUE):
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=color, hover_color="#1558B0",
        font=("Arial", 12, "bold"),
        height=36, width=width, corner_radius=8
    )


def danger_button(parent, text, command, width=140):
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=RED, hover_color="#B71C1C",
        font=("Arial", 12, "bold"),
        height=36, width=width, corner_radius=8
    )


def success_button(parent, text, command, width=140):
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=GREEN, hover_color="#1B5E20",
        font=("Arial", 12, "bold"),
        height=36, width=width, corner_radius=8
    )


def build_table(parent, headers, rows, col_widths=None):
    """Build a simple grid-based table."""
    frame = ctk.CTkScrollableFrame(parent, fg_color=WHITE)

    # Header row
    for c, h in enumerate(headers):
        w = col_widths[c] if col_widths else 140
        ctk.CTkLabel(
            frame, text=h,
            font=("Arial", 12, "bold"), text_color=DARK,
            fg_color="#EEF2F7", width=w, anchor="w",
            corner_radius=0
        ).grid(row=0, column=c, padx=1, pady=1, sticky="nsew")

    # Data rows
    for r, row in enumerate(rows, start=1):
        bg = WHITE if r % 2 == 0 else GRAY
        for c, cell in enumerate(row):
            w = col_widths[c] if col_widths else 140
            ctk.CTkLabel(
                frame, text=str(cell),
                font=("Arial", 12), text_color=DARK,
                fg_color=bg, width=w, anchor="w",
                corner_radius=0
            ).grid(row=r, column=c, padx=1, pady=1, sticky="nsew")
    return frame


def show_message(parent, message, msg_type="info"):
    color = {"info": BLUE, "success": GREEN,
             "error": RED, "warning": ORANGE}.get(msg_type, BLUE)
    popup = ctk.CTkToplevel(parent)
    popup.title("")
    popup.geometry("380x160")
    popup.resizable(False, False)
    popup.grab_set()
    ctk.CTkLabel(
        popup, text=message,
        font=("Arial", 13), text_color=DARK,
        wraplength=320
    ).pack(expand=True, pady=20)
    ctk.CTkButton(
        popup, text="OK", width=100,
        fg_color=color, command=popup.destroy
    ).pack(pady=(0, 20))


def confirm_dialog(parent, message) -> bool:
    result = [False]
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Confirm")
    dialog.geometry("380x180")
    dialog.resizable(False, False)
    dialog.grab_set()

    ctk.CTkLabel(
        dialog, text=message,
        font=("Arial", 13), text_color=DARK,
        wraplength=320
    ).pack(expand=True, pady=20)

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(pady=(0, 20))

    def yes():
        result[0] = True
        dialog.destroy()

    ctk.CTkButton(
        btn_frame, text="Confirm", fg_color=RED,
        command=yes, width=100
    ).pack(side="left", padx=10)
    ctk.CTkButton(
        btn_frame, text="Cancel", fg_color="#7A8BA0",
        command=dialog.destroy, width=100
    ).pack(side="left", padx=10)

    dialog.wait_window()
    return result[0]