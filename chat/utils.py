import os
import base64
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from config.settings import SECRET_KEY


def encrypt_message_and_file(plain_text: str):
    key = SHA256.new(SECRET_KEY.encode()).digest()
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(plain_text.encode(), AES.block_size))
    return base64.b64encode(iv + encrypted).decode()

def decrypt_message_and_file(encrypted_text: str):
    key = SHA256.new(SECRET_KEY.encode()).digest()
    data = base64.b64decode(encrypted_text)
    iv, encrypted = data[:16], data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted), AES.block_size).decode()
