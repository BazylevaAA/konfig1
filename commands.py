import datetime
import os
import tarfile
import chardet
import tkinter as tk


def ls(current_dir, tar_path, text_output):
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
            # Убираем './' если оно присутствует в начале пути
            member_name = member.name.lstrip("./")

            # Фильтруем только файлы и директории в пределах текущей директории
            if member_name.startswith(current_dir):
                stripped_name = member_name[len(current_dir):]

                # Убираем / на конце для файлов и директорий
                stripped_name = stripped_name.rstrip("/")

                # Добавляем в список с цветами
                if member.isdir():
                    contents.append((stripped_name, 'directory'))  # Фиолетовый для директорий
                else:
                    contents.append((stripped_name, 'file'))  # Синий для файлов

        # Если содержимое пусто, возвращаем сообщение
        if not contents:
            return "Directory is empty."

        # Не очищаем вывод, а добавляем вывод в конец
        for item in sorted(contents):
            name, type_of_item = item
            if type_of_item == 'directory':
                text_output.insert(tk.END, name + "\n", "directory")
            else:
                text_output.insert(tk.END, name + "\n", "file")

        # Автопрокрутка вниз
        text_output.yview(tk.END)

    return ""  # Возвращаем пустое сообщение, так как вывод будет в text_output

def cd(current_dir, target_dir, tar_path):
    try:
        with tarfile.open(tar_path, "r") as tar:
            # Если путь "..", перемещаемся на уровень вверх
            if target_dir == "..":
                # Если текущий путь пустой (корень), остаемся в корне
                if not current_dir:
                    return ""
                # Убираем последний элемент из пути
                return "/".join(current_dir.rstrip("/").split("/")[:-1])

            elif target_dir == "/":
                # Если путь "/", переходим в корень
                return ""

            else:
                # Строим новый путь, комбинируя текущий и целевой
                target_path = os.path.normpath(f"{current_dir.rstrip('/')}/{target_dir}".lstrip("/"))

                # Печатаем все доступные директории и файлы для отладки
                print("Checking directories in archive:")
                for member in tar.getmembers():
                    print(f"Found: {member.name}")  # Печатаем все пути в архиве
                    # Проверяем, существует ли директория в архиве
                    if member.isdir():
                        # Убираем './' и / на конце, если есть
                        normalized_member_name = member.name.lstrip("./").rstrip("/")
                        if normalized_member_name == target_path:
                            return target_path

                # Если директория не найдена, возвращаем текущий путь
                return current_dir
    except Exception as e:
        print(f"Error in cd: {e}")
        return current_dir

def uniq(file_path, tar_path, current_dir=""):
    try:
        # Если указан current_dir, добавляем его к file_path
        if current_dir:
            # Проверяем, не начинается ли file_path с ./ или /
            if not file_path.startswith(("./", "/")):
                file_path = os.path.join(current_dir, file_path)

        # Нормализуем путь
        normalized_path = os.path.normpath(file_path).replace("\\", "/")

        # Убираем начальный "./" для пути в архиве
        archive_path = normalized_path.lstrip("./")

        with tarfile.open(tar_path, "r") as tar:
            # Проверяем содержимое архива
            for member in tar.getmembers():
                member_name = member.name.lstrip("./")  # Убираем начальный './'
                if member_name == archive_path:
                    # Извлекаем файл
                    file = tar.extractfile(member)
                    if not file:
                        return f"Error: Unable to read file '{file_path}'."

                    # Читаем содержимое файла
                    file_content = file.read()

                    # Определяем кодировку
                    detected = chardet.detect(file_content)
                    encoding = detected.get('encoding', 'utf-8')

                    # Обрабатываем строки
                    lines = file_content.decode(encoding).splitlines()
                    unique_lines = sorted(set(line.strip() for line in lines if line.strip()))
                    return "\n".join(unique_lines)

            # Если файл не найден
            return f"Error: File '{archive_path}' not found inside the archive."

    except Exception as e:
        return f"An error occurred: {str(e)}"


def date():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def exit_command(is_gui_running, root):
    if is_gui_running:
        root.quit()
    else:
        exit()