import csv
import os
import hashlib

USERS_FILE = "users.csv"


def _ensure_users_file_exists():
    """Crée le fichier users.csv avec l'en-tête s'il n'existe pas."""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["username", "password"],
                delimiter=";"
            )
            writer.writeheader()


def hash_password(password: str) -> str:
    """Retourne 'salt:hash' où hash = SHA-256(salt + password)."""
    salt = os.urandom(16).hex()  # sel aléatoire 16 octets -> 32 caractères hex
    h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}:{h}"


def verify_password(stored: str, password: str) -> bool:
    """Vérifie qu'un mot de passe correspond au 'salt:hash' stocké."""
    try:
        salt, h_stored = stored.split(":", 1)
    except ValueError:
        return False
    h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return h == h_stored


def create_user(username: str, password: str) -> bool:
    """
    Crée un utilisateur.
    Retourne False si le username existe déjà, True sinon.
    """
    _ensure_users_file_exists()
    users = {}

    # Charger les utilisateurs existants
    with open(USERS_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            users[row["username"]] = row["password"]

    # Vérifier unicité du username
    if username in users:
        return False

    # Hasher + saler le mot de passe
    stored = hash_password(password)

    # Ajouter l'utilisateur
    with open(USERS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["username", "password"],
            delimiter=";"
        )
        writer.writerow({"username": username, "password": stored})

    return True


def check_login(username: str, password: str) -> bool:
    """Retourne True si le couple login / mot de passe est valide."""
    _ensure_users_file_exists()

    with open(USERS_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            if row["username"] == username:
                return verify_password(row["password"], password)
    return False
