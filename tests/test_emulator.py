import unittest
import os
import tarfile
import tkinter as tk
import datetime
from commands import ls, cd, uniq, date, exit_command


class MockTextOutput:
    """Класс для эмуляции текстового вывода в GUI."""

    def __init__(self):
        self.text = []

    def insert(self, _, text, tag=None):
        self.text.append(text)

    def get_text(self):
        return "".join(self.text)

    def yview(self, *args):
        pass


class TestUniqFunction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Подготовка тестового архива перед выполнением тестов."""
        cls.test_tar_path = "test_archive.tar"
        with tarfile.open(cls.test_tar_path, "w") as tar:
            # Создаем тестовые файлы для архива
            file1_content = b"line1\nline2\nline3\nline1\nline2\n"
            file2_content = b""  # Пустой файл
            os.makedirs("test_dir", exist_ok=True)

            # Записываем файл с содержимым
            with open("test_dir/file1.txt", "wb") as f:
                f.write(file1_content)

            # Пустой файл
            with open("test_dir/file2.txt", "wb") as f:
                f.write(file2_content)

            tar.add("test_dir/file1.txt", arcname="file1.txt")
            tar.add("test_dir/file2.txt", arcname="file2.txt")

    @classmethod
    def tearDownClass(cls):
        """Удаление тестового архива и временных файлов."""
        os.remove(cls.test_tar_path)
        if os.path.exists("test_dir"):
            for file in os.listdir("test_dir"):
                os.remove(os.path.join("test_dir", file))
            os.rmdir("test_dir")

    def test_existing_file_with_content(self):
        """Тест: файл существует и содержит строки."""
        result = uniq("file1.txt", self.test_tar_path)
        expected_result = "line1\nline2\nline3"  # Ожидаем уникальные строки в алфавитном порядке
        self.assertEqual(result, expected_result)

    def test_file_not_found(self):
        """Тест: файл отсутствует в архиве."""
        result = uniq("nonexistent.txt", self.test_tar_path)
        expected_result = "Error: File 'nonexistent.txt' not found inside the archive."
        self.assertEqual(result, expected_result)

    def test_empty_file(self):
        """Тест: файл существует, но пустой."""
        result = uniq("file2.txt", self.test_tar_path)
        expected_result = ""  # Пустая строка, если файл пустой
        self.assertEqual(result, expected_result)


class TestLSFunction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Создаем временную файловую структуру
        os.makedirs("test_fs/dir1", exist_ok=True)
        os.makedirs("test_fs/dir2", exist_ok=True)
        with open("test_fs/file1.txt", "w") as f:
            f.write("File 1 content")
        with open("test_fs/dir1/file2.txt", "w") as f:
            f.write("File 2 content")

        # Создаем тестовый архив
        with tarfile.open("test_archive.tar", "w") as tar:
            tar.add("test_fs", arcname="my_virtual_fs")

    @classmethod
    def tearDownClass(cls):
        # Удаляем временные файлы и папки
        if os.path.exists("test_archive.tar"):
            os.remove("test_archive.tar")
        if os.path.exists("test_fs"):
            for root, dirs, files in os.walk("test_fs", topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir("test_fs")

    def setUp(self):
        # Создаем виджет text для вывода
        self.root = tk.Tk()
        self.text_output = tk.Text(self.root)
        self.text_output.tag_configure("directory", foreground="purple")
        self.text_output.tag_configure("file", foreground="blue")

    def tearDown(self):
        self.root.destroy()

    def test_archive_not_found(self):
        """Тест: архив не найден."""
        result = ls("my_virtual_fs", "nonexistent_archive.tar", self.text_output)
        self.assertEqual(result, "Error: Archive 'nonexistent_archive.tar' not found.")
        self.assertEqual(self.text_output.get("1.0", tk.END).strip(), "")

    def test_empty_directory(self):
        """Тест: пустая директория."""
        result = ls("my_virtual_fs/dir2", "test_archive.tar", self.text_output)
        self.assertEqual(result, "Directory is empty.")
        self.assertEqual(self.text_output.get("1.0", tk.END).strip(), "")

    def test_list_directory_contents(self):
        """Тест: содержимое директории."""
        result = ls("my_virtual_fs", "test_archive.tar", self.text_output)
        self.assertEqual(result, "")  # Ожидаем пустой возврат, т.к. вывод идет в text_output

        # Проверяем содержимое text_output
        output = self.text_output.get("1.0", tk.END).strip()
        expected_output = "dir1\ndir1/file2.txt\ndir2\nfile1.txt"
        self.assertEqual(output, expected_output)


from unittest.mock import patch, MagicMock


class TestCdFunction(unittest.TestCase):

    # Тест для перехода на родительскую директорию
    @patch("tarfile.open")
    def test_cd_to_parent_directory(self, mock_tarfile):
        # Мокаем поведение tarfile
        mock_tar = MagicMock()
        mock_tarfile.return_value.__enter__.return_value = mock_tar
        mock_tar.getmembers.return_value = []

        current_dir = "my_virtual_fs/dir1"
        target_dir = ".."
        tar_path = "test_archive.tar"

        result = cd(current_dir, target_dir, tar_path)
        self.assertEqual(result, "my_virtual_fs")  # Ожидаем переход в родительскую директорию

    # Тест для перехода в корневую директорию
    @patch("tarfile.open")
    def test_cd_to_root_directory(self, mock_tarfile):
        # Мокаем поведение tarfile
        mock_tar = MagicMock()
        mock_tarfile.return_value.__enter__.return_value = mock_tar
        mock_tar.getmembers.return_value = []

        current_dir = "my_virtual_fs/dir1"
        target_dir = "/"
        tar_path = "test_archive.tar"

        result = cd(current_dir, target_dir, tar_path)
        self.assertEqual(result, "")  # Ожидаем, что вернется корень

    # Тест для перехода в существующую директорию в архиве
    @patch("tarfile.open")
    def test_cd_to_non_existing_directory(self, mock_tarfile):
        # Мокаем поведение tarfile
        mock_tar = MagicMock()
        mock_tarfile.return_value.__enter__.return_value = mock_tar
        # Мокаем список файлов и директорий в архиве
        mock_tar.getmembers.return_value = [tarfile.TarInfo(name="my_virtual_fs/dir1"),
                                            tarfile.TarInfo(name="my_virtual_fs/dir2")]

        current_dir = "my_virtual_fs"
        target_dir = "dir3"  # Директория, которой нет в архиве
        tar_path = "test_archive.tar"

        # Переход в несуществующую директорию
        result = cd(current_dir, target_dir, tar_path)

        # Ожидаем, что вернется текущая директория, т.е. "my_virtual_fs"
        self.assertEqual(result, "my_virtual_fs")


class TestDateFunction(unittest.TestCase):

    # Тест на корректность формата возвращаемой даты
    def test_date_format(self):
        result = date()
        try:
            datetime.datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            self.fail("Date format is incorrect")

    # Тест на стабильность возвращаемой даты
    def test_date_consistency(self):
        result1 = date()
        result2 = date()
        self.assertEqual(result1, result2)

    # Тест с моком времени
    @patch('datetime.datetime')
    def test_date_with_mock(self, mock_datetime):
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2024-12-09 17:30:45"
        mock_datetime.now.return_value = mock_now
        result = date()
        self.assertEqual(result, "2024-12-09 17:30:45")


import unittest
from unittest.mock import MagicMock, patch

class TestExitCommand(unittest.TestCase):

    # Тест с мокированием Tkinter
    @patch('tkinter.Tk')
    def test_exit_with_gui_running(self, MockTk):
        mock_root = MagicMock()
        MockTk.return_value = mock_root  # Мокаем Tk, чтобы не вызывать реальный Tkinter
        exit_command(True, mock_root)
        mock_root.quit.assert_called_once()  # Проверка, что метод quit был вызван

    # Тест для случая, когда is_gui_running == False
    @patch('builtins.exit')
    def test_exit_without_gui_running(self, mock_exit):
        mock_root = MagicMock()
        exit_command(False, mock_root)
        mock_exit.assert_called_once()
        mock_root.quit.assert_not_called()

    # Тест с другими значениями для is_gui_running
    @patch('builtins.exit')
    def test_exit_with_invalid_gui_state(self, mock_exit):
        mock_root = MagicMock()
        exit_command(False, mock_root)
        mock_exit.assert_called_once()
        mock_root.quit.assert_not_called()

        exit_command(True, mock_root)
        mock_root.quit.assert_called_once()


if __name__ == '__main__':
    unittest.main()

if __name__ == "__main__":
    unittest.main()
