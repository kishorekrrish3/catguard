from app.core.security import get_password_hash, verify_password, create_access_token, decode_token

def test_password_hashing():
    password = "SecurePass@123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPass", hashed)

def test_create_and_decode_token():
    data = {"sub": "test-user-id", "role": "forest_manager"}
    token = create_access_token(data)
    payload = decode_token(token)
    assert payload["sub"] == "test-user-id"
    assert payload["type"] == "access"