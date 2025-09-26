"""
Module centralisé pour la gestion des chemins du projet
"""
from pathlib import Path
import os
from typing import Optional

class ProjectPaths:
    """
    Classe singleton pour gérer tous les chemins du projet de façon centralisée
    """
    _instance = None
    _project_root: Optional[Path] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProjectPaths, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._project_root is None:
            self._project_root = self._find_project_root()
            self._setup_paths()

    def _find_project_root(self) -> Path:
        """
        Trouve la racine du projet de façon robuste
        """
        # Méthode 1: Chercher depuis le répertoire courant
        current = Path.cwd()
        while current != current.parent:
            if (current / "pyproject.toml").exists() or (current / "README.md").exists():
                return current
            current = current.parent

        # Méthode 2: Chercher depuis le fichier __file__ (si disponible)
        try:
            # Chercher dans la pile d'appels pour trouver un fichier du projet
            import inspect
            frame = inspect.currentframe()
            while frame:
                filename = frame.f_code.co_filename
                if "interflow-backend" in filename:
                    file_path = Path(filename)
                    # Remonter jusqu'à la racine du projet
                    current = file_path.parent
                    while current != current.parent:
                        if (current / "pyproject.toml").exists():
                            return current
                        current = current.parent
                frame = frame.f_back
        except:
            pass

        # Méthode 3: Fallback - utiliser le répertoire courant
        return Path.cwd()

    def _setup_paths(self):
        """Configure tous les chemins du projet"""
        self.project_root = self._project_root

        # Répertoires principaux
        self.src = self.project_root / "src"
        self.data = self.project_root / "data"
        self.refs = self.project_root / "refs"
        self.outputs = self.project_root / "outputs"
        self.inputs = self.project_root / "inputs"
        self.tests = self.project_root / "tests"
        self.docs = self.project_root / "docs"

        # Répertoires de données spécifiques
        self.data_repositories = self.data / "repositories"
        self.data_temp = self.data / "temp"

        # Répertoires de tests
        self.tests_temp = self.tests / "temp"
        self.tests_data = self.tests / "data"

        # Répertoires de sortie
        self.outputs_reports = self.outputs / "reports"
        self.outputs_logs = self.outputs / "logs"

        # Créer les répertoires s'ils n'existent pas
        self._ensure_directories()

    def _ensure_directories(self):
        """Crée les répertoires nécessaires s'ils n'existent pas"""
        directories = [
            self.data,
            self.data_repositories,
            self.data_temp,
            self.outputs,
            self.outputs_reports,
            self.outputs_logs,
            self.tests_temp,
            self.tests_data
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_repository_file(self, model_name: str) -> Path:
        """
        Retourne le chemin du fichier JSON pour un repository

        Args:
            model_name: Nom du modèle (ex: 'matiere', 'besoin', etc.)

        Returns:
            Path: Chemin vers le fichier JSON du repository
        """
        return self.data_repositories / f"{model_name.lower()}.json"

    def get_reference_file(self, filename: str, subdir: str = "") -> Path:
        """
        Retourne le chemin d'un fichier de référence

        Args:
            filename: Nom du fichier (ex: 'matieres.json')
            subdir: Sous-répertoire optionnel

        Returns:
            Path: Chemin vers le fichier de référence
        """
        if subdir:
            return self.refs / subdir / filename
        return self.refs / filename

    def get_input_file(self, filename: str, subdir: str = "") -> Path:
        """
        Retourne le chemin d'un fichier d'entrée

        Args:
            filename: Nom du fichier (ex: 'besoins.csv')
            subdir: Sous-répertoire optionnel

        Returns:
            Path: Chemin vers le fichier d'entrée
        """
        if subdir:
            return self.inputs / subdir / filename
        return self.inputs / filename

    def get_output_file(self, filename: str, subdir: str = "") -> Path:
        """
        Retourne le chemin d'un fichier de sortie

        Args:
            filename: Nom du fichier
            subdir: Sous-répertoire optionnel

        Returns:
            Path: Chemin vers le fichier de sortie
        """
        if subdir:
            return self.outputs / subdir / filename
        return self.outputs / filename

    def get_test_file(self, filename: str, subdir: str = "") -> Path:
        """
        Retourne le chemin d'un fichier de test

        Args:
            filename: Nom du fichier
            subdir: Sous-répertoire optionnel

        Returns:
            Path: Chemin vers le fichier de test
        """
        if subdir:
            return self.tests_data / subdir / filename
        return self.tests_data / filename

    def relative_to_project(self, path: Path) -> str:
        """
        Retourne le chemin relatif par rapport à la racine du projet

        Args:
            path: Chemin absolu

        Returns:
            str: Chemin relatif
        """
        try:
            return str(path.relative_to(self.project_root))
        except ValueError:
            return str(path)

    def __str__(self) -> str:
        return f"ProjectPaths(root={self.project_root})"

    def __repr__(self) -> str:
        return self.__str__()


# Instance globale
paths = ProjectPaths()

# Exports pour compatibilité
PROJECT_ROOT = paths.project_root
SRC_DIR = paths.src
DATA_DIR = paths.data
REFS_DIR = paths.refs
OUTPUTS_DIR = paths.outputs
INPUTS_DIR = paths.inputs
TESTS_DIR = paths.tests
DOCS_DIR = paths.docs

# Fonctions utilitaires
def get_repository_file(model_name: str) -> Path:
    """Raccourci pour obtenir le fichier d'un repository"""
    return paths.get_repository_file(model_name)

def get_reference_file(filename: str, subdir: str = "") -> Path:
    """Raccourci pour obtenir un fichier de référence"""
    return paths.get_reference_file(filename, subdir)

def get_input_file(filename: str, subdir: str = "") -> Path:
    """Raccourci pour obtenir un fichier d'entrée"""
    return paths.get_input_file(filename, subdir)

def get_output_file(filename: str, subdir: str = "") -> Path:
    """Raccourci pour obtenir un fichier de sortie"""
    return paths.get_output_file(filename, subdir)

def get_test_file(filename: str, subdir: str = "") -> Path:
    """Raccourci pour obtenir un fichier de test"""
    return paths.get_test_file(filename, subdir)
