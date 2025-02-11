import os
import base64
import urllib.parse
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

from config.settings import SECRET_KEY



def fix_base64_padding(b64_string):
    missing_padding = len(b64_string) % 4
    if missing_padding:
        b64_string += "=" * (4 - missing_padding)
    return b64_string


def encrypt_message_and_file(plaintext, file_url):
    salt = os.urandom(16)
    key = PBKDF2(SECRET_KEY, salt, dkLen=32)

    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce

    encrypted_text, tag_text = cipher.encrypt_and_digest(plaintext.encode())
    encrypted_file_url, tag_file = cipher.encrypt_and_digest(file_url.encode())

    encrypted_data = base64.b64encode(salt + nonce + tag_text + encrypted_text).decode()
    encrypted_file = base64.b64encode(salt + nonce + tag_file + encrypted_file_url).decode()

    return encrypted_data, encrypted_file


def decrypt_message_and_file(encrypted_text, encrypted_file_url):
    encrypted_text = base64.b64decode(encrypted_text)
    encrypted_file_url = base64.b64decode(encrypted_file_url)

    salt = encrypted_text[:16]
    nonce = encrypted_text[16:32]
    tag_text = encrypted_text[32:48]
    cipher_text = encrypted_text[48:]

    key = PBKDF2(SECRET_KEY, salt, dkLen=32)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

    decrypted_text = cipher.decrypt_and_verify(cipher_text, tag_text).decode()

    nonce = encrypted_file_url[16:32]
    tag_file = encrypted_file_url[32:48]
    cipher_file = encrypted_file_url[48:]

    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    decrypted_file_url = cipher.decrypt_and_verify(cipher_file, tag_file).decode()

    return decrypted_text, decrypted_file_url
