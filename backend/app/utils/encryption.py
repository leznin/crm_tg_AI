"""Encryption utilities for sensitive data."""
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.core.config import settings


class EncryptionManager:
    """Manages encryption and decryption of sensitive data."""
    
    def __init__(self):
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize Fernet encryption with key from settings."""
        # Generate key from SECRET_KEY
        password = settings.SECRET_KEY.encode()
        salt = b'telegram_crm_salt'  # In production, use a random salt per installation
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self._fernet = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string and return base64 encoded result."""
        if not data:
            return ""
        
        encrypted_data = self._fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded encrypted data."""
        if not encrypted_data:
            return ""
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception:
            # Return empty string if decryption fails
            return ""
    
    def is_encrypted(self, data: str) -> bool:
        """Check if data appears to be encrypted (base64 format)."""
        if not data:
            return False
        
        try:
            # Try to decode as base64
            base64.urlsafe_b64decode(data.encode())
            return True
        except Exception:
            return False


# Global encryption manager instance
encryption_manager = EncryptionManager()


def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data like API keys."""
    return encryption_manager.encrypt(data)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data like API keys."""
    return encryption_manager.decrypt(encrypted_data)


def mask_api_key(api_key: str) -> str:
    """Mask API key for display purposes."""
    if not api_key or len(api_key) < 8:
        return "*" * 8
    
    return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
