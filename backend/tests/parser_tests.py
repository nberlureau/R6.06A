"""
Unit tests for the backend/parser.py module.
"""
import unittest
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from io import StringIO

# Add parent directory to path to allow importing parser
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# pylint: disable=wrong-import-position, deprecated-module
import parser as code_parser


class TestParser(unittest.TestCase):
    """
    Test suite for the Parser module.
    """

    def setUp(self):
        """
        Set up a temporary directory with a dummy Java file and a text file.
        """
        # Create a dummy java file for testing
        # pylint: disable=consider-using-with
        self.test_dir = tempfile.TemporaryDirectory()
        self.java_file_path = Path(self.test_dir.name) / "Test.java"
        self.java_content = """
        public class Test {
            private int x;
            public void myMethod(int param) {
                int y = 0;
            }
        }
        """
        with open(self.java_file_path, "w", encoding="utf-8") as f:
            f.write(self.java_content)

        self.txt_file_path = Path(self.test_dir.name) / "wrong.txt"
        with open(self.txt_file_path, "w", encoding="utf-8") as f:
            f.write("text")

    def tearDown(self):
        """
        Clean up the temporary directory.
        """
        self.test_dir.cleanup()

    def test_01_extract_name(self):
        """
        Test the extract_name function for different node types.
        """
        # Test class_declaration
        mock_node = MagicMock()
        mock_node.type = 'class_declaration'
        mock_name_node = MagicMock()
        mock_name_node.text = b'MyClass'
        # Configure child_by_field_name to return mock_name_node when called with 'name'
        mock_node.child_by_field_name.side_effect = \
            lambda name: mock_name_node if name == 'name' else None

        self.assertEqual(code_parser.extract_name(mock_node), 'MyClass')

        # Test variable_declarator
        mock_node.type = 'variable_declarator'
        self.assertEqual(code_parser.extract_name(mock_node), 'MyClass')

        # Test formal_parameter
        mock_node.type = 'formal_parameter'
        self.assertEqual(code_parser.extract_name(mock_node), 'MyClass')

        # Test unknown type
        mock_node.type = 'unknown'
        self.assertIsNone(code_parser.extract_name(mock_node))

        # Test None name
        mock_node.type = 'class_declaration'
        mock_node.child_by_field_name.side_effect = lambda name: None
        self.assertIsNone(code_parser.extract_name(mock_node))

    def test_02_traverse(self):
        """
        Test the traverse function.
        """
        # Create a simple tree: Root -> [Class -> [Method]]
        root = MagicMock()
        root.type = 'program'
        root.children = []

        cls_node = MagicMock()
        cls_node.type = 'class_declaration'
        cls_name = MagicMock()
        cls_name.text = b'TestClass'
        cls_node.child_by_field_name.side_effect = \
            lambda name: cls_name if name == 'name' else None
        cls_node.children = []

        root.children.append(cls_node)

        names = []
        code_parser.traverse(root, names)
        # Should contain 'TestClass'
        self.assertIn('TestClass', names)

    def test_03_parse_file_success(self):
        """
        Test that finding imports works.
        """
        tree, root = code_parser.parse_file(self.java_file_path)
        self.assertIsNotNone(tree)
        self.assertIsNotNone(root)

    def test_04_parse_file_invalid_extension(self):
        """
        Test that ValueError is raised for non-java files.
        """
        with self.assertRaises(ValueError):
            code_parser.parse_file(self.txt_file_path)

    def test_05_analyze_file_return_data(self):
        """
        Test analyze_file with return_data=True.
        """
        data = code_parser.analyze_file(self.java_file_path, return_data=True)
        self.assertEqual(data['lang'], 'java')
        self.assertGreater(len(data['names_list']), 0)
        self.assertGreater(data['total'], 0)
        self.assertGreater(data['unique'], 0)

    def test_06_analyze_file_print(self):
        """
        Test analyze_file with return_data=False (printing).
        """
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            code_parser.analyze_file(self.java_file_path, return_data=False)
            output = out.getvalue()
            # Note: "Langage détecté: JAVA" string was modified in refactor
            self.assertIn("Langage détecté: JAVA", output)
            self.assertIn("Test", output)  # Class name
        finally:
            sys.stdout = saved_stdout

    def test_07_analyze_file_exception_exit(self):
        """
        Test that analyze_file exits on error when return_data=False.
        """
        # Suppress stderr to keep test output clean
        with patch('sys.stderr', new=StringIO()):
            with self.assertRaises(SystemExit) as cm:
                code_parser.analyze_file("non_existent_file.java", return_data=False)
            self.assertEqual(cm.exception.code, 1)

    def test_08_analyze_file_exception_raise(self):
        """
        Test that analyze_file raises exception when return_data=True.
        """
        with self.assertRaises(FileNotFoundError):
            code_parser.analyze_file("non_existent_file.java", return_data=True)

    def test_09_analyze_file_for_test(self):
        """
        Test wrapper function.
        """
        result = code_parser.analyze_file_for_test(self.java_file_path)
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(result['lang'], 'java')


if __name__ == '__main__':
    unittest.main()
