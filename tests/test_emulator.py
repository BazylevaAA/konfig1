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


if __name__ == "__main__":
    unittest.main()
