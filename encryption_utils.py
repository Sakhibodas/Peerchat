from cryptography.fernet import Fernet

# -------------------------------
# Key Management
# -------------------------------

def generate_key(filename: str = "secret.key") -> bytes:
    """
    Generates a symmetric encryption key and saves it in a file.
    Returns the generated key.
    """
    key = Fernet.generate_key()
    with open(filename, "wb") as key_file:
        key_file.write(key)
    return key

def load_key(filename: str = "secret.key") -> bytes:
    """
    Loads the encryption key from a file.
    """
    with open(filename, "rb") as key_file:
        return key_file.read()

# -------------------------------
# Message Encryption / Decryption
# -------------------------------

def encrypt_message(message: str, key: bytes) -> bytes:
    """
    Encrypts a text message using the provided key.
    """
    f = Fernet(key)
    encrypted = f.encrypt(message.encode())
    return encrypted

def decrypt_message(encrypted_message: bytes, key: bytes) -> str:
    """
    Decrypts a text message using the provided key.
    """
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_message).decode()
    return decrypted

# -------------------------------
# File Encryption / Decryption
# -------------------------------

def encrypt_file(input_file: str, output_file: str, key: bytes):
    """
    Encrypts the contents of a file and writes it to a new file.
    """
    f = Fernet(key)
    with open(input_file, "rb") as file:
        data = file.read()
    encrypted_data = f.encrypt(data)
    with open(output_file, "wb") as file:
        file.write(encrypted_data)

def decrypt_file(input_file: str, output_file: str, key: bytes):
    """
    Decrypts the contents of a file and writes it to a new file.
    """
    f = Fernet(key)
    with open(input_file, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data)
    with open(output_file, "wb") as file:
        file.write(decrypted_data)




