import socket
import threading
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from cryptography.fernet import Fernet
import mysql.connector

# -------------------------------
# DB Config
# -------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "peer_chat"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def save_message(sender, receiver, message, file_name=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (sender, receiver, message, file_name) VALUES (%s, %s, %s, %s)",
                (sender, receiver, message, file_name))
    conn.commit()
    conn.close()

def load_users(current_user):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username FROM users WHERE username != %s", (current_user,))
    users = [row[0] for row in cur.fetchall()]
    conn.close()
    return users


# -------------------------------
# Network Config
# -------------------------------
HOST = "127.0.0.1"
PORT = 5050
SECRET_KEY = b'zpUxW2WF9XboYxuFiaXoDVZ9PSzNf1TIxmBpq0JBW2s='
cipher = Fernet(SECRET_KEY)

client_socket = None
username_global = None
chat_area = None
current_receiver = None


# -------------------------------
# Socket Functions
# -------------------------------
def receive_messages():
    global chat_area
    file_mode = False
    file_data = b""
    filename = ""
    sender_user = ""

    while True:
        try:
            message = client_socket.recv(4096)
            if not message:
                break

            try:
                decrypted = cipher.decrypt(message).decode(errors="ignore")
            except Exception:
                decrypted = None

            if not file_mode:
                # Detect file start
                if decrypted and decrypted.startswith("/file:"):
                    parts = decrypted.split(":", 3)
                    if len(parts) == 4:
                        _, sender_user, filename, filesize = parts
                        file_mode = True
                        file_data = b""
                        append_chat(f"[FILE INCOMING] {filename} from {sender_user}")
                elif decrypted:
                    append_chat(f"[CHAT] {decrypted}")

            else:
                # Receiving encrypted file chunks
                try:
                    chunk_decrypted = cipher.decrypt(message).decode(errors="ignore")
                    if chunk_decrypted == "/endfile":
                        # Save the file once end marker arrives
                        save_path = filedialog.asksaveasfilename(
                            initialfile=filename,
                            title="Save File As",
                            defaultextension=os.path.splitext(filename)[1]
                        )
                        if save_path:
                            with open(save_path, "wb") as f:
                                f.write(file_data)
                            append_chat(f"[FILE RECEIVED] Saved as {save_path}")
                        else:
                            append_chat("[FILE RECEIVED] File not saved.")

                        # Reset file transfer state
                        file_mode = False
                        file_data = b""
                        filename = ""
                        sender_user = ""
                        continue

                except Exception:
                    # Not decryptable → raw binary data
                    try:
                        file_data += cipher.decrypt(message)
                    except:
                        # If still fails, just append raw bytes
                        file_data += message

        except Exception as e:
            append_chat(f"[ERROR] Connection lost: {e}")
            client_socket.close()
            break



def send_text(receiver, text):
    payload = f"/private:{receiver}:{text}"
    encrypted = cipher.encrypt(payload.encode())
    client_socket.send(encrypted)
    save_message(username_global, receiver, text)


def send_file(receiver, filepath):
    if not os.path.isfile(filepath):
        append_chat("[ERROR] File not found.")
        return

    filename_only = os.path.basename(filepath).replace(":", "_")
    filesize = os.path.getsize(filepath)

    header = f"/file:{receiver}:{filename_only}:{filesize}"
    client_socket.send(cipher.encrypt(header.encode()))

    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            client_socket.send(chunk)

    client_socket.send(cipher.encrypt(b"/endfile"))
    append_chat(f"[SENT] {filename_only} → {receiver}")
    save_message(username_global, receiver, "[File Sent]", filename_only)


# -------------------------------
# Tkinter UI
# -------------------------------
def append_chat(text):
    chat_area.config(state="normal")
    chat_area.insert(tk.END, text + "\n")
    chat_area.config(state="disabled")
    chat_area.yview(tk.END)


def open_chat(username="User", master=None):
    global chat_area, current_receiver, client_socket, username_global
    username_global = username

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.send(f"/username:{username}".encode())

    threading.Thread(target=receive_messages, daemon=True).start()

    chat_win = tk.Toplevel(master) if master else tk.Tk()
    chat_win.title(f"💬 ChatApp - {username}")
    chat_win.geometry("750x500")
    chat_win.configure(bg="#F0F4FF")

    top_frame = tk.Frame(chat_win, bg="#457B9D", height=50)
    top_frame.pack(fill=tk.X)
    tk.Label(top_frame, text=f"💬 Welcome, {username}",
             font=("Arial", 14, "bold"), bg="#457B9D", fg="white").pack(side=tk.LEFT, padx=10)
    tk.Button(top_frame, text="🚪 Logout", bg="#E63946", fg="white",
              font=("Arial", 10, "bold"), command=chat_win.destroy).pack(side=tk.RIGHT, padx=10, pady=5)

    body_frame = tk.Frame(chat_win, bg="#F0F4FF")
    body_frame.pack(fill=tk.BOTH, expand=True)

    left_panel = tk.Frame(body_frame, bg="#A8DADC", width=180)
    left_panel.pack(side=tk.LEFT, fill=tk.Y)
    tk.Label(left_panel, text="🟢 Users", font=("Arial", 12, "bold"),
             bg="#1D3557", fg="white").pack(fill=tk.X)
    user_listbox = tk.Listbox(left_panel, font=("Arial", 11), bg="#F1FAEE", fg="#1D3557")
    user_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    all_users = load_users(username)
    for u in all_users:
        user_listbox.insert(tk.END, u)

    right_panel = tk.Frame(body_frame, bg="#F0F4FF")
    right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    global_chat = scrolledtext.ScrolledText(right_panel, wrap=tk.WORD, font=("Arial", 12),
                                            bg="#F1FAEE", fg="#1D3557",
                                            relief="groove", bd=2, state="disabled")
    global_chat.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    chat_area = global_chat
    current_receiver = tk.StringVar(value="")

    bottom_frame = tk.Frame(right_panel, bg="#A8DADC")
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
    msg_entry = tk.Text(bottom_frame, height=3, font=("Arial", 12),
                        bg="#F1FAEE", fg="#1D3557", relief="groove", bd=2)
    msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

    def on_user_select(event):
        selection = user_listbox.curselection()
        if selection:
            receiver = user_listbox.get(selection[0])
            current_receiver.set(receiver)

    def send_message():
        receiver = current_receiver.get()
        if not receiver:
            messagebox.showwarning("Chat", "⚠️ Select a user to chat with!")
            return
        message = msg_entry.get("1.0", tk.END).strip()
        if message:
            send_text(receiver, message)
            msg_entry.delete("1.0", tk.END)

    def send_file_ui():
        receiver = current_receiver.get()
        if not receiver:
            messagebox.showwarning("Chat", "⚠️ Select a user to chat with!")
            return
        filepath = filedialog.askopenfilename()
        if filepath:
            send_file(receiver, filepath)

    tk.Button(bottom_frame, text="📎 File", bg="#1D3557", fg="#F1FAEE",
              font=("Arial", 10, "bold"), command=send_file_ui).pack(side=tk.LEFT, padx=5)
    tk.Button(bottom_frame, text="➡ Send", bg="#457B9D", fg="#F1FAEE",
              font=("Arial", 10, "bold"), command=send_message).pack(side=tk.LEFT, padx=5)

    msg_entry.bind("<Return>", lambda event: (send_message(), "break"))
    user_listbox.bind("<<ListboxSelect>>", on_user_select)

    chat_win.mainloop()
