from pathlib import Path
import os

def validate_path(path_input: str | Path) -> Path:
    """
    Valide et sécurise un chemin de fichier fourni par l'utilisateur.
    
    Vérifie que :
    1. Le chemin n'est pas vide.
    2. Le fichier existe.
    3. Le chemin est résolu en chemin absolu (pour éviter les attaques par traversée relative).
    
    Args:
        path_input (str | Path): Le chemin du fichier à valider.
        
    Returns:
        Path: Un objet Path absolu et validé.
        
    Raises:
        ValueError: Si le chemin est vide ou invalide.
        FileNotFoundError: Si le fichier n'existe pas.
    """
    if not path_input:
        raise ValueError("Le chemin du fichier ne peut pas être vide.")
    
    if isinstance(path_input, str):
        if not path_input.strip():
             raise ValueError("Le chemin du fichier ne peut pas être vide.")
        path_input = Path(path_input)

    # Conversion en objet Path
    try:
        path = path_input.resolve()
    except Exception as e:
        raise ValueError(f"Chemin invalide: {e}")

    # Vérification de l'existence
    if not path.exists():
        raise FileNotFoundError(f"Le fichier ou dossier n'existe pas: {path}")

    return path
