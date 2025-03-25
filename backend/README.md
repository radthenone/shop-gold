GENERACJA
uv pip compile pyproject.toml -o requirements.txt
uv pip compile pyproject.toml --extra dev --extra lint -o requirements-dev.txt

GET /api/v1/users/ - lista użytkowników (tylko zalogowany użytkownik)
POST /api/v1/users/setup_mfa/ - inicjacja MFA
POST /api/v1/users/confirm_mfa/ - potwierdzenie MFA
POST /api/v1/users/disable_mfa/ - wyłączenie MFA
GET /api/v1/users/profile/ - pobranie profilu
PUT/PATCH /api/v1/users/update_profile/ - aktualizacja profilu

Autentykacja (dj-rest-auth):
POST /api/v1/auth/login/ - logowanie
POST /api/v1/auth/logout/ - wylogowanie
POST /api/v1/auth/password/reset/ - reset hasła
POST /api/v1/auth/password/reset/confirm/ - potwierdzenie resetu hasła
POST /api/v1/auth/password/change/ - zmiana hasła

Rejestracja:
POST /api/v1/auth/registration/ - rejestracja nowego użytkownika
POST /api/v1/auth/registration/verify-email/ - weryfikacja email
POST /api/v1/auth/registration/resend-email/ - ponowne wysłanie emaila weryfikacyjnego