import hashlib


def check_new_password(pass_str):
    """Check if a password is strong."""
    if len(pass_str) < 8:
        return False
    if not any(char.isdigit() for char in pass_str):
        return False
    if not any(char.isupper() for char in pass_str):
        return False
    if not any(char.islower() for char in pass_str):
        return False
    if not any(char in "!@#$%^&*()-_+=~`[]{}|;:,.<>?/" for char in pass_str):
        return False
    return True


def hash_password(pass_str):
    """Hash a password string."""
    return hashlib.sha256(pass_str.encode()).hexdigest()


def check_password(pass_str, pass_hash):
    """Check if a password matches its hash."""
    return hash_password(pass_str) == pass_hash
