"""
Exemple d'utilisation du décodeur de stocks
"""
from pathlib import Path
from datetime import datetime


from lib.paths import paths, get_input_file
from lib.decoders.stocks.csv import CSVStocksDecoder
from lib.decoders.stocks.xlsx import XLSXStocksDecoder
from models.stock import Stock
from pathlib import Path
from typing import List, Tuple, Dict
import sys
import io
from lib.utils import compare_models
from lib.decoders.decoder import Decoder
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def exemple_simple(decoder: Decoder[Stock], file_path: Path) -> List[Stock]:
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
        stocks = decoder.decode_file(file_path)

        if stocks:
            print(f"Stocks trouvés : {len(stocks)}")

            for i, stock in enumerate(stocks[:5], 1):
                print(stock)
                print("✅ Décodage réussi !")
        else:
            print("❌ Aucun stock trouvé")

    except Exception as e:
        print(f"❌ Erreur : {e}")

    return stocks


def exemple_comparaison_csv_xlsx(csv_file: Path, xlsx_file: Path) -> Tuple[List[Stock], List[Stock]]:
    """
    Exemple de comparaison entre CSV et XLSX
    """
    print("\n🔄 Exemple : Comparaison CSV vs XLSX")
    print("-" * 50)

    csv_stocks = CSVStocksDecoder().decode_file(csv_file)
    xlsx_stocks = XLSXStocksDecoder().decode_file(xlsx_file)

    print(f"✅ {len(csv_stocks)} stocks décodés avec CSV")
    print(f"✅ {len(xlsx_stocks)} stocks décodés avec XLSX")
    print("-" * 50)

    stock_diffs: Dict[str, List[Dict[str, Stock]]] = {}


    for csv_stock, xlsx_stock in zip(csv_stocks, xlsx_stocks):
        diffs = compare_models(csv_stock, xlsx_stock)
        if diffs:
            stock_diffs[csv_stock.matiere.code_mp] = diffs

    if stock_diffs:
        print(f"❌ {len(stock_diffs)} stocks avec des différences")
        print("-" * 50)
        for stock_code, diffs in stock_diffs.items():
            print(f"Stock: {stock_code}")
            for diff in diffs:
                print(f"  {diff['key']}: {diff['value1']} -> {diff['value2']}")
                print("-" * 50)
    else:
        print("✅ Aucune différence trouvée")

    return csv_stocks, xlsx_stocks


def main():
    """
    Fonction principale qui lance tous les exemples
    """
    print("🚀 Exemples d'utilisation du décodeur de stocks")
    print("=" * 60)
    print(f"�� Racine du projet : {paths.project_root}")
    print(f"📁 Répertoire inputs : {paths.inputs}")
    print(f"�� Répertoire outputs : {paths.outputs}")
    print()

    csv_file = get_input_file("stocks.csv", "2025-07-10/csv")
    xlsx_file = get_input_file("stocks.xlsx", "2025-07-10")

    # Exécuter tous les exemples

    # exemple_simple(CSVStocksDecoder(), csv_file)
    # exemple_simple(XLSXStocksDecoder(), xlsx_file)
    exemple_comparaison_csv_xlsx(csv_file, xlsx_file)


    print("\n✅ Tous les exemples terminés!")


if __name__ == "__main__":
    main()
