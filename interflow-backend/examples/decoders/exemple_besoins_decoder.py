"""
Exemple d'utilisation du décodeur de besoins
"""
from pathlib import Path
from datetime import datetime
import json

from lib.paths import paths, get_input_file
from lib.decoders.besoins.csv import CSVBesoinsDecoder
from lib.decoders.besoins.xlsx import XLSXBesoinsDecoder
from models.besoin import Besoin
from pathlib import Path
from typing import List, Tuple, Dict
import sys
import io
from lib.utils import compare_models
from lib.decoders.decoder import Decoder
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def exemple_simple(decoder: Decoder[Besoin], file_path: Path) -> List[Besoin]:
    """
    Exemple simple d'utilisation d'un decoder
    """
    print(f"🔍 Exemple simple d'utilisation du decoder {decoder.__class__.__name__}")
    print(f"Fichier : {file_path}")
    print("-" * 50)

    if not file_path.exists():
        print(f"❌ Fichier introuvable : {file_path}")
        return

    try:
        besoins = decoder.decode_file(file_path)

        if besoins:
            print(f"Besoins trouvés : {len(besoins)}")

            for i, besoin in enumerate(besoins[:5], 1):
                print(besoin)
                print("✅ Décodage réussi !")
        else:
            print("❌ Aucun besoin trouvé")

    except Exception as e:
        print(f"❌ Erreur : {e}")


    with open(f"besoins_{decoder.__class__.__name__}.json", "w") as f:
        for besoin in besoins:
            f.write(json.dumps(besoin.model_dump(), indent=4, ensure_ascii=False))
            f.write("\n")


    return besoins


def exemple_comparaison_csv_xlsx(csv_file: Path, xlsx_file: Path) -> Tuple[List[Besoin], List[Besoin]]:
    """
    Exemple de comparaison entre CSV et XLSX
    """
    print("\n🔄 Exemple : Comparaison CSV vs XLSX")
    print("-" * 50)

    csv_besoins = CSVBesoinsDecoder().decode_file(csv_file)
    xlsx_besoins = XLSXBesoinsDecoder().decode_file(xlsx_file)

    print(f"✅ {len(csv_besoins)} besoins décodés avec CSV")
    print(f"✅ {len(xlsx_besoins)} besoins décodés avec XLSX")
    print("-" * 50)

    besoin_diffs: Dict[str, List[Dict[str, Besoin]]] = {}


    for csv_besoin, xlsx_besoin in zip(csv_besoins, xlsx_besoins):
        diffs = compare_models(csv_besoin, xlsx_besoin)
        if diffs:
            besoin_diffs[csv_besoin.matiere.code_mp] = diffs

    if besoin_diffs:
        print(f"❌ {len(besoin_diffs)} besoins avec des différences")
        print("-" * 50)
        for besoin_code, diffs in besoin_diffs.items():
            print(f"Besoin: {besoin_code}")
            for diff in diffs:
                print(f"  {diff['key']}: {diff['value1']} -> {diff['value2']}")
                print("-" * 50)
    else:
        print("✅ Aucune différence trouvée")

    return csv_besoins, xlsx_besoins


def main():
    """
    Fonction principale qui lance tous les exemples
    """
    print("🚀 Exemples d'utilisation du décodeur de besoins")
    print("=" * 60)
    print(f"🏠 Racine du projet : {paths.project_root}")
    print(f"📁 Répertoire inputs : {paths.inputs}")
    print(f"📤 Répertoire outputs : {paths.outputs}")
    print()

    csv_file = get_input_file("besoins.csv", "2025-07-10/csv")
    xlsx_file = get_input_file("besoins.xlsx", "2025-07-10")

    # Exécuter tous les exemples

    # exemple_simple(CSVBesoinsDecoder(), csv_file)
    # exemple_simple(XLSXBesoinsDecoder(), xlsx_file)
    exemple_comparaison_csv_xlsx(csv_file, xlsx_file)


    print("\n✅ Tous les exemples terminés!")


if __name__ == "__main__":
    main()
