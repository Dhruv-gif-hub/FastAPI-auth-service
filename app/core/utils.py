from pwdlib import PasswordHash
# Initialize the password hasher with recommended settings
password_hash = PasswordHash.recommended() 

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

# Function to hash a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)