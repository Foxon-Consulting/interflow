"""
Module repositories - Gestion des données avec pattern Repository et Strategy
"""

from .besoins_repository import BesoinsRepository
from .receptions_repository import ReceptionsRepository
from .stocks_repository import StocksRepository
from .matieres_premieres_repository import MatieresPremieresRepository
from .rappatriements_repository import RappatriementsRepository
from .storage_strategies import JSONStorageStrategy, CSVStorageStrategy, SQLiteStorageStrategy, S3StorageStrategy

__all__ = [
    'BesoinsRepository',
    'ReceptionsRepository',
    'StocksRepository',
    'MatieresPremieresRepository',
    'RappatriementsRepository',
    'JSONStorageStrategy',
    'CSVStorageStrategy',
    'SQLiteStorageStrategy',
    'S3StorageStrategy',
]
