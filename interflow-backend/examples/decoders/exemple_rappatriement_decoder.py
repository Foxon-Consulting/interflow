"""
Exemple d'utilisation du décodeur de rapatriements
"""
from pathlib import Path
from datetime import datetime


from lib.paths import paths, get_input_file

from lib.decoders.rappatriements.xlsx import XLSXRappatriementsDecoder
from models.rappatriement import Rappatriement
from pathlib import Path
from typing import List, Tuple, Dict
import sys
import io
from lib.utils import compare_models
from lib.decoders.decoder import Decoder
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def exemple_simple(decoder: Decoder[Rappatriement], file_path: Path) -> List[Rappatriement]:
    """
    Exemple simple d'utilisation d'un decoder
    """
    print(f"🔍 Exemple simple d'utilisation du decoder {decoder.__class__.__name__}")
    print(f"Fichier : {file_path}")
    print("-" * 50)

    if not file_path.exists():
        print(f"❌ Fichier introuvable : {file_path}")
        return []

    try:
        rapatriements = decoder.decode_file(file_path)

        if rapatriements:
            print(f"Rapatriements trouvés : {len(rapatriements)}")

            for i, rapatriement in enumerate(rapatriements):
                print(f"\nRapatriement {i}:")
                print(rapatriement.model_dump_json(indent=4))
                print("✅ Décodage réussi !")
        else:
            print("❌ Aucun rapatriement trouvé")

    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()

    return rapatriements


# def exemple_comparaison_csv_xlsx(csv_file: Path, xlsx_file: Path) -> Tuple[List[Rappatriement], List[Rappatriement]]:
#     """
#     Exemple de comparaison entre CSV et XLSX
#     """
#     print("\n🔄 Exemple : Comparaison CSV vs XLSX")
#     print("-" * 50)

#     csv_rapatriements = []
#     xlsx_rapatriements = []


#     csv_rapatriements = CSVRappatriementsDecoder().decode_file(csv_file)
#     xlsx_rapatriements = XLSXRappatriementsDecoder().decode_file(xlsx_file)

#     print(f"✅ {len(csv_rapatriements)} rapatriements décodés avec CSV")
#     print(f"✅ {len(xlsx_rapatriements)} rapatriements décodés avec XLSX")
#     print("-" * 50)


#     rapatriement_diffs: Dict[str, List[Dict[str, any]]] = {}

#     for csv_rap, xlsx_rap in zip(csv_rapatriements, xlsx_rapatriements):
#         diffs = compare_models(csv_rap, xlsx_rap)
#         if diffs:
#             rapatriement_diffs[csv_rap.numero_transfert] = diffs

#         if rapatriement_diffs:
#             print(f"❌ {len(rapatriement_diffs)} rapatriements avec des différences")
#             print("-" * 50)
#             for rapatriement_num, diffs in rapatriement_diffs.items():
#                 print(f"Rapatriement: {rapatriement_num}")
#                 for diff in diffs:
#                     print(f"  {diff['key']}: {diff['value1']} -> {diff['value2']}")
#                 print("-" * 50)
#         else:
#             print("✅ Aucune différence trouvée")


#     return csv_rapatriements, xlsx_rapatriements



def main():
    """
    Fonction principale qui lance tous les exemples
    """
    print("🚀 Exemples d'utilisation du décodeur de rapatriements")
    print("=" * 60)
    print(f"🏠 Racine du projet : {paths.project_root}")
    print(f"📁 Répertoire inputs : {paths.inputs}")
    print(f"📤 Répertoire outputs : {paths.outputs}")
    print()

    csv_file = get_input_file("rappatriements_exmc.csv", "2025-07-09/csv/rappatriements")
    xlsx_file = get_input_file("rappatriements_exmc.xlsx", "2025-07-09")

    # Exécuter tous les exemples

    exemple_simple(XLSXRappatriementsDecoder(), xlsx_file)

    # csv_rapatriements, xlsx_rapatriements = exemple_comparaison_csv_xlsx(csv_file, xlsx_file)


    print("\n✅ Tous les exemples terminés!")


if __name__ == "__main__":
    rapatriements = main()
    print(rapatriements)
