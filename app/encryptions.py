# Code taken from: https://medium.com/@bh03051999/aes-gcm-encryption-and-decryption-for-python-java-and-typescript-562dcaa96c22

import base64
import hashlib

from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

HASH_NAME = "SHA512"
IV_LENGTH = 12
ITERATION_COUNT = 65535
KEY_LENGTH = 32
SALT_LENGTH = 16
TAG_LENGTH = 16


def encrypt(password, plain_message):
    salt = get_random_bytes(SALT_LENGTH)
    iv = get_random_bytes(IV_LENGTH)
    secret = get_secret_key(password, salt)
    cipher = AES.new(secret, AES.MODE_GCM, iv)
    encrypted_message_byte, tag = cipher.encrypt_and_digest(
        plain_message.encode("utf-8")
    )
    cipher_byte = salt + iv + encrypted_message_byte + tag
    encoded_cipher_byte = base64.b64encode(cipher_byte)
    return bytes.decode(encoded_cipher_byte)


def decrypt(password, cipher_message):
    decoded_cipher_byte = base64.b64decode(cipher_message)
    salt = decoded_cipher_byte[:SALT_LENGTH]
    iv = decoded_cipher_byte[SALT_LENGTH : (SALT_LENGTH + IV_LENGTH)]
    encrypted_message_byte = decoded_cipher_byte[
        (IV_LENGTH + SALT_LENGTH) : -TAG_LENGTH
    ]
    tag = decoded_cipher_byte[-TAG_LENGTH:]
    secret = get_secret_key(password, salt)
    cipher = AES.new(secret, AES.MODE_GCM, iv)
    decrypted_message_byte = cipher.decrypt_and_verify(encrypted_message_byte, tag)
    return decrypted_message_byte.decode("utf-8")


def get_secret_key(password, salt):
    return hashlib.pbkdf2_hmac(
        HASH_NAME, password.encode(), salt, ITERATION_COUNT, KEY_LENGTH
    )


def test():
    outputFormat = "{:<25}:{}"

    secret_key = "your_secure_key"
    plain_text = "organizations/93643ddf-fa0d-4b94-acf2-e7df9332b811/apiKeys/3a50434b-0cf0-42ac-a16c-be26d73f7b65"

    print("------ AES-GCM Encryption ------")
    cipher_text = encrypt(secret_key, plain_text)
    print(outputFormat.format("encryption input", plain_text))
    print(outputFormat.format("encryption output", cipher_text))

    decrypted_text = decrypt(secret_key, cipher_text)

    print("\n------ AES-GCM Decryption ------")
    print(outputFormat.format("decryption input", cipher_text))
    print(outputFormat.format("decryption output", decrypted_text))


if __name__ == "__main__":
    test()
