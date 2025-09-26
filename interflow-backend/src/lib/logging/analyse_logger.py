"""
Logger pour capturer et sauvegarder les logs d'analyse
"""
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Optional


class AnalyseLogger:
    """
    Classe pour capturer l'output et l'écrire dans un fichier de log
    """
    
    def __init__(self, log_file_path: Path):
        """
        Initialise le logger
        
        Args:
            log_file_path: Chemin vers le fichier de log
        """
        self.log_file_path = log_file_path
        self.log_buffer = StringIO()
        self.original_stdout = sys.stdout
    
    def __enter__(self):
        """Début du contexte de logging"""
        sys.stdout = self
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fin du contexte de logging"""
        sys.stdout = self.original_stdout
        self.flush()
    
    def write(self, text: str):
        """Capture l'output et l'écrit dans le buffer"""
        self.original_stdout.write(text)
        self.log_buffer.write(text)
    
    def flush(self):
        """Écrit le contenu du buffer dans le fichier de log"""
        try:
            # Créer le répertoire logs s'il n'existe pas
            log_dir = self.log_file_path.parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Écrire dans le fichier de log
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                f.write(f"=== LOG D'ANALYSE DE COUVERTURE DES BESOINS ===\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Fichier: {self.log_file_path}\n")
                f.write("=" * 80 + "\n\n")
                f.write(self.log_buffer.getvalue())
            
            print(f"\n📝 Log sauvegardé dans: {self.log_file_path}")
            
        except Exception as e:
            print(f"\n⚠️  Erreur lors de l'écriture du log: {e}")
    
    def fileno(self):
        """Nécessaire pour la compatibilité avec sys.stdout"""
        return self.original_stdout.fileno()
    
    def get_log_content(self) -> str:
        """Retourne le contenu du buffer de log"""
        return self.log_buffer.getvalue()
    
    def clear_buffer(self):
        """Vide le buffer de log"""
        self.log_buffer = StringIO() 