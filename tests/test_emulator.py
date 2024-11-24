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


if __name__ == "__main__":
    unittest.main()
