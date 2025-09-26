"""
Exemple spécifique pour l'import CSV des commandes
"""
from repositories import CommandesRepository, create_json_repository
from models.commande import Commande, Etat as CommandeEtat, TypeCommande
from lib.paths import get_input_file
from datetime import datetime

def exemple_import_csv():
    """Exemple d'import depuis le fichier commandes.csv"""
    print("=== Import CSV des Commandes ===\n")

    # Créer le repository
    commandes_repo = create_json_repository(CommandesRepository)

    # Import depuis le fichier CSV
    print("Import depuis le fichier CSV:")
    try:
        commandes_file = get_input_file("commandes.csv")
        commandes_repo.import_from_csv(str(commandes_file))
        print("   ✓ Import réussi")

        # Afficher les commandes importées
        commandes_list = commandes_repo.get_commandes_list()
        print(f"   - Nombre de commandes importées: {len(commandes_list)}")

        if len(commandes_list) > 0:
            print("   - Exemples de commandes:")
            for i, commande in enumerate(commandes_list[:5]):
                print(f"     {i+1}. {commande.matiere.code_mp} - {commande.matiere.nom}")
                print(f"        Quantité: {commande.quantite}, Lot: {commande.lot}")
                print(f"        État: {commande.etat.value}, Qualification: {commande.qualification}")
        else:
            print("   ❌ Aucune commande importée")

    except FileNotFoundError as e:
        print(f"   ⚠ Fichier non trouvé: {e}")
        print("   💡 Vérifiez que le fichier inputs/commandes.csv existe")
    except Exception as e:
        print(f"   ❌ Erreur lors de l'import: {e}")

    print()


def exemple_utilisation_avancee():
    """Exemple d'utilisation avancée des commandes"""
    print("=== Utilisation Avancée des Commandes ===\n")

    # Créer le repository
    commandes_repo = create_json_repository(CommandesRepository)

    # Vider le repository avant de créer les commandes de test
    print("1. Nettoyage du repository:")
    commandes_repo.flush()
    print()

    # Créer quelques commandes de test
    from models.matieres import Matiere
    commandes_test = [
        Commande(
            id="CMD001",
            type=TypeCommande.PRESTATAIRE,
            matiere=Matiere(code_mp="V22270", nom="ETHYL MALTOL"),
            quantite=100,
            lot="LOT001",
            qualification=False,
            date_creation=datetime.now(),
            etat=CommandeEtat.EN_COURS
        ),
        Commande(
            id="CMD002",
            type=TypeCommande.PRESTATAIRE,
            matiere=Matiere(code_mp="C03177", nom="CAMPHRE SYNTHETIQUE POUDRE"),
            quantite=250,
            lot="LOT002",
            qualification=True,
            date_creation=datetime.now(),
            etat=CommandeEtat.TERMINEE
        ),
        Commande(
            id="CMD003",
            type=TypeCommande.PRESTATAIRE,
            matiere=Matiere(code_mp="I09912", nom="IONONE BETA"),
            quantite=75,
            lot="LOT003",
            qualification=False,
            date_creation=datetime.now(),
            etat=CommandeEtat.ANNULEE
        )
    ]

    print("2. Création de commandes de test:")
    for commande in commandes_test:
        try:
            commandes_repo.create(commande)
            print(f"   ✓ {commande.matiere.code_mp} - {commande.matiere.nom}")
        except ValueError as e:
            print(f"   ⚠ {commande.matiere.code_mp} existe déjà")

    print()

    # Récupération par état
    print("3. Récupération par état:")
    commandes_en_cours = commandes_repo.get_commandes_en_cours()
    commandes_terminees = commandes_repo.get_commandes_terminees()
    commandes_annulees = commandes_repo.get_commandes_annulees()

    print(f"   - Commandes en cours: {len(commandes_en_cours)}")
    print(f"   - Commandes terminées: {len(commandes_terminees)}")
    print(f"   - Commandes annulées: {len(commandes_annulees)}")

    print()

    # Récupération par matière
    print("4. Récupération par matière:")
    commandes_matiere = commandes_repo.get_commandes_by_matiere("V22270")
    print(f"   - Commandes pour V22270: {len(commandes_matiere)}")
    for commande in commandes_matiere:
        print(f"     • Quantité: {commande.quantite}, État: {commande.etat.value}")

    print()

    # Mise à jour d'état
    print("5. Mise à jour d'état:")
    if len(commandes_en_cours) > 0:
        premiere_commande = commandes_en_cours[0]
        commande_mise_a_jour = commandes_repo.update_etat(premiere_commande.id, CommandeEtat.TERMINEE)
        if commande_mise_a_jour:
            print(f"   ✓ État mis à jour: {premiere_commande.matiere.code_mp} → {commande_mise_a_jour.etat.value}")

    print()

    # Calcul de quantité totale par matière
    print("6. Calcul de quantité totale par matière:")
    total_v22270 = commandes_repo.get_total_quantity_by_matiere("V22270")
    print(f"   - Quantité totale commandée V22270: {total_v22270}")

    print()


def exemple_analyse_commandes():
    """Exemple d'analyse des commandes importées"""
    print("=== Analyse des Commandes Importées ===\n")

    # Créer le repository
    commandes_repo = create_json_repository(CommandesRepository)

    # Importer les commandes
    try:
        commandes_file = get_input_file("commandes.csv")
        commandes_repo.import_from_csv(str(commandes_file))
        commandes_list = commandes_repo.get_commandes_list()

        print(f"Nombre total de commandes: {len(commandes_list)}")

        # Statistiques par état
        commandes_en_cours = commandes_repo.get_commandes_en_cours()
        commandes_terminees = commandes_repo.get_commandes_terminees()
        commandes_annulees = commandes_repo.get_commandes_annulees()

        print(f"Commandes en cours: {len(commandes_en_cours)}")
        print(f"Commandes terminées: {len(commandes_terminees)}")
        print(f"Commandes annulées: {len(commandes_annulees)}")

        # Statistiques par matière
        print("\nTop 5 des matières avec le plus de commandes:")
        matieres_count = {}
        for commande in commandes_list:
            code_mp = commande.matiere.code_mp
            matieres_count[code_mp] = matieres_count.get(code_mp, 0) + 1

        top_matieres = sorted(matieres_count.items(), key=lambda x: x[1], reverse=True)[:5]
        for code_mp, count in top_matieres:
            print(f"  - {code_mp}: {count} commandes")

        # Commandes de qualification
        commandes_qualification = [c for c in commandes_list if c.qualification]
        print(f"\nCommandes de qualification: {len(commandes_qualification)}")

        # Quantités totales par matière
        print("\nQuantités totales commandées par matière (top 5):")
        matieres_quantite = {}
        for commande in commandes_en_cours:
            code_mp = commande.matiere.code_mp
            if code_mp not in matieres_quantite:
                matieres_quantite[code_mp] = 0
            matieres_quantite[code_mp] += commande.quantite

        top_quantites = sorted(matieres_quantite.items(), key=lambda x: x[1], reverse=True)[:5]
        for code_mp, quantite in top_quantites:
            print(f"  - {code_mp}: {quantite}")

        # Exemples de commandes
        print("\nExemples de commandes:")
        for i, commande in enumerate(commandes_list[:10]):
            print(f"  {i+1:2d}. {commande.matiere.code_mp} - {commande.matiere.nom}")
            print(f"      Quantité: {commande.quantite}, État: {commande.etat.value}")
            print(f"      Qualification: {commande.qualification}, Lot: {commande.lot}")

    except Exception as e:
        print(f"Erreur lors de l'analyse: {e}")

    print()


def exemple_filtrage_avance():
    """Exemple de filtrage avancé des commandes"""
    print("=== Filtrage Avancé des Commandes ===\n")

    # Créer le repository
    commandes_repo = create_json_repository(CommandesRepository)

    # Importer les commandes
    try:
        commandes_file = get_input_file("commandes.csv")
        commandes_repo.import_from_csv(str(commandes_file))
        commandes_list = commandes_repo.get_commandes_list()

        print(f"Nombre total de commandes: {len(commandes_list)}")

        # Filtrage par matière spécifique
        print("\n1. Commandes pour une matière spécifique:")
        commandes_ethyl = commandes_repo.get_commandes_by_matiere("V22270")  # ETHYL MALTOL
        print(f"   - ETHYL MALTOL (V22270): {len(commandes_ethyl)} commandes")

        if len(commandes_ethyl) > 0:
            total_quantite = sum(c.quantite for c in commandes_ethyl)
            print(f"   - Quantité totale: {total_quantite}")

            # Répartition par état
            etats_ethyl = {}
            for commande in commandes_ethyl:
                etat = commande.etat.value
                if etat not in etats_ethyl:
                    etats_ethyl[etat] = 0
                etats_ethyl[etat] += 1

            print("   - Répartition par état:")
            for etat, count in etats_ethyl.items():
                print(f"     • {etat}: {count}")

        # Filtrage par type de commande
        print("\n2. Répartition par type de commande:")
        commandes_qualification = [c for c in commandes_list if c.qualification]
        commandes_production = [c for c in commandes_list if not c.qualification]

        print(f"   - Commandes de qualification: {len(commandes_qualification)}")
        print(f"   - Commandes de production: {len(commandes_production)}")

        # Quantités totales par type
        total_qualification = sum(c.quantite for c in commandes_qualification)
        total_production = sum(c.quantite for c in commandes_production)
        print(f"   - Quantité totale qualification: {total_qualification}")
        print(f"   - Quantité totale production: {total_production}")

        # Filtrage par état
        print("\n3. Commandes par état:")
        etats = [CommandeEtat.EN_COURS, CommandeEtat.TERMINEE, CommandeEtat.ANNULEE]
        for etat in etats:
            commandes_etat = commandes_repo.get_commandes_by_etat(etat)
            if len(commandes_etat) > 0:
                total_quantite = sum(c.quantite for c in commandes_etat)
                print(f"   - {etat.value}: {len(commandes_etat)} commandes ({total_quantite} total)")

        # Commandes récentes
        print("\n4. Commandes récentes (7 derniers jours):")
        from datetime import timedelta
        date_limite = datetime.now() - timedelta(days=7)
        commandes_recentes = [c for c in commandes_list if c.date_creation >= date_limite]
        print(f"   - Nombre: {len(commandes_recentes)}")

        if len(commandes_recentes) > 0:
            print("   - Détail:")
            for commande in commandes_recentes[:5]:
                jours_ecoules = (datetime.now() - commande.date_creation).days
                print(f"     • {commande.matiere.code_mp} - {commande.matiere.nom}")
                print(f"       Quantité: {commande.quantite}, J-{jours_ecoules}, État: {commande.etat.value}")

    except Exception as e:
        print(f"Erreur lors du filtrage: {e}")

    print()


def exemple_commandes_internes():
    """Exemple d'utilisation des commandes internes"""
    print("=== Commandes Internes ===\n")

    # Créer le repository
    commandes_repo = create_json_repository(CommandesRepository)

    # Vider le repository avant de créer les commandes de test
    print("1. Nettoyage du repository:")
    commandes_repo.flush()
    print()

    # Créer quelques commandes internes de test
    from models.matieres import Matiere
    commandes_internes_test = [
        Commande(
            type=TypeCommande.INTERNE,
            ordre="CI001",
            type_ordre="INTERNE",
            statut_ordre="RELÂCHÉ",
            poste="POSTE1",
            statut_poste="ACTIF",
            division="DIV1",
            magasin="MAG1",
            article="V22270",
            libelle_article="ETHYL MALTOL",
            quantite=50.0,
            quantite_ordre=50.0,
            quantite_receptionnee=0.0,
            udm="KG",
            fournisseur="Fournisseur A",
            matiere=Matiere(code_mp="V22270", nom="ETHYL MALTOL"),
            date_creation=datetime.now()
        ),
        Commande(
            type=TypeCommande.INTERNE,
            ordre="CI002",
            type_ordre="INTERNE",
            statut_ordre="EN_ATTENTE",
            poste="POSTE2",
            statut_poste="ACTIF",
            division="DIV1",
            magasin="MAG1",
            article="C03177",
            libelle_article="CAMPHRE SYNTHETIQUE POUDRE",
            quantite=100.0,
            quantite_ordre=100.0,
            quantite_receptionnee=0.0,
            udm="KG",
            fournisseur="Fournisseur B",
            matiere=Matiere(code_mp="C03177", nom="CAMPHRE SYNTHETIQUE POUDRE"),
            date_creation=datetime.now()
        )
    ]

    print("2. Création de commandes internes de test:")
    for commande in commandes_internes_test:
        try:
            commandes_repo.create(commande)
            print(f"   ✓ {commande.ordre} - {commande.matiere.code_mp}")
        except ValueError as e:
            print(f"   ⚠ {commande.ordre} existe déjà")

    print()

    # Récupération par statut
    print("3. Récupération par statut:")
    commandes_relachees = commandes_repo.get_commandes_relachees()
    print(f"   - Commandes relâchées: {len(commandes_relachees)}")

    # Récupération par fournisseur
    print("4. Récupération par fournisseur:")
    commandes_fournisseur = commandes_repo.get_commandes_by_fournisseur("Fournisseur A")
    print(f"   - Commandes Fournisseur A: {len(commandes_fournisseur)}")

    # Calcul de quantité totale par matière
    print("5. Calcul de quantité totale par matière:")
    total_v22270 = commandes_repo.get_total_quantity_by_matiere("V22270")
    print(f"   - Quantité totale commandée V22270: {total_v22270}")

    print()


def main():
    """Fonction principale"""
    print("=== Exemple Import CSV des Commandes ===\n")

    # Exemples
    exemple_import_csv()
    # exemple_utilisation_avancee()
    # exemple_analyse_commandes()
    # exemple_filtrage_avance()
    # exemple_commandes_internes()

    print("=== Exemple terminé ===")
    print("\n💡 L'import CSV utilise le fichier inputs/commandes.csv avec le CommandeDecoder !")

if __name__ == "__main__":
    main()
