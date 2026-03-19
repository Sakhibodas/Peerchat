import socket
import threading
import zlib
from cryptography.fernet import Fernet
import os

# -------------------------------
# Client Configuration
# -------------------------------
HOST = "127.0.0.1"  # Change to server's LAN IP
PORT = 5050
SECRET_KEY = b'zpUxW2WF9XboYxuFiaXoDVZ9PSzNf1TIxmBpq0JBW2s='
cipher = Fernet(SECRET_KEY)

# -------------------------------
# Receive Messages
# -------------------------------
def receive_messages(client_socket):
    file_mode = False
    file_data = b""
    filename = ""

    while True:
        try:
            message = client_socket.recv(4096)
            if not message:
                break

            # Try to decrypt
            try:
                decrypted = cipher.decrypt(message).decode(errors="ignore")
            except:
                decrypted = None

            if decrypted:
                if decrypted.startswith("/file:"):
                    filename = decrypted.split(":", 1)[1]
                    file_data = b""
                    file_mode = True
                    print(f"[FILE INCOMING] {filename}")
                elif decrypted == "/endfile":
                    # Decrypt and decompress the received file data
                    try:
                        final_decrypted = cipher.decrypt(file_data)
                        # Uncomment if you compress on server:
                        # final_file = zlib.decompress(final_decrypted)
                        final_file = final_decrypted  # if no compression
                        save_path = "received_" + filename
                        with open(save_path, "wb") as f:
                            f.write(final_file)
                        print(f"[FILE RECEIVED] Saved as {save_path}")
                    except Exception as e:
                        print(f"[ERROR] Saving file: {e}")
                    file_mode = False
                    file_data = b""
                    filename = ""
                else:
                    print(f"[CHAT] {decrypted}")
            elif file_mode:
                file_data += message  # Collect raw data

        except Exception as e:
            print(f"[ERROR] Connection lost: {e}")
            client_socket.close()
            break

# -------------------------------
# Send Messages / Files
# -------------------------------
def send_messages(client_socket, username):
    while True:
        msg = input("")

        try:
            if msg.startswith("/sendfile "):
                filepath = msg.split(" ", 1)[1]
                if not os.path.isfile(filepath):
                    print("[ERROR] File not found.")
                    continue

                filename_only = os.path.basename(filepath)
                with open(filepath, "rb") as f:
                    raw_data = f.read()

                compressed = zlib.compress(raw_data)
                encrypted_data = cipher.encrypt(compressed)

                client_socket.send(cipher.encrypt(f"/file:{filename_only}".encode()))
                chunk_size = 4096
                sent = 0
                while sent < len(encrypted_data):
                    chunk = encrypted_data[sent:sent+chunk_size]
                    client_socket.send(chunk)
                    sent += chunk_size
                client_socket.send(cipher.encrypt(b"/endfile"))
                print(f"[SENT] {filename_only}")

            elif msg.startswith("/msg "):
                # /msg Bob Hello!
                parts = msg.split(" ", 2)
                if len(parts) < 3:
                    print("Usage: /msg <user> <message>")
                    continue
                target = parts[1]
                real_msg = parts[2]
                payload = f"/private:{target}:{real_msg}"
                encrypted = cipher.encrypt(payload.encode())
                client_socket.send(encrypted)

            else:
                # Global broadcast (if needed)
                encrypted = cipher.encrypt(msg.encode())
                client_socket.send(encrypted)

        except Exception as e:
            print(f"[ERROR] Could not send: {e}")
            client_socket.close()
            break

# -------------------------------
# Start Client
# -------------------------------
def start_client(username):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"[CONNECTED] Connected to {HOST}:{PORT}")

    # Send username to server
    client_socket.send(f"/username:{username}".encode())

    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()
    threading.Thread(target=send_messages, args=(client_socket, username), daemon=True).start()

    while True:
        pass

if __name__ == "__main__":
    uname = input("Enter your username: ")
    start_client(uname)
