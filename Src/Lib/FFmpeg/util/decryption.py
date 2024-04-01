# 29.04.24

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import cmac
from cryptography.hazmat.primitives.asymmetric import rsa as RSA

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

    def _check_iv_size(self, expected_size: int) -> None:
        """
        Check the size of the initialization vector (IV).

        Args:
            - expected_size (int): The expected size of the IV.
        """

        if self.iv is not None and len(self.iv) != expected_size:
            raise ValueError(f"Invalid IV size ({len(self.iv)}) for {self.method}. Expected size: {expected_size}")

    def generate_cmac(self, data: bytes) -> bytes:
        """
        Generate CMAC (Cipher-based Message Authentication Code).

        Args:
            - data (bytes): The data to generate CMAC for.

        Returns:
            - bytes: The CMAC digest.
        """

        if self.method == "AES-CMAC":
            cipher = Cipher(algorithms.AES(self.key), modes.ECB(), backend=default_backend())
            encryptor = cipher.encryptor()
            cmac_obj = cmac.CMAC(encryptor)
            cmac_obj.update(data)
            return cmac_obj.finalize()
        else:
            raise ValueError("Invalid method")

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt the ciphertext using the specified encryption method.

        Args:
            - ciphertext (bytes): The ciphertext to decrypt.

        Returns:
            - bytes: The decrypted data.
        """

        if self.method == "AES":
            self._check_iv_size(16)
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=default_backend())

        elif self.method == "AES-128":
            self._check_iv_size(16)
            cipher = Cipher(algorithms.AES(self.key[:16]), modes.CBC(self.iv), backend=default_backend())

        elif self.method == "AES-128-CTR":
            self._check_iv_size(16)
            cipher = Cipher(algorithms.AES(self.key[:16]), modes.CTR(self.iv), backend=default_backend())

        elif self.method == "Blowfish":
            self._check_iv_size(8)
            cipher = Cipher(algorithms.Blowfish(self.key), modes.CBC(self.iv), backend=default_backend())

        elif self.method == "RSA":
            private_key = RSA.import_key(self.key)
            cipher = Cipher(algorithms.RSA(private_key), backend=default_backend())

        else:
            raise ValueError("Invalid or unsupported method")

        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        return decrypted_data