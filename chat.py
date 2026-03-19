# chat.py (private chat with MySQL)
import tkinter as tk
from tkinter import filedialog, scrolledtext
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "peer_chat"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# --- Database Functions ---
def save_message(sender, receiver, message, file_name=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (sender, receiver, message, file_name) VALUES (%s, %s, %s, %s)",
                (sender, receiver, message, file_name))
    conn.commit()
    conn.close()

def load_messages(sender, receiver):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT sender, message, timestamp 
        FROM logs 
        WHERE (sender=%s AND receiver=%s) OR (sender=%s AND receiver=%s) 
        ORDER BY timestamp ASC
    """, (sender, receiver, receiver, sender))
    rows = cur.fetchall()
    conn.close()
    return rows

def load_users(current_user):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE username != %s", (current_user,))
    users = [row[0] for row in cur.fetchall()]
    conn.close()
    return users

# --- Chat Window ---
def open_chat(username="User", master=None):
    chat_win = tk.Toplevel(master) if master else tk.Tk()
    chat_win.title(f"💬 ChatApp - {username}")
    chat_win.geometry("750x500")
    chat_win.configure(bg="#F0F4FF")

    # --- Top bar ---
    top_frame = tk.Frame(chat_win, bg="#457B9D", height=50)
    top_frame.pack(fill=tk.X)

    tk.Label(top_frame, text=f"💬 Welcome, {username}",
             font=("Arial", 14, "bold"), bg="#457B9D", fg="white").pack(side=tk.LEFT, padx=10)

    def logout():
        chat_win.destroy()
        if master:
            master.deiconify()

    tk.Button(top_frame, text="🚪 Logout", bg="#E63946", fg="white",
              font=("Arial", 10, "bold"), command=logout).pack(side=tk.RIGHT, padx=10, pady=5)

    # --- Main body ---
    body_frame = tk.Frame(chat_win, bg="#F0F4FF")
    body_frame.pack(fill=tk.BOTH, expand=True)

    # Left panel (user list)
    left_panel = tk.Frame(body_frame, bg="#A8DADC", width=180)
    left_panel.pack(side=tk.LEFT, fill=tk.Y)

    tk.Label(left_panel, text="🟢 Users", font=("Arial", 12, "bold"),
             bg="#1D3557", fg="white").pack(fill=tk.X)

    user_listbox = tk.Listbox(left_panel, font=("Arial", 11),
                              bg="#F1FAEE", fg="#1D3557")
    user_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Load users from DB
    all_users = load_users(username)
    for u in all_users:
        user_listbox.insert(tk.END, u)

    # Right panel (chat area)
    right_panel = tk.Frame(body_frame, bg="#F0F4FF")
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    chat_area = scrolledtext.ScrolledText(right_panel, wrap=tk.WORD,
                                          font=("Arial", 12),
                                          bg="#F1FAEE", fg="#1D3557",
                                          relief="groove", bd=2, state="disabled")
    chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Current receiver
    current_receiver = tk.StringVar(value="")

    # Bottom input
    bottom_frame = tk.Frame(right_panel, bg="#A8DADC")
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    msg_entry = tk.Text(bottom_frame, height=3, font=("Arial", 12),
                        bg="#F1FAEE", fg="#1D3557", relief="groove", bd=2)
    msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

    # --- Functions ---
    def refresh_chat():
        receiver = current_receiver.get()
        if not receiver:
            return
        chat_area.config(state="normal")
        chat_area.delete("1.0", tk.END)
        msgs = load_messages(username, receiver)
        for sender, msg, ts in msgs:
            chat_area.insert(tk.END, f"[{ts}] {sender}: {msg}\n")
        chat_area.config(state="disabled")
        chat_area.yview(tk.END)

    def on_user_select(event):
        selection = user_listbox.curselection()
        if selection:
            receiver = user_listbox.get(selection[0])
            current_receiver.set(receiver)
            refresh_chat()

    def send_message(event=None):
        receiver = current_receiver.get()
        if not receiver:
            messagebox.showwarning("Chat", "⚠️ Select a user to chat with!")
            return
        message = msg_entry.get("1.0", tk.END).strip()
        if message:
            save_message(sender=username, receiver=receiver, message=message)
            msg_entry.delete("1.0", tk.END)
            refresh_chat()

    def send_file():
        receiver = current_receiver.get()
        if not receiver:
            messagebox.showwarning("Chat", "⚠️ Select a user to chat with!")
            return
        filepath = filedialog.askopenfilename()
        if filepath:
            save_message(sender=username, receiver=receiver, message="[File Sent]", file_name=filepath)
            refresh_chat()

    # Buttons
    tk.Button(bottom_frame, text="📎 File", bg="#1D3557", fg="#F1FAEE",
              font=("Arial", 10, "bold"), command=send_file).pack(side=tk.LEFT, padx=5)

    tk.Button(bottom_frame, text="➡ Send", bg="#457B9D", fg="#F1FAEE",
              font=("Arial", 10, "bold"), command=send_message).pack(side=tk.LEFT, padx=5)

    msg_entry.bind("<Return>", lambda event: (send_message(), "break"))
    user_listbox.bind("<<ListboxSelect>>", on_user_select)

    chat_win.mainloop()

if __name__ == "__main__":
    open_chat("TestUser")
