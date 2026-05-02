from pwdlib import PasswordHash

password_hash = PasswordHash.recommended() 

blacklisted_tokens = set()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)