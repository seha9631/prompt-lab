"""
API 키 암호화/복호화 유틸리티
team_id를 키로 사용하여 API 키를 안전하게 저장하고 복원합니다.
"""

import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """API 키 암호화/복호화 서비스"""

    @staticmethod
    def _generate_key_from_team_id(team_id: str) -> bytes:
        """team_id로부터 암호화 키를 생성합니다."""
        # team_id를 바이트로 변환하고 SHA-256 해시 생성
        team_id_bytes = team_id.encode("utf-8")
        hash_object = hashlib.sha256(team_id_bytes)
        hash_bytes = hash_object.digest()

        # PBKDF2를 사용하여 키 생성
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=hash_bytes[:16],  # 해시의 처음 16바이트를 salt로 사용
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(hash_bytes))
        return key

    @staticmethod
    def encrypt_api_key(api_key: str, team_id: str) -> str:
        """
        API 키를 암호화합니다.

        Args:
            api_key: 암호화할 API 키
            team_id: 팀 ID (암호화 키 생성에 사용)

        Returns:
            암호화된 API 키 (base64 인코딩된 문자열)
        """
        try:
            key = EncryptionService._generate_key_from_team_id(team_id)
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(api_key.encode("utf-8"))
            return base64.urlsafe_b64encode(encrypted_data).decode("utf-8")
        except Exception as e:
            logger.error(f"API 키 암호화 실패: {e}")
            raise ValueError("API 키 암호화에 실패했습니다.")

    @staticmethod
    def decrypt_api_key(encrypted_api_key: str, team_id: str) -> str:
        """
        암호화된 API 키를 복호화합니다.

        Args:
            encrypted_api_key: 암호화된 API 키 (base64 인코딩된 문자열)
            team_id: 팀 ID (복호화 키 생성에 사용)

        Returns:
            복호화된 API 키
        """
        try:
            key = EncryptionService._generate_key_from_team_id(team_id)
            fernet = Fernet(key)

            # base64 디코딩
            encrypted_bytes = base64.urlsafe_b64decode(
                encrypted_api_key.encode("utf-8")
            )

            # 복호화
            decrypted_data = fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode("utf-8")
        except Exception as e:
            logger.error(f"API 키 복호화 실패: {e}")
            raise ValueError("API 키 복호화에 실패했습니다.")
