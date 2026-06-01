import sys
import os

# Make sure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import DatabaseConfig
from views.shared.login_window import LoginWindow


def main():
    # Initialize DB connection pool
    try:
        DatabaseConfig.initialize_pool()
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Database Error",
            f"Could not connect to the database.\n\n{e}\n\n"
            "Please check your .env file and PostgreSQL settings."
        )
        root.destroy()
        sys.exit(1)

    # Launch login window
    app = LoginWindow()
    app.mainloop()

    # Cleanup
    DatabaseConfig.close_all()


if __name__ == "__main__":
    main()