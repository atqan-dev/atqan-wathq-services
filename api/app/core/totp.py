"""
TOTP (Time-based One-Time Password) service implementing RFC 6238.

Security Best Practices:
- Secrets are encrypted at rest using Fernet (AES-128-CBC)
- Rate limiting on verification attempts
- Backup codes with secure hashing
- Time window tolerance for clock drift
- Secure secret generation using cryptographic RNG
"""

import base64
import hashlib
import secrets
from io import BytesIO
from typing import Optional

import pyotp
import qrcode
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings


class TOTPService:
    """
    TOTP service for two-factor authentication.

    Implements RFC 6238 with security best practices:
    - 30-second time step (standard)
    - 6-digit codes (standard)
    - SHA-1 algorithm (standard, widely compatible)
    - ±1 time step tolerance for clock drift
    """

    # TOTP Configuration
    DIGITS = 6
    INTERVAL = 30  # seconds
    ALGORITHM = "SHA1"
    VALID_WINDOW = 1  # Allow ±1 time step for clock drift

    # Backup codes configuration
    BACKUP_CODE_LENGTH = 8
    BACKUP_CODE_COUNT = 10

    # Rate limiting
    MAX_VERIFICATION_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15

    def __init__(self):
        """Initialize TOTP service with encryption key."""
        self._fernet = self._get_fernet()

    def _get_fernet(self) -> Fernet:
        """
        Derive a Fernet encryption key from the application secret.
        Uses PBKDF2 for key derivation.
        """
        # Use a fixed salt derived from the secret key for consistency
        salt = hashlib.sha256(settings.SECRET_KEY.encode()).digest()[:16]

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
        return Fernet(key)

    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret.

        Returns:
            Base32-encoded secret (unencrypted, for immediate use)
        """
        return pyotp.random_base32(length=32)

    def encrypt_secret(self, secret: str) -> str:
        """
        Encrypt a TOTP secret for storage.

        Args:
            secret: Base32-encoded TOTP secret

        Returns:
            Encrypted secret (base64-encoded)
        """
        return self._fernet.encrypt(secret.encode()).decode()

    def decrypt_secret(self, encrypted_secret: str) -> str:
        """
        Decrypt a stored TOTP secret.

        Args:
            encrypted_secret: Encrypted secret from database

        Returns:
            Base32-encoded TOTP secret
        """
        return self._fernet.decrypt(encrypted_secret.encode()).decode()

    def get_totp(self, secret: str) -> pyotp.TOTP:
        """
        Create a TOTP instance from a secret.

        Args:
            secret: Base32-encoded TOTP secret

        Returns:
            pyotp.TOTP instance
        """
        return pyotp.TOTP(
            secret,
            digits=self.DIGITS,
            interval=self.INTERVAL,
        )

    def verify_code(self, secret: str, code: str, valid_window: int = None) -> bool:
        """
        Verify a TOTP code.

        Args:
            secret: Base32-encoded TOTP secret
            code: 6-digit code to verify
            valid_window: Number of time steps to check (default: VALID_WINDOW)

        Returns:
            True if code is valid, False otherwise
        """
        if valid_window is None:
            valid_window = self.VALID_WINDOW

        totp = self.get_totp(secret)
        return totp.verify(code, valid_window=valid_window)

    def get_current_code(self, secret: str) -> str:
        """
        Get the current TOTP code (for testing purposes).

        Args:
            secret: Base32-encoded TOTP secret

        Returns:
            Current 6-digit code
        """
        totp = self.get_totp(secret)
        return totp.now()

    def get_provisioning_uri(self, secret: str, email: str, issuer: str = None) -> str:
        """
        Generate a provisioning URI for authenticator apps.

        Args:
            secret: Base32-encoded TOTP secret
            email: User's email address
            issuer: Application name (default: from settings)

        Returns:
            otpauth:// URI for QR code generation
        """
        if issuer is None:
            issuer = getattr(settings, "APP_NAME", "Atqan Wathq")

        totp = self.get_totp(secret)
        return totp.provisioning_uri(name=email, issuer_name=issuer)

    def generate_qr_code(self, secret: str, email: str, issuer: str = None) -> bytes:
        """
        Generate a QR code image for authenticator app setup.

        Args:
            secret: Base32-encoded TOTP secret
            email: User's email address
            issuer: Application name

        Returns:
            PNG image bytes
        """
        uri = self.get_provisioning_uri(secret, email, issuer)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer.getvalue()

    def generate_qr_code_base64(
        self, secret: str, email: str, issuer: str = None
    ) -> str:
        """
        Generate a base64-encoded QR code for embedding in responses.

        Args:
            secret: Base32-encoded TOTP secret
            email: User's email address
            issuer: Application name

        Returns:
            Base64-encoded PNG image with data URI prefix
        """
        qr_bytes = self.generate_qr_code(secret, email, issuer)
        b64 = base64.b64encode(qr_bytes).decode()
        return f"data:image/png;base64,{b64}"

    def generate_backup_codes(self) -> list[str]:
        """
        Generate a set of backup codes for account recovery.

        Returns:
            List of backup codes (plaintext, for display to user)
        """
        codes = []
        for _ in range(self.BACKUP_CODE_COUNT):
            # Generate a random code with alphanumeric characters
            code = secrets.token_hex(self.BACKUP_CODE_LENGTH // 2).upper()
            # Format as XXXX-XXXX for readability
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        return codes

    def hash_backup_code(self, code: str) -> str:
        """
        Hash a backup code for secure storage.

        Args:
            code: Backup code (with or without dash)

        Returns:
            SHA-256 hash of the normalized code
        """
        # Normalize: remove dashes and convert to uppercase
        normalized = code.replace("-", "").upper()
        return hashlib.sha256(normalized.encode()).hexdigest()

    def verify_backup_code(
        self, code: str, hashed_codes: list[str]
    ) -> tuple[bool, Optional[str]]:
        """
        Verify a backup code against stored hashes.

        Args:
            code: Backup code to verify
            hashed_codes: List of hashed backup codes

        Returns:
            Tuple of (is_valid, matched_hash) - matched_hash is for removal
        """
        code_hash = self.hash_backup_code(code)
        if code_hash in hashed_codes:
            return True, code_hash
        return False, None


# Global instance
totp_service = TOTPService()
