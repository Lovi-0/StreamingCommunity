# 03.04.24

import subprocess
import logging
import os


# External library
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad



class M3U8_Decryption:
    def __init__(self, key: bytes, iv: bytes = None) -> None:
        """
        Initialize the M3U8_Decryption class.

        Args:
            - key (bytes): Encryption key.
            - method (str): Encryption method (e.g., "AES", "Blowfish").
            - iv (bytes): Initialization Vector (bytes), default is None.
        """

        self.key = key
        self.iv = iv

    def set_method(self, method: str):
        """
        Set the encryption method.

        Args:
            - method (str): Encryption method (e.g., "AES", "Blowfish").
        """

        self.method = method

    def parse_key(self, raw_iv: str) -> None:
        """
        Parse the raw IV string and set the IV.

        Args:
            - raw_iv (str): Raw IV string in hexadecimal format (e.g., "43A6D967D5C17290D98322F5C8F6660B").
        """

        if "0x" in str(raw_iv):
            self.iv = bytes.fromhex(raw_iv.replace("0x", ""))
        else:
            self.iv = raw_iv

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt the ciphertext using the specified encryption method.

        Args:
            ciphertext (bytes): The encrypted content to decrypt.

        Returns:
            bytes: The decrypted content.
        """
        if self.method == "AES":
            cipher = AES.new(self.key, AES.MODE_ECB)
            decrypted_data = cipher.decrypt(ciphertext)
            return unpad(decrypted_data, AES.block_size)

        elif self.method == "AES-128":
            cipher = AES.new(self.key[:16], AES.MODE_CBC, iv=self.iv)
            decrypted_data = cipher.decrypt(ciphertext)
            return unpad(decrypted_data, AES.block_size)

        elif self.method == "AES-128-CTR":
            cipher = AES.new(self.key[:16], AES.MODE_CTR, nonce=self.iv)
            return cipher.decrypt(ciphertext)

        else:
            raise ValueError("Invalid or unsupported method")