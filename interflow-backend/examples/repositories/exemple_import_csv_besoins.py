"""
Exemple spécifique pour l'import CSV des besoins
"""
from repositories import BesoinsRepository, create_json_repository
from models.besoin import Besoin, Etat
from lib.paths import get_input_file
from datetime import datetime, timedelta

def exemple_import_csv():
    """Exemple d'import depuis le fichier besoins.csv"""
    print("=== Import CSV des Besoins ===\n")

    # Créer le repository
    besoins_repo = create_json_repository(BesoinsRepository)

    besoins_repo.flush()
    # Import depuis le fichier CSV
    print("Import depuis le fichier CSV:")
    try:
        besoins_file = get_input_file("besoins.csv")
        besoins_repo.import_from_csv(str(besoins_file))
        print("   ✓ Import réussi")

        # Afficher les besoins importés
        besoins_list = besoins_repo.get_besoins_list()
        print(f"   - Nombre de besoins importés: {len(besoins_list)}")

        if len(besoins_list) > 0:
            print("   - Exemples de besoins:")
            for i, besoin in enumerate(besoins_list[:5]):
                print(f"     {i+1}. {besoin.matiere.code_mp} - {besoin.matiere.nom}")
                print(f"        Quantité: {besoin.quantite}, Échéance: {besoin.echeance.strftime('%d/%m/%Y')}")
                print(f"        État: {besoin.etat.value}, Lot: {besoin.lot}")
        else:
            print("   ❌ Aucun besoin importé")

    except FileNotFoundError as e:
        print(f"   ⚠ Fichier non trouvé: {e}")
        print("   💡 Vérifiez que le fichier inputs/besoins.csv existe")
    except Exception as e:
        print(f"   ❌ Erreur lors de l'import: {e}")

    print()


def exemple_utilisation_avancee():
    """Exemple d'utilisation avancée des besoins"""
    print("=== Utilisation Avancée des Besoins ===\n")

    # Créer le repository
    besoins_repo = create_json_repository(BesoinsRepository)

    # Vider le repository avant de créer les besoins de test
    print("1. Nettoyage du repository:")
    besoins_repo.flush()
    print()

    # Créer quelques besoins de test
    from models.matieres import Matiere
    besoins_test = [
        Besoin(
            id=1,
            matiere=Matiere(code_mp="TEST001", nom="Matière Test 1"),
            quantite=100.0,
            echeance=datetime.now() + timedelta(days=30),
                            etat=Etat.INCONNU,
            lot="LOT001"
        ),
        Besoin(
            id=2,
            matiere=Matiere(code_mp="TEST002", nom="Matière Test 2"),
            quantite=250.0,
            echeance=datetime.now() + timedelta(days=15),
            etat=Etat.PARTIEL,
            lot="LOT002"
        ),
        Besoin(
            id=3,
            matiere=Matiere(code_mp="TEST003", nom="Matière Test 3"),
            quantite=75.5,
            echeance=datetime.now() + timedelta(days=7),
            etat=Etat.COUVERT,
            lot="LOT003"
        )
    ]

    print("2. Création de besoins de test:")
    for besoin in besoins_test:
        try:
            besoins_repo.create(besoin)
            print(f"   ✓ {besoin.matiere.code_mp} - {besoin.matiere.nom}")
        except ValueError as e:
            print(f"   ⚠ {besoin.matiere.code_mp} existe déjà")

    print()

    # Récupération par état
    print("3. Récupération par état:")
    besoins_actuels = besoins_repo.get_besoins_by_etat(Etat.INCONNU)
    besoins_partiels = besoins_repo.get_besoins_by_etat(Etat.PARTIEL)
    besoins_couverts = besoins_repo.get_besoins_by_etat(Etat.COUVERT)

    print(f"   - Besoins inconnus: {len(besoins_actuels)}")
    print(f"   - Besoins partiels: {len(besoins_partiels)}")
    print(f"   - Besoins couverts: {len(besoins_couverts)}")

    print()

    # Récupération par matière
    print("4. Récupération par matière:")
    besoins_matiere = besoins_repo.get_besoins_by_matiere("TEST001")
    print(f"   - Besoins pour TEST001: {len(besoins_matiere)}")
    for besoin in besoins_matiere:
        print(f"     • Quantité: {besoin.quantite}, Échéance: {besoin.echeance.strftime('%d/%m/%Y')}")

    print()

    # Récupération par intervalle de temps
    print("5. Récupération par intervalle de temps:")
    date_debut = datetime.now()
    besoins_30_jours = besoins_repo.get_besoins_by_timelapse(30, date_debut)
    print(f"   - Besoins sur 30 jours: {len(besoins_30_jours)}")

    # Besoins agrégés
    besoins_aggregated = besoins_repo.get_besoins_aggregated_by_timelapse(30, date_debut)
    print(f"   - Besoins agrégés sur 30 jours: {len(besoins_aggregated)}")

    print()

    # Mise à jour d'état
    print("6. Mise à jour d'état:")
    if len(besoins_actuels) > 0:
        premier_besoin = besoins_actuels[0]
        besoin_mis_a_jour = besoins_repo.update_etat(premier_besoin.id, Etat.COUVERT)
        if besoin_mis_a_jour:
            print(f"   ✓ État mis à jour: {premier_besoin.matiere.code_mp} → {besoin_mis_a_jour.etat.value}")

    print()


def exemple_analyse_besoins():
    """Exemple d'analyse des besoins importés"""
    print("=== Analyse des Besoins Importés ===\n")

    # Créer le repository
    besoins_repo = create_json_repository(BesoinsRepository)

    # Importer les besoins
    try:
        besoins_file = get_input_file("besoins.csv")
        besoins_repo.import_from_csv(str(besoins_file))
        besoins_list = besoins_repo.get_besoins_list()

        print(f"Nombre total de besoins: {len(besoins_list)}")

        # Statistiques par état
        besoins_actuels = besoins_repo.get_besoins_by_etat(Etat.INCONNU)
        besoins_partiels = besoins_repo.get_besoins_by_etat(Etat.PARTIEL)
        besoins_couverts = besoins_repo.get_besoins_by_etat(Etat.COUVERT)

        print(f"Besoins inconnus: {len(besoins_actuels)}")
        print(f"Besoins partiels: {len(besoins_partiels)}")
        print(f"Besoins couverts: {len(besoins_couverts)}")

        # Statistiques par matière
        print("\nTop 5 des matières avec le plus de besoins:")
        matieres_count = {}
        for besoin in besoins_list:
            code_mp = besoin.matiere.code_mp
            matieres_count[code_mp] = matieres_count.get(code_mp, 0) + 1

        top_matieres = sorted(matieres_count.items(), key=lambda x: x[1], reverse=True)[:5]
        for code_mp, count in top_matieres:
            print(f"  - {code_mp}: {count} besoins")

        # Besoins urgents (7 jours)
        print("\nBesoins urgents (7 jours):")
        date_debut = datetime.now()
        besoins_urgents = besoins_repo.get_besoins_by_timelapse(7, date_debut)
        print(f"  - Nombre: {len(besoins_urgents)}")

        if len(besoins_urgents) > 0:
            print("  - Exemples:")
            for i, besoin in enumerate(besoins_urgents[:3]):
                print(f"    {i+1}. {besoin.matiere.code_mp} - {besoin.matiere.nom}")
                print(f"       Quantité: {besoin.quantite}, Échéance: {besoin.echeance.strftime('%d/%m/%Y')}")

        # Besoins par mois
        print("\nBesoins par mois:")
        besoins_30_jours = besoins_repo.get_besoins_by_timelapse(30, date_debut)
        besoins_60_jours = besoins_repo.get_besoins_by_timelapse(60, date_debut)
        besoins_90_jours = besoins_repo.get_besoins_by_timelapse(90, date_debut)

        print(f"  - 30 jours: {len(besoins_30_jours)}")
        print(f"  - 60 jours: {len(besoins_60_jours)}")
        print(f"  - 90 jours: {len(besoins_90_jours)}")

        # Exemples de besoins
        print("\nExemples de besoins:")
        for i, besoin in enumerate(besoins_list[:10]):
            print(f"  {i+1:2d}. {besoin.matiere.code_mp} - {besoin.matiere.nom}")
            print(f"      Quantité: {besoin.quantite}, Échéance: {besoin.echeance.strftime('%d/%m/%Y')}")

    except Exception as e:
        print(f"Erreur lors de l'analyse: {e}")

    print()


def exemple_filtrage_avance():
    """Exemple de filtrage avancé des besoins"""
    print("=== Filtrage Avancé des Besoins ===\n")

    # Créer le repository
    besoins_repo = create_json_repository(BesoinsRepository)

    # Importer les besoins
    try:
        besoins_file = get_input_file("besoins.csv")
        besoins_repo.import_from_csv(str(besoins_file))
        besoins_list = besoins_repo.get_besoins_list()

        print(f"Nombre total de besoins: {len(besoins_list)}")

        # Filtrage par matière spécifique
        print("\n1. Besoins pour une matière spécifique:")
        besoins_ethyl = besoins_repo.get_besoins_by_matiere("V22270")  # ETHYL MALTOL
        print(f"   - ETHYL MALTOL (V22270): {len(besoins_ethyl)} besoins")

        if len(besoins_ethyl) > 0:
            total_quantite = sum(b.quantite for b in besoins_ethyl)
            print(f"   - Quantité totale: {total_quantite}")

            # Trier par échéance
            besoins_tries = sorted(besoins_ethyl, key=lambda x: x.echeance)
            print("   - Prochaines échéances:")
            for i, besoin in enumerate(besoins_tries[:3]):
                print(f"     {i+1}. {besoin.echeance.strftime('%d/%m/%Y')}: {besoin.quantite}")

        # Filtrage par période
        print("\n2. Besoins par période:")
        date_debut = datetime.now()

        # Cette semaine
        besoins_semaine = besoins_repo.get_besoins_by_timelapse(7, date_debut)
        print(f"   - Cette semaine: {len(besoins_semaine)}")

        # Ce mois
        besoins_mois = besoins_repo.get_besoins_by_timelapse(30, date_debut)
        print(f"   - Ce mois: {len(besoins_mois)}")

        # Ce trimestre
        besoins_trimestre = besoins_repo.get_besoins_by_timelapse(90, date_debut)
        print(f"   - Ce trimestre: {len(besoins_trimestre)}")

        # Besoins urgents (échéance dans les 3 jours)
        print("\n3. Besoins urgents (3 jours):")
        besoins_urgents = besoins_repo.get_besoins_by_timelapse(3, date_debut)
        print(f"   - Nombre: {len(besoins_urgents)}")

        if len(besoins_urgents) > 0:
            print("   - Détail:")
            for besoin in besoins_urgents[:5]:
                jours_restants = (besoin.echeance - date_debut).days
                print(f"     • {besoin.matiere.code_mp} - {besoin.matiere.nom}")
                print(f"       Quantité: {besoin.quantite}, J-{jours_restants}")

    except Exception as e:
        print(f"Erreur lors du filtrage: {e}")

    print()


def main():
    """Fonction principale"""
    print("=== Exemple Import CSV des Besoins ===\n")

    # Exemples
    exemple_import_csv()
    # exemple_utilisation_avancee()
    # exemple_analyse_besoins()
    # exemple_filtrage_avance()

    print("=== Exemple terminé ===")
    print("\n💡 L'import CSV utilise le fichier inputs/besoins.csv avec le BODecoder !")

if __name__ == "__main__":
    main()
