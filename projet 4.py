import csv
import os
import time
from auth import create_user, check_login

# --- Constantes ---
PAUSE_MESSAGE = "Appuyez sur Entrée pour continuer..."

# --- Configuration fichier csv ---
fichier_csv = 'inventaire.csv'
data = {}
max_id = 0


def charger_fichier():
    global data
    global max_id
    global fichier_csv
    data = {}
    """Établit la connexion à la DB et crée la table 'produits' si elle n'existe pas."""
    try:
        with open(fichier_csv, "r", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                print(row)
                id = int(row["id"])
                if id > max_id:
                    max_id = id
                data[id] = row
            print(f"fichier load {len(data)}")
    except Exception as e:
        print(f"error {e}")
    time.sleep(2)


def sauver():
    global data
    global fichier_csv

    with open(fichier_csv, 'w', newline='') as csvfile:
        fieldnames = ['id', 'nom', 'prix', 'quantite']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")

        writer.writeheader()
        for item in data.values():
            writer.writerow(item)


def nettoyer_ecran():
    """Nettoie la console pour une meilleure lisibilité du menu."""
    os.system('cls' if os.name == 'nt' else 'clear')


# --- 1. Opération CREATE (Ajouter) ---

def ajouter_produit():
    global data
    global max_id
    nettoyer_ecran()
    print("✨ Ajouter un Nouveau Produit")

    try:
        nom = input("Nom du produit : ").strip()
        if not nom:
            print("🛑 Le nom ne peut pas être vide.")
            input(f"\n{PAUSE_MESSAGE}")
            return

        prix = float(input("Prix unitaire (ex: 19.99) : "))
        quantite = int(input("Quantité en stock : "))

        if prix <= 0 or quantite < 0:
            print("🛑 Le prix doit être positif et la quantité non négative.")
            input(f"\n{PAUSE_MESSAGE}")
            return

        max_id = max_id + 1
        row = {"id": max_id, "nom": nom, "prix": prix, "quantite": quantite}
        data[max_id] = row
        print(f"\n✅ Produit {row} ajouté avec succès (ID: {max_id}).")
        sauver()
    except ValueError as e:
        print(f"\n🛑 Erreur de saisie : Veuillez entrer un nombre valide pour le prix et la quantité. {e}")
    except Exception as e:
        print(f"\n❌ Une erreur inattendue est survenue: {e}")
    finally:
        input("\nAppuyez sur Entrée pour revenir au menu principal...")


# --- 2. Opération READ (Afficher) ---

def afficher_inventaire():
    nettoyer_ecran()
    print("📚 Inventaire Complet des Produits")

    global data

    if not data:
        print("\n⚠️ L'inventaire est actuellement vide.")
        input(f"\n{PAUSE_MESSAGE}")
        return

    # Affichage formaté en tableau
    print("-" * 50)
    print(f"{'ID':<4} | {'Nom':<25} | {'Prix':<8} | {'Stock':<5}")
    print("-" * 50)
    for item in data.values():
        id = item["id"]
        nom = item["nom"]
        prix = float(item["prix"])
        quantite = item["quantite"]
        print(f"{id:<4} | {nom:<25} | {prix:>8.2f} | {quantite:>5}")
    print("-" * 50)
    print(f"Total de {len(data)} produits différents en stock.")

    input(f"\n{PAUSE_MESSAGE}")


# --- 3. Opération UPDATE (Modifier) ---
# À adapter plus tard pour le CSV, actuellement basé sur une DB

def modifier_produit(conn):
    nettoyer_ecran()
    print("✏️ Modifier un Produit Existant")

    try:
        produit_id = int(input("Entrez l'ID du produit à modifier : "))
    except ValueError:
        print("🛑 L'ID doit être un nombre entier.")
        input(f"\n{PAUSE_MESSAGE}")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT nom, prix, quantite FROM produits WHERE id = ?", (produit_id,))
    produit = cursor.fetchone()

    if not produit:
        print(f"\n⚠️ Aucun produit trouvé avec l'ID {produit_id}.")
        input(f"\n{PAUSE_MESSAGE}")
        return

    nom_actuel, prix_actuel, quantite_actuelle = produit
    print(f"\n--- Modification de : {nom_actuel} (ID: {produit_id}) ---")
    print(f"Nom actuel: {nom_actuel}")
    nouveau_nom = input(f"Nouveau nom (Laissez vide pour garder '{nom_actuel}') : ").strip() or nom_actuel

    print(f"Prix actuel: {prix_actuel}")
    nouveau_prix_str = input(f"Nouveau prix (Laissez vide pour garder '{prix_actuel}') : ").strip()

    print(f"Quantité actuelle: {quantite_actuelle}")
    nouvelle_quantite_str = input(f"Nouvelle quantité (Laissez vide pour garder '{quantite_actuelle}') : ").strip()

    try:
        nouveau_prix = float(nouveau_prix_str) if nouveau_prix_str else prix_actuel
        nouvelle_quantite = int(nouvelle_quantite_str) if nouvelle_quantite_str else quantite_actuelle

        if nouveau_prix <= 0 or nouvelle_quantite < 0:
            print("🛑 Modification annulée. Le prix doit être positif et la quantité non négative.")
            input(f"\n{PAUSE_MESSAGE}")
            return

        cursor.execute(
            "UPDATE produits SET nom = ?, prix = ?, quantite = ? WHERE id = ?",
            (nouveau_nom, nouveau_prix, nouvelle_quantite, produit_id)
        )
        conn.commit()
        if cursor.rowcount > 0:
            print(f"\n✅ Produit ID {produit_id} mis à jour avec succès.")
        else:
            print("\n⚠️ Aucune modification effectuée.")

    except ValueError:
        print("\n🛑 Erreur de saisie : Veuillez entrer un nombre valide.")

    input(f"\n{PAUSE_MESSAGE}")


# --- 4. Opération DELETE (Supprimer) ---
# À adapter plus tard pour le CSV, actuellement basé sur une DB

def supprimer_produit(conn):
    nettoyer_ecran()
    print("🗑️ Supprimer un Produit")

    try:
        produit_id = int(input("Entrez l'ID du produit à supprimer : "))
    except ValueError:
        print("🛑 L'ID doit être un nombre entier.")
        input(f"\n{PAUSE_MESSAGE}")
        return

    cursor = conn.cursor()
    cursor.execute("SELECT nom FROM produits WHERE id = ?", (produit_id,))
    produit = cursor.fetchone()

    if not produit:
        print(f"\n⚠️ Aucun produit trouvé avec l'ID {produit_id}.")
        input(f"\n{PAUSE_MESSAGE}")
        return

    nom_produit = produit[0]
    confirmation = input(f"Confirmez-vous la suppression de '{nom_produit}' (ID: {produit_id})? (oui/non) : ").lower()

    if confirmation == 'oui':
        cursor.execute("DELETE FROM produits WHERE id = ?", (produit_id,))
        conn.commit()
        print(f"\n✅ Produit '{nom_produit}' (ID: {produit_id}) a été supprimé.")
    else:
        print("\nℹ️ Suppression annulée.")

    input(f"\n{PAUSE_MESSAGE}")


# --- Boucle Principale du Menu ---

def afficher_menu():
    """Affiche le menu et demande le choix de l'utilisateur."""
    nettoyer_ecran()
    print("=========================================")
    print("🚀 SYSTÈME DE GESTION D'INVENTAIRE (CLI) 🚀")
    print("=========================================")
    print("1. [C] Créer / Ajouter un nouveau produit")
    print("2. [R] Lire / Afficher l'inventaire complet")
    print("3. [U] Mettre à jour / Modifier un produit")
    print("4. [D] Supprimer un produit")
    print("-----------------------------------------")
    print("5. Quitter le programme")
    print("=========================================")

    return input("Entrez votre choix (1-5) : ").strip()


def main():
    # ---------- Authentification ----------
    while True:
        nettoyer_ecran()
        print("=========================================")
        print("🔐 AUTHENTIFICATION REQUISE")
        print("=========================================")
        print("1. Se connecter")
        print("2. Créer un compte")
        print("3. Quitter")
        print("=========================================")
        choix = input("Votre choix (1-3) : ").strip()

        if choix == "1":
            username = input("Nom d'utilisateur : ").strip()
            password = input("Mot de passe : ").strip()
            if check_login(username, password):
                print("\n✅ Connexion réussie. Bienvenue", username)
                time.sleep(1.5)
                break
            else:
                print("\n🛑 Identifiants incorrects.")
                input(PAUSE_MESSAGE)
        elif choix == "2":
            username = input("Choisissez un nom d'utilisateur : ").strip()
            password = input("Choisissez un mot de passe : ").strip()
            if create_user(username, password):
                print("\n✅ Compte créé avec succès, vous pouvez vous connecter.")
            else:
                print("\n⚠️ Ce nom d'utilisateur existe déjà.")
            input(PAUSE_MESSAGE)
        elif choix == "3":
            return
        else:
            print("\n❌ Choix invalide.")
            input(PAUSE_MESSAGE)

    # ---------- Partie inventaire ----------
    charger_fichier()

    while True:
        choix = afficher_menu()

        if choix == '1' or choix.lower() == 'c':
            ajouter_produit()
        elif choix == '2' or choix.lower() == 'r':
            afficher_inventaire()
        elif choix == '3' or choix.lower() == 'u':
            print("⚠️ Fonction modifier_produit à adapter pour le CSV.")
            input(PAUSE_MESSAGE)
        elif choix == '4' or choix.lower() == 'd':
            print("⚠️ Fonction supprimer_produit à adapter pour le CSV.")
            input(PAUSE_MESSAGE)
        elif choix == '5' or choix.lower() == 'q':
            nettoyer_ecran()
            print("👋 Fermeture du programme. Merci d'avoir utilisé l'outil d'inventaire.")
            break
        else:
            print("\n❌ Choix invalide. Veuillez entrer un numéro (1-5) ou la lettre correspondante.")
            input(PAUSE_MESSAGE)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
