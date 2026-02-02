"""
Module for parsing Java files using tree-sitter.
Extracts declarations (classes, methods, variables, etc.) and analyzes their frequency.
"""
import sys
from collections import Counter
from security import validate_path

try:
    from tree_sitter import Language, Parser
    import tree_sitter_java as tsjava
except ImportError:
    print("tree sitter introuvable")
    sys.exit(1)


# déclaration des termes
NODE_TYPES = [
    'class_declaration',
    'method_declaration',
    'variable_declarator',
    'formal_parameter',
    'interface_declaration',
    'enum_declaration',
    'field_declaration'
]


def extract_name(node):
    """
    Extrait le nom d'un nœud Java selon son type.
    """
    # Simplification: Tous les cas cherchent le champ 'name'
    if ('declaration' in node.type or
            node.type in ('variable_declarator', 'formal_parameter')):
        name_node = node.child_by_field_name('name')
        return name_node.text.decode('utf8') if name_node else None

    return None


def traverse(node, names_list):
    """
    Parcourt récursivement l'arbre syntaxique et collecte les noms déclarés.
    """
    if node.type in NODE_TYPES:
        name = extract_name(node)
        if name and len(name) > 0:
            names_list.append(name)

    for child in node.children:
        traverse(child, names_list)


def parse_file(filepath):
    """
    Parse un fichier Java et retourne l'arbre syntaxique.
    """
    file_path = validate_path(filepath)

    if file_path.suffix.lower() != '.java':
        raise ValueError(f'Extension de fichier non supportée pour "{filepath}". '
                         f'Seuls les fichiers .java sont acceptés.')

    # Lire fichier
    source_code = file_path.read_bytes()

    parser = Parser()
    java_language = Language(tsjava.language())

    # gestion des versions de tree sitter
    if hasattr(parser, 'set_language'):
        parser.set_language(java_language)
    elif hasattr(parser, 'language'):
        parser.language = java_language
    else:
        parser = Parser(java_language)

    tree = parser.parse(source_code)

    return tree, tree.root_node


def get_file_stats(filepath):
    """
    Analyse un fichier et retourne les statistiques brutes.
    Lève des exceptions en cas d'erreur.
    """
    validated_path = validate_path(filepath)
    _, root_node = parse_file(validated_path)

    names_list = []
    traverse(root_node, names_list)

    # compter les occurrences
    name_counter = Counter(names_list)
    sorted_names = sorted(name_counter.items(), key=lambda x: x[1], reverse=True)

    return {
        'lang': 'java',
        'names_list': names_list,
        'sorted': sorted_names,
        'total': len(names_list),
        'unique': len(name_counter)
    }


def analyze_file(filepath, return_data=False):
    """
    Analyse un fichier Java.
    Affiche les résultats ou retourne un dictionnaire selon return_data.
    """
    try:
        stats = get_file_stats(filepath)

        if return_data:
            return stats

        # Affichage normal
        print(f"\n{filepath}")
        print("Langage détecté: JAVA")
        print(f"\nNoms déclarés ({stats['unique']} uniques):\n")

        for name, count in stats['sorted']:
            plural = 's' if count > 1 else ''
            print(f"{name:<30} → {count} occurrence{plural}")

        print(f"\nTotal: {stats['total']} déclarations\n")
        return None  # Explicite return None for consistency (R1710)

    except Exception as e:  # pylint: disable=broad-exception-caught
        if return_data:
            raise e  # Reraise l'exception pour l'appelant API

        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)


def analyze_file_for_test(filepath):
    """
    Pour les tests ou appels internes : retourne les données.
    """
    return analyze_file(filepath, return_data=True)


def main():
    """Fonction principale."""
    if len(sys.argv) < 2:
        sys.exit(1)

    filepath = sys.argv[1]
    analyze_file(filepath)


if __name__ == '__main__':
    main()