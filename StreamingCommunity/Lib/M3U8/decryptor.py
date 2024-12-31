# 03.04.24

import sys
import time
import logging
import subprocess
import importlib.util


# Internal utilities
from StreamingCommunity.Util.console import console


# Check if Crypto module is installed
crypto_spec = importlib.util.find_spec("Cryptodome")
crypto_installed = crypto_spec is not None


if crypto_installed:
    logging.info("[cyan]Decrypy use: Cryptodomex")
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import unpad

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
            self.iv = iv
            if "0x" in str(iv): 
                self.iv = bytes.fromhex(iv.replace("0x", ""))
            self.method = method

            # Precreate cipher based on encryption method
            if self.method == "AES":
                self.cipher = AES.new(self.key, AES.MODE_ECB)
            elif self.method == "AES-128":
                self.cipher = AES.new(self.key[:16], AES.MODE_CBC, iv=self.iv)
            elif self.method == "AES-128-CTR":
                self.cipher = AES.new(self.key[:16], AES.MODE_CTR, nonce=self.iv)
            else:
                raise ValueError("Invalid or unsupported method")

        def decrypt(self, ciphertext: bytes) -> bytes:
            """
            Decrypt the ciphertext using the specified encryption method.

            Parameters:
                - ciphertext (bytes): The encrypted content to decrypt.

            Returns:
                bytes: The decrypted content.
            """
            start = time.perf_counter_ns()

            # Decrypt based on encryption method
            if self.method in {"AES", "AES-128"}:
                decrypted_data = self.cipher.decrypt(ciphertext)
                decrypted_content = unpad(decrypted_data, AES.block_size)
                
            elif self.method == "AES-128-CTR":
                decrypted_content = self.cipher.decrypt(ciphertext)
            else:
                raise ValueError("Invalid or unsupported method")

            end = time.perf_counter_ns() 

            # Calculate elapsed time with high precision
            elapsed_nanoseconds = end - start
            elapsed_milliseconds = elapsed_nanoseconds / 1_000_000
            elapsed_seconds = elapsed_nanoseconds / 1_000_000_000

            # Print performance metrics
            logging.info(f"[Crypto Decryption Performance]")
            logging.info(f"Method: {self.method}")
            logging.info(f"Decryption Time: {elapsed_milliseconds:.4f} ms ({elapsed_seconds:.6f} s)")
            logging.info(f"Decrypted Content Length: {len(decrypted_content)} bytes")

            return decrypted_content


else:

    # Check if openssl command is available
    try:
        openssl_available = subprocess.run(["openssl", "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        logging.info("[cyan]Decrypy use: OPENSSL")
    except:
        openssl_available = False

    if not openssl_available:
        console.log("[red]Neither python library: pycryptodomex nor openssl software is installed. Please install either one of them. Read readme.md [Requirement].")
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
            self.iv = iv
            if "0x" in str(iv): 
                self.iv = bytes.fromhex(iv.replace("0x", ""))
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
            start = time.perf_counter_ns()

            # Construct OpenSSL command based on encryption method
            if self.method == "AES":
                openssl_cmd = f'openssl enc -d -aes-256-ecb -K {self.key.hex()} -nosalt'
            elif self.method == "AES-128":
                openssl_cmd = f'openssl enc -d -aes-128-cbc -K {self.key[:16].hex()} -iv {self.iv.hex()}'
            elif self.method == "AES-128-CTR":
                openssl_cmd = f'openssl enc -d -aes-128-ctr -K {self.key[:16].hex()} -iv {self.iv.hex()}'
            else:
                raise ValueError("Invalid or unsupported method")

            try:
                decrypted_content = subprocess.check_output(openssl_cmd.split(), input=ciphertext, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                raise ValueError(f"Decryption failed: {e.output.decode()}")

            end = time.perf_counter_ns()

            # Calculate elapsed time with high precision
            elapsed_nanoseconds = end - start
            elapsed_milliseconds = elapsed_nanoseconds / 1_000_000
            elapsed_seconds = elapsed_nanoseconds / 1_000_000_000

            # Print performance metrics
            logging.info(f"[OpenSSL Decryption Performance]")
            logging.info(f"Method: {self.method}")
            logging.info(f"Decryption Time: {elapsed_milliseconds:.4f} ms ({elapsed_seconds:.6f} s)")
            logging.info(f"Decrypted Content Length: {len(decrypted_content)} bytes")

            return decrypted_content