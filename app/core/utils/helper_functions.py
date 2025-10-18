import argon2

_password_hasher = argon2.PasswordHasher()


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_hash(hash: str, password: str) -> bool:
    try:
        return _password_hasher.verify(hash=hash, password=password)
    except argon2.exceptions.VerifyMismatchError:
        return False


def hash_needs_rehashing(hash: str) -> bool:
    return _password_hasher.check_needs_rehash(hash)


__all__ = ["hash_password", "verify_hash", "hash_needs_rehashing"]
