#!/usr/bin/env python3
"""
Module pour analyser récursivement les dossiers contenant des fichiers Java.
Il utilise le module parser local pour extraire les déclarations de chaque fichier.
"""
import sys
import os
from pathlib import Path
from collections import Counter

# importation du parser existant avec un alias pour éviter
# les conflits avec le module standard 'parser' (W4901)
try:
    sys.path.insert(0, str(Path(__file__).parent))
    import parser as code_parser
except ImportError:
    print("pas de module")
    sys.exit(1)


def trouver_fichiers_java(dossier: str) -> list[str]:
    """
    Trouve récursivement tous les fichiers Java dans un dossier.

    Args:
        dossier: Le chemin du dossier à explorer.

    Returns:
        Une liste de chemins vers les fichiers .java trouvés.
    """
    dossier_path = Path(dossier)
    if not dossier_path.exists():
        print(f"le dossier '{dossier}' n'existe pas.")
        sys.exit(1)

    if not dossier_path.is_dir():
        print(f" '{dossier}' n'est pas un dossier.")
        sys.exit(1)

    fichiers_java = []
    for fichier in dossier_path.rglob("*.java"):
        if not any(part.startswith('.') for part in fichier.parts):
            fichiers_java.append(str(fichier))

    return fichiers_java


def get_folder_stats(dossier: str, fichiers: list[str]) -> tuple[list[dict], list[str]]:
    """
    Analyse les fichiers donnés et retourne les statistiques.

    Args:
        dossier: Le dossier racine (pour information).
        fichiers: Liste des fichiers à analyser.

    Returns:
        Un tuple contenant (resultats_fichiers, noms_globaux_liste).
    """
    noms_globaux_liste = []
    resultats_fichiers = []

    for fichier in sorted(fichiers):
        try:
            resultat = code_parser.analyze_file_for_test(fichier)
            resultats_fichiers.append({
                'fichier': fichier,
                'data': resultat
            })

            # ajouter tous les noms de ce fichier à la liste globale
            noms_globaux_liste.extend(resultat['names_list'])

        except Exception as e:
            # On propage l'exception si on veut la gérer plus haut, ou on l'ignore
            # Ici, l'ancien code imprimait l'erreur si return_data=False, ou raise si True.
            # Pour simplifier, on stocke l'erreur dans les résultats ou on log.
            # Si on veut maintenir le comportement exact :
            raise e

    return resultats_fichiers, noms_globaux_liste


def analyser_dossier(dossier, return_data=False):
    """
    Analyse tous les fichiers Java d'un dossier.

    Args:
        dossier: Le chemin du dossier à analyser.
        return_data: Si True, retourne un dictionnaire de résultats.
                     Sinon, affiche les résultats sur la sortie standard.

    Returns:
        Un dictionnaire de résultats si return_data est True, sinon None.
    """
    if not return_data:
        print(f"analyse du dossier: {dossier}")

    fichiers = trouver_fichiers_java(dossier)

    if not fichiers:
        if return_data:
            return None
        print("aucun fichier trouvé.")
        return None

    if not return_data:
        print(f"{len(fichiers)} fichiers trouvés.\n")

    # Logique d'analyse
    noms_globaux_liste = []
    resultats_fichiers = []

    # On réimplémente la boucle ici pour gérer l'affichage progressif si return_data=False
    # afin de conserver le comportement original de print("Analyse: ...")
    for fichier in sorted(fichiers):
        try:
            if not return_data:
                print(f"Analyse: {os.path.basename(fichier)}")

            resultat = code_parser.analyze_file_for_test(fichier)
            resultats_fichiers.append({
                'fichier': fichier,
                'data': resultat
            })

            noms_globaux_liste.extend(resultat['names_list'])

            if not return_data:
                declarations = resultat['total']
                uniques = resultat['unique']
                print(f"  -> {declarations} declarations ({uniques} uniques)")

        except Exception as e:  # pylint: disable=broad-exception-caught
            if return_data:
                raise e
            print(f"  -> Erreur: {e}")

    # Compter les occurrences globales à partir de la liste
    compteur_global = Counter(noms_globaux_liste)
    noms_tries = sorted(compteur_global.items(), key=lambda x: x[1], reverse=True)

    if return_data:
        return {
            'dossier': dossier,
            'fichiers': fichiers,
            'resultats_fichiers': resultats_fichiers,
            'noms_liste': noms_globaux_liste,
            'compteur_global': dict(compteur_global),
            'noms_tries': noms_tries,
            'total': len(noms_globaux_liste),
            'uniques': len(compteur_global)
        }

    # Affichage normal
    print("\nOCCURRENCES GLOBALES (tous fichiers):")
    for nom, compte in noms_tries:
        print(f"{nom:<30} -> {compte}")

    print(f"\nTotal: {len(noms_globaux_liste)} declarations")
    print(f"Termes uniques: {len(compteur_global)}")
    return None


def main():
    """Fonction principale."""
    if len(sys.argv) < 2:
        print("manque un dossier")
        sys.exit(1)

    dossier = sys.argv[1]

    # mettre en silencieux
    if len(sys.argv) > 2 and sys.argv[2] == '--silent':
        resultat = analyser_dossier(dossier, return_data=True)
        if resultat:
            print(f"{resultat['total']} déclarations dans {len(resultat['fichiers'])} fichiers")
    else:
        analyser_dossier(dossier)


if __name__ == '__main__':
    main()