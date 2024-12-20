import sys
import xml.etree.ElementTree as ET

def evaluate_postfix(expr_tokens, constants):
    stack = []
    for token in expr_tokens:
        token = token.strip()
        if token == '':
            continue
        if token.lstrip('-').isdigit():
            # Число
            stack.append(int(token))
        elif token in constants:
            # Константа
            stack.append(constants[token])
        elif token == '+':
            if len(stack) < 2:
                raise ValueError("Недостаточно операндов для операции +")
            b = stack.pop()
            a = stack.pop()
            stack.append(a+b)
        elif token == '-':
            if len(stack) < 2:
                raise ValueError("Недостаточно операндов для операции -")
            b = stack.pop()
            a = stack.pop()
            stack.append(a-b)
        elif token == 'abs':
            if len(stack) < 1:
                raise ValueError("Недостаточно операндов для abs")
            a = stack.pop()
            stack.append(abs(a))
        else:
            raise ValueError(f"Неизвестный токен в выражении: {token}")
    if len(stack) != 1:
        raise ValueError("Выражение не свелось к одному значению")
    return stack[0]

def process_node(node, constants):
    tag = node.tag
    if tag == 'const':
        name = node.attrib.get('name')
        if name is None:
            raise ValueError("Константа без имени")
        expr = node.find('expr')
        if expr is not None:
            expr_content = expr.text.strip()
            if expr_content.startswith('|') and expr_content.endswith('|'):
                expr_content = expr_content[1:-1].strip()
            tokens = expr_content.split()
            val = evaluate_postfix(tokens, constants)
            constants[name] = val
            return f"const {name} = {val}"
        else:
            val = node.text.strip()
            # Попытаемся привести к числу
            if val.lstrip('-').isdigit():
                val = int(val)
            constants[name] = val
            return f"const {name} = {val}"

    elif tag == 'array':
        elements = []
        for child in node.findall('value'):
            val = process_node(child, constants)
            elements.append(val)
        # Формат массива: '( elem elem ... )
        return "'( " + " ".join(str(v) for v in elements) + " )"

    elif tag == 'value':
        # MODIFIED: теперь проверяем наличие array, string, expr или просто текст
        arr_child = node.find('array')
        if arr_child is not None:
            # Вложенный массив
            return process_node(arr_child, constants)

        str_child = node.find('string')
        if str_child is not None:
            text = str_child.text
            return f"[[{text}]]"

        expr_child = node.find('expr')
        if expr_child is not None:
            expr_content = expr_child.text.strip()
            if expr_content.startswith('|') and expr_content.endswith('|'):
                expr_content = expr_content[1:-1].strip()
            tokens = expr_content.split()
            val = evaluate_postfix(tokens, constants)
            return str(val)

        # Если нет дочерних узлов, это просто значение (число или строка)
        val = node.text.strip()
        if val.lstrip('-').isdigit():
            return val
        else:
            # Если это не число, считаем строкой
            return f"[[{val}]]"

    elif tag == 'string':
        text = node.text
        return f"[[{text}]]"

    elif tag == 'comment':
        ctype = node.attrib.get('type')
        text = node.text.strip()
        if ctype == 'line':
            return f"# {text}"
        elif ctype == 'multi':
            return f"=begin\n{text}\n=cut"
        else:
            raise ValueError("Неизвестный тип комментария")

    else:
        raise ValueError(f"Неизвестный тег: {tag}")

def main():
    if len(sys.argv) < 2:
        print("Использование: script.py path_to_xml")
        sys.exit(1)
    xml_path = sys.argv[1]

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Ошибка при чтении XML: {e}")
        sys.exit(1)

    constants = {}
    output_lines = []
    for child in root:
        try:
            line = process_node(child, constants)
            output_lines.append(line)
        except ValueError as e:
            print(f"Ошибка: {e}", file=sys.stderr)
            sys.exit(1)

    for line in output_lines:
        print(line)

if __name__ == "__main__":
    main()
