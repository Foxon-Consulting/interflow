"""
Test simple du décodeur de rapatriements
"""
import logging
import sys
from pathlib import Path

# Configurer les logs
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lib.decoders.rappatriementdecoder_xlsx import RappatriementDecoderXLSX
import pandas as pd
import tempfile

def test_rappatriement_decoder():
    """
    Test du décodeur avec un fichier XLSX créé dynamiquement
    """
    print("🧪 Test du décodeur de rapatriements")
    print("-" * 50)

    # Créer un fichier XLSX de test
    test_data = {
        'Code Prdt': ['PROD001', 'PROD002', 'PROD003'],
        'Designation Prdt': ['Produit Test 1', 'Produit Test 2', 'Produit Test 3'],
        'Lot': ['LOT001', 'LOT002', 'LOT003'],
        'Poids Net': [100.5, 250.0, 75.25],
        'Type Emballage': ['Carton', 'Sac', 'Conteneur'],
        'Stock Solde': [True, False, True],
        'Nb Contenants': [5, 10, 3],
        'Nb Palettes': [2, 4, 1],
        'Dimension Palettes': ['80x120', '100x120', '60x80'],
        'Code ONU': ['UN1234', 'UN5678', 'UN9012'],
        'Grp Emballage': ['II', 'III', 'I'],
        'PO': ['PO001', 'PO002', 'PO003']
    }

    df = pd.DataFrame(test_data)

    # Créer un fichier temporaire
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
        df.to_excel(tmp_file.name, index=False)
        test_file = tmp_file.name

    try:
        print(f"📄 Fichier de test créé : {test_file}")
        print(f"📊 Données de test : {len(df)} lignes")
        print(f"📋 Colonnes : {list(df.columns)}")

        # Tester le décodeur
        decoder = RappatriementDecoderXLSX()
        rapatriements = decoder.decode_xlsx_file(test_file)

        print(f"\n✅ Résultats du décodage :")
        print(f"   Nombre de rapatriements : {len(rapatriements)}")

        if rapatriements:
            rappatriement = rapatriements[0]
            print(f"   Numéro de transfert : {rappatriement.numero_transfert}")
            print(f"   Nombre de produits : {len(rappatriement.produits)}")
            print(f"   Responsable : {rappatriement.responsable_diffusion}")

            # Afficher les produits
            print(f"\n📦 Produits décodés :")
            for i, produit in enumerate(rappatriement.produits, 1):
                print(f"   {i}. {produit.code_prdt} - {produit.designation_prdt}")
                print(f"      Lot: {produit.lot}, Poids: {produit.poids_net} kg")
                print(f"      Type emballage: {produit.type_emballage.value}")
                print(f"      Stock solde: {produit.stock_solde}")
                print(f"      Contenants: {produit.nb_contenants}, Palettes: {produit.nb_palettes}")
                print(f"      Code ONU: {produit.code_onu}, Groupe: {produit.grp_emballage}")
                print(f"      PO: {produit.po}")

        print("\n✅ Test réussi !")

    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Nettoyer le fichier temporaire
        try:
            Path(test_file).unlink()
            print(f"🧹 Fichier temporaire supprimé")
        except:
            pass

if __name__ == "__main__":
    test_rappatriement_decoder()
