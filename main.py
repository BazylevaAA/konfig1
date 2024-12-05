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
# Работа с относительными путями вида ../dir1/../dir2
# Доп после 1 дек: Раскрасить файлы и папки разными цветами (файлы - синие, папки - тёмно-фиолетовые)

def normalize_path(path: str) -> str:
    """Удаляет ./ в начале пути и нормализует его."""
    return os.path.normpath(path.lstrip("./"))


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

        self.command_entry = tk.Entry(root, width=80)
        self.command_entry.grid(row=1, column=0, padx=10, pady=10)
        self.command_entry.bind("<Return>", self.on_command_enter)

        self.is_running = True
        self.run_startup_script()

    def load_config(self, config_path: str) -> dict:
        with open(config_path, 'r') as f:
            return toml.load(f)

    def execute_command(self, command: str) -> str:
        pack_virtual_fs()
        command = command.strip()
        parts = command.split()

        if not parts:
            return "No command provided."

        if parts[0] == "ls":
            return self.ls(parts)

        elif parts[0] == "cd":
            return self.cd(parts)

        elif parts[0] == "date":
            return self.date()

        elif parts[0] == "exit":
            exit_command(is_gui_running=True, root=self.text_output.master)

        elif parts[0] == "uniq":
            return self.uniq(parts)

        else:
            return f"Unknown command: {command}"

    def ls(self, parts):
        path = normalize_path(parts[1] if len(parts) > 1 else self.current_directory)
        items = ls(path, self.filesystem_tar)

        output = ""
        for item in items.splitlines():
            is_dir = not "." in item.split("/")[-1]  # Простая проверка на директорию
            color = "blue" if not is_dir else "dark violet"
            self.text_output.insert(tk.END, item + "\n", color)

            # Регистрируем цвета
            self.text_output.tag_configure("blue", foreground="blue")
            self.text_output.tag_configure("dark violet", foreground="dark violet")

    def cd(self, parts: list) -> str:
        if len(parts) < 2 or parts[1] == "":
            return "Error: Directory path is empty."

        target_dir = normalize_path(parts[1])
        if target_dir.startswith("../"):
            steps_up = target_dir.count("../")
            current_parts = self.current_directory.rstrip("/").split("/")
            if steps_up >= len(current_parts):
                target_dir = ""
            else:
                target_dir = "/".join(current_parts[:-steps_up]) + "/" + target_dir.lstrip("../")

        new_directory = cd(self.current_directory, target_dir, self.filesystem_tar)

        if new_directory == self.current_directory:
            return f"Error: Directory '{target_dir}' not found."

        self.current_directory = new_directory
        return f"Changed directory to {self.current_directory}"

    def uniq(self, parts: list) -> str:
        if len(parts) < 2:
            return "No file specified for uniq."
        file_path = os.path.join(self.current_directory, normalize_path(parts[1]))
        return uniq(file_path, self.filesystem_tar)

    def date(self) -> str:
        return date()

    def run_startup_script(self):
        try:
            with open(self.startup_script, 'r') as script_file:
                commands = script_file.readlines()
            for command in commands:
                self.print_output(self.execute_command(command.strip()))
        except FileNotFoundError:
            self.print_output(f"Startup script {self.startup_script} not found.")

    def on_command_enter(self, event):
        command = self.command_entry.get()
        if command:
            result = self.execute_command(command)
            self.print_output(result)
        self.command_entry.delete(0, tk.END)

    def print_output(self, output: str) -> None:
        self.text_output.insert(tk.END, output + "\n")
        self.text_output.yview(tk.END)

    def start(self):
        tk.mainloop()


if __name__ == "__main__":
    emulator = Emulator(config_path="config.toml", root=tk.Tk())
    emulator.start()
