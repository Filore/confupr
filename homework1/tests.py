import unittest
from unittest.mock import patch
import tarfile
import tempfile
import os
from io import BytesIO

from shell_emulator import CommandProcessor

class MockShell:
    def __init__(self, tar_path):
        self.current_directory = "/"
        self.displayed_output = []
        self.filesystem_path = tar_path
        self.tar = tarfile.open(self.filesystem_path, 'r')

    def display_output(self, text):
        self.displayed_output.append(text)

    def load_filesystem(self):
        self.tar.close()
        self.tar = tarfile.open(self.filesystem_path, 'r')

    def close_filesystem(self):
        if self.tar:
            self.tar.close()

    def close(self):
        self.displayed_output.append("Shell closed.")

class TestCommandProcessor(unittest.TestCase):
    def setUp(self):
        # Создаем временный tarfile для тестирования
        self.temp_tar = tempfile.NamedTemporaryFile(delete=False)
        with tarfile.open(self.temp_tar.name, "w") as tar:
            # Добавляем несколько файлов и директорий
            tarinfo = tarfile.TarInfo(name="file1.txt")
            tarinfo.size = len(b"Hello World\n")
            tar.addfile(tarinfo, BytesIO(b"Hello World\n"))

            tarinfo = tarfile.TarInfo(name="dir1/")
            tarinfo.type = tarfile.DIRTYPE
            tar.addfile(tarinfo)

            tarinfo = tarfile.TarInfo(name="dir1/file2.txt")
            tarinfo.size = len(b"Another file\n")
            tar.addfile(tarinfo, BytesIO(b"Another file\n"))

            tarinfo = tarfile.TarInfo(name="script.sh")
            tarinfo.size = len(b"echo Start\n")
            tar.addfile(tarinfo, BytesIO(b"echo Start\n"))

        self.mock_shell = MockShell(self.temp_tar.name)
        self.command_processor = CommandProcessor()

    def tearDown(self):
        self.mock_shell.close_filesystem()
        os.unlink(self.temp_tar.name)

    # Тесты для команды ls
    def test_ls_root_directory(self):
        self.command_processor.ls(self.mock_shell)
        self.assertEqual(len(self.mock_shell.displayed_output), 1)
        output = self.mock_shell.displayed_output[0]
        self.assertIn("file1.txt", output)
        self.assertIn("dir1", output)
        self.assertIn("script.sh", output)

    def test_ls_empty_directory(self):
        # Создаем пустую директорию
        with tarfile.open(self.temp_tar.name, "a") as tar:
            tarinfo = tarfile.TarInfo(name="empty_dir/")
            tarinfo.type = tarfile.DIRTYPE
            tar.addfile(tarinfo)

        self.mock_shell.current_directory = "/empty_dir/"
        self.command_processor.ls(self.mock_shell)
        self.assertIn("No files or directories in the current directory.", self.mock_shell.displayed_output)

    def test_ls_subdirectory(self):
        self.mock_shell.current_directory = "/dir1/"
        self.command_processor.ls(self.mock_shell)
        self.assertIn("file2.txt", self.mock_shell.displayed_output)

    # Тесты для команды cd
    def test_cd_into_existing_directory(self):
        self.command_processor.cd(self.mock_shell, ["dir1"])
        self.assertEqual(self.mock_shell.current_directory, "/dir1/")
        self.assertIn("Current directory: /dir1/", self.mock_shell.displayed_output)

    def test_cd_into_nonexistent_directory(self):
        self.command_processor.cd(self.mock_shell, ["nonexistent"])
        self.assertIn("Directory 'nonexistent' not found.", self.mock_shell.displayed_output)

    def test_cd_to_parent_directory(self):
        # Сначала переходим в поддиректорию
        self.command_processor.cd(self.mock_shell, ["dir1"])
        # Теперь возвращаемся в корень
        self.command_processor.cd(self.mock_shell, [".."])
        self.assertEqual(self.mock_shell.current_directory, "/")
        self.assertIn("Current directory: /", self.mock_shell.displayed_output)

    # Тесты для команды whoami
    @patch('shell_emulator.os.getlogin', return_value='testuser')
    def test_whoami_normal(self, mock_getlogin):
        self.command_processor.whoami(self.mock_shell)
        self.assertIn("testuser", self.mock_shell.displayed_output)

    @patch('shell_emulator.os.getlogin', side_effect=OSError("Cannot determine user"))
    def test_whoami_no_user(self, mock_getlogin):
        self.command_processor.whoami(self.mock_shell)
        self.assertIn("Error executing command 'whoami': Cannot determine user", self.mock_shell.displayed_output)

    # Тесты для команды tac
    def test_tac_existing_file(self):
        self.command_processor.tac(self.mock_shell, ["file1.txt"])
        # Проверяем, что строки выведены в обратном порядке
        # "Hello World\n" -> ["Hello World"]
        # Reversed: ["Hello World"]
        self.assertIn("Hello World", self.mock_shell.displayed_output)

    def test_tac_nonexistent_file(self):
        self.command_processor.tac(self.mock_shell, ["nofile.txt"])
        self.assertIn("File 'nofile.txt' not found.", self.mock_shell.displayed_output)

    def test_tac_empty_file(self):
        # Добавляем пустой файл
        with tarfile.open(self.temp_tar.name, "a") as tar:
            tarinfo = tarfile.TarInfo(name="empty.txt")
            tarinfo.size = 0
            tar.addfile(tarinfo, BytesIO(b""))

        # Обновляем файловую систему в MockShell, чтобы увидеть добавленный файл
        self.mock_shell.load_filesystem()

        # Проверяем начальное состояние
        initial_output_length = len(self.mock_shell.displayed_output)

        # Выполняем команду tac для пустого файла
        self.command_processor.tac(self.mock_shell, ["empty.txt"])

        # Для отладки: выводим содержимое displayed_output после выполнения tac
        print("Displayed Output After tac:", self.mock_shell.displayed_output)

        # Проверяем, что ничего не добавилось
        self.assertEqual(len(self.mock_shell.displayed_output), initial_output_length)

    # Тесты для команды touch
    def test_touch_new_file(self):
        self.command_processor.touch(self.mock_shell, ["newfile.txt"])
        self.assertIn("File 'newfile.txt' created successfully.", self.mock_shell.displayed_output)
        # Проверяем, что файл появился в tar
        with tarfile.open(self.temp_tar.name, "r") as tar:
            self.assertIn("newfile.txt", tar.getnames())

    def test_touch_existing_file(self):
        self.command_processor.touch(self.mock_shell, ["file1.txt"])
        self.assertIn("File 'file1.txt' already exists.", self.mock_shell.displayed_output)

    def test_touch_no_filename(self):
        self.command_processor.touch(self.mock_shell, [])
        self.assertIn("No file name specified.", self.mock_shell.displayed_output)

    # Тесты для команды exit
    def test_exit_command(self):
        self.command_processor.execute("exit", self.mock_shell)
        self.assertIn("Exiting emulator...", self.mock_shell.displayed_output)
        self.assertIn("Shell closed.", self.mock_shell.displayed_output)

    def test_exit_command_multiple_times(self):
        self.command_processor.execute("exit", self.mock_shell)
        self.command_processor.execute("exit", self.mock_shell)
        # Должно быть два вызова: два сообщения "Exiting emulator..." и два "Shell closed."
        self.assertEqual(self.mock_shell.displayed_output.count("Exiting emulator..."), 2)
        self.assertEqual(self.mock_shell.displayed_output.count("Shell closed."), 2)

    def test_exit_command_with_arguments(self):
        self.command_processor.execute("exit now", self.mock_shell)
        # Команда 'exit now' всё ещё должна закрывать оболочку
        self.assertIn("Exiting emulator...", self.mock_shell.displayed_output)
        self.assertIn("Shell closed.", self.mock_shell.displayed_output)

if __name__ == '__main__':
    unittest.main()
