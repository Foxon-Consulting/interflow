"""
Exemple spécifique pour l'import CSV des stocks
"""
from repositories import StocksRepository, create_json_repository
from models.stock import Stock
from lib.paths import get_input_file

def exemple_import_csv():
    """Exemple d'import depuis le fichier stocks.csv"""
    print("=== Import CSV des Stocks ===\n")

    # Créer le repository
    stocks_repo = create_json_repository(StocksRepository)
    stocks_repo.flush()

    # Import depuis le fichier CSV
    print("Import depuis le fichier CSV:")
    try:
        stocks_file = get_input_file("stocks.csv")
        stocks_repo.import_from_csv(str(stocks_file))
        print("   ✓ Import réussi")

        # Afficher les stocks importés
        stocks_list = stocks_repo.get_stocks_list()
        print(f"   - Nombre de stocks importés: {len(stocks_list)}")

        if len(stocks_list) > 0:
            print("   - Exemples de stocks:")
            for i, stock in enumerate(stocks_list[:5]):
                print(f"     {i+1}. {stock.article} - {stock.libelle_article}")
                print(f"        Quantité: {stock.quantite} {stock.udm}, Magasin: {stock.magasin}")
                print(f"        Statut: {stock.statut_lot}, Emplacement: {stock.emplacement}")
        else:
            print("   ❌ Aucun stock importé")

    except FileNotFoundError as e:
        print(f"   ⚠ Fichier non trouvé: {e}")
        print("   💡 Vérifiez que le fichier inputs/stocks.csv existe")
    except Exception as e:
        print(f"   ❌ Erreur lors de l'import: {e}")

    print()


def exemple_utilisation_custom():
    """Exemple d'utilisation avancée des stocks"""
    print("=== Utilisation Avancée des Stocks ===\n")

    # Créer le repository
    stocks_repo = create_json_repository(StocksRepository)

    # Vider le repository avant de créer les stocks de test
    print("1. Nettoyage du repository:")
    stocks_repo.flush()
    print()

    # Créer quelques stocks de test
    from models.matieres import Matiere
    stocks_test = [
        Stock(
            id="STOCK001",
            article="V22270",
            libelle_article="ETHYL MALTOL",
            du="2025-01-01",
            quantite=100.0,
            udm="KG",
            statut_lot="OK",
            division="PROD",
            magasin="MAG01",
            emplacement="A1-B2-C3",
            contenant="FUT",
            statut_proprete="PROPRE",
            reutilisable="OUI",
            statut_contenant="BON"
        ),
        Stock(
            id="STOCK002",
            article="C03177",
            libelle_article="CAMPHRE SYNTHETIQUE POUDRE",
            du="2025-02-01",
            quantite=250.0,
            udm="KG",
            statut_lot="OK",
            division="PROD",
            magasin="EX01",
            emplacement="EXT-A1",
            contenant="SAC",
            statut_proprete="PROPRE",
            reutilisable="NON",
            statut_contenant="BON"
        ),
        Stock(
            id="STOCK003",
            article="I09912",
            libelle_article="IONONE BETA",
            du="2025-03-01",
            quantite=75.5,
            udm="L",
            statut_lot="EN_ATTENTE",
            division="QUAL",
            magasin="MAG02",
            emplacement="B3-C4-D5",
            contenant="BIDON",
            statut_proprete="PROPRE",
            reutilisable="OUI",
            statut_contenant="BON"
        )
    ]

    print("2. Création de stocks de test:")
    for stock in stocks_test:
        try:
            stocks_repo.create(stock)
            print(f"   ✓ {stock.article} - {stock.libelle_article}")
        except ValueError as e:
            print(f"   ⚠ {stock.article} existe déjà")

    print()

    # Récupération par type de magasin
    print("3. Récupération par type de magasin:")
    stocks_internes = stocks_repo.get_internal_stocks()
    stocks_externes = stocks_repo.get_external_stocks()

    print(f"   - Stocks internes: {len(stocks_internes)}")
    print(f"   - Stocks externes: {len(stocks_externes)}")

    print()

    # Récupération par matière
    print("4. Récupération par matière:")
    stocks_matiere = stocks_repo.get_stocks_by_matiere("V22270")
    print(f"   - Stocks pour V22270: {len(stocks_matiere)}")
    for stock in stocks_matiere:
        print(f"     • Quantité: {stock.quantite} {stock.udm}, Magasin: {stock.magasin}")

    print()

    # Récupération par magasin
    print("5. Récupération par magasin:")
    stocks_magasin = stocks_repo.get_stocks_by_magasin("MAG01")
    print(f"   - Stocks dans MAG01: {len(stocks_magasin)}")

    # Récupération par statut
    stocks_ok = stocks_repo.get_stocks_by_statut("OK")
    stocks_attente = stocks_repo.get_stocks_by_statut("EN_ATTENTE")
    print(f"   - Stocks OK: {len(stocks_ok)}")
    print(f"   - Stocks en attente: {len(stocks_attente)}")

    print()

    # Mise à jour de quantité
    print("6. Mise à jour de quantité:")
    if len(stocks_internes) > 0:
        premier_stock = stocks_internes[0]
        stock_mis_a_jour = stocks_repo.update_quantity(premier_stock.id, 150.0)
        if stock_mis_a_jour:
            print(f"   ✓ Quantité mise à jour: {premier_stock.article} → {stock_mis_a_jour.quantite}")

    print()

    # Calcul de quantité totale par matière
    print("7. Calcul de quantité totale par matière:")
    total_v22270 = stocks_repo.get_total_quantity_by_matiere("V22270")
    print(f"   - Quantité totale V22270: {total_v22270}")

    print()


def exemple_analyse_stocks():
    """Exemple d'analyse des stocks importés"""
    print("=== Analyse des Stocks Importés ===\n")

    # Créer le repository
    stocks_repo = create_json_repository(StocksRepository)

    # Importer les stocks
    try:
        stocks_file = get_input_file("stocks.csv")
        stocks_repo.import_from_csv(str(stocks_file))
        stocks_list = stocks_repo.get_stocks_list()

        print(f"Nombre total de stocks: {len(stocks_list)}")

        # Statistiques par type de magasin
        stocks_internes = stocks_repo.get_internal_stocks()
        stocks_externes = stocks_repo.get_external_stocks()

        print(f"Stocks internes: {len(stocks_internes)}")
        print(f"Stocks externes: {len(stocks_externes)}")

        # Statistiques par statut
        stocks_ok = stocks_repo.get_stocks_by_statut("OK")
        stocks_attente = stocks_repo.get_stocks_by_statut("EN_ATTENTE")
        stocks_bloque = stocks_repo.get_stocks_by_statut("BLOQUE")

        print(f"Stocks OK: {len(stocks_ok)}")
        print(f"Stocks en attente: {len(stocks_attente)}")
        print(f"Stocks bloqués: {len(stocks_bloque)}")

        # Statistiques par matière
        print("\nTop 5 des matières avec le plus de stocks:")
        matieres_count = {}
        for stock in stocks_list:
            article = stock.article
            matieres_count[article] = matieres_count.get(article, 0) + 1

        top_matieres = sorted(matieres_count.items(), key=lambda x: x[1], reverse=True)[:5]
        for article, count in top_matieres:
            print(f"  - {article}: {count} stocks")

        # Stocks par magasin
        print("\nStocks par magasin:")
        magasins_count = {}
        for stock in stocks_list:
            magasin = stock.magasin
            magasins_count[magasin] = magasins_count.get(magasin, 0) + 1

        top_magasins = sorted(magasins_count.items(), key=lambda x: x[1], reverse=True)[:5]
        for magasin, count in top_magasins:
            print(f"  - {magasin}: {count} stocks")

        # Quantités totales par matière
        print("\nQuantités totales par matière (top 5):")
        matieres_quantite = {}
        for stock in stocks_list:
            article = stock.article
            if article not in matieres_quantite:
                matieres_quantite[article] = 0
            matieres_quantite[article] += stock.quantite

        top_quantites = sorted(matieres_quantite.items(), key=lambda x: x[1], reverse=True)[:5]
        for article, quantite in top_quantites:
            print(f"  - {article}: {quantite}")

        # Exemples de stocks
        print("\nExemples de stocks:")
        for i, stock in enumerate(stocks_list[:10]):
            print(f"  {i+1:2d}. {stock.article} - {stock.libelle_article}")
            print(f"      Quantité: {stock.quantite} {stock.udm}, Magasin: {stock.magasin}")
            print(f"      Statut: {stock.statut_lot}, Emplacement: {stock.emplacement}")

    except Exception as e:
        print(f"Erreur lors de l'analyse: {e}")

    print()


def exemple_filtrage_avance():
    """Exemple de filtrage avancé des stocks"""
    print("=== Filtrage Avancé des Stocks ===\n")

    # Créer le repository
    stocks_repo = create_json_repository(StocksRepository)

    # Importer les stocks
    try:
        stocks_file = get_input_file("stocks.csv")
        stocks_repo.import_from_csv(str(stocks_file))
        stocks_list = stocks_repo.get_stocks_list()

        print(f"Nombre total de stocks: {len(stocks_list)}")

        # Filtrage par matière spécifique
        print("\n1. Stocks pour une matière spécifique:")
        stocks_ethyl = stocks_repo.get_stocks_by_matiere("V22270")  # ETHYL MALTOL
        print(f"   - ETHYL MALTOL (V22270): {len(stocks_ethyl)} stocks")

        if len(stocks_ethyl) > 0:
            total_quantite = sum(s.quantite for s in stocks_ethyl)
            print(f"   - Quantité totale: {total_quantite}")

            # Répartition par magasin
            magasins_ethyl = {}
            for stock in stocks_ethyl:
                magasin = stock.magasin
                if magasin not in magasins_ethyl:
                    magasins_ethyl[magasin] = 0
                magasins_ethyl[magasin] += stock.quantite

            print("   - Répartition par magasin:")
            for magasin, quantite in magasins_ethyl.items():
                print(f"     • {magasin}: {quantite}")

        # Filtrage par type de stock
        print("\n2. Répartition par type de stock:")
        stocks_internes = stocks_repo.get_internal_stocks()
        stocks_externes = stocks_repo.get_external_stocks()

        print(f"   - Stocks internes: {len(stocks_internes)}")
        print(f"   - Stocks externes: {len(stocks_externes)}")

        # Quantités totales par type
        total_internes = sum(s.quantite for s in stocks_internes)
        total_externes = sum(s.quantite for s in stocks_externes)
        print(f"   - Quantité totale interne: {total_internes}")
        print(f"   - Quantité totale externe: {total_externes}")

        # Filtrage par statut
        print("\n3. Stocks par statut:")
        statuts = ["OK", "EN_ATTENTE", "BLOQUE", "QUARANTAINE"]
        for statut in statuts:
            stocks_statut = stocks_repo.get_stocks_by_statut(statut)
            if len(stocks_statut) > 0:
                total_quantite = sum(s.quantite for s in stocks_statut)
                print(f"   - {statut}: {len(stocks_statut)} stocks ({total_quantite} total)")

        # Stocks par contenant
        print("\n4. Stocks par type de contenant:")
        contenants_count = {}
        for stock in stocks_list:
            contenant = stock.contenant
            contenants_count[contenant] = contenants_count.get(contenant, 0) + 1

        top_contenants = sorted(contenants_count.items(), key=lambda x: x[1], reverse=True)[:5]
        for contenant, count in top_contenants:
            print(f"   - {contenant}: {count} stocks")

    except Exception as e:
        print(f"Erreur lors du filtrage: {e}")

    print()


def main():
    """Fonction principale"""
    print("=== Exemple Import CSV des Stocks ===\n")

    # Exemples
    exemple_import_csv()
    # exemple_utilisation_custom()
    # exemple_analyse_stocks()
    # exemple_filtrage_avance()

    print("=== Exemple terminé ===")
    print("\n💡 L'import CSV utilise le fichier inputs/stocks.csv avec le StockDecoder !")

if __name__ == "__main__":
    main()
