"""
Exemple spécifique pour l'import JSON des matières premières
"""
from repositories import MatieresPremieresRepository, create_json_repository
from models.matieres import Matiere
from lib.paths import get_reference_file

def exemple_import_json():
    """Exemple d'import depuis le fichier matieres.json"""
    print("=== Import JSON des Matières Premières ===\n")

    # Créer le repository
    matieres_repo = create_json_repository(MatieresPremieresRepository)

    # Import depuis le fichier réel
    print("Import depuis le fichier de référence:")
    try:
        matieres_file = get_reference_file("matieres.json")
        matieres_repo.import_from_json(str(matieres_file))
        print("   ✓ Import réussi")

        # Afficher les matières importées
        matieres = matieres_repo.get_all()
        print(f"   - Nombre de matières importées: {len(matieres)}")

        if len(matieres) > 0:
            print("   - Exemples de matières:")
            for i, matiere in enumerate(matieres[:5]):
                print(f"     {i+1}. {matiere.code_mp} - {matiere.nom}")
                if matiere.description:
                    print(f"        Description: {matiere.description}")
        else:
            print("   ❌ Aucune matière importée")

    except FileNotFoundError as e:
        print(f"   ⚠ Fichier non trouvé: {e}")
        print("   💡 Vérifiez que le fichier refs/matieres.json existe")
    except Exception as e:
        print(f"   ❌ Erreur lors de l'import: {e}")

    print()


def exemple_utilisation_custom():
    """Exemple d'utilisation avancée des matières"""
    print("=== Utilisation Avancée des Matières ===\n")

    # Créer le repository
    matieres_repo = create_json_repository(MatieresPremieresRepository)

    # Vider le repository avant de créer les matières de test
    print("1. Nettoyage du repository:")
    matieres_repo.flush()
    print()

    # Créer quelques matières de test
    matieres_test = [
        Matiere(code_mp="ACIDE001", nom="Acide chlorhydrique", description="Acide minéral fort"),
        Matiere(code_mp="BASE001", nom="Hydroxyde de sodium", description="Base forte"),
        Matiere(code_mp="SOLV001", nom="Éthanol", description="Solvant organique"),
        Matiere(code_mp="CAT001", nom="Catalyseur A", description="Catalyseur de synthèse"),
        Matiere(code_mp="CAT002", nom="Catalyseur B", description="Catalyseur de polymérisation")
    ]

    print("2. Création de matières de test:")
    for matiere in matieres_test:
        try:
            matieres_repo.create(matiere)
            print(f"   ✓ {matiere.code_mp} - {matiere.nom}")
        except ValueError as e:
            print(f"   ⚠ {matiere.code_mp} existe déjà")

    print()

    # Recherche par terme
    print("3. Recherche par terme:")
    resultats_acide = matieres_repo.search_matieres("acide")
    print(f"   - Matières contenant 'acide': {len(resultats_acide)}")
    for matiere in resultats_acide:
        print(f"     • {matiere.code_mp} - {matiere.nom}")

    resultats_cat = matieres_repo.search_matieres("cat")
    print(f"   - Matières contenant 'cat': {len(resultats_cat)}")
    for matiere in resultats_cat:
        print(f"     • {matiere.code_mp} - {matiere.nom}")

    print()

    # Filtrage par description
    print("4. Filtrage par description:")
    matieres_avec_desc = matieres_repo.get_matieres_by_description("catalyseur")
    print(f"   - Matières avec description contenant 'catalyseur': {len(matieres_avec_desc)}")
    for matiere in matieres_avec_desc:
        print(f"     • {matiere.code_mp} - {matiere.nom}")

    print()

    # Récupération par code
    print("5. Récupération par code:")
    matiere = matieres_repo.get_matiere_by_code("ACIDE001")
    if matiere:
        print(f"   ✓ Trouvée: {matiere.code_mp} - {matiere.nom}")
        if matiere.description:
            print(f"      Description: {matiere.description}")
    else:
        print("   ❌ Matière non trouvée")

    print()


def exemple_analyse_matieres():
    """Exemple d'analyse des matières importées"""
    print("=== Analyse des Matières Importées ===\n")

    # Créer le repository
    matieres_repo = create_json_repository(MatieresPremieresRepository)

    # Importer les matières
    try:
        matieres_file = get_reference_file("matieres.json")
        matieres_repo.import_from_json(str(matieres_file))
        matieres = matieres_repo.get_all()

        print(f"Nombre total de matières: {len(matieres)}")

        # Statistiques
        matieres_avec_description = [m for m in matieres if m.description]
        matieres_seveso = [m for m in matieres if m.seveso]
        matieres_avec_fds = [m for m in matieres if m.fds]

        print(f"Matières avec description: {len(matieres_avec_description)}")
        print(f"Matières Seveso: {len(matieres_seveso)}")
        print(f"Matières avec FDS: {len(matieres_avec_fds)}")

        # Recherche par type
        print("\nRecherche par type de matière:")
        matiere_isononyl = matieres_repo.search_matieres("ISONONYL")
        matieres_ethylique = matieres_repo.search_matieres("ETHYL")

        print(f"Isononyl: {len(matiere_isononyl)}")
        print(f"Ethyl: {len(matieres_ethylique)}")

        # Exemples de matières
        print("\nExemples de matières:")
        for i, matiere in enumerate(matieres[:10]):
            print(f"  {i+1:2d}. {matiere.code_mp} - {matiere.nom}")

    except Exception as e:
        print(f"Erreur lors de l'analyse: {e}")

    print()


def main():
    """Fonction principale"""
    print("=== Exemple Import JSON des Matières ===\n")

    # Exemples
    # exemple_import_json()
    # exemple_utilisation_custom()
    exemple_analyse_matieres()

    print("=== Exemple terminé ===")
    print("\n💡 L'import JSON utilise le format du fichier refs/matieres.json existant !")

if __name__ == "__main__":
    main()
