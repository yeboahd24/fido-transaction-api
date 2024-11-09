from cryptography.fernet import Fernet
import cryptography
import os

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()
f = Fernet(ENCRYPTION_KEY)


def encrypt_data(data: str) -> str:
    return f.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str) -> str:
    return f.decrypt(encrypted_data.encode()).decode()


def hash_password(password: str) -> str:
    return f.encrypt(password.encode()).decode()


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return f.decrypt(hashed_password.encode()).decode() == password
    except cryptography.fernet.InvalidToken:
        return False
