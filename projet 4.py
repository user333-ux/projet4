import sqlite3
import os

# --- Configuration de la Base de Données ---
DB_NAME = 'inventaire.db'

def connecter_db():
    """Établit la connexion à la DB et crée la table 'produits' si elle n'existe pas."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prix REAL NOT NULL,
            quantite INTEGER NOT NULL
        )
    ''')
    conn.commit()
    return conn

def nettoyer_ecran():
    """Nettoie la console pour une meilleure lisibilité du menu."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- 1. Opération CREATE (Ajouter) ---

def ajouter_produit(conn):
    nettoyer_ecran()
    print("✨ Ajouter un Nouveau Produit")
    
    try:
        nom = input("Nom du produit : ").strip()
        if not nom:
            print("🛑 Le nom ne peut pas être vide.")
            return

        prix = float(input("Prix unitaire (ex: 19.99) : "))
        quantite = int(input("Quantité en stock : "))
        
        if prix <= 0 or quantite < 0:
             print("🛑 Le prix doit être positif et la quantité non négative.")
             return
        
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO produits (nom, prix, quantite) VALUES (?, ?, ?)", 
            (nom, prix, quantite)
        )
        conn.commit()
        print(f"\n✅ Produit '{nom}' ajouté avec succès (ID: {cursor.lastrowid}).")
        
    except ValueError:
        print("\n🛑 Erreur de saisie : Veuillez entrer un nombre valide pour le prix et la quantité.")
    except Exception as e:
        print(f"\n❌ Une erreur inattendue est survenue: {e}")
    finally:
        input("\nAppuyez sur Entrée pour revenir au menu principal...")


# --- 2. Opération READ (Afficher) ---

def afficher_inventaire(conn):
    nettoyer_ecran()
    print("📚 Inventaire Complet des Produits")

    cursor = conn.cursor()
    cursor.execute("SELECT id, nom, prix, quantite FROM produits ORDER BY id")
    produits = cursor.fetchall()
    
    if not produits:
        print("\n⚠️ L'inventaire est actuellement vide.")
        input("\nAppuyez sur Entrée pour revenir au menu principal...")
        return
        
    # Affichage formaté en tableau
    print("-" * 50)
    print(f"{'ID':<4} | {'Nom':<25} | {'Prix':<8} | {'Stock':<5}")
    print("-" * 50)
    for id, nom, prix, quantite in produits:
        print(f"{id:<4} | {nom:<25} | {prix:>8.2f} | {quantite:>5}")
    print("-" * 50)
    print(f"Total de {len(produits)} produits différents en stock.")
    
    input("\nAppuyez sur Entrée pour revenir au menu principal...")

# --- 3. Opération UPDATE (Modifier) ---

def modifier_produit(conn):
    nettoyer_ecran()
    print("✏️ Modifier un Produit Existant")
    
    try:
        produit_id = int(input("Entrez l'ID du produit à modifier : "))
    except ValueError:
        print("🛑 L'ID doit être un nombre entier.")
        input("\nAppuyez sur Entrée pour revenir au menu principal...")
        return
    
    cursor = conn.cursor()
    cursor.execute("SELECT nom, prix, quantite FROM produits WHERE id = ?", (produit_id,))
    produit = cursor.fetchone()
    
    if not produit:
        print(f"\n⚠️ Aucun produit trouvé avec l'ID {produit_id}.")
        input("\nAppuyez sur Entrée pour revenir au menu principal...")
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
             input("\nAppuyez sur Entrée pour revenir au menu principal...")
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
        
    input("\nAppuyez sur Entrée pour revenir au menu principal...")

# --- 4. Opération DELETE (Supprimer) ---

def supprimer_produit(conn):
    nettoyer_ecran()
    print("🗑️ Supprimer un Produit")

    try:
        produit_id = int(input("Entrez l'ID du produit à supprimer : "))
    except ValueError:
        print("🛑 L'ID doit être un nombre entier.")
        input("\nAppuyez sur Entrée pour revenir au menu principal...")
        return
        
    cursor = conn.cursor()
    cursor.execute("SELECT nom FROM produits WHERE id = ?", (produit_id,))
    produit = cursor.fetchone()

    if not produit:
        print(f"\n⚠️ Aucun produit trouvé avec l'ID {produit_id}.")
        input("\nAppuyez sur Entrée pour revenir au menu principal...")
        return
    
    nom_produit = produit[0]
    confirmation = input(f"Confirmez-vous la suppression de '{nom_produit}' (ID: {produit_id})? (oui/non) : ").lower()

    if confirmation == 'oui':
        cursor.execute("DELETE FROM produits WHERE id = ?", (produit_id,))
        conn.commit()
        print(f"\n✅ Produit '{nom_produit}' (ID: {produit_id}) a été supprimé.")
    else:
        print("\nℹ️ Suppression annulée.")
        
    input("\nAppuyez sur Entrée pour revenir au menu principal...")


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
    conn = connecter_db()
    
    while True:
        choix = afficher_menu()
        
        if choix == '1' or choix.lower() == 'c':
            ajouter_produit(conn)
        elif choix == '2' or choix.lower() == 'r':
            afficher_inventaire(conn)
        elif choix == '3' or choix.lower() == 'u':
            modifier_produit(conn)
        elif choix == '4' or choix.lower() == 'd':
            supprimer_produit(conn)
        elif choix == '5' or choix.lower() == 'q':
            nettoyer_ecran()
            print("👋 Fermeture du programme. Merci d'avoir utilisé l'outil d'inventaire.")
            conn.close()
            break
        else:
            print("\n❌ Choix invalide. Veuillez entrer un numéro (1-5) ou la lettre correspondante.")
            input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    main()