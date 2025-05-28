import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class UpperCaseValidator:
    """
    Validates that the password contains at least one uppercase letter.
    """

    def validate(self, password, user=None):
        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                _("This password must contain at least one uppercase letter."),
                code="password_no_upper",
            )

    def get_help_text(self):
        return _("Your password must contain at least one uppercase letter.")


class LowerCaseValidator:
    """
    Validates that the password contains at least one lowercase letter.
    """

    def validate(self, password, user=None):
        if not re.search(r"[a-z]", password):
            raise ValidationError(
                _("This password must contain at least one lowercase letter."),
                code="password_no_lower",
            )

    def get_help_text(self):
        return _("Your password must contain at least one lowercase letter.")


class DigitValidator:
    """
    Validates that the password contains at least one digit.
    """

    def validate(self, password, user=None):
        if not re.search(r"\d", password):
            raise ValidationError(
                _("This password must contain at least one digit."),
                code="password_no_digit",
            )

    def get_help_text(self):
        return _("Your password must contain at least one digit.")


class SpecialCharValidator:
    """
    Validates that the password contains at
    least one special character from the defined set.
    """

    SPECIAL_CHAR_REGEX = r"[@$!%*?&]"

    def validate(self, password, user=None):
        if not re.search(self.SPECIAL_CHAR_REGEX, password):
            raise ValidationError(
                _(
                    "This password must contain at least one special "
                    "character (e.g., @, $, !, %, *, ?, &)."
                ),
                code="password_no_special_char",
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one "
            "special character from the set: @$!%*?&"
        )
