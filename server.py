import socket
import threading
from cryptography.fernet import Fernet

# -------------------------------
# Server Configuration
# -------------------------------
HOST = "0.0.0.0"
PORT = 5050
SECRET_KEY = b'zpUxW2WF9XboYxuFiaXoDVZ9PSzNf1TIxmBpq0JBW2s='
cipher = Fernet(SECRET_KEY)

clients = {}  # username -> socket


def send_to_user(target, message: bytes):
    if target in clients:
        try:
            clients[target].send(message)
        except:
            print(f"[ERROR] Could not send to {target}")
            clients.pop(target, None)


def broadcast(message: bytes, exclude_socket=None):
    for user, client in list(clients.items()):
        if client != exclude_socket:
            try:
                client.send(message)
            except:
                print(f"[ERROR] Could not send to {user}")
                clients.pop(user, None)


def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr}")
    username = None

    try:
        raw = client_socket.recv(1024).decode()
        if raw.startswith("/username:"):
            username = raw.split(":", 1)[1].strip()
            clients[username] = client_socket
            print(f"[LOGIN] {username} connected from {addr}")
        else:
            client_socket.close()
            return
    except Exception as e:
        print(f"[ERROR] Failed login from {addr}: {e}")
        client_socket.close()
        return

    file_mode = False
    file_target = None
    filename = ""
    filesize = 0

    while True:
        try:
            message = client_socket.recv(4096)
            if not message:
                break

            text_msg = None
            try:
                decrypted = cipher.decrypt(message).decode(errors="ignore")
                text_msg = decrypted
            except:
                pass

            if text_msg:
                # Handle private message
                if text_msg.startswith("/private:"):
                    parts = text_msg.split(":", 2)
                    if len(parts) == 3:
                        target, msg = parts[1], parts[2]
                        print(f"[PRIVATE] {username} -> {target}: {msg}")
                        encrypted_forward = cipher.encrypt(f"{username}:{msg}".encode())
                        send_to_user(target, encrypted_forward)

                # Handle file transfer header
                elif text_msg.startswith("/file:"):
                    parts = text_msg.split(":", 3)
                    if len(parts) == 4:
                        _, file_target, filename, filesize = parts
                        file_mode = True
                        filesize = int(filesize)
                        print(f"[FILE START] {username} sending {filename} ({filesize} bytes) to {file_target}")
                        header = f"/file:{username}:{filename}:{filesize}"
                        send_to_user(file_target, cipher.encrypt(header.encode()))
                    else:
                        print(f"[ERROR] Invalid file command: {text_msg}")
                        send_to_user(username, cipher.encrypt(b"[ERROR] Invalid file command"))

                # Handle file transfer end
                elif text_msg == "/endfile":
                    if file_target:
                        send_to_user(file_target, cipher.encrypt(b"/endfile"))
                        print(f"[FILE COMPLETE] {filename} sent to {file_target}")
                    file_mode = False
                    file_target = None
                    filename = ""
                    filesize = 0

                # Handle normal broadcast message
                else:
                    print(f"[CHAT] {username}: {text_msg}")
                    broadcast(message, exclude_socket=client_socket)

            # Forward file chunks (raw bytes)
            elif file_mode and file_target:
                send_to_user(file_target, message)

        except Exception as e:
            print(f"[ERROR] {username} disconnected. {e}")
            break

    print(f"[DISCONNECTED] {username}")
    if username in clients:
        del clients[username]
    client_socket.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[STARTED] Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True)
        thread.start()


if __name__ == "__main__":
    start_server()
