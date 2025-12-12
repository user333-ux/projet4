import csv
import os
import time
import hashlib  # Pour le hachage SHA-256
import secrets  # Pour générer un salt aléatoire fort
import hmac     # Pour la comparaison sécurisée (temps constant)
import logging  # Pour les logs d'audit
import re       # Pour la validation du mot de passe (Regex)

# --- CONFIGURATION SÉCURITÉ & LOGS ---
fichier_csv = 'inventaire.csv'
fichier_users = 'utilisateurs.csv'
fichier_log = 'security.log'

# Configuration du logging (Audit)
logging.basicConfig(
    filename=fichier_log,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Variables globales
data = {}
max_id = 0
users_db = {} # Stockage mémoire des utilisateurs: {username: {'salt': x, 'hash': y}}

# --- GESTION DES FICHIERS ---

def charger_users():
    """Charge les utilisateurs depuis le CSV sécurisé."""
    global users_db
    users_db = {}
    
    if not os.path.exists(fichier_users):
        with open(fichier_users, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['username', 'salt', 'hash'], delimiter=";")
            writer.writeheader()
            
    try:
        with open(fichier_users, "r", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                users_db[row['username']] = {
                    'salt': row['salt'],
                    'hash': row['hash']
                }
    except Exception as e:
        print(f"Erreur chargement utilisateurs: {e}")
        logging.error(f"SYSTEM: Erreur chargement users DB - {e}")

def sauver_user(username, salt, hashed_pw):
    """Ajoute un utilisateur au CSV."""
    try:
        with open(fichier_users, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['username', 'salt', 'hash'], delimiter=";")
            # Si le fichier est vide (juste créé), on réécrit l'en-tête
            if os.stat(fichier_users).st_size == 0:
                writer.writeheader()
            writer.writerow({'username': username, 'salt': salt, 'hash': hashed_pw})
    except Exception as e:
        logging.error(f"SYSTEM: Erreur sauvegarde user {username} - {e}")

def charger_fichier():
    """Charge l'inventaire."""
    global data
    global max_id
    data = {}
    
    if not os.path.exists(fichier_csv):
        with open(fichier_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'nom', 'prix', 'quantite'], delimiter=";")
            writer.writeheader()

    try:
        with open(fichier_csv, "r", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                id_prod = int(row["id"])
                row["id"] = id_prod
                row["prix"] = float(row["prix"])
                row["quantite"] = int(row["quantite"])
                
                if id_prod > max_id:
                    max_id = id_prod
                data[id_prod] = row
    except Exception as e:
        print(f"Erreur au chargement inventaire : {e}")

def sauver():
    """Sauvegarde l'inventaire."""
    try:
        with open(fichier_csv, 'w', newline='') as csvfile:
            fieldnames = ['id', 'nom', 'prix', 'quantite']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            for item in data.values():
                writer.writerow(item)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")

def nettoyer_ecran():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- FONCTIONS DE SÉCURITÉ CRYPTOGRAPHIQUE ---

def hacher_mdp(password, salt):
    """
    Combine le mot de passe et le salt, puis retourne le hash SHA-256.
    Structure : SHA256( salt + password )
    """
    payload = salt + password
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def valider_complexite_mdp(password):
    """
    Vérifie les critères et retourne un message précis.
    Critères : 8 chars min, 1 chiffre, 1 majuscule.
    """
    if len(password) < 8:
        return False, "Trop court (minimum 8 caractères)."
    if not re.search(r"\d", password):
        return False, "Doit contenir au moins un chiffre (0-9)."
    if not re.search(r"[A-Z]", password):
        return False, "Doit contenir au moins une lettre majuscule."
    return True, "Valide"

def inscription():
    nettoyer_ecran()
    print("🔐 CRÉATION DE COMPTE")
    print("=====================")
    
    # 1. Gestion du nom d'utilisateur avec boucle
    while True:
        username = input("Choisissez un identifiant : ").strip()
        if not username:
            print("⚠️ L'identifiant ne peut pas être vide.")
            continue
            
        if username in users_db:
            print(f"❌ L'utilisateur '{username}' existe déjà. Choisissez-en un autre.")
        else:
            break # L'identifiant est libre

    print("\n--- Sécurité du mot de passe ---")
    print("Votre mot de passe doit contenir :")
    print("👉 Au moins 8 caractères")
    print("👉 Au moins 1 chiffre")
    print("👉 Au moins 1 majuscule")
    print("--------------------------------")

    # 2. Gestion du mot de passe avec boucle
    while True:
        password = input("Choisissez un mot de passe : ").strip()
        
        # Validation
        is_valid, msg = valider_complexite_mdp(password)
        
        if not is_valid:
            print(f"❌ Mot de passe refusé : {msg}")
            print("Veuillez réessayer.\n")
        else:
            break # Mot de passe valide

    # 3. Création technique
    try:
        # Génération du Salt (32 caractères hexadécimaux uniques)
        salt = secrets.token_hex(16)
        
        # Hachage
        hashed_pw = hacher_mdp(password, salt)
        
        # Stockage Mémoire + CSV
        users_db[username] = {'salt': salt, 'hash': hashed_pw}
        sauver_user(username, salt, hashed_pw)
        
        print(f"\n✅ Compte '{username}' créé avec succès !")
        logging.info(f"INSCRIPTION: Nouvel utilisateur '{username}' créé.")
        
    except Exception as e:
        print(f"\n❌ Erreur technique lors de la création : {e}")
        logging.error(f"INSCRIPTION: Erreur technique - {e}")

    # Pause pour lecture
    input("\nAppuyez sur Entrée pour revenir au menu de connexion...")

def connexion():
    """Gère la tentative de connexion."""
    nettoyer_ecran()
    print("🔑 CONNEXION SÉCURISÉE")
    print("----------------------")
    
    username = input("Identifiant : ").strip()
    password = input("Mot de passe : ").strip()
    
    # Vérification existence user
    if username not in users_db:
        # Simulation temps de calcul (Protection Timing Attack)
        fake_salt = secrets.token_hex(16)
        hacher_mdp("dummy", fake_salt)
        print("❌ Identifiant ou mot de passe incorrect.")
        logging.warning(f"LOGIN: Échec pour '{username}' (Utilisateur inconnu).")
        input("\nAppuyez sur Entrée...")
        return False

    stored_salt = users_db[username]['salt']
    stored_hash = users_db[username]['hash']
    
    # Recalcul du hash avec le salt stocké et le mot de passe fourni
    computed_hash = hacher_mdp(password, stored_salt)
    
    # COMPARAISON CONSTANTE (Protection Timing Attacks)
    if hmac.compare_digest(stored_hash, computed_hash):
        print(f"✅ Bienvenue, {username} !")
        logging.info(f"LOGIN: Succès pour l'utilisateur '{username}'.")
        time.sleep(1)
        return True
    else:
        print("❌ Identifiant ou mot de passe incorrect.")
        logging.warning(f"LOGIN: Échec pour '{username}' (Mauvais mot de passe).")
        input("\nAppuyez sur Entrée...")
        return False

# --- MENU D'AUTHENTIFICATION ---

def menu_auth():
    charger_users()
    while True:
        nettoyer_ecran()
        print("=========================================")
        print("🔒 PORTAIL DE SÉCURITÉ")
        print("=========================================")
        print("1. Se connecter")
        print("2. Créer un compte")
        print("3. Quitter")
        
        choix = input("Votre choix : ").strip()
        
        if choix == '1':
            if connexion():
                return True # Authentification réussie
        elif choix == '2':
            inscription()
        elif choix == '3':
            print("Au revoir.")
            exit()
        else:
            print("Choix invalide.")

# --- FONCTIONS MÉTIER ---

def ajouter_produit():
    global data, max_id
    nettoyer_ecran()
    print("✨ Ajouter un Nouveau Produit")
    try:
        nom = input("Nom du produit : ").strip()
        if not nom: return
        prix = float(input("Prix unitaire : "))
        quantite = int(input("Quantité en stock : "))
        if prix <= 0 or quantite < 0: return
        max_id += 1
        data[max_id] = {"id": max_id, "nom": nom, "prix": prix, "quantite": quantite}
        sauver()
        print(f"\n✅ Produit ajouté.")
        logging.info(f"ACTION: Produit {max_id} ajouté.")
    except ValueError: print("Erreur de saisie.")
    except Exception as e: print(f"Erreur: {e}")
    input("\nEntrée pour continuer...")

def afficher_inventaire():
    nettoyer_ecran()
    print("📚 Inventaire")
    if not data: print("Vide."); input(); return
    print(f"{'ID':<4} | {'Nom':<25} | {'Prix':<8} | {'Stock':<5}")
    print("-" * 55)
    for v in data.values():
        print(f"{v['id']:<4} | {v['nom']:<25} | {v['prix']:>8.2f} | {v['quantite']:>5}")
    logging.info("ACTION: Consultation inventaire.")
    input("\nEntrée pour continuer...")

def modifier_produit():
    global data
    nettoyer_ecran()
    print("✏️ Modifier")
    try:
        pid = int(input("ID produit : "))
        if pid not in data: print("Inconnu."); input(); return
        p = data[pid]
        nn = input(f"Nom ({p['nom']}) : ").strip() or p['nom']
        np_s = input(f"Prix ({p['prix']}) : ").strip()
        nq_s = input(f"Qté ({p['quantite']}) : ").strip()
        np = float(np_s) if np_s else p['prix']
        nq = int(nq_s) if nq_s else p['quantite']
        data[pid].update({'nom': nn, 'prix': np, 'quantite': nq})
        sauver()
        print("✅ Modifié.")
        logging.info(f"ACTION: Produit {pid} modifié.")
    except ValueError: print("Erreur valeur.")
    input("\nEntrée pour continuer...")

def supprimer_produit():
    global data
    nettoyer_ecran()
    print("🗑️ Supprimer")
    try:
        pid = int(input("ID : "))
        if pid not in data: return
        if input("Confirmer (oui/non) ? ") == 'oui':
            del data[pid]
            sauver()
            print("✅ Supprimé.")
            logging.info(f"ACTION: Produit {pid} supprimé.")
    except ValueError: pass
    input("\nEntrée pour continuer...")

def menu_app():
    while True:
        nettoyer_ecran()
        print("=========================================")
        print("🚀 GESTION STOCK (Connecté)")
        print("=========================================")
        print("1. Ajouter")
        print("2. Voir")
        print("3. Modifier")
        print("4. Supprimer")
        print("5. Déconnexion")
        
        c = input("Choix : ")
        if c == '1': ajouter_produit()
        elif c == '2': afficher_inventaire()
        elif c == '3': modifier_produit()
        elif c == '4': supprimer_produit()
        elif c == '5': 
            logging.info("LOGOUT: Déconnexion utilisateur.")
            return # Retour au menu auth
        
# --- POINT D'ENTRÉE ---

def main():
    charger_fichier() # Charge le stock
    
    while True:
        # 1. On force l'authentification
        if menu_auth():
            # 2. Si succès, on lance l'application métier
            menu_app()

if __name__ == "__main__":
    main()