# 03.04.24

# Import
import subprocess
import logging
import os

# External library
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

class AES_ECB:
    def __init__(self, key: bytes) -> None:
        """
        Initialize AES ECB mode encryption/decryption object.

        Args:
            key (bytes): The encryption key.

        Returns:
            None
        """
        self.key = key

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypt plaintext using AES ECB mode.

        Args:
            plaintext (bytes): The plaintext to encrypt.

        Returns:
            bytes: The encrypted ciphertext.
        """
        cipher = AES.new(self.key, AES.MODE_ECB)
        return cipher.encrypt(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt ciphertext using AES ECB mode.

        Args:
            ciphertext (bytes): The ciphertext to decrypt.

        Returns:
            bytes: The decrypted plaintext.
        """
        cipher = AES.new(self.key, AES.MODE_ECB)
        decrypted_data = cipher.decrypt(ciphertext)
        return unpad(decrypted_data, AES.block_size)

class AES_CBC:
    def __init__(self, key: bytes, iv: bytes) -> None:
        """
        Initialize AES CBC mode encryption/decryption object.

        Args:
            key (bytes): The encryption key.
            iv (bytes): The initialization vector.

        Returns:
            None
        """
        self.key = key
        self.iv = iv

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypt plaintext using AES CBC mode.

        Args:
            plaintext (bytes): The plaintext to encrypt.

        Returns:
            bytes: The encrypted ciphertext.
        """
        cipher = AES.new(self.key, AES.MODE_CBC, iv=self.iv)
        return cipher.encrypt(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt ciphertext using AES CBC mode.

        Args:
            ciphertext (bytes): The ciphertext to decrypt.

        Returns:
            bytes: The decrypted plaintext.
        """
        cipher = AES.new(self.key, AES.MODE_CBC, iv=self.iv)
        decrypted_data = cipher.decrypt(ciphertext)
        return unpad(decrypted_data, AES.block_size)

class AES_CTR:
    def __init__(self, key: bytes, nonce: bytes) -> None:
        """
        Initialize AES CTR mode encryption/decryption object.

        Args:
            key (bytes): The encryption key.
            nonce (bytes): The nonce value.

        Returns:
            None
        """
        self.key = key
        self.nonce = nonce

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypt plaintext using AES CTR mode.

        Args:
            plaintext (bytes): The plaintext to encrypt.

        Returns:
            bytes: The encrypted ciphertext.
        """
        cipher = AES.new(self.key, AES.MODE_CTR, nonce=self.nonce)
        return cipher.encrypt(plaintext)

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt ciphertext using AES CTR mode.

        Args:
            ciphertext (bytes): The ciphertext to decrypt.

        Returns:
            bytes: The decrypted plaintext.
        """
        cipher = AES.new(self.key, AES.MODE_CTR, nonce=self.nonce)
        return cipher.decrypt(ciphertext)

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
        Decrypt ciphertext using the specified method.

        Args:
            ciphertext (bytes): The ciphertext to decrypt.

        Returns:
            bytes: The decrypted plaintext.
        """

        if self.method == "AES":
            aes_ecb = AES_ECB(self.key)
            decrypted_data = aes_ecb.decrypt(ciphertext)

        elif self.method == "AES-128":
            aes_cbc = AES_CBC(self.key[:16], self.iv)
            decrypted_data = aes_cbc.decrypt(ciphertext)

        elif self.method == "AES-128-CTR":
            aes_ctr = AES_CTR(self.key[:16], self.nonce)
            decrypted_data = aes_ctr.decrypt(ciphertext)

        else:
            raise ValueError("Invalid or unsupported method")

        return decrypted_data
    
    def decrypt_openssl(self, encrypted_content: bytes, output_path: str) -> None:
        """
        Decrypts encrypted content using OpenSSL and writes the decrypted content to a file.

        Args:
            encrypted_content (bytes): The content to be decrypted.
            output_path (str): The path to write the decrypted content to.
        """
        
        # Create a temporary file to store the encrypted content
        temp_encrypted_file = str(output_path).replace(".ts", "_.ts")

        # Write the encrypted content to the temporary file
        with open(temp_encrypted_file, 'wb') as f:
            f.write(encrypted_content)

        # Convert key and IV to hexadecimal strings
        key_hex = self.key.hex()
        iv_hex = self.iv.hex()

        # OpenSSL command to decrypt the content
        openssl_cmd = [
            'openssl', 'aes-128-cbc',
            '-d',
            '-in', temp_encrypted_file,
            '-out', output_path,
            '-K', key_hex,
            '-iv', iv_hex
        ]

        # Execute the OpenSSL command
        try:
            subprocess.run(openssl_cmd, check=True)
        except subprocess.CalledProcessError as e:
            logging.error("Decryption failed:", e)

        # Remove the temporary encrypted file
        os.remove(temp_encrypted_file)