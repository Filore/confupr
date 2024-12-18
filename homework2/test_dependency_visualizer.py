import unittest
from unittest import mock
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import os
import dependency_visualizer
import tarfile


class TestDependencyVisualizer(unittest.TestCase):

    @patch('dependency_visualizer.requests.get')
    def test_download_apkindex(self, mock_get):
        # Настройка мок-ответа для requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Создание тестового tar.gz файла с APKINDEX
        with tempfile.TemporaryDirectory() as temp_dir:
            apkindex_content = "P:packageA\nD:packageB packageC\n"
            with tempfile.NamedTemporaryFile('w', delete=False) as tmp_apkindex:
                tmp_apkindex.write(apkindex_content)
                tmp_apkindex_path = tmp_apkindex.name
            with tarfile.open(tmp_apkindex_path + '.tar.gz', 'w:gz') as tar:
                tar.add(tmp_apkindex_path, arcname='APKINDEX')
            with open(tmp_apkindex_path + '.tar.gz', 'rb') as f:
                content = f.read()
            # Чтение содержимого заранее
            mock_response.iter_content = lambda chunk_size: iter([content])
            mock_get.return_value = mock_response

            # Вызов тестируемой функции
            repo_url = "https://dl-cdn.alpinelinux.org/alpine/latest-stable/main"
            apkindex_path = dependency_visualizer.download_apkindex(repo_url, temp_dir)

            # Проверка, что файл APKINDEX был извлечен и переименован
            expected_path = os.path.join(temp_dir, 'APKINDEX-main')
            self.assertTrue(os.path.exists(expected_path))
            with open(expected_path, 'r') as f:
                content_read = f.read()
            self.assertEqual(content_read, apkindex_content)

            # Очистка временных файлов
            os.remove(tmp_apkindex_path)
            os.remove(tmp_apkindex_path + '.tar.gz')

    @patch('builtins.open', new_callable=mock_open, read_data=(
            "P:packageA\n"
            "S:1.0\n"
            "D:packageB packageC\n\n"
            "P:packageB\n"
            "S:2.0\n"
            "D:packageC\n\n"
            "P:packageC\n"
            "S:3.0\n\n"
            "P:packageD\n"
            "S:1.2\n"
            "D:\n\n"
    ))
    @patch('dependency_visualizer.os.path.exists', return_value=True)
    def test_parse_apkindex(self, mock_exists, mock_file):
        # Вызов функции parse_apkindex
        packages_db = dependency_visualizer.parse_apkindex('dummy_path')
        expected = {
            'packageA': ['packageB', 'packageC'],
            'packageB': ['packageC'],
            'packageC': [],
            'packageD': []
        }
        self.assertEqual(packages_db, expected)

    @patch('builtins.open', new_callable=mock_open, read_data=(
            "P:packageA\n"
            "S:1.0\n"
            "D:packageB packageC\n\n"
            "P:packageB\n"
            "S:2.0\n"
            "D:packageC\n\n"
            "P:packageC\n"
            "S:3.0\n\n"
            "P:packageD\n"
            "S:1.2\n"
            "D:\n\n"
    ))
    @patch('dependency_visualizer.os.path.exists', return_value=True)
    def test_parse_apkindex_with_no_dependencies(self, mock_exists, mock_file):
        # Вызов функции parse_apkindex
        packages_db = dependency_visualizer.parse_apkindex('dummy_path')
        expected = {
            'packageA': ['packageB', 'packageC'],
            'packageB': ['packageC'],
            'packageC': [],
            'packageD': []
        }
        self.assertEqual(packages_db, expected)

    def test_build_dependency_graph(self):
        packages_db = {
            'packageA': ['packageB', 'packageC'],
            'packageB': ['packageC', 'packageD'],
            'packageC': [],
            'packageD': ['packageE'],
            'packageE': []
        }
        dependency_graph = dependency_visualizer.build_dependency_graph('packageA', packages_db)
        expected = {
            'packageA': ['packageB', 'packageC'],
            'packageB': ['packageC', 'packageD'],
            'packageC': [],
            'packageD': ['packageE'],
            'packageE': []
        }
        self.assertEqual(dependency_graph, expected)

    def test_build_dependency_graph_with_cycle(self):
        # Тестирование с циклическими зависимостями
        packages_db = {
            'packageA': ['packageB'],
            'packageB': ['packageC'],
            'packageC': ['packageA']  # Цикл A -> B -> C -> A
        }
        dependency_graph = dependency_visualizer.build_dependency_graph('packageA', packages_db)
        expected = {
            'packageA': ['packageB'],
            'packageB': ['packageC'],
            'packageC': ['packageA']
        }
        self.assertEqual(dependency_graph, expected)

    def test_generate_graphviz(self):
        dependency_graph = {
            'packageA': ['packageB', 'packageC'],
            'packageB': ['packageC'],
            'packageC': []
        }
        dot_code = dependency_visualizer.generate_graphviz(dependency_graph)
        expected = (
            "digraph G {\n"
            "    node [shape=box];\n"
            '    "packageA" -> "packageB";\n'
            '    "packageA" -> "packageC";\n'
            '    "packageB" -> "packageC";\n'
            "}"
        )
        self.assertEqual(dot_code, expected)

    @patch('dependency_visualizer.subprocess.run')
    @patch('dependency_visualizer.os.path.exists', return_value=True)
    @patch('dependency_visualizer.os.remove')
    def test_generate_image(self, mock_remove, mock_exists, mock_run):
        # Настройка мока subprocess.run
        mock_run.return_value = MagicMock(returncode=0)
        # Настройка мока os.path.exists
        mock_exists.return_value = True
        # Настройка мока tempfile.NamedTemporaryFile
        with patch('dependency_visualizer.tempfile.NamedTemporaryFile') as mock_tmp:
            mock_tmp_instance = MagicMock()
            mock_tmp_instance.name = 'temp.dot'
            mock_tmp.return_value.__enter__.return_value = mock_tmp_instance

            dot_code = 'digraph G { "A" -> "B"; }'
            graphviz_path = 'dot.exe'
            output_image_path = 'output.png'

            dependency_visualizer.generate_image(dot_code, graphviz_path, output_image_path)

            # Проверка, что tempfile.NamedTemporaryFile был вызван
            mock_tmp.assert_called_with('w', delete=False, suffix='.dot')

            # Проверка, что subprocess.run был вызван с правильными аргументами
            mock_run.assert_called_with(
                [graphviz_path, '-Tpng', 'temp.dot', '-o', output_image_path],
                check=True,
                stdout=unittest.mock.ANY,  # stdout=subprocess.PIPE
                stderr=unittest.mock.ANY  # stderr=subprocess.PIPE
            )

            # Проверка, что os.remove был вызван с правильным аргументом
            mock_remove.assert_called_with('temp.dot')

    @patch('dependency_visualizer.subprocess.run')
    def test_display_image_posix(self, mock_run):
        # Тестирование функции display_image на POSIX
        with patch('dependency_visualizer.sys.platform', 'linux'), \
                patch('dependency_visualizer.os.name', 'posix'), \
                patch('dependency_visualizer.subprocess.run') as mock_subproc_run:
            dependency_visualizer.display_image('output.png')
            mock_subproc_run.assert_called_with(['xdg-open', 'output.png'])

    @patch('dependency_visualizer.print')
    def test_display_image_unknown_os(self, mock_print):
        # Тестирование функции display_image на неизвестной ОС
        with patch('dependency_visualizer.sys.platform', 'unknown'), \
                patch('dependency_visualizer.os.name', 'unknown'):
            dependency_visualizer.display_image('output.png')
            mock_print.assert_called_with(
                'Невозможно автоматически открыть изображение. Оно сохранено по пути: output.png'
            )

    @patch('dependency_visualizer.requests.get')
    def test_download_apkindex_failure(self, mock_get):
        # Имитация неудачной загрузки
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_url = "https://dl-cdn.alpinelinux.org/alpine/latest-stable/main"
            with self.assertRaises(ConnectionError) as context:
                dependency_visualizer.download_apkindex(repo_url, temp_dir)
            self.assertIn("Не удалось скачать APKINDEX из", str(context.exception))

    @patch('dependency_visualizer.requests.get')
    def test_download_apkindex_invalid_tar(self, mock_get):
        # Имитация загрузки некорректного tar.gz
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content = lambda chunk_size: iter([b'not a tar.gz file'])
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_url = "https://dl-cdn.alpinelinux.org/alpine/latest-stable/main"
            with self.assertRaises(RuntimeError) as context:
                dependency_visualizer.download_apkindex(repo_url, temp_dir)
            self.assertIn("Ошибка при распаковке", str(context.exception))

    def test_parse_apkindex_file_not_found(self):
        with self.assertRaises(FileNotFoundError) as context:
            dependency_visualizer.parse_apkindex('nonexistent_file')
        self.assertIn("Файл APKINDEX не найден", str(context.exception))

    @patch('dependency_visualizer.requests.get')
    def test_download_apkindex_missing_file(self, mock_get):
        # Имитация архива без APKINDEX файла
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Создание тестового tar.gz без APKINDEX
        with tempfile.TemporaryDirectory() as temp_dir:
            with tempfile.NamedTemporaryFile('w', delete=False) as tmp_file:
                tmp_file.write("Some other file")
                tmp_file_path = tmp_file.name
            with tarfile.open(tmp_file_path + '.tar.gz', 'w:gz') as tar:
                tar.add(tmp_file_path, arcname='OTHERFILE')
            with open(tmp_file_path + '.tar.gz', 'rb') as f:
                content = f.read()
            # Чтение содержимого заранее
            mock_response.iter_content = lambda chunk_size: iter([content])
            mock_get.return_value = mock_response

            repo_url = "https://dl-cdn.alpinelinux.org/alpine/latest-stable/main"
            with self.assertRaises(FileNotFoundError) as context:
                dependency_visualizer.download_apkindex(repo_url, temp_dir)
            self.assertIn("Файл APKINDEX не найден", str(context.exception))

            # Очистка временных файлов
            os.remove(tmp_file_path)
            os.remove(tmp_file_path + '.tar.gz')

    @patch('builtins.open', new_callable=mock_open, read_data=(
            "P:packageA\n"
            "S:1.0\n"
            "D:\n\n"
            "P:packageB\n"
            "S:2.0\n\n"
    ))
    @patch('dependency_visualizer.os.path.exists', return_value=True)
    def test_parse_apkindex_with_no_dependencies(self, mock_exists, mock_file):
        # Вызов функции parse_apkindex
        packages_db = dependency_visualizer.parse_apkindex('dummy_path')
        expected = {
            'packageA': [],
            'packageB': []
        }
        self.assertEqual(packages_db, expected)

    def test_generate_graphviz_empty(self):
        dependency_graph = {}
        dot_code = dependency_visualizer.generate_graphviz(dependency_graph)
        expected = (
            "digraph G {\n"
            "    node [shape=box];\n"
            "}"
        )
        self.assertEqual(dot_code, expected)

    def test_build_dependency_graph_nonexistent_package(self):
        packages_db = {
            'packageA': ['packageB'],
            'packageB': []
        }
        with self.assertRaises(ValueError) as context:
            dependency_visualizer.build_dependency_graph('packageC', packages_db)
        self.assertIn("Пакет 'packageC' не найден в APKINDEX.", str(context.exception))


if __name__ == '__main__':
    unittest.main()
