# login.py (MySQL + Login + Launch chat_client)
import tkinter as tk
from tkinter import messagebox
import chat_client   # ✅ use the merged chat client
import mysql.connector

# --- Database Config ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",        # change if needed
    "password": "",        # add your MySQL password if set
    "database": "peer_chat"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# --- Database Functions ---
def load_user(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password, email FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"password": row[0], "email": row[1]}
    return None

def save_user(username, password, email):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                    (username, email, password))
        conn.commit()
    except mysql.connector.IntegrityError:
        conn.rollback()
        conn.close()
        return False
    conn.close()
    return True

# --- Login GUI ---
def open_login():
    login_win = tk.Tk()
    login_win.title("🔑 Login")
    login_win.geometry("420x360")
    login_win.configure(bg="#F0F4FF")

    tk.Label(login_win, text="💬 ChatApp Login",
             font=("Arial", 18, "bold"), bg="#F0F4FF", fg="#1D3557").pack(pady=15)

    tk.Label(login_win, text="Username:", bg="#F0F4FF", font=("Arial", 12)).pack()
    username_entry = tk.Entry(login_win, font=("Arial", 12), width=25)
    username_entry.pack(pady=6)

    tk.Label(login_win, text="Password:", bg="#F0F4FF", font=("Arial", 12)).pack()
    password_entry = tk.Entry(login_win, show="*", font=("Arial", 12), width=25)
    password_entry.pack(pady=6)

    # 👁️ Show Password Checkbox
    def toggle_password():
        password_entry.config(show="" if show_pass_var.get() else "*")

    show_pass_var = tk.BooleanVar()
    tk.Checkbutton(login_win, text="Show Password 👁️",
                   variable=show_pass_var, command=toggle_password,
                   bg="#F0F4FF", font=("Arial", 10)).pack()

    # --- Login Function ---
    def login_user():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        user = load_user(username)
        if user and user["password"] == password:
            messagebox.showinfo("Login", "✅ Login successful!")
            login_win.withdraw()  # hide login window
            # ✅ open chat client as Toplevel attached to login window
            chat_client.open_chat(username, master=login_win)
        else:
            messagebox.showerror("Login", "❌ Invalid credentials")

    # --- Register Window ---
    def open_register():
        reg_win = tk.Toplevel(login_win)
        reg_win.title("📝 Register")
        reg_win.geometry("420x430")
        reg_win.configure(bg="#F0F4FF")

        tk.Label(reg_win, text="📝 Register New User",
                 font=("Arial", 16, "bold"), bg="#F0F4FF", fg="#1D3557").pack(pady=15)

        tk.Label(reg_win, text="Username:", bg="#F0F4FF", font=("Arial", 12)).pack()
        reg_user = tk.Entry(reg_win, font=("Arial", 12), width=25)
        reg_user.pack(pady=6)

        tk.Label(reg_win, text="Password:", bg="#F0F4FF", font=("Arial", 12)).pack()
        reg_pass = tk.Entry(reg_win, show="*", font=("Arial", 12), width=25)
        reg_pass.pack(pady=6)

        def toggle_reg_password():
            reg_pass.config(show="" if reg_show_pass_var.get() else "*")

        reg_show_pass_var = tk.BooleanVar()
        tk.Checkbutton(reg_win, text="Show Password 👁️",
                       variable=reg_show_pass_var, command=toggle_reg_password,
                       bg="#F0F4FF", font=("Arial", 10)).pack()

        tk.Label(reg_win, text="Email:", bg="#F0F4FF", font=("Arial", 12)).pack()
        reg_email = tk.Entry(reg_win, font=("Arial", 12), width=25)
        reg_email.pack(pady=6)

        def register_user():
            u = reg_user.get().strip()
            p = reg_pass.get().strip()
            e = reg_email.get().strip()

            if u and p and e:
                if save_user(u, p, e):
                    messagebox.showinfo("Register", "✅ Registration successful!")
                    reg_win.destroy()
                else:
                    messagebox.showerror("Register", "⚠️ User already exists!")
            else:
                messagebox.showerror("Register", "❌ Please fill all fields!")

        tk.Button(reg_win, text="Register", bg="#457B9D", fg="white",
                  font=("Arial", 12), command=register_user).pack(pady=15)

    # Buttons
    tk.Button(login_win, text="Login", bg="#457B9D", fg="white",
              font=("Arial", 12), command=login_user).pack(pady=10)
    tk.Button(login_win, text="Register", bg="#1D3557", fg="white",
              font=("Arial", 12), command=open_register).pack()

    login_win.mainloop()

if __name__ == "__main__":
    open_login()
