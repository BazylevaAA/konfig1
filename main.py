import os
import tarfile
import datetime
import toml
import tkinter as tk
from tkinter import scrolledtext
from commands import ls, cd, uniq, date, exit_command


# TODO:
# Убрать ./ в начале всех путей
# uniq работает с относительными путями (учитывает текущую папку)
# Доп после 1 дек: Раскрасить файлы и папки разными цветами (файлы - синие, папки - тёмно-фиолетовые)
def pack_virtual_fs(folder_name="my_virtual_fs", archive_name="filesystem.tar"):
    """ Упаковывает папку в tar-архив. """
    if os.path.exists(folder_name):
        with tarfile.open(archive_name, "w") as tar:
            tar.add(folder_name, arcname=".")
        print(f"Папка '{folder_name}' упакована в архив '{archive_name}'.")
    else:
        print(f"Ошибка: Папка '{folder_name}' не существует.")


class Emulator:
    def __init__(self, config_path: str, root):
        """ Инициализация эмулятора с поддержкой GUI. """
        config = self.load_config(config_path)
        self.user_name = config['user_name']
        self.filesystem_tar = config['filesystem_tar']
        self.startup_script = config['startup_script']

        pack_virtual_fs()
        self.current_directory = ""

        # GUI элементы
        self.text_output = scrolledtext.ScrolledText(root, width=80, height=20)
        self.text_output.grid(row=0, column=0, padx=10, pady=10)
        self.text_output.insert(tk.END, f"Welcome to {self.user_name}'s shell!\n")
        self.text_output.insert(tk.END, f"Current directory: {self.current_directory}\n")
        self.text_output.insert(tk.END, "Type a command...\n")

        # Настройка тегов для цветного выделения файлов и директорий
        self.text_output.tag_configure("directory", foreground="purple")  # Для директорий
        self.text_output.tag_configure("file", foreground="blue")  # Для файлов

        self.command_entry = tk.Entry(root, width=80)
        self.command_entry.grid(row=1, column=0, padx=10, pady=10)
        self.command_entry.bind("<Return>", self.on_command_enter)

        self.is_running = True
        self.run_startup_script()

    def load_config(self, config_path: str) -> dict:
        """ Загрузка конфигурации из TOML файла. """
        with open(config_path, 'r') as f:
            return toml.load(f)

    def execute_command(self, command: str) -> str:
        """ Выполнение команды в эмуляторе. """
        command = command.strip()
        parts = command.split()

        if not parts:
            return "No command provided."

        if parts[0] == "ls":
            return ls(self.current_directory, self.filesystem_tar, self.text_output)
        elif parts[0] == "cd":
            return self.cd(parts)
        elif parts[0] == "date":
            return date()
        elif parts[0] == "exit":
            exit_command(is_gui_running=True, root=self.text_output.master)
        elif parts[0] == "uniq":
            return self.uniq(parts)
        else:
            return f"Unknown command: {command}"

    def ls(self, parts):
        """ Команда ls для отображения содержимого каталога. """
        return ls(self.current_directory, self.filesystem_tar, self.text_output)

    def cd(self, parts: list) -> str:
        """ Команда 'cd' - изменяет текущую директорию. """
        if len(parts) < 2 or parts[1] == "":
            return "Error: Directory path is empty."

        target_dir = parts[1]
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

        # Проверяем текущую директорию и корректно формируем путь
        if self.current_directory:
            # Если текущая директория уже начинается с пути файла, не добавляем её снова
            if not file_path.startswith(self.current_directory):
                file_path = os.path.join(self.current_directory, file_path)

        # Нормализуем путь для Windows (замена слэшей на правильный)
        file_path = os.path.normpath(file_path)

        # Приводим путь к формату с прямым слэшем для архивов
        file_path = file_path.replace(os.sep, '/')

        # Убедимся, что путь начинается с './', так как это путь в архиве
        if not file_path.startswith('./'):
            file_path = './' + file_path.lstrip('./')

        return uniq(file_path, self.filesystem_tar, self.current_directory)

    def date(self) -> str:
        """ Команда 'date' - выводит текущую дату и время. """
        return date()

    def run_startup_script(self):
        """ Запуск стартового скрипта. """
        try:
            with open(self.startup_script, 'r') as script_file:
                commands = script_file.readlines()
            for command in commands:
                self.print_output(self.execute_command(command.strip()))
        except FileNotFoundError:
            self.print_output(f"Startup script {self.startup_script} not found.")

    def on_command_enter(self, event):
        """ Обработчик для ввода команды через клавишу Enter в GUI. """
        command = self.command_entry.get()
        if command:
            result = self.execute_command(command)
            self.print_output(result)
        self.command_entry.delete(0, tk.END)
        return "break"

    def print_output(self, output: str) -> None:
        """ Вывод текста в окно консоли. """
        self.text_output.insert(tk.END, output + "\n")
        self.text_output.yview(tk.END)  # Автопрокрутка вниз

    def start(self):
        """ Запуск эмулятора с GUI. """
        tk.mainloop()

if __name__ == "__main__":
    emulator = Emulator(config_path="config.toml", root=tk.Tk())
    emulator.start()