import base64
import hashlib
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.models import IdentityRecord


def normalize_national_id(national_id: str) -> str:
    return "".join(ch for ch in national_id if ch.isdigit())


def hash_national_id(national_id: str) -> str:
    normalized = normalize_national_id(national_id)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def encrypt_national_id(national_id: str, key_text: str) -> str:
    key = key_text.encode("utf-8")[:32].ljust(32, b"0")
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, national_id.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def build_mpid(national_id_hash: str) -> str:
    return f"MPID-{national_id_hash[:20]}"


def identity_exists(national_id_hash: str) -> bool:
    return IdentityRecord.query.filter_by(national_id_hash=national_id_hash).first() is not None
