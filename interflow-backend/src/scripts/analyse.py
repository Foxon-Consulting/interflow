"""
Script pour analyser la couverture des besoins
"""
from datetime import datetime, timedelta
from typing import Optional
import logging

from services.analyse_service import AnalyseService
from services.analyse_display_service import AnalyseDisplayService
from repositories.storage_strategies import JSONStorageStrategy
from repositories import (
    BesoinsRepository,
    StocksRepository,
    ReceptionsRepository,
    RappatriementsRepository
)
from lib.logging.analyse_logger import AnalyseLogger
from lib.paths import OUTPUTS_DIR


def _analyse(**kwargs):

    # Validation et conversion de la date
    try:
        date_initiale = datetime.strptime(kwargs["date"], "%Y-%m-%d")
    except ValueError as e:
        logging.error(f"Format de date invalide: {kwargs['date']}. Format attendu: YYYY-MM-DD")
        raise ValueError(f"Format de date invalide: {kwargs['date']}. Format attendu: YYYY-MM-DD") from e

    # Validation de l'horizon
    try:
        horizon_days = int(kwargs["horizon"])
        if horizon_days <= 0:
            raise ValueError("L'horizon doit être un nombre positif")
    except (ValueError, TypeError) as e:
        logging.error(f"Horizon invalide: {kwargs['horizon']}. Doit être un nombre entier positif")
        raise ValueError(f"Horizon invalide: {kwargs['horizon']}. Doit être un nombre entier positif") from e

    print("📊 Utilisation des données existantes en mémoire")

    # Définir le chemin du fichier de log
    if kwargs["code_mp"]:
        log_file_path = OUTPUTS_DIR / "logs" / date_initiale.strftime("%Y-%m-%d") / f"analyse_{kwargs['code_mp']}.log"
    else:
        log_file_path = OUTPUTS_DIR / "logs" / date_initiale.strftime("%Y-%m-%d") / "analyse.log"

    with AnalyseLogger(log_file_path):
        # Utiliser le logger pour capturer tout l'output
        # Créer les services directement
        storage_strategy = JSONStorageStrategy()
        analyse_service = AnalyseService(
            besoins_repo=BesoinsRepository(storage_strategy),
            stocks_repo=StocksRepository(storage_strategy),
            receptions_repo=ReceptionsRepository(storage_strategy),
            rappatriements_repo=RappatriementsRepository(storage_strategy)
        )

        # Effectuer l'analyse et l'afficher
        if kwargs["code_mp"]:
            analyse = analyse_service.analyze_matiere_coverage(
                code_mp=kwargs["code_mp"],
                date_initiale=date_initiale,
                horizon_days=horizon_days
            )
        else:
            analyse = analyse_service.analyze_coverage(
                date_initiale=date_initiale,
                horizon_days=horizon_days
            )

        # Afficher les résultats
        AnalyseDisplayService.display_coverage_analysis(analyse)


    # Return arguments
    return {
        "date_initiale": date_initiale.strftime("%Y-%m-%d"),
        "horizon_days": horizon_days,
        "code_mp": kwargs["code_mp"],
        "log_file": str(log_file_path)
    }


def main():
    import argparse

    script_parser = argparse.ArgumentParser(
        prog="analyse",
        description="Script d'analyse de couverture des besoins",
    )

    script_parser.add_argument(
        "-d",
        "--date",
        action="store",
        metavar="date",
        help="Date initiale au format YYYY-MM-DD (défaut: aujourd'hui)",
        required=False,
        default=datetime.now().strftime("%Y-%m-%d"),
    )

    script_parser.add_argument(
        "--horizon",
        action="store",
        metavar="horizon",
        help="Horizon d'analyse en jours (défaut: 5)",
        required=False,
        default=5,
        type=int,
    )



    script_parser.add_argument(
        "--code-mp",
        action="store",
        metavar="code_mp",
        help="Code de matière première pour filtrer l'analyse (ex: 380700)",
        required=False,
        default=None,
    )

    result = _analyse(**vars(script_parser.parse_args()))

    logging.debug(result)


if __name__ == "__main__":
    main()
