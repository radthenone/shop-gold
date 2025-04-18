from typing import TypeVar

from allauth.mfa.models import Authenticator
from allauth.utils import import_attribute
from django.conf import settings
from django.http import HttpRequest

from core.adapters.account import AccountAdapter
from core.adapters.mfa import MFAAdapter

T = TypeVar("T", AccountAdapter, MFAAdapter)


def get_adapter(
    is_mfa: bool = False,
) -> AccountAdapter | MFAAdapter:
    """
    Universal adapter getter that automatically selects between MFA and Account adapters
    based on whether the user has MFA enabled
    """
    if is_mfa:
        adapter_path = settings.MFA_ADAPTER
    else:
        adapter_path = settings.ACCOUNT_ADAPTER

    adapter_class = import_attribute(adapter_path)
    return adapter_class()


__all__ = [
    "AccountAdapter",
    "MFAAdapter",
    "get_adapter",
]
