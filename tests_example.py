import unittest
import xml.etree.ElementTree as ET
from main import evaluate_postfix, process_node

class TestConverter(unittest.TestCase):
    def test_evaluate_postfix_simple(self):
        constants = {}
        self.assertEqual(evaluate_postfix(["2"], constants), 2)
        self.assertEqual(evaluate_postfix(["-5", "abs"], constants), 5)
        self.assertEqual(evaluate_postfix(["2", "3", "+"], constants), 5)
        self.assertEqual(evaluate_postfix(["5", "3", "-"], constants), 2)

    def test_evaluate_postfix_with_constants(self):
        constants = {"x": 10, "y": -5}
        # Изменяем ожидаемое значение на 5, поскольку 10 + (-5) = 5, abs(5) = 5
        self.assertEqual(evaluate_postfix(["x", "y", "+", "abs"], constants), 5)
        self.assertEqual(evaluate_postfix(["x", "1", "+"], constants), 11)

    def test_evaluate_postfix_errors(self):
        constants = {}
        # Неизвестный токен
        with self.assertRaises(ValueError):
            evaluate_postfix(["x"], constants)
        # Недостаточно операндов для операции
        with self.assertRaises(ValueError):
            evaluate_postfix(["2", "+"], constants)
        # Несводимое выражение (пустое)
        with self.assertRaises(ValueError):
            evaluate_postfix([], constants)

    def test_process_node_const_number(self):
        # <const name="size">42</const>
        xml_str = '<const name="size">42</const>'
        node = ET.fromstring(xml_str)
        constants = {}
        result = process_node(node, constants)
        self.assertEqual(result, "const size = 42")
        self.assertEqual(constants["size"], 42)

    def test_process_node_const_expr(self):
        # <const name="offset"><expr>|size 1 +|</expr></const>
        # При этом size уже известен: size = 42
        xml_str = '<const name="offset"><expr>|size 1 +|</expr></const>'
        node = ET.fromstring(xml_str)
        constants = {"size": 42}
        result = process_node(node, constants)
        self.assertEqual(result, "const offset = 43")
        self.assertEqual(constants["offset"], 43)

    def test_process_node_string(self):
        # <value><string>Это строка</string></value>
        xml_str = '<value><string>Это строка</string></value>'
        node = ET.fromstring(xml_str)
        constants = {}
        result = process_node(node, constants)
        self.assertEqual(result, "[[Это строка]]")

    def test_process_node_array(self):
        # <array><value>1</value><value>2</value></array>
        xml_str = '''
        <array>
            <value>1</value>
            <value>2</value>
        </array>
        '''
        node = ET.fromstring(xml_str)
        constants = {}
        result = process_node(node, constants)
        self.assertEqual(result, "'( 1 2 )")

    def test_process_node_nested_array(self):
        # <array><value>2</value><value><array><value>1</value><value>2</value></array></value><value>6</value></array>
        xml_str = '''
        <array>
          <value>2</value>
          <value>
            <array>
              <value>1</value>
              <value>2</value>
            </array>
          </value>
          <value>6</value>
        </array>
        '''
        node = ET.fromstring(xml_str)
        constants = {}
        result = process_node(node, constants)
        # Ожидаем: '( 2 '( 1 2 ) 6 )
        self.assertEqual(result, "'( 2 '( 1 2 ) 6 )")

    def test_process_node_comment_line(self):
        # <comment type="line">Однострочный</comment>
        xml_str = '<comment type="line">Однострочный комментарий</comment>'
        node = ET.fromstring(xml_str)
        constants = {}
        result = process_node(node, constants)
        self.assertEqual(result, "# Однострочный комментарий")

    def test_process_node_comment_multi(self):
        # <comment type="multi">Многострочный\nкомментарий</comment>
        xml_str = '<comment type="multi">Многострочный\nкомментарий</comment>'
        node = ET.fromstring(xml_str)
        constants = {}
        result = process_node(node, constants)
        self.assertEqual(result, "=begin\nМногострочный\nкомментарий\n=cut")

    def test_process_node_unknown_tag(self):
        xml_str = '<unknown>test</unknown>'
        node = ET.fromstring(xml_str)
        constants = {}
        with self.assertRaises(ValueError):
            process_node(node, constants)

    def test_process_node_const_no_name(self):
        xml_str = '<const>42</const>'
        node = ET.fromstring(xml_str)
        constants = {}
        with self.assertRaises(ValueError):
            process_node(node, constants)

    def test_process_node_const_expr_unknown_token(self):
        # <const name="test"><expr>|test q +|</expr></const>
        # q - неизвестный токен
        xml_str = '<const name="test"><expr>|test q +|</expr></const>'
        node = ET.fromstring(xml_str)
        constants = {"test": 10}
        with self.assertRaises(ValueError):
            process_node(node, constants)


if __name__ == '__main__':
    unittest.main()
