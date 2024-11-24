import shutil
import unittest
import os
import tarfile
from datetime import datetime
from io import StringIO
import sys
from time import sleep
from unittest.mock import patch, MagicMock

# Импортируем функции из ваших файлов
from commands import ls, cd, uniq, date, exit_command


class TestShellEmulator(unittest.TestCase):

    def setUp(self):
        # Подготовка тестовой среды
        self.tar_name = "test_filesystem.tar"

        os.makedirs("dir1", exist_ok=True)
        with open("dir1/file2.txt", "w") as f:
            f.write("Test file 2")

        with open("test.txt", "w") as f:
            f.write("clouds\nsky\nstar\nplanet\nclouds\nstar")

        with tarfile.open(self.tar_name, "w") as tar:
            tar.add("dir1", arcname="dir1")
            tar.add("test.txt", arcname="test.txt")

    def tearDown(self):
        if os.path.exists("dir1"):
            shutil.rmtree("dir1")
        if os.path.exists(self.tar_name):
            os.remove(self.tar_name)
        if os.path.exists("test.txt"):
            os.remove("test.txt")

    def test_ls(self):
        """Тестируем команду ls."""
        # Проверяем содержимое корневой директории
        result = ls("", self.tar_name)
        self.assertEqual(result, "dir1\ntest.txt")  # В корне должны быть только dir1 и test.txt

        # Проверяем содержимое подкаталога dir1
        result = ls("dir1", self.tar_name)
        self.assertEqual(result, "file2.txt")  # В dir1 должен быть только file2.txt

        # Проверяем пустую директорию
        result = ls("empty_dir", self.tar_name)
        self.assertEqual(result, "Directory path is empty.")

        # Проверяем ошибку при неверном пути
        result = ls("non_existent_directory/", self.tar_name)
        self.assertEqual(result, "Directory path is empty.")

    def test_cd(self):
        """Тестируем команду cd."""
        # Переход в поддиректорию
        result = cd("", "dir1", self.tar_name)
        self.assertEqual(result, "dir1")

        # Переход в несуществующую директорию
        result = cd("", "non_existent_dir", self.tar_name)
        self.assertEqual(result, "")

        # Переход назад
        result = cd("dir1", "..", self.tar_name)
        self.assertEqual(result, "")

        # Переход на два уровня вверх
        result = cd("dir1/subdir", "..", self.tar_name)
        self.assertEqual(result, "dir1")

        # Переход в корень
        result = cd("dir1", "/", self.tar_name)
        self.assertEqual(result, "")

        # Оставление текущей директории при ошибке
        result = cd("dir1", "non_existent_subdir", self.tar_name)
        self.assertEqual(result, "dir1")

    def test_uniq(self):
        """Тестируем команду uniq."""

        # Тест 1: Уникальные строки из файла
        result = uniq("test.txt", self.tar_name)
        self.assertIn("clouds", result)
        self.assertIn("sky", result)
        self.assertIn("star", result)
        self.assertIn("planet", result)
        self.assertEqual(result, "clouds\nplanet\nsky\nstar")  # Уникальные строки

        # Тест 2: Пустой файл
        result = uniq("empty_file.txt", self.tar_name)
        self.assertEqual(result, "Error: File 'empty_file.txt' not found inside the archive.")

        # Тест 3: Ошибка при неверном пути к файлу
        result = uniq("non_existent_file.txt", self.tar_name)
        self.assertEqual(result, "Error: File 'non_existent_file.txt' not found inside the archive.")


    @patch("os._exit")
    def test_exit(self, mock_exit):
        """Тестируем команду exit."""
        with patch("builtins.print") as mock_print:
            # Сценарий без GUI
            exit_command(is_gui_running=False)

            # Проверяем, что сообщение было напечатано
            mock_print.assert_called_with("Exiting application...")

            # Проверяем, что вызван os._exit(0)
            mock_exit.assert_called_once_with(0)

            # Сценарий с GUI
            mock_root = MagicMock()
            exit_command(is_gui_running=True, root=mock_root)

            # Проверяем, что destroy был вызван
            mock_root.destroy.assert_called_once()


if __name__ == "__main__":
    unittest.main()
