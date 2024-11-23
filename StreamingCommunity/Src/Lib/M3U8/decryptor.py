# 03.04.24

import sys
import logging
import subprocess
import importlib.util


# Internal utilities
from StreamingCommunity.Src.Util.console import console


# Check if Crypto module is installed
crypto_spec = importlib.util.find_spec("Crypto")
crypto_installed = crypto_spec is not None


if crypto_installed:
    logging.info("Decrypy use: Crypto")
    from Crypto.Cipher import AES # type: ignore
    from Crypto.Util.Padding import unpad # type: ignore

    class M3U8_Decryption:
        """
        Class for decrypting M3U8 playlist content using AES encryption when the Crypto module is available.
        """
        def __init__(self, key: bytes, iv: bytes, method: str) -> None:
            """
            Initialize the M3U8_Decryption object.

            Parameters:
                - key (bytes): The encryption key.
                - iv (bytes): The initialization vector (IV).
                - method (str): The encryption method.
            """
            self.key = key
            if "0x" in str(iv):
                self.iv = bytes.fromhex(iv.replace("0x", ""))
            else:
                self.iv = iv
            self.method = method
            logging.info(f"Decrypt add: ('key': {self.key}, 'iv': {self.iv}, 'method': {self.method})")

        def decrypt(self, ciphertext: bytes) -> bytes:
            """
            Decrypt the ciphertext using the specified encryption method.

            Parameters:
                - ciphertext (bytes): The encrypted content to decrypt.

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

else:

    # Check if openssl command is available
    try:
        openssl_available = subprocess.run(["openssl", "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        logging.info("Decrypy use: OPENSSL")
    except:
        openssl_available = False

    if not openssl_available:
        console.log("[red]Neither python library: pycryptodome nor openssl software is installed. Please install either one of them. Read readme.md [Requirement].")
        sys.exit(0)

    class M3U8_Decryption:
        """
        Class for decrypting M3U8 playlist content using OpenSSL when the Crypto module is not available.
        """
        def __init__(self, key: bytes, iv: bytes, method: str) -> None:
            """
            Initialize the M3U8_Decryption object.

            Parameters:
                - key (bytes): The encryption key.
                - iv (bytes): The initialization vector (IV).
                - method (str): The encryption method.
            """
            self.key = key
            if "0x" in str(iv):
                self.iv = bytes.fromhex(iv.replace("0x", ""))
            else:
                self.iv = iv
            self.method = method
            logging.info(f"Decrypt add: ('key': {self.key}, 'iv': {self.iv}, 'method': {self.method})")

        def decrypt(self, ciphertext: bytes) -> bytes:
            """
            Decrypt the ciphertext using the specified encryption method.

            Parameters:
                - ciphertext (bytes): The encrypted content to decrypt.

            Returns:
                bytes: The decrypted content.
            """
            if self.method == "AES":
                openssl_cmd = f'openssl enc -d -aes-256-ecb -K {self.key.hex()} -nosalt'
            elif self.method == "AES-128":
                openssl_cmd = f'openssl enc -d -aes-128-cbc -K {self.key[:16].hex()} -iv {self.iv.hex()}'
            elif self.method == "AES-128-CTR":
                openssl_cmd = f'openssl enc -d -aes-128-ctr -K {self.key[:16].hex()} -iv {self.iv.hex()}'
            else:
                raise ValueError("Invalid or unsupported method")

            try:
                decrypted_data = subprocess.check_output(openssl_cmd.split(), input=ciphertext, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                raise ValueError(f"Decryption failed: {e.output.decode()}")

            return decrypted_data