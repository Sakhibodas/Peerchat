# 💬 PeerChat - Secure Messaging Application

PeerChat is a secure chat application that enables real-time messaging and file sharing between users. It is designed with encryption, compression, and database integration to ensure secure and efficient communication.

---

## 🚀 Features

* 🔐 End-to-end encryption using Fernet
* 💬 Real-time messaging using socket programming
* 📎 File sharing between users
* 🗜️ Data compression for efficient transfer
* 👤 User authentication system
* 🗄️ Chat history stored using MySQL database
* 🖥️ User-friendly GUI built with Tkinter

---

## 🛠️ Tech Stack

* **Language:** Python
* **GUI:** Tkinter
* **Networking:** Socket Programming
* **Encryption:** Cryptography (Fernet)
* **Database:** MySQL
* **Compression:** zlib

---

## 📂 Project Structure

```
peerchat/
│
├── server.py
├── client.py
├── chat.py
├── login.py
├── compression_utils.py
├── encryption_utils.py
├── README.md
```

---

## ⚙️ How to Run the Project

1. Install required libraries:

```
pip install cryptography mysql-connector-python
```

2. Setup MySQL database:

* Create a database named `peer_chat`
* Create required tables (`users`, `logs`)

3. Start the server:

```
python server.py
```

4. Run the client:

```
python client.py
```

5. Login and start chatting 🎉

---

## 📸 Screenshots

### Chat UI

![Chat](screenshots/chat.png)

### Login Page

![Login](screenshots/peerchat_login.png)

---

## 🔒 Security Note

⚠️ Do NOT upload `secret.key` or sensitive credentials to GitHub.

---

## 🌟 Future Improvements

* Group chat functionality
* Online/offline status
* Message notifications
* Improved UI/UX

---

## 👩‍💻 Author

**Sakhi Bodas**
