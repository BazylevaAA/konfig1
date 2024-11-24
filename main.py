import os
import tarfile
import datetime
import toml
import tkinter as tk
from tkinter import scrolledtext
from commands import ls, cd, uniq, date, exit_command


def pack_virtual_fs(folder_name="my_virtual_fs", archive_name="filesystem.tar"):
    """
    Упаковывает папку в tar-архив.

    :param folder_name: Название папки, которую нужно упаковать.
    :param archive_name: Название создаваемого архива.
    """
    if os.path.exists(folder_name):
        with tarfile.open(archive_name, "w") as tar:
            tar.add(folder_name, arcname=".")
        print(f"Папка '{folder_name}' упакована в архив '{archive_name}'.")
    else:
        print(f"Ошибка: Папка '{folder_name}' не существует.")

class Emulator:
    def __init__(self, config_path: str, root):
        """
        Инициализация эмулятора с поддержкой GUI.

        :param config_path: Путь к конфигурационному файлу TOML.
        :param root: Основное окно tkinter.
        """
        # Загрузка конфигурации
        config = self.load_config(config_path)
        self.user_name = config['user_name']
        self.filesystem_tar = config['filesystem_tar']
        self.startup_script = config['startup_script']

        pack_virtual_fs()
        # Текущая директория в виртуальной файловой системе
        self.current_directory = ""

        # GUI элементы
        self.text_output = scrolledtext.ScrolledText(root, width=80, height=20)
        self.text_output.grid(row=0, column=0, padx=10, pady=10)
        self.text_output.insert(tk.END, f"Welcome to {self.user_name}'s shell!\n")
        self.text_output.insert(tk.END, f"Current directory: {self.current_directory}\n")
        self.text_output.insert(tk.END, "Type a command...\n")

        self.command_entry = tk.Entry(root, width=80)
        self.command_entry.grid(row=1, column=0, padx=10, pady=10)
        self.command_entry.bind("<Return>", self.on_command_enter)

        self.is_running = True

        # Выполнение стартового скрипта
        self.run_startup_script()

    def load_config(self, config_path: str) -> dict:
        """Загрузка конфигурации из TOML файла."""
        with open(config_path, 'r') as f:
            return toml.load(f)

    def execute_command(self, command: str) -> str:
        """Выполнение команды в эмуляторе."""
        pack_virtual_fs()  # Обновляем архив перед выполнением команды
        command = command.strip()
        parts = command.split()

        if not parts:
            return "No command provided."

        if parts[0] == "ls":
            return ls(self.current_directory, self.filesystem_tar)

        elif parts[0] == "cd":
            return self.cd(parts)

        elif parts[0] == "date":
            return self.date()

        elif parts[0] == "exit":
            # Вызываем exit_command из commands.py
            exit_command(is_gui_running=True, root=self.text_output.master)

        elif parts[0] == "uniq":
            return self.uniq(parts)

        else:
            return f"Unknown command: {command}"

    def ls(self, parts):
        """Команда ls для отображения содержимого каталога."""
        if len(parts) < 2:
            return "Directory path is empty."

        directory_path = parts[1]

        # Проверяем, что путь не пустой
        if not directory_path:
            return "Directory path is empty."

        # Проверяем существование директории
        if not os.path.isdir(directory_path):
            return f"Directory '{directory_path}' not found."

        # Выводим содержимое директории
        try:
            files = os.listdir(directory_path)
            return "\n".join(files) if files else "Directory is empty."
        except FileNotFoundError:
            return f"Directory '{directory_path}' not found."
        except PermissionError:
            return f"Permission denied for directory '{directory_path}'."

    def cd(self, parts: list) -> str:
        """Команда 'cd' - изменяет текущую директорию."""
        if len(parts) < 2 or parts[1] == "":
            return "Error: Directory path is empty."

        target_dir = parts[1]
        # Используем функцию cd из commands.py для изменения директории
        new_directory = cd(self.current_directory, target_dir, self.filesystem_tar)

        if new_directory == self.current_directory:
            return f"Error: Directory '{target_dir}' not found."

        self.current_directory = new_directory
        return f"Changed directory to {self.current_directory}"

    def uniq(self, parts: list) -> str:
        """Команда 'uniq' - выводит уникальные строки из файла."""
        if len(parts) < 2:
            return "No file specified for uniq."
        file_path = parts[1]  # Имя файла из команды
        return uniq(file_path, self.filesystem_tar)  # Передача пути к архиву

    def date(self) -> str:
        """Команда 'date' - выводит текущую дату и время."""
        return date()


    def _is_directory(self, path: str) -> bool:
        # Проверка, является ли путь директорией
        return path in self.directories  # Здесь self.directories - это список директорий

    def _list_directory(self, path: str) -> list:
        # Возвращаем список файлов в директории
        if path in self.directories:
            return self.directories[path]  # Возвращаем список файлов в директории
        return []

