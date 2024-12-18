import os
import sys
import tarfile
from io import BytesIO
import time
import toml
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit

class ShellEmulatorGUI(QWidget):
    def __init__(self, config_path):
        super().__init__()
        self.start_time = time.time()
        self.load_config(config_path)
        self.command_processor = CommandProcessor()
        self.load_filesystem()


        self.init_ui()


        self.execute_start_script()

    def init_ui(self):
        self.setWindowTitle('Shell Emulator')


        self.layout = QVBoxLayout()


        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.layout.addWidget(self.output_area)

        self.command_input = QLineEdit(self)
        self.command_input.setPlaceholderText("Enter command here...")
        self.command_input.returnPressed.connect(self.handle_command)
        self.layout.addWidget(self.command_input)

        self.setLayout(self.layout)

    def handle_command(self):
        command = self.command_input.text().strip()
        if command:
            self.execute_command(command)
            self.command_input.clear()

    def display_output(self, text):
        self.output_area.append(text)

    def load_filesystem(self):
        self.current_directory = "/"
        self.tar = tarfile.open(self.filesystem_path, 'r')

    def load_config(self, config_path):
        try:
            config = toml.load(config_path)
            self.filesystem_path = config['filesystem']['virtual_filesystem_path']
            self.start_script_path = config['filesystem']['start_script_path']
        except Exception as e:
            self.display_output(f"Error loading config: {e}")
            raise

    def close_filesystem(self):
        if self.tar:
            self.tar.close()

    def close_application(self):
        self.display_output("Exiting emulator...")
        self.close_filesystem()
        self.close()

    def execute_command(self, command):
        if command:
            try:
                self.command_processor.execute(command, self)
            except Exception as e:
                self.display_output(f"Error executing command '{command}': {e}")

    def execute_start_script(self):

        if not os.path.exists(self.start_script_path):
            self.display_output(f"Start script not found: {self.start_script_path}")
            return

        try:
            with open(self.start_script_path, 'r') as script_file:
                for line in script_file:
                    command = line.strip()
                    if command:
                        self.display_output(f"Executing start script command: {command}")
                        self.execute_command(command)
        except Exception as e:
            self.display_output(f"Error reading start script: {e}")

class CommandProcessor:
    def __init__(self):
        self.start_time = time.time()

    def execute(self, command, shell):
        cmd_parts = command.split()
        cmd_name = cmd_parts[0]
        args = cmd_parts[1:]

        if cmd_name == "ls":
            self.ls(shell)
        elif cmd_name == "cd":
            self.cd(shell, args)
        elif cmd_name == "whoami":
            self.whoami(shell)
        elif cmd_name == "tac":
            self.tac(shell, args)
        elif cmd_name == "touch":
            self.touch(shell, args)
        elif cmd_name == "exit":
            self.close_application(shell)
        else:
            shell.display_output(f"Command '{cmd_name}' is not supported.")

    def close_application(self, shell):
        shell.display_output("Exiting emulator...")
        shell.close_filesystem()
        shell.close()

    def ls(self, shell):
        current_dir = shell.current_directory.strip('/')
        if not current_dir:
            current_dir = "."
        contents = []
        for member in shell.tar.getmembers():
            member_path = member.name.strip('/')
            if current_dir == "." and '/' not in member_path:
                contents.append(member_path)
            elif member_path.startswith(current_dir + '/'):
                relative_path = member_path[len(current_dir) + 1:]
                if '/' not in relative_path:
                    contents.append(relative_path)

        if contents:
            shell.display_output("\n".join(contents))
        else:
            shell.display_output("No files or directories in the current directory.")

    def cd(self, shell, args):
        if not args:
            shell.display_output("No directory specified.")
            return

        path = args[0]
        if path == "..":
            if shell.current_directory != "/":
                shell.current_directory = os.path.dirname(shell.current_directory.rstrip('/'))
                if not shell.current_directory or shell.current_directory == "":
                    shell.current_directory = "/"
                shell.display_output(f"Current directory: {shell.current_directory}")
            else:
                shell.display_output("You are already at the root directory.")
            return

        if path.startswith('/'):
            path = path[1:]

        new_dir = os.path.join(shell.current_directory, path).strip('/')
        if new_dir and not new_dir.startswith('/'):
            new_dir = "/" + new_dir

        try:
            dir_exists = any(
                member.name.rstrip('/') == new_dir.strip('/')
                for member in shell.tar.getmembers()
                if member.isdir()
            )

            if dir_exists:
                shell.current_directory = new_dir + "/"
                if shell.current_directory == "//":
                    shell.current_directory = "/"
                shell.display_output(f"Current directory: {shell.current_directory}")
            else:
                shell.display_output(f"Directory '{path}' not found.")
        except Exception as e:
            shell.display_output(f"Error accessing archive: {e}")

    def whoami(self, shell):
        try:
            user = os.getlogin()
            shell.display_output(user)
        except Exception as e:
            shell.display_output(f"Error executing command 'whoami': {e}")

    def tac(self, shell, args):
        if not args:
            shell.display_output("No file specified.")
            return

        filename = args[0]
        try:
            file_found = False
            for member in shell.tar.getmembers():
                if filename == os.path.basename(member.name):
                    file_found = True
                    if member.isfile():
                        file_data = shell.tar.extractfile(member).read()
                        try:
                            file_data = file_data.decode('utf-8', errors='ignore')
                        except UnicodeDecodeError:

                            file_data = file_data.decode('ASCII', errors='ignore')
                        lines = file_data.splitlines()
                        if lines:
                            for line in reversed(lines):
                                shell.display_output(line)
                    break

            if not file_found:
                shell.display_output(f"File '{filename}' not found.")
        except Exception as e:
            shell.display_output(f"Error opening archive: {e}")

    def touch(self, shell, args):
        if not args:
            shell.display_output("No file name specified.")
            return

        filename = args[0]
        full_path = os.path.join(shell.current_directory.strip('/'), filename).strip('/')

        try:
            shell.tar.close()
            with tarfile.open(shell.filesystem_path, mode='a') as tar:
                if any(member.name == full_path for member in tar.getmembers()):
                    shell.display_output(f"File '{filename}' already exists.")
                    return
                file_data = BytesIO(b'')
                tar_info = tarfile.TarInfo(name=full_path)
                tar_info.size = 0
                tar_info.mtime = time.time()
                tar.addfile(tarinfo=tar_info, fileobj=file_data)

            shell.load_filesystem()
            shell.display_output(f"File '{filename}' created successfully.")
        except Exception as e:
            shell.display_output(f"Error creating or updating file: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    emulator_gui = ShellEmulatorGUI("/Users/matvej/PycharmProjects/dz1/config.toml")
    emulator_gui.show()
    sys.exit(app.exec_())

