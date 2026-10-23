
from app.security import hash_password, verify_password


def test_password_is_hashed():
    password = "LearningFastAPI123!"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)


def test_wrong_password_is_rejected():
    hashed = hash_password("CorrectPassword123!")

    assert not verify_password("WrongPassword123!", hashed)


def test_same_password_produces_different_hashes():
    password = "LearningFastAPI123!"

    hash_one = hash_password(password)
    hash_two = hash_password(password)

    # Argon2 uses a random salt, so hashes should differ.
    assert hash_one != hash_two

    # Both hashes should still verify the original password.
    assert verify_password(password, hash_one)
    assert verify_password(password, hash_two)
