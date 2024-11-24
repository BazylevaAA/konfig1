import datetime
import os
import tarfile
import chardet


def ls(current_dir, tar_path):
    if not os.path.exists(tar_path):
        return f"Error: Archive '{tar_path}' not found."

    with tarfile.open(tar_path, "r") as tar:
        contents = []

        # Формируем путь для фильтрации
        if current_dir:
            current_dir = current_dir.rstrip("/") + "/"
        else:
            current_dir = ""

        for member in tar.getmembers():
            # Проверяем, лежит ли элемент в указанной директории
            if member.name.startswith(current_dir):
                # Убираем префикс текущей директории из имени
                stripped_name = member.name[len(current_dir):]

                # Учитываем только элементы верхнего уровня
                if "/" not in stripped_name.rstrip("/"):
                    contents.append(stripped_name.rstrip("/"))

        # Если содержимое пусто, возвращаем сообщение
        if not contents:
            return "Directory path is empty."

        # Сортируем содержимое и возвращаем
        return "\n".join(sorted(contents))

def cd(current_dir, target_dir, tar_path):
    try:
        with tarfile.open(tar_path, "r") as tar:
            if target_dir == "..":
                # Если текущая директория пуста, остаемся в корне
                if not current_dir:
                    return ""
                # Переход на уровень вверх: убираем последний компонент пути
                return "/".join(current_dir.rstrip("/").split("/")[:-1])

            elif target_dir == "/":
                # Возврат в корневую директорию
                return ""

            else:
                # Переход в указанную директорию
                if current_dir:
                    target_path = f"{current_dir.rstrip('/')}/{target_dir}".lstrip("/")
                else:
                    target_path = target_dir

                # Проверяем, существует ли указанная директория
                for member in tar.getmembers():
                    if member.isdir() and member.name.rstrip("/") == target_path.rstrip("/"):
                        return target_path
                return current_dir  # Если директория не найдена, остаемся в текущей
    except Exception as e:
        return current_dir




def uniq(file_path, tar_path, current_dir=""):
    try:
        with tarfile.open(tar_path, "r") as tar:
            if current_dir:
                file_path = os.path.join(current_dir, file_path).lstrip(os.sep)

            try:
                file = tar.extractfile(file_path)
                file_content = file.read()  # Считываем весь файл как байты

                # Определяем кодировку файла
                detected = chardet.detect(file_content)
                encoding = detected['encoding']

                if encoding is None:
                    return f"Error: Could not determine encoding for '{file_path}'."

                # Декодируем файл в строки
                lines = file_content.decode(encoding).splitlines()

                # Уникализация строк
                unique_lines = sorted(set(line.strip() for line in lines))
                return "\n".join(unique_lines)

            except KeyError:
                return f"Error: File '{file_path}' not found inside the archive."
    except FileNotFoundError:
        return f"Error: Archive '{tar_path}' not found.'"


def date():
    return str(datetime.datetime.now())

def exit_command(is_gui_running=True, root=None):
    """
    Завершает работу приложения.

    :param is_gui_running: Флаг, указывает, используется ли GUI.
    :param root: Объект корневого окна tkinter, если приложение работает с GUI.
    :return: Сообщение о завершении работы.
    """
    if is_gui_running and root:
        root.destroy()  # Закрываем главное окно tkinter
    print("Exiting application...")
    os._exit(0)  # Полное завершение программы




