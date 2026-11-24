USERS = {
    "ash": "pikachu",
    "misty": "staryu"
}


def authenticate(username: str, password: str) -> bool:
    return USERS.get(username) == password