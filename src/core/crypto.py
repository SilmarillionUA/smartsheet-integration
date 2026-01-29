from base64 import b64decode, b64encode

from django.conf import settings

from Crypto.Cipher import AES

CIPHER_SEPARATOR = "$"


def get_encryption_key():
    key = getattr(settings, "DB_ENCRYPTION_KEY", "")
    if not key or len(key) != 32:
        raise ValueError("DB_ENCRYPTION_KEY must be exactly 32 characters")
    return bytes(key, "utf-8")


def encrypt(plaintext):
    if not plaintext:
        return plaintext
    plaintext = bytes(plaintext, "utf-8")
    key = get_encryption_key()
    cipher = AES.new(key, AES.MODE_CTR)
    ciphertext = cipher.encrypt(plaintext)
    ciphertext_b64 = b64encode(ciphertext).decode("utf-8")
    nonce_b64 = b64encode(cipher.nonce).decode("utf-8")
    return f"{nonce_b64}{CIPHER_SEPARATOR}{ciphertext_b64}"


def decrypt(encrypted):
    if not encrypted or CIPHER_SEPARATOR not in encrypted:
        return encrypted
    nonce_b64, ciphertext_b64 = encrypted.split(CIPHER_SEPARATOR)
    nonce = b64decode(nonce_b64)
    ciphertext = b64decode(ciphertext_b64)
    key = get_encryption_key()
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    return cipher.decrypt(ciphertext).decode("utf-8")
