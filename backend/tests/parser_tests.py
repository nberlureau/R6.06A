
import unittest
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from io import StringIO

# Add parent directory to path to allow importing parser
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import parser

class TestParser(unittest.TestCase):
    
    def setUp(self):
        # Create a dummy java file for testing
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
        with open(self.java_file_path, "w") as f:
            f.write(self.java_content)
            
        self.txt_file_path = Path(self.test_dir.name) / "wrong.txt"
        with open(self.txt_file_path, "w") as f:
            f.write("text")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_01_extract_name(self):
        # Test class_declaration
        mock_node = MagicMock()
        mock_node.type = 'class_declaration'
        mock_name_node = MagicMock()
        mock_name_node.text = b'MyClass'
        mock_node.child_by_field_name.return_value = mock_name_node
        self.assertEqual(parser.extract_name(mock_node), 'MyClass')

        # Test variable_declarator
        mock_node.type = 'variable_declarator'
        mock_node.child_by_field_name.return_value = mock_name_node
        self.assertEqual(parser.extract_name(mock_node), 'MyClass')
        
        # Test formal_parameter
        mock_node.type = 'formal_parameter'
        mock_node.child_by_field_name.return_value = mock_name_node
        self.assertEqual(parser.extract_name(mock_node), 'MyClass')
        
        # Test unknown type
        mock_node.type = 'unknown'
        self.assertIsNone(parser.extract_name(mock_node))
        
        # Test None name
        mock_node.type = 'class_declaration'
        mock_node.child_by_field_name.return_value = None
        self.assertIsNone(parser.extract_name(mock_node))

    def test_02_traverse(self):
        # Create a simple tree: Root -> [Class -> [Method]]
        root = MagicMock()
        root.type = 'program'
        root.children = []
        
        cls_node = MagicMock()
        cls_node.type = 'class_declaration'
        cls_name = MagicMock()
        cls_name.text = b'TestClass'
        cls_node.child_by_field_name.return_value = cls_name
        cls_node.children = []
        
        root.children.append(cls_node)
        
        names = []
        parser.traverse(root, names)
        # Should contain 'TestClass'
        self.assertIn('TestClass', names)

    def test_03_parse_file_success(self):
        tree, root = parser.parse_file(self.java_file_path)
        self.assertIsNotNone(tree)
        self.assertIsNotNone(root)

    def test_04_parse_file_invalid_extension(self):
        with self.assertRaises(ValueError):
            parser.parse_file(self.txt_file_path)

    def test_05_analyze_file_return_data(self):
        data = parser.analyze_file(self.java_file_path, return_data=True)
        self.assertEqual(data['lang'], 'java')
        self.assertGreater(len(data['names_list']), 0)
        self.assertGreater(data['total'], 0)
        self.assertGreater(data['unique'], 0)

    def test_06_analyze_file_print(self):
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            parser.analyze_file(self.java_file_path, return_data=False)
            output = out.getvalue()
            self.assertIn("Langage détecté: JAVA", output)
            self.assertIn("Test", output) # Class name
        finally:
            sys.stdout = saved_stdout

    def test_07_analyze_file_exception_exit(self):
        # Suppress stderr to keep test output clean
        with patch('sys.stderr', new=StringIO()):
            with self.assertRaises(SystemExit) as cm:
                parser.analyze_file("non_existent_file.java", return_data=False)
            self.assertEqual(cm.exception.code, 1)

    def test_08_analyze_file_exception_raise(self):
        with self.assertRaises(FileNotFoundError):
             parser.analyze_file("non_existent_file.java", return_data=True)

    def test_09_analyze_file_for_test(self):
        result = parser.analyze_file_for_test(self.java_file_path)
        self.assertTrue(isinstance(result, dict))
        self.assertEqual(result['lang'], 'java')

if __name__ == '__main__':
    unittest.main()
