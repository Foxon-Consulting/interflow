"""
Repository pour les stocks
"""
from typing import List, Optional
from repositories.base_repository import BaseRepository
from repositories.storage_strategies import StorageStrategy
from models.stock import Stock


class StocksRepository(BaseRepository[Stock]):
    """
    Repository pour les stocks avec méthodes métier spécifiques
    """

    def __init__(self, storage: StorageStrategy):
        super().__init__(Stock, storage, id_field="id")

    def get_stocks_list(self) -> List[Stock]:
        """
        Récupère tous les stocks (en excluant le magasin 30)

        Returns:
            List[Stock]: Une liste de stocks
        """
        stocks = self.get_all()
        return [stock for stock in stocks if stock.magasin != "30"]

    def get_internal_stocks(self) -> List[Stock]:
        """
        Récupère tous les stocks internes (magasins ne commençant pas par "EX" et différents de "30")

        Returns:
            List[Stock]: Liste des stocks internes
        """
        stocks = self.get_stocks_list()
        internal_stocks = [stock for stock in stocks if not stock.magasin.startswith("EX")]
        return internal_stocks

    def get_external_stocks(self) -> List[Stock]:
        """
        Récupère tous les stocks externes (magasins commençant par "EX" et différents de "30")

        Returns:
            List[Stock]: Liste des stocks externes
        """
        stocks = self.get_stocks_list()
        external_stocks = [stock for stock in stocks if stock.magasin.startswith("EX")]
        return external_stocks

    def get_stocks_by_matiere(self, code_mp: str) -> List[Stock]:
        """
        Récupère tous les stocks d'une matière donnée (en excluant le magasin 30)

        Args:
            code_mp: Le code de la matière première

        Returns:
            List[Stock]: Liste des stocks correspondants
        """
        stocks = self.get_all()
        filtered_stocks = [stock for stock in stocks if stock.matiere and stock.matiere.code_mp == code_mp and stock.magasin != "30"]
        return filtered_stocks

    def get_internal_stocks_by_matiere(self, code_mp: str) -> List[Stock]:
        """
        Récupère tous les stocks internes d'une matière donnée (magasins ne commençant pas par "EX" et différents de "30")

        Args:
            code_mp: Le code de la matière première

        Returns:
            List[Stock]: Liste des stocks internes de cette matière
        """
        stocks = self.get_stocks_by_matiere(code_mp)
        internal_stocks = [stock for stock in stocks if not stock.magasin.startswith("EX")]
        return internal_stocks

    def get_external_stocks_by_matiere(self, code_mp: str) -> List[Stock]:
        """
        Récupère tous les stocks externes d'une matière donnée (magasins commençant par "EX" et différents de "30")

        Args:
            code_mp: Le code de la matière première

        Returns:
            List[Stock]: Liste des stocks externes de cette matière
        """
        stocks = self.get_stocks_by_matiere(code_mp)
        external_stocks = [stock for stock in stocks if stock.magasin.startswith("EX")]
        return external_stocks

    def get_stocks_by_magasin(self, magasin: str) -> List[Stock]:
        """
        Récupère tous les stocks d'un magasin donné (en excluant le magasin 30)

        Args:
            magasin: Le nom du magasin

        Returns:
            List[Stock]: Liste des stocks correspondants
        """
        stocks = self.get_all()
        stocks = [stock for stock in stocks if stock.magasin == magasin and stock.magasin != "30"]
        return stocks

    def get_stocks_by_statut(self, statut_lot: str) -> List[Stock]:
        """
        Récupère tous les stocks ayant un statut de lot donné (en excluant le magasin 30)

        Args:
            statut_lot: Le statut du lot (ex: "OK", "EN_ATTENTE", etc.)

        Returns:
            List[Stock]: Liste des stocks correspondants
        """
        stocks = self.get_all()
        stocks = [stock for stock in stocks if stock.statut_lot == statut_lot and stock.magasin != "30"]
        return stocks

    def filter_stocks(self, stocks: List[Stock], **filters) -> List[Stock]:
        """
        Filtre les stocks selon les critères spécifiés.

        Args:
            stocks: Liste des stocks à filtrer
            **filters: Critères de filtrage sous forme de paires clé-valeur
                     (ex: matiere=matiere_obj, statut_lot="OK", etc.)

        Returns:
            List[Stock]: Nouvelle liste contenant uniquement les stocks correspondant aux critères
        """
        filtered_stocks = stocks

        for key, value in filters.items():
            if value is not None:  # On ignore les filtres None
                filtered_stocks = [
                    stock for stock in filtered_stocks
                    if getattr(stock, key) == value
                ]

        return filtered_stocks

    def update_quantity(self, id: str, nouvelle_quantite: float) -> Optional[Stock]:
        """
        Met à jour la quantité d'un stock

        Args:
            id: L'identifiant du stock
            nouvelle_quantite: La nouvelle quantité

        Returns:
            Optional[Stock]: Le stock mis à jour ou None si non trouvé
        """
        stock = self.get_by_id(id)
        if stock:
            stock.quantite = nouvelle_quantite
            return self.update(id, stock)
        return None

    def get_total_quantity_by_matiere(self, code_mp: str) -> float:
        """
        Calcule la quantité totale d'une matière en stock

        Args:
            code_mp: Le code de la matière première

        Returns:
            float: La quantité totale
        """
        stocks = self.get_stocks_by_matiere(code_mp)
        return sum(stock.quantite for stock in stocks)

    def get_total_internal_quantity_by_matiere(self, code_mp: str) -> float:
        """
        Calcule la quantité totale d'une matière en stock interne

        Args:
            code_mp: Le code de la matière première

        Returns:
            float: La quantité totale en stock interne
        """
        stocks = self.get_internal_stocks_by_matiere(code_mp)
        return sum(stock.quantite for stock in stocks)

    def get_total_external_quantity_by_matiere(self, code_mp: str) -> float:
        """
        Calcule la quantité totale d'une matière en stock externe

        Args:
            code_mp: Le code de la matière première

        Returns:
            float: La quantité totale en stock externe
        """
        stocks = self.get_external_stocks_by_matiere(code_mp)
        return sum(stock.quantite for stock in stocks)

    def import_from_file(self, file_path: str) -> None:
        """
        Importe les stocks depuis un fichier CSV ou XLSX

        Args:
            file_path: Chemin vers le fichier des stocks
        """
        if file_path.endswith('.csv'):
            from lib.decoders.stocks.csv import CSVStocksDecoder
            super().import_from_file(file_path, CSVStocksDecoder)
        elif file_path.endswith('.xlsx'):
            from lib.decoders.stocks.xlsx import XLSXStocksDecoder
            super().import_from_file(file_path, XLSXStocksDecoder)
        else:
            raise ValueError("Le fichier doit être un fichier CSV ou XLSX")

    def import_from_csv(self, csv_path: str = "data/stocks.csv") -> None:
        """
        Importe les stocks depuis un fichier CSV (compatibilité)

        Args:
            csv_path: Chemin vers le fichier CSV des stocks
        """
        self.import_from_file(csv_path)

    def filter_stocks_advanced(self,
                              code_mp: Optional[str] = None,
                              nom_matiere: Optional[str] = None,
                              magasin: Optional[str] = None,
                              statut_lot: Optional[str] = None,
                              quantite_min: Optional[float] = None,
                              quantite_max: Optional[float] = None,
                              lot: Optional[str] = None,
                              interne_only: Optional[bool] = None) -> List[Stock]:
        """
        Filtre les stocks selon des critères avancés (en excluant le magasin 30)

        Args:
            code_mp: Code de la matière première
            nom_matiere: Nom de la matière première (recherche partielle)
            magasin: Nom du magasin
            statut_lot: Statut du lot
            quantite_min: Quantité minimale
            quantite_max: Quantité maximale
            lot: Numéro de lot spécifique
            interne_only: True pour stocks internes seulement, False pour externes seulement

        Returns:
            List[Stock]: Liste des stocks filtrés
        """
        stocks = self.get_all()
        # Exclure le magasin 30 de manière systématique
        filtered_stocks = [s for s in stocks if s.magasin != "30"]

        # Filtre par code matière première
        if code_mp is not None:
            filtered_stocks = [s for s in filtered_stocks
                             if s.matiere and s.matiere.code_mp == code_mp]

        # Filtre par nom de matière (recherche partielle)
        if nom_matiere is not None:
            nom_lower = nom_matiere.lower()
            filtered_stocks = [s for s in filtered_stocks
                             if s.matiere and nom_lower in s.matiere.nom.lower()]

        # Filtre par magasin
        if magasin is not None:
            filtered_stocks = [s for s in filtered_stocks if s.magasin == magasin]

        # Filtre par statut de lot
        if statut_lot is not None:
            filtered_stocks = [s for s in filtered_stocks if s.statut_lot == statut_lot]

        # Filtre par quantité
        if quantite_min is not None:
            filtered_stocks = [s for s in filtered_stocks if s.quantite >= quantite_min]

        if quantite_max is not None:
            filtered_stocks = [s for s in filtered_stocks if s.quantite <= quantite_max]

        # Filtre par lot
        if lot is not None:
            filtered_stocks = [s for s in filtered_stocks if s.lot == lot]

        # Filtre par type de stock (interne/externe)
        if interne_only is not None:
            if interne_only:
                filtered_stocks = [s for s in filtered_stocks if not s.magasin.startswith("EX")]
            else:
                filtered_stocks = [s for s in filtered_stocks if s.magasin.startswith("EX")]

        return filtered_stocks

    def get_stocks_critiques(self, seuil_quantite: float = 100.0) -> List[Stock]:
        """
        Récupère les stocks critiques (quantité faible)

        Args:
            seuil_quantite: Seuil de quantité pour considérer un stock comme critique

        Returns:
            List[Stock]: Liste des stocks critiques
        """
        return self.filter_stocks_advanced(quantite_max=seuil_quantite)

    def get_stocks_par_matiere(self, code_mp: str) -> List[Stock]:
        """
        Récupère tous les stocks d'une matière première spécifique

        Args:
            code_mp: Code de la matière première

        Returns:
            List[Stock]: Liste des stocks de la matière
        """
        return self.filter_stocks_advanced(code_mp=code_mp)

    def get_stocks_par_magasin(self, magasin: str) -> List[Stock]:
        """
        Récupère tous les stocks d'un magasin spécifique

        Args:
            magasin: Nom du magasin

        Returns:
            List[Stock]: Liste des stocks du magasin
        """
        return self.filter_stocks_advanced(magasin=magasin)

    def get_stocks_disponibles(self) -> List[Stock]:
        """
        Récupère les stocks disponibles (statut OK)

        Returns:
            List[Stock]: Liste des stocks disponibles
        """
        return self.filter_stocks_advanced(statut_lot="OK")
