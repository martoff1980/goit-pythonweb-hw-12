from datetime import timedelta
from services.auth import create_access_token


def generate_test_token(email: str):
    return create_access_token(subject=email,role="user", expires_delta=timedelta(minutes=30))
