import random
import string


def generate_auth_code(length: int) -> str:
    return ''.join(random.choices
                   (string.ascii_uppercase + string.digits, k=length))
