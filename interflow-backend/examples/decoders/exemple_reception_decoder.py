"""
Exemple d'utilisation du décodeur de réceptions
"""
from pathlib import Path
from datetime import datetime


from lib.paths import paths, get_input_file
from lib.decoders.receptions.csv import CSVReceptionsDecoder
from lib.decoders.receptions.xlsx import XLSXReceptionsDecoder
from models.reception import Reception
from pathlib import Path
from typing import List, Tuple, Dict
import sys
import io
from lib.utils import compare_models
from lib.decoders.decoder import Decoder

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def exemple_simple(decoder: Decoder[Reception], file_path: Path) -> List[Reception]:
    """
    Exemple simple d'utilisation d'un decoder
    """
    print(f"🔍 Exemple simple d'utilisation du decoder {decoder.__class__.__name__}")
    print(f"Fichier : {file_path}")
    print("-" * 50)
    
    receptions = []
    
    if not file_path.exists():
        print(f"❌ Fichier introuvable : {file_path}")
        return receptions
    
    try:
        receptions = decoder.decode_file(file_path)
        
        if receptions:
            print(f"Réceptions trouvées : {len(receptions)}")
            
            for i, reception in enumerate(receptions[:5], 1):
                print(f"\nRéception {i}:")
                print(reception)
                print("✅ Décodage réussi !")
        else:
            print("❌ Aucune réception trouvée")
            
    except Exception as e:
        print(f"❌ Erreur : {e}")

    return receptions


def exemple_comparaison_csv_xlsx(csv_file: Path, xlsx_file: Path) -> Tuple[List[Reception], List[Reception]]:
    """
    Exemple de comparaison entre CSV et XLSX
    """
    print("\n🔄 Exemple : Comparaison CSV vs XLSX")
    print("-" * 50)
    
    csv_receptions = []
    xlsx_receptions = []
    
    try:
        csv_decoder = CSVReceptionsDecoder()
        csv_receptions = csv_decoder.decode_file(csv_file)
        print(f"✅ {len(csv_receptions)} réceptions décodées avec CSV")
    except Exception as e:
        print(f"❌ Erreur avec CSV: {e}")
    
    try:
        xlsx_decoder = XLSXReceptionsDecoder()
        xlsx_receptions = xlsx_decoder.decode_file(str(xlsx_file))
        print(f"✅ {len(xlsx_receptions)} réceptions décodées avec XLSX")
    except Exception as e:
        print(f"❌ Erreur avec XLSX: {e}")
    
    print("-" * 50)

    if csv_receptions and xlsx_receptions:
        reception_diffs: Dict[str, List[Dict[str, Reception]]] = {}

        # Comparer les réceptions par ordre (si disponible)
        csv_by_ordre = {rec.ordre: rec for rec in csv_receptions if rec.ordre}
        xlsx_by_ordre = {rec.ordre: rec for rec in xlsx_receptions if rec.ordre}
        
        # Comparer les réceptions qui ont le même ordre
        for ordre in set(csv_by_ordre.keys()) & set(xlsx_by_ordre.keys()):
            csv_rec = csv_by_ordre[ordre]
            xlsx_rec = xlsx_by_ordre[ordre]
            diffs = compare_models(csv_rec, xlsx_rec)
            if diffs:
                reception_diffs[ordre] = diffs

        if reception_diffs:
            print(f"❌ {len(reception_diffs)} réceptions avec des différences")
            print("-" * 50)
            for ordre, diffs in reception_diffs.items():
                print(f"Réception: {ordre}")
                for diff in diffs:
                    print(f"  {diff['key']}: {diff['value1']} -> {diff['value2']}")
                print("-" * 50)
        else:
            print("✅ Aucune différence trouvée")
    else:
        print("⚠️  Impossible de comparer - un des fichiers n'a pas pu être décodé")

    return csv_receptions, xlsx_receptions


def exemple_statistiques(receptions: List[Reception]) -> None:
    """
    Exemple d'analyse statistique des réceptions
    """
    print("\n📊 Exemple : Statistiques des réceptions")
    print("-" * 50)
    
    if not receptions:
        print("❌ Aucune réception à analyser")
        return
    
    # Statistiques par fournisseur
    fournisseurs = {}
    for rec in receptions:
        fournisseur = rec.fournisseur or "Inconnu"
        if fournisseur not in fournisseurs:
            fournisseurs[fournisseur] = {"count": 0, "total_quantite": 0.0}
        fournisseurs[fournisseur]["count"] += 1
        fournisseurs[fournisseur]["total_quantite"] += rec.quantite
    
    print(f"📈 Statistiques par fournisseur ({len(fournisseurs)} fournisseurs):")
    for fournisseur, stats in sorted(fournisseurs.items(), key=lambda x: x[1]["count"], reverse=True)[:5]:
        print(f"   {fournisseur}: {stats['count']} réceptions, {stats['total_quantite']:.1f} total")
    
    # Statistiques par type de réception
    types_reception = {}
    for rec in receptions:
        type_reception = rec.type.value if rec.type else "Inconnu"
        if type_reception not in types_reception:
            types_reception[type_reception] = 0
        types_reception[type_reception] += 1
    
    print(f"\n📋 Répartition par type de réception:")
    for type_rec, count in sorted(types_reception.items(), key=lambda x: x[1], reverse=True):
        print(f"   {type_rec}: {count} réceptions")
    
    # Statistiques par statut
    statuts = {}
    for rec in receptions:
        statut = rec.etat.value if rec.etat else "Inconnu"
        if statut not in statuts:
            statuts[statut] = 0
        statuts[statut] += 1
    
    print(f"\n📊 Répartition par statut:")
    for statut, count in sorted(statuts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {statut}: {count} réceptions")


def main():
    """
    Fonction principale qui lance tous les exemples
    """
    print("🚀 Exemples d'utilisation du décodeur de réceptions")
    print("=" * 60)
    print(f"🏠 Racine du projet : {paths.project_root}")
    print(f"📁 Répertoire inputs : {paths.inputs}")
    print(f"📤 Répertoire outputs : {paths.outputs}")
    print()
    
    # Chercher les fichiers de réceptions
    csv_file = get_input_file("receptions.csv", "2025-07-10/csv")
    xlsx_file = get_input_file("receptions.xlsx", "2025-07-10")

    # Exécuter tous les exemples
    
    # exemple_simple(XLSXReceptionsDecoder(), xlsx_file)
    
    # exemple_simple(CSVReceptionsDecoder(), csv_file)

    csv_receptions, xlsx_receptions = exemple_comparaison_csv_xlsx(csv_file, xlsx_file)
    
    # Afficher les statistiques sur les réceptions CSV si disponibles
    if csv_receptions:
        exemple_statistiques(csv_receptions)
        
    print("\n✅ Tous les exemples terminés!")


if __name__ == "__main__":
    main()
