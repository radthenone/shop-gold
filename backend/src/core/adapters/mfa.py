import logging

import pyotp
from allauth.mfa.adapter import DefaultMFAAdapter

logger = logging.getLogger(__name__)


class MFAAdapter(DefaultMFAAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def verify_totp(secret: str, code: str) -> bool:
        totp = pyotp.TOTP(secret)
        logger.info(f"Expected: {totp.now()}, Received: {code}")
        return totp.verify(code, valid_window=1)
